import os
import asyncio
import sys
from dotenv import load_dotenv
from telegram import Bot
from google import genai
from ddgs import DDGS

# Завантаження змінних оточення
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_KIDS_ID = os.getenv("CHANNEL_KIDS_ID")
CHANNEL_ADULTS_ID = os.getenv("CHANNEL_ADULTS_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not all([TELEGRAM_BOT_TOKEN, CHANNEL_KIDS_ID, CHANNEL_ADULTS_ID, GEMINI_API_KEY]):
    print("❌ Помилка: Не всі обов'язкові змінні середовища встановлені!")
    sys.exit(1)

# Ініціалізація клієнтів
bot = Bot(token=TELEGRAM_BOT_TOKEN)
ai_client = genai.Client(api_key=GEMINI_API_KEY)


def fetch_web_news(query: str) -> str:
    """Безкоштовно шукає свіжі новини в Інтернеті."""
    print(f"🔍 Пошук новин в Інтернеті за запитом: '{query}'...")
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, timelimit="d", max_results=5):
                title = r.get("title", "")
                snippet = r.get("body", "")
                results.append(f"- **{title}**: {snippet}")
    except Exception as e:
        print(f"⚠️ Попередження пошуку: {e}")

    if not results:
        return "Актуальні новини у сфері цифрових технологій та штучного інтелекту."
    return "\n\n".join(results)


def get_available_gemini_models():
    """Отримує перелік доступних моделей Gemini для даного API ключа."""
    try:
        models = list(ai_client.models.list())
        names = []
        for m in models:
            clean_name = m.name.replace("models/", "")
            names.append(clean_name)
        return names
    except Exception as e:
        print(f"⚠️ Не вдалося отримати список моделей через API: {e}")
        return ["gemini-2.0-flash-lite", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"]


def generate_post_with_gemini(news_text: str, audience_type: str) -> str:
    """Генерує підсумковий пост на основі знайдених новин."""
    if audience_type == "kids":
        prompt = f"""
        Ти — захопливий та дружній ведучий IT-каналу для дітей 7-14 років.
        Ось останні новини технологій та штучного інтелекту:

        {news_text}

        На основі цих новин напиши один яскравий пост для Telegram-каналу українською мовою.

        Вимоги:
        1. Проста, драйвова мова без складного жаргону. Пояснюй складне через ігри (Minecraft, Roblox) чи приклади.
        2. Кілька кольорових емодзі у заголовку та тексті.
        3. 2-3 цікаві новини/факти.
        4. Обов'язкове запитання в кінці для підписників.
        5. До 1200 символів.
        """
    else:
        prompt = f"""
        Ти — досвідчений IT-аналітик.
        Ось останні новини технологій та штучного інтелекту:

        {news_text}

        На основі цих новин створи стислий, якісний дайджест для Telegram-каналу для дорослих українською мовою.

        Вимоги:
        1. Професійний, діловий та лаконічний тон.
        2. Яскравий заголовок з емодзі.
        3. Основні новини у вигляді списку (Bullet Points).
        4. Короткий висновок або головна думка дня.
        5. До 1500 символів.
        """

    # Динамічно отримуємо список доступних моделей для даного акаунта
    models_to_try = get_available_gemini_models()
    print(f"ℹ️ Доступні моделі для вашого API ключа: {models_to_try}")

    last_error = None
    for model_name in models_to_try:
        # Пропускаємо спеціальні ембеддінг-моделі
        if "embed" in model_name or "imagen" in model_name or "text-embedding" in model_name:
            continue
        try:
            print(f"🤖 Пробуємо згенерувати пост моделлю: {model_name}...")
            response = ai_client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            if response and response.text:
                return response.text
        except Exception as e:
            print(f"⚠️ Модель {model_name} повернула помилку: {e}")
            last_error = e
            continue

    raise Exception(f"Не вдалося згенерувати пост жодною з доступних моделей. Останнє повідомлення: {last_error}")


async def run():
    print("⏳ Розпочато процес збору новин та генерації постів...")

    # 1. Пост для дітей (Канал №1)
    try:
        print("👶 Шукаємо новини та генеруємо пост для дітей (7-14 років)...")
        kids_news = fetch_web_news("artificial intelligence technology gaming news for kids")
        kids_post = generate_post_with_gemini(kids_news, "kids")
        await bot.send_message(chat_id=CHANNEL_KIDS_ID, text=kids_post)
        print("✅ Пост успішно опубліковано у дитячому каналі!")
    except Exception as e:
        print(f"❌ Помилка публікації у дитячий канал: {e}")

    await asyncio.sleep(5)

    # 2. Пост для дорослих (Канал №2)
    try:
        print("👨‍💼 Шукаємо новини та генеруємо пост для дорослих...")
        adults_news = fetch_web_news("IT artificial intelligence tech business news")
        adults_post = generate_post_with_gemini(adults_news, "adults")
        await bot.send_message(chat_id=CHANNEL_ADULTS_ID, text=adults_post)
        print("✅ Пост успішно опубліковано у дорослому каналі!")
    except Exception as e:
        print(f"❌ Помилка публікації у дорослий канал: {e}")


if __name__ == "__main__":
    asyncio.run(run())
