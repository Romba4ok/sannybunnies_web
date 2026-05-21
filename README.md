# Flask Admin Panel для Sanny Bunnies

Админка для проекта на базе Firebase. Содержит авторизацию и разделы:
- Пользователи
- Расписание
- Группы
- Воспитатели
- Отзывы
- Новости
- Интерьер
- Меню питания

## Как запустить

1. Скопируй `serviceAccountKey.json` в папку `C:\Users\romal\Desktop\Коды\sannybunnies`.
2. Если файл называется иначе, укажи свой путь в `.env`:
   ```env
   FIREBASE_CREDENTIALS=путь\к\твоему\serviceAccountKey.json
   ```
3. Скопируй `.env.example` в `.env` и заполни значения.
4. Установи зависимости:

```bash
pip install -r requirements.txt
```

4. Запусти приложение:

```bash
python app.py
```

5. Открой в браузере:

```
http://127.0.0.1:5000
```

## Требования Firebase

- `FIREBASE_CREDENTIALS` должен ссылаться на JSON-сервисный аккаунт.
- `FIREBASE_API_KEY` должен быть API ключом из Firebase Web app.
- В коллекции `users` у администратора должно быть поле `role: 'admin'`.
