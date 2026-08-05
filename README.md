# 🤖 Telegram IT & AI News Bot (Gemini + GitHub Actions)

Автоматичний Телеграм-бот, який щодня шукає найновіші IT та ШІ новини через **Google Gemini (з пошуком Google Search Grounding)**, генерує 2 адаптовані пости (для дітей 7–14 років та для дорослих) і публікує їх у 2 відповідні Telegram-канали.

Запуск здійснюється повністю **безкоштовно** за розкладом через **GitHub Actions**.

---

## 🛠️ Склад проекту

- [`main.py`](file:///c:/Users/shust/Documents/AI/NEWS_BOT/main.py) — основний Python-скрипт з логікою генерації та відправки постів.
- [`requirements.txt`](file:///c:/Users/shust/Documents/AI/NEWS_BOT/requirements.txt) — необхідні бібліотеки (`google-genai`, `python-telegram-bot`, `python-dotenv`).
- [`.github/workflows/daily_news.yml`](file:///c:/Users/shust/Documents/AI/NEWS_BOT/.github/workflows/daily_news.yml) — конфігурація GitHub Actions для щоденного автозапуску о 09:00 за Києвом.
- [`.env.example`](file:///c:/Users/shust/Documents/AI/NEWS_BOT/.env.example) — шаблон змінних середовища для локального тестування.

---

## 📋 Покрокова інструкція з налаштування

### Крок 1. Підготовка Telegram Ботів та Каналів
1. Відкрийте [@BotFather](https://t.me/BotFather) у Telegram і створіть бота за допомогою теми `/newbot`. Збережіть `TELEGRAM_BOT_TOKEN`.
2. Створіть 2 канали:
   - **Канал №1** (Тема №1: Новини для дітей 7-14 років).
   - **Канал №2** (Тема №2: Новини для дорослих).
3. Додайте вашого бота в обидва канали як **Адміністратора** з правом публікації дописів.
4. Скопіюйте username або ID каналів (наприклад, `@kids_it_news` та `@adults_it_news`).

---

### Крок 2. Отримання Google Gemini API Ключа
1. Перейдіть у [Google AI Studio](https://aistudio.google.com/).
2. Натисніть **Get API Key** -> **Create API Key**.
3. Збережіть отриманий `GEMINI_API_KEY`. *(Використання безкоштовне у межах стандартних лімітів)*.

---

### Крок 3. Налаштування хостингу на GitHub

1. Створіть репозиторій на GitHub та завантажте туди всі файли проекту:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/ВАШ_USERNAME/НАЗВА_РЕПОЗИТОРІЮ.git
   git push -u origin main
   ```

2. Додайте Секрети у GitHub (Secrets):
   - Перейдіть у репозиторії: `Settings` ➔ `Secrets and variables` ➔ `Actions`.
   - Натисніть **New repository secret** і додайте 4 секрети:
     - `TELEGRAM_BOT_TOKEN` : ваш токен бота з BotFather.
     - `CHANNEL_KIDS_ID` : ID або username Каналу №1 (наприклад `@kids_it_news`).
     - `CHANNEL_ADULTS_ID` : ID або username Каналу №2 (наприклад `@adults_it_news`).
     - `GEMINI_API_KEY` : ваш ключ Google Gemini API.

---

### 🚀 Перевірка та ручний запуск

1. Зайдіть у вкладку **Actions** у вашому GitHub репозиторії.
2. Виберіть workflow **Daily IT & AI News Posting**.
3. Натисніть **Run workflow** -> **Run workflow**.
4. Зачекайте 10–20 секунд і перевірте ваші Telegram-канали!

Бот буде автоматично запускатися щодня о **09:00 за київським часом** (06:00 UTC).
