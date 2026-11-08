# PRO-CLEAN RENT — Автопостер для Facebook та Instagram (GitHub Actions + Gemini AI)

Цей репозиторій автоматично генерує нові продаючі дописи українською мовою через **Google Gemini API**, бере відповідні фірмові ілюстрації з папки `images/` і публікує їх одночасно на вашу бізнес-сторінку **Facebook (`PRO-CLEAN Дрогобич`)** та в **Instagram (`@proclean.rent.ua`)** через офіційний **Meta Graph API**.

- **Вартість роботи**: 0 грн (повністю безкоштовно на GitHub Actions).
- **Графік публікацій**: щовівторка, щочетверга та щосуботи о 09:30 ранку за київським часом (або будь-коли вручну кнопкою `Run workflow`).
- **Жодних зовнішніх бібліотек**: скрипт `autopost.py` використовує лише стандартну бібліотеку Python 3.11 (`urllib`), тому ніколи не ламається через оновлення пакетів.

---

## Крок 1. Створіть публічний репозиторій на GitHub (2 хвилини)

> **Важливо**: Репозиторій має бути **Public (Публічним)**, щоб сервери Facebook та Instagram могли завантажити картинки з папки `images/` за прямим посиланням `raw.githubusercontent.com` (або всі ваші секретні ключі все одно надійно сховані у `GitHub Secrets` і нікому не видимі!).

1. Зайдіть на [github.com/new](https://github.com/new).
2. Назвіть репозиторій, наприклад: `proclean-autoposter`.
3. Оберіть **Public** і натисніть **Create repository**.
4. Натисніть **uploading an existing file**, перетягніть усі файли та папки з цього розпакованого архіву (`.github/workflows/autopost.yml`, `autopost.py`, папку `images/` та `README.md`) і натисніть **Commit changes**.

---

## Крок 2. Отримайте безкоштовний ключ `GEMINI_API_KEY` (1 хвилина)

1. Відкрийте [Google AI Studio (aistudio.google.com/apikey)](https://aistudio.google.com/apikey) під своїм Google-акаунтом.
2. Натисніть **Create API key** → скопіюйте згенерований ключ.

---

## Крок 3. Отримайте токен Meta (`META_PAGE_ACCESS_TOKEN`, `FB_PAGE_ID`, `IG_USER_ID`) (5 хвилин)

1. Переконайтеся, що ваш Instagram `@proclean.rent.ua` переведений у **Професійний (Бізнес) акаунт** і прив'язаний до вашої сторінки Facebook `PRO-CLEAN Дрогобич`.
2. Зайдіть на [developers.facebook.com/apps](https://developers.facebook.com/apps) → натисніть **Create App** → оберіть **Other** → **Business** → вкажіть назву `ProClean AutoPoster`.
3. Відкрийте інструмент [Graph API Explorer](https://developers.facebook.com/tools/explorer/):
   - У полі **Meta App** праворуч оберіть ваш додаток `ProClean AutoPoster`.
   - У полі **User or Page** оберіть **Get Page Access Token** і дайте дозвіл вашій сторінці `PRO-CLEAN Дрогобич`.
   - У списку **Permissions (Дозволи)** додайте 4 дозволи:
     - `pages_manage_posts`
     - `pages_read_engagement`
     - `instagram_basic`
     - `instagram_content_publish`
   - Натисніть **Generate Access Token** (підтвердіть у вікні Facebook).
   - Щоб токен не закінчувався щогодини, натисніть синій значок **`(i)`** біля токена → **Open in Access Token Tool** → унизу натисніть синю кнопку **Extend Access Token** і скопіюйте довгостроковий токен сторінки — це ваш **`META_PAGE_ACCESS_TOKEN`**.
4. Як дізнатися **`FB_PAGE_ID`** та **`IG_USER_ID`** прямо в тому ж вікні Graph API Explorer:
   - У рядку запиту зверху впишіть:
     `me?fields=id,name,instagram_business_account`
   - Натисніть **Submit**:
     - Поле `"id"` — це ваш **`FB_PAGE_ID`**.
     - Поле `"instagram_business_account" -> "id"` — це ваш **`IG_USER_ID`**.

---

## Крок 4. Пропишіть ці 4 ключі в GitHub Secrets (1 хвилина)

У вашому репозиторії на GitHub перейдіть у вкладку **Settings** → у меню зліва **Secrets and variables** → **Actions** → натисніть зелену кнопку **New repository secret** і додайте по черзі 4 секрети:

| Назва секрету (`Name`) | Що вставити у поле `Secret` |
| :--- | :--- |
| `GEMINI_API_KEY` | Ваш ключ із Google AI Studio |
| `META_PAGE_ACCESS_TOKEN` | Довгостроковий Page Access Token із Graph API Explorer |
| `FB_PAGE_ID` | Цифровий ID вашої сторінки Facebook `PRO-CLEAN Дрогобич` |
| `IG_USER_ID` | Цифровий ID вашого Instagram-акаунта `@proclean.rent.ua` |

---

## Крок 5. Протестуйте перший автоматичний пост у 1 клік!

1. Перейдіть у вкладку **Actions** у вашому репозиторії на GitHub.
2. Зліва натисніть на **PRO-CLEAN RENT AutoPoster (FB + Instagram)**.
3. Праворуч натисніть кнопку **Run workflow** → зелена кнопка **Run workflow**.
4. За 20 секунд скрипт згенерує свіжий пост і одночасно опублікує його з картинкою на вашій сторінці Facebook та в Instagram! А далі він робитиме це сам щовівторка, щочетверга та щосуботи о 09:30 ранку.
