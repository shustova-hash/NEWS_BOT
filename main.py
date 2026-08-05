import os
import asyncio
import sys
from dotenv import load_dotenv
from telegram import Bot
from google import genai
from google.genai import types

# Завантаження змінних оточення
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_KIDS_ID = os.getenv("CHANNEL_KIDS_ID")
CHANNEL_ADULTS_ID = os.getenv("CHANNEL_ADULTS_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not all([TELEGRAM_BOT_TOKEN, CHANNEL_KIDS_ID, CHANNEL_ADULTS_ID, GEMINI_API_KEY]):
    print("❌ Помилка: Не всі обов'язкові змінні середовища встановлені!")
    print("Перевірте наявність TELEGRAM_BOT_TOKEN, CHANNEL_KIDS_ID, CHANNEL_ADULTS_ID, GEMINI_API_KEY.")
    sys.exit(1)

# Ініціалізація клієнтів
bot = Bot(token=TELEGRAM_BOT_TOKEN)
ai_client = genai.Client(api_key=GEMINI_API_KEY)


def generate_post_with_gemini(audience_type: str) -> str:
    """Використовує Google Gemini з увімкненим пошуком Google для збору новин та написання поста."""
    if audience_type == "kids":
        prompt = """
        Знайди найсвіжіші та найцікавіші новини у сфері ІТ, штучного інтелекту, робототехніки чи ігрових технологій за останні 24-48 годин, які будуть цікаві дітям та підліткам віком 7-14 років.
        
        На основі знайденого сформуй один захопливий пост для Telegram-каналу українською мовою.

        Вимоги до поста для дітей:
        1. Проста, драйвова та зрозуміла мова без складного жаргону. Якщо є складні терміни — поясни їх на аналогіях (наприклад, з Minecraft, Roblox чи повсякденного життя).
        2. Заголовок із яскравими емодзі.
        3. 2-3 короткі цікаві факти/новини.
        4. Запитання в кінці для обговорення в коментарях.
        5. Форматування: використовуй лише стандартний Markdown (наприклад *жирний*, _курсив_).
        6. Обсяг: до 1200 символів.
        """
    else:
        prompt = """
        Знайди найважливіші та найсвіжіші новини у сфері ІТ, штучного інтелекту, стартапів та цифрових технологій за останні 24-48 годин для дорослої аудиторії (фахівців, підприємців, інвесторів).

        На основі знайденого сформуй стислий та якісний дайджест для Telegram-каналу українською мовою.

        Вимоги до поста для дорослих:
        1. Професійний, аналітичний та лаконічний стиль.
        2. Яскравий заголовок з емодзі.
        3. Основні новини у вигляді списку (Bullet Points): заголовок новини, 1-2 речення про суть та чому це важливо.
        4. Короткий підсумок або головна думка дня.
        5. Форматування: використовуй лише стандартний Markdown (наприклад *жирний*, _курсив_).
        6. Обсяг: до 1500 символів.
        """

    # Модель Gemini 1.5 Flash із пошуковим заземленням (Google Search Grounding)
    response = ai_client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[{"google_search": {}}],
            temperature=0.7,
        ),
    )
    return response.text


async def run():
    print("⏳ Розпочато процес збору новин та генерації постів за допомогою Google Gemini...")

    # 1. Пост для дітей (Канал №1)
    try:
        print("👶 Генерація поста для дітей (7-14 років)...")
        kids_post = generate_post_with_gemini("kids")
        await bot.send_message(chat_id=CHANNEL_KIDS_ID, text=kids_post, parse_mode="Markdown")
        print("✅ Пост успішно опубліковано у дитячому каналі!")
    except Exception as e:
        print(f"❌ Помилка публікації у дитячий канал: {e}")

    # Затримка 15 секунд для дотримання лімітів безкоштовного тарифу (Free Tier)
    print("⏳ Пауза 15 секунд для дотримання лімітів API...")
    await asyncio.sleep(15)

    # 2. Пост для дорослих (Канал №2)
    try:
        print("👨‍💼 Генерація поста для дорослих...")
        adults_post = generate_post_with_gemini("adults")
        await bot.send_message(chat_id=CHANNEL_ADULTS_ID, text=adults_post, parse_mode="Markdown")
        print("✅ Пост успішно опубліковано у дорослому каналі!")
    except Exception as e:
        print(f"❌ Помилка публікації у дорослий канал: {e}")


if __name__ == "__main__":
    asyncio.run(run())
