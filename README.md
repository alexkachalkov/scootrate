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

## Запуск фронтенда

```bash
cd frontend
npm install
npm run dev
```

Фронтенд будет доступен по адресу: http://localhost:3000
