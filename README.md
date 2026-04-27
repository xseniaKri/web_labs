# Разработка веб-приложений
ЛР по предмету "разработка веб приложений". 1 ветка = 1 ЛР.
Выполнила Крипак Ксения, студентка гр. 241-326.

## Запуск приложения

1. Установить зависимости:

```bash
pip install -r requirements.txt
```

2. Запустить PostgreSQL в Docker:

```bash
docker compose up -d
```

3. Применить миграции Alembic:

```bash
alembic upgrade head
```

4. Создать первого администратора:

```bash
flask --app app.app:app create-admin
```

По умолчанию создается пользователь `admin` с паролем `admin`. Значения можно переопределить через переменные окружения `ADMIN_USERNAME`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`.

5. Запустить Flask:

```bash
flask --app app.app:app run
```

## Конфигурация БД

Строка подключения задается в переменной окружения `DATABASE_URL`. Пример находится в `.env.example`:

```text
postgresql+psycopg2://lab_user:lab_password@localhost:5432/lab_db
```
