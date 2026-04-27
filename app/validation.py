import re


LOGIN_RE = re.compile(r"^[A-Za-z0-9]{5,}$")
PASSWORD_LETTER_RE = re.compile(r"^[A-Za-zА-Яа-яЁё]$")
PASSWORD_SPECIALS = set("~!?@#$%^&*_-+()[]{}></\\|\"'.,:;")
ASCII_DIGITS = set("0123456789")


def validate_login(login):
    if not login:
        return "Поле обязательно для заполнения."
    if not LOGIN_RE.fullmatch(login):
        return "Логин должен содержать только латинские буквы и цифры, минимум 5 символов."
    return None


def validate_password(password):
    if not password:
        return "Поле обязательно для заполнения."
    if not 8 <= len(password) <= 128:
        return "Пароль должен иметь длину от 8 до 128 символов."
    if any(char.isspace() for char in password):
        return "Пароль не должен содержать пробелы."
    if not any(char.isupper() for char in password if PASSWORD_LETTER_RE.fullmatch(char)):
        return "Пароль должен содержать минимум одну заглавную букву."
    if not any(char.islower() for char in password if PASSWORD_LETTER_RE.fullmatch(char)):
        return "Пароль должен содержать минимум одну строчную букву."
    if not any(char in ASCII_DIGITS for char in password):
        return "Пароль должен содержать минимум одну цифру."

    for char in password:
        if (
            PASSWORD_LETTER_RE.fullmatch(char)
            or char in ASCII_DIGITS
            or char in PASSWORD_SPECIALS
        ):
            continue
        return "Пароль содержит недопустимые символы."

    return None


def validate_required(value):
    if not value.strip():
        return "Поле обязательно для заполнения."
    return None


def validate_user_create_form(form):
    errors = {}
    login = form.get("login", "").strip()
    password = form.get("password", "")
    password_confirm = form.get("password_confirm", "")

    login_error = validate_login(login)
    if login_error:
        errors["login"] = login_error

    password_error = validate_password(password)
    if password_error:
        errors["password"] = password_error

    if password and password_confirm and password != password_confirm:
        errors["password_confirm"] = "Пароли не совпадают."
    elif password and not password_confirm:
        errors["password_confirm"] = "Поле обязательно для заполнения."

    for field in ("last_name", "first_name"):
        error = validate_required(form.get(field, ""))
        if error:
            errors[field] = error

    return errors


def validate_user_edit_form(form):
    errors = {}

    for field in ("last_name", "first_name"):
        error = validate_required(form.get(field, ""))
        if error:
            errors[field] = error

    return errors
