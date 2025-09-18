# Scootrate

Приложение на Python (Flask) и Vue.js.

## Структура проекта

```
scootrate/
├── backend/         # Python/Flask бэкенд
│   ├── venv/        # Виртуальное окружение Python
│   ├── app.py       # Основной файл приложения Flask
│   └── requirements.txt  # Зависимости Python
└── frontend/        # Vue.js фронтенд
    ├── public/      # Статические файлы
    ├── src/         # Исходный код Vue
    ├── package.json # Зависимости NPM
    └── vite.config.js # Конфигурация Vite
```

## Запуск бэкенда

```bash
cd backend
source venv/bin/activate  # Для Linux/Mac
# или
# venv\Scripts\activate  # Для Windows
pip install -r requirements.txt
python app.py
```

Бэкенд будет доступен по адресу: http://localhost:5000

### Запуск через gunicorn (как на Heroku)

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
gunicorn app:app --chdir backend
```

## Запуск фронтенда

```bash
cd frontend
npm install
npm run dev
```

Фронтенд будет доступен по адресу: http://localhost:3000

## Деплой на Heroku

В корне проекта добавлены файлы для Python buildpack:

- `requirements.txt` — проксирует зависимости из `backend/requirements.txt`.
- `runtime.txt` — фиксирует версию Python (3.12.3).
- `Procfile` — указывает команду запуска `web: gunicorn backend.app:app`.

Пошагово:

```bash
heroku create your-app-name
heroku stack:set heroku-24
git push heroku main
```

Не забудьте настроить переменные окружения через `heroku config:set`, например:

```bash
heroku config:set \
  TOPSCOOT_SECRET=... \
  TOPSCOOT_DATABASE=data/top-scoot.sqlite3 \
  TOPSCOOT_DATABASE_READONLY=1
```

`TOPSCOOT_DATABASE` можно задавать относительным путём от корня проекта (например, `data/top-scoot.sqlite3`) — внутри приложения он преобразуется в абсолютный. Флаг `TOPSCOOT_DATABASE_READONLY=1` сообщает приложению, что база лежит в read-only slug, и оно открывает SQLite в режиме `mode=ro`.

## Деплой в Dokploy

Проект может быть задеплоен в Dokploy с использованием Docker. В проект добавлен Dockerfile для сборки приложения.

Для работы с MariaDB в Dokploy, приложение использует следующие переменные окружения:

- `USE_MARIADB=true` - включает использование MariaDB
- `DB_HOST` - хост базы данных (по умолчанию scootrate-mariadb-wmclth)
- `DB_PORT` - порт базы данных (по умолчанию 3306)
- `DB_USER` - пользователь базы данных (по умолчанию scootrate)
- `DB_PASSWORD` - пароль базы данных (по умолчанию secret)
- `DB_NAME` - имя базы данных (по умолчанию scootrate)

После деплоя приложения, необходимо запустить миграции базы данных:

```bash
# Внутри контейнера приложения
python backend/migrate_mariadb.py
```

