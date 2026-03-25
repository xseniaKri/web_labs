# Flask Lab1 - Веб-приложение

## Запуск
1. Активируйте venv (если не активна): `source venv/bin/activate`
2. `export FLASK_APP=app`
3. `flask run` или `python run.py`

Откройте http://127.0.0.1:5000/

## Функции
- `/` - Инфо о запросе (args, headers, cookies)
- `/login` - Форма авторизации (показывает данные POST)
- `/phone` - Проверка/форматирование номера телефона (с ошибками Bootstrap)
