from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.extensions import db
from app.models import Role, User
from app.validation import (
    validate_password,
    validate_user_create_form,
    validate_user_edit_form,
)


main_bp = Blueprint("main", __name__)


ADMIN_ROLE = "Администратор"
USER_ROLE = "Пользователь"
RIGHTS_ERROR = "У вас недостаточно прав для доступа к данной странице."


def is_admin(user=None):
    user = user or current_user
    return user.is_authenticated and user.role and user.role.name == ADMIN_ROLE


def is_regular_user(user=None):
    user = user or current_user
    return user.is_authenticated and user.role and user.role.name == USER_ROLE


def can(action, user=None):
    if not current_user.is_authenticated:
        return False

    if is_admin():
        return action in {
            "create_user",
            "edit_user",
            "view_user",
            "delete_user",
            "view_visit_log",
            "view_visit_reports",
            "change_user_password",
        }

    if not is_regular_user():
        return False

    if action in {"view_visit_log", "view_visit_reports"}:
        return True

    if user is None:
        return False

    own_profile = user.id == current_user.id
    return own_profile and action in {"edit_user", "view_user"}


def check_rights(action, get_resource=None):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(*args, **kwargs):
            resource = get_resource(*args, **kwargs) if get_resource else None
            if get_resource and resource is None:
                return view_func(*args, **kwargs)

            if can(action, resource):
                return view_func(*args, **kwargs)

            flash(RIGHTS_ERROR, "danger")
            return redirect(url_for("main.index"))

        return wrapper

    return decorator


def get_user_from_route(*args, **kwargs):
    user_id = kwargs.get("user_id")
    if user_id is None:
        return None
    return db.session.get(User, user_id)


@main_bp.context_processor
def inject_permissions():
    return {"can": can, "is_admin": is_admin}


@main_bp.route("/")
def index():
    users_list = User.query.order_by(User.id).all()
    return render_template("index.html", users=users_list, title="Главная страница")


@main_bp.route("/counter")
def counter():
    session["visits"] = session.get("visits", 0) + 1
    return render_template("counter.html", visits=session["visits"])


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        login_value = request.form.get("login", "").strip()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"
        user = User.query.filter_by(login=login_value).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash("Вы успешно вошли.", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.users"))

        flash("Неверный логин или пароль.", "danger")

    return render_template("login.html")


@main_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта.", "info")
    return redirect(url_for("main.index"))


@main_bp.route("/secret")
@login_required
def secret():
    return render_template("secret.html")


@main_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_own_password():
    errors = {}

    if request.method == "POST":
        old_password = request.form.get("old_password", "")
        new_password = request.form.get("new_password", "")
        new_password_confirm = request.form.get("new_password_confirm", "")

        if not old_password:
            errors["old_password"] = "Поле обязательно для заполнения."
        elif not current_user.check_password(old_password):
            errors["old_password"] = "Старый пароль указан неверно."

        new_password_error = validate_password(new_password)
        if new_password_error:
            errors["new_password"] = new_password_error

        if new_password and new_password_confirm and new_password != new_password_confirm:
            errors["new_password_confirm"] = "Пароли не совпадают."
        elif new_password and not new_password_confirm:
            errors["new_password_confirm"] = "Поле обязательно для заполнения."

        if errors:
            flash("Проверьте корректность заполнения формы.", "danger")
            return render_template("change_own_password.html", errors=errors)

        current_user.set_password(new_password)
        db.session.commit()
        flash("Пароль успешно изменен.", "success")
        return redirect(url_for("main.index"))

    return render_template("change_own_password.html", errors=errors)


@main_bp.get("/users")
def users():
    users_list = User.query.order_by(User.id).all()
    return render_template("index.html", users=users_list, title="Учетные записи")


@main_bp.get("/users/create")
@check_rights("create_user")
def new_user():
    roles = Role.query.order_by(Role.name).all()
    return render_template(
        "user_form.html",
        user=None,
        roles=roles,
        errors={},
        can_edit_role=True,
    )


@main_bp.post("/users")
@check_rights("create_user")
def create_user():
    errors = validate_user_create_form(request.form)
    if errors:
        flash("Проверьте корректность заполнения формы.", "danger")
        roles = Role.query.order_by(Role.name).all()
        return render_template(
            "user_form.html",
            user=None,
            roles=roles,
            errors=errors,
            can_edit_role=True,
        )

    password = request.form.get("password", "")
    user = User(
        login=request.form.get("login", "").strip(),
        last_name=request.form.get("last_name", "").strip(),
        first_name=request.form.get("first_name", "").strip(),
        middle_name=request.form.get("middle_name", "").strip(),
        role_id=request.form.get("role_id") or None,
    )
    user.set_password(password)
    db.session.add(user)

    try:
        db.session.commit()
        flash("Пользователь создан.", "success")
        return redirect(url_for("main.index"))
    except IntegrityError:
        db.session.rollback()
        errors["login"] = "Пользователь с таким логином уже существует."
        flash("Пользователь с таким логином уже существует.", "danger")

    roles = Role.query.order_by(Role.name).all()
    return render_template(
        "user_form.html",
        user=None,
        roles=roles,
        errors=errors,
        can_edit_role=True,
    )


@main_bp.get("/users/<int:user_id>")
@check_rights("view_user", get_user_from_route)
def user_detail(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        flash("Пользователь не найден.", "warning")
        return redirect(url_for("main.users"))

    return render_template("user_detail.html", user=user)


@main_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@check_rights("edit_user", get_user_from_route)
def edit_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        flash("Пользователь не найден.", "warning")
        return redirect(url_for("main.users"))

    if request.method == "POST":
        errors = validate_user_edit_form(request.form)
        if errors:
            flash("Проверьте корректность заполнения формы.", "danger")
            roles = Role.query.order_by(Role.name).all()
            return render_template(
                "user_form.html",
                user=user,
                roles=roles,
                errors=errors,
                can_edit_role=is_admin(),
            )

        user.last_name = request.form.get("last_name", "").strip()
        user.first_name = request.form.get("first_name", "").strip()
        user.middle_name = request.form.get("middle_name", "").strip()
        if is_admin():
            user.role_id = request.form.get("role_id") or None

        try:
            db.session.commit()
            flash("Пользователь обновлен.", "success")
            return redirect(url_for("main.index"))
        except IntegrityError:
            db.session.rollback()
            flash("Не удалось обновить пользователя.", "danger")

    roles = Role.query.order_by(Role.name).all()
    return render_template(
        "user_form.html",
        user=user,
        roles=roles,
        errors={},
        can_edit_role=is_admin(),
    )


@main_bp.route("/users/<int:user_id>/password", methods=["GET", "POST"])
@check_rights("change_user_password", get_user_from_route)
def change_password(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        flash("Пользователь не найден.", "warning")
        return redirect(url_for("main.users"))

    if request.method == "POST":
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")
        errors = {}

        password_error = validate_password(password)
        if password_error:
            errors["password"] = password_error
        if password and password_confirm and password != password_confirm:
            errors["password_confirm"] = "Пароли не совпадают."
        elif password and not password_confirm:
            errors["password_confirm"] = "Поле обязательно для заполнения."

        if errors:
            flash("Проверьте корректность заполнения формы.", "danger")
            return render_template("change_password.html", user=user, errors=errors)

        user.set_password(password)
        db.session.commit()
        flash("Пароль изменен.", "success")
        return redirect(url_for("main.user_detail", user_id=user.id))

    return render_template("change_password.html", user=user, errors={})


@main_bp.post("/users/<int:user_id>/delete")
@check_rights("delete_user", get_user_from_route)
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        flash("Пользователь не найден.", "warning")
        return redirect(url_for("main.index"))

    if user.id == current_user.id:
        flash("Нельзя удалить собственную учетную запись.", "warning")
        return redirect(url_for("main.index"))

    try:
        db.session.delete(user)
        db.session.commit()
        flash("Пользователь удален.", "success")
    except SQLAlchemyError:
        db.session.rollback()
        flash("Не удалось удалить пользователя.", "danger")

    return redirect(url_for("main.index"))
