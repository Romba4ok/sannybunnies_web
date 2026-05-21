# Sanny Bunnies — Flask Admin Panel

Админ-панель для сайта детского сада. Позволяет администраторам управлять контентом и данными, которые хранятся в Firebase: пользователями, группами, расписанием, воспитателями, новостями, меню, интерьером, отзывами и запросами от пользователей.

**Ключевые возможности**
- Аутентификация и управление ролями (админ/пользователь)
- CRUD-интерфейс для разделов: `users`, `groups`, `schedule`, `teachers`, `news`, `menu`, `interior`, `reviews`, `requests`, `faq`
- Загрузка файлов (папка `uploads`)
- Шаблоны Jinja2 для админ-интерфейса

**Технологии**
- Python, Flask
- Firebase Admin SDK (серверная часть)
- Firebase Web SDK (фронтенд/авторизация)
- Jinja2, dotenv

## Структура проекта (кратко)
- `app.py` — точка входа Flask-приложения
- `config.py` — конфигурация и переменные окружения
- `auth_service.py`, `firebase_admin_service.py` — обёртки для работы с Firebase
- `routes/` — маршруты для разных разделов админки (см. файлы в папке)
- `templates/` — HTML-шаблоны
- `uploads/` — загруженные файлы

## Требования
- Python 3.10+ (рекомендуется)
- Зависимости из `requirements.txt`

## Переменные окружения
Конфигурация берётся из `.env` (в `config.py`):

- `SECRET_KEY` — секрет Flask (по умолчанию `replace-this-secret`)
- `FIREBASE_CREDENTIALS` — путь к JSON-файлу сервисного аккаунта (по умолчанию `serviceAccountKey.json`)
- `FIREBASE_API_KEY`
- `FIREBASE_AUTH_DOMAIN`
- `FIREBASE_PROJECT_ID`
- `FIREBASE_STORAGE_BUCKET`
- `FIREBASE_MESSAGING_SENDER_ID`
- `FIREBASE_APP_ID`
- `FIREBASE_MEASUREMENT_ID`
- `ADMIN_ROLE` — роль администратора (по умолчанию `admin`)

Пример `.env` (основано на `config.py`):

```env
SECRET_KEY=change-me
FIREBASE_CREDENTIALS=serviceAccountKey.json
FIREBASE_API_KEY=YOUR_FIREBASE_API_KEY
FIREBASE_AUTH_DOMAIN=your-app.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=...
FIREBASE_APP_ID=...
FIREBASE_MEASUREMENT_ID=...
ADMIN_ROLE=admin
```

## Быстрый старт
1. Клонируйте репозиторий и перейдите в папку проекта

```bash
python -m venv .venv
source .venv/Scripts/activate      # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Поместите файл сервисного аккаунта Firebase `serviceAccountKey.json` в корень проекта либо укажите путь через `FIREBASE_CREDENTIALS`.

3. Создайте `.env` по образцу и заполните значения.

4. Запустите приложение:

```bash
python app.py
```

5. Откройте в браузере: `http://127.0.0.1:5000`

## Примечания по Firebase
- Для работы серверной части нужен JSON сервисного аккаунта (Console → Project settings → Service accounts).
- Убедитесь, что в коллекции `users` у аккаунта с правами администратора есть поле `role` с значением, соответствующим `ADMIN_ROLE`.

## Вклад и поддержка
- Ошибки и предложения — через issues в репозитории или напрямую автору проекта.

---
Файл README обновлён. Для просмотра откройте [README.md](README.md).
