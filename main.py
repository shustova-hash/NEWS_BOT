import os
import asyncio
import sys
from dotenv import load_dotenv
from telegram import Bot, LinkPreviewOptions
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
    """Безкоштовно шукає свіжі новини в Інтернеті разом із посиланнями."""
    print(f"🔍 Пошук новин в Інтернеті за запитом: '{query}'...")
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, timelimit="d", max_results=5):
                title = r.get("title", "")
                snippet = r.get("body", "")
                url = r.get("href", "")
                if url:
                    results.append(f"- **{title}**: {snippet}\n  Джерело: {url}")
                else:
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
        return ["gemma-4-26b-a4b-it", "gemini-flash-latest"]


def generate_post_with_gemini(news_text: str, audience_type: str) -> str:
    """Генерує підсумковий пост на основі знайдених новин."""
    if audience_type == "kids":
        prompt = f"""
        Ти — захопливий та дружній ведучий IT-каналу для дітей 7-14 років.
        Ось останні новини технологій та штучного інтелекту:

        {news_text}

        На основі цих новин напиши один яскравий пост для Telegram-каналу українською мовою.

        КРИТИЧНО ВАЖЛИВІ РУБРИКИ ТА ФОРМАТУВАННЯ:
        1. НЕ ДУМАЙ і НЕ ПИШИ ЖОДНИХ ВСТУПНИХ СЛІВ ВІД СЕБЕ! (Категорично заборонено писати "Оскільки...", "Я підготував...", "Ось ваші новини...").
        2. Пост повинен починатися ОДРАЗУ з першого символу заголовка!
        3. КАТЕГОРИЧНО ЗАБОРОНЕНО використовувати зірочки (** або *) та Markdown-символи (#, _, `). Пиши чистою мовою без зірочок! Заголовки виділяй ЕМОДЗІ та ВЕЛИКИМИ ЛІТЕРАМИ.
        4. Проста, цікава мова без складного жаргону. Пояснюй складне через ігри (Minecraft, Roblox) чи повсякденні приклади.
        5. 2-3 цікаві новини або факти у вигляді списку.
        6. В кінці поста обов'язково додай посилання на оригінал у форматі:
           🔗 Докладніше: URL
        7. В самому кінці — цікаве запитання до дітей для обговорення.
        8. Загальний обсяг: до 1200 символів.
        """
    else:
        prompt = f"""
        Ти — досвідчений IT-аналітик.
        Ось останні новини технологій та штучного інтелекту:

        {news_text}

        На основі цих новин створи стислий, якісний дайджест для Telegram-каналу для дорослих українською мовою.

        КРИТИЧНО ВАЖЛИВІ РУБРИКИ ТА ФОРМАТУВАННЯ:
        1. НЕ ДУМАЙ і НЕ ПИШИ ЖОДНИХ ВСТУПНИХ СЛІВ ВІД СЕБЕ! (Категорично заборонено писати "Оскільки...", "Я підготував...", "Аналізуючи активність...").
        2. Пост повинен починатися ОДРАЗУ з першого символу заголовка з емодзі!
        3. КАТЕГОРИЧНО ЗАБОРОНЕНО використовувати зірочки (** або *) та будь-які Markdown-символи (#, _, `). Пиши чистою мовою без зірочок! Для акцентів використовуй ЕМОДЗІ та ВЕЛИКІ ЛІТЕРИ.
        4. Професійний, діловий та лаконічний тон.
        5. Основні новини у вигляді списку з емодзі.
        6. В кінці поста обов'язково додай посилання на джерело у форматі:
           🔗 Читати детальніше: URL
        7. Короткий підсумок або думка дня.
        8. Загальний обсяг: до 1500 символів.
        """

    # Список найбільш стабільних та робочих моделей для даного ключа
    preferred_models = [
        "gemma-4-26b-a4b-it",
        "gemma-4-31b-it",
        "gemini-flash-latest",
        "gemini-flash-lite-latest",
        "gemini-pro-latest"
    ]
    
    # Спочатку пробуємо рекомендовані робочі моделі
    all_models = preferred_models + [m for m in get_available_gemini_models() if m not in preferred_models]

    last_error = None
    for model_name in all_models:
        # Пропускаємо аудіо, ембеддінг та відео моделі
        if any(bad in model_name for bad in ["embed", "imagen", "veo", "audio", "tts", "2.5-flash"]):
            continue
        try:
            print(f"🤖 Звертаємося до Gemini моделі: {model_name}...")
            response = ai_client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            if response and response.text:
                clean_text = response.text.replace("**", "").replace("*", "").strip()
                print(f"✨ Пост успішно згенеровано моделлю {model_name}!")
                return clean_text
        except Exception as e:
            last_error = e
            continue

    raise Exception(f"Не вдалося згенерувати пост жодною з моделей. Останнє повідомлення: {last_error}")


async def run():
    print("⏳ Розпочато процес збору новин та генерації постів...")
    print(f"📌 Налаштовані канали: Kids = '{CHANNEL_KIDS_ID}', Adults = '{CHANNEL_ADULTS_ID}'")

    # Налаштування великого прев'ю посилань
    preview_config = LinkPreviewOptions(is_disabled=False, prefer_large_media=True)

    # 1. Пост для дітей (Канал №1)
    try:
        print("👶 Шукаємо новини та генеруємо пост для дітей (7-14 років)...")
        kids_news = fetch_web_news("artificial intelligence technology gaming news for kids")
        kids_post = generate_post_with_gemini(kids_news, "kids")
        print(f"📤 Відправляємо пост у дитячу групу ({CHANNEL_KIDS_ID})...")
        await bot.send_message(chat_id=CHANNEL_KIDS_ID, text=kids_post, link_preview_options=preview_config)
        print("✅ Пост успішно опубліковано у дитячій групі!")
    except Exception as e:
        print(f"❌ Помилка публікації у дитячий канал: {e}")

    await asyncio.sleep(5)

    # 2. Пост для дорослих (Канал №2)
    try:
        print("👨‍💼 Шукаємо новини та генеруємо пост для дорослих...")
        adults_news = fetch_web_news("IT artificial intelligence tech business news")
        adults_post = generate_post_with_gemini(adults_news, "adults")
        print(f"📤 Відправляємо пост у дорослу групу ({CHANNEL_ADULTS_ID})...")
        await bot.send_message(chat_id=CHANNEL_ADULTS_ID, text=adults_post, link_preview_options=preview_config)
        print("✅ Пост успішно опубліковано у дорослій групі!")
    except Exception as e:
        print(f"❌ Помилка публікації у дорослий канал: {e}")


if __name__ == "__main__":
    asyncio.run(run())
