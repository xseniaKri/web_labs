from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Role, User


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    users_list = User.query.order_by(User.id).all()
    return render_template("users.html", users=users_list, title="Главная страница")


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


@main_bp.get("/users")
def users():
    users_list = User.query.order_by(User.id).all()
    return render_template("users.html", users=users_list, title="Учетные записи")


@main_bp.get("/users/create")
@login_required
def new_user():
    roles = Role.query.order_by(Role.name).all()
    return render_template("user_form.html", user=None, roles=roles)


@main_bp.post("/users")
@login_required
def create_user():
    password = request.form.get("password", "")
    password_confirm = request.form.get("password_confirm", "")

    if password != password_confirm:
        flash("Пароли не совпадают.", "danger")
        roles = Role.query.order_by(Role.name).all()
        return render_template("user_form.html", user=None, roles=roles)

    user = User(
        login=request.form.get("login", "").strip(),
        last_name=request.form.get("last_name", "").strip() or None,
        first_name=request.form.get("first_name", "").strip(),
        middle_name=request.form.get("middle_name", "").strip(),
        role_id=request.form.get("role_id") or None,
    )
    user.set_password(password)
    db.session.add(user)

    try:
        db.session.commit()
        flash("Пользователь создан.", "success")
        return redirect(url_for("main.user_detail", user_id=user.id))
    except IntegrityError:
        db.session.rollback()
        flash("Пользователь с таким логином уже существует.", "danger")

    roles = Role.query.order_by(Role.name).all()
    return render_template("user_form.html", user=None, roles=roles)


@main_bp.get("/users/<int:user_id>")
def user_detail(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        flash("Пользователь не найден.", "warning")
        return redirect(url_for("main.users"))

    return render_template("user_detail.html", user=user)


@main_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        flash("Пользователь не найден.", "warning")
        return redirect(url_for("main.users"))

    if request.method == "POST":
        user.last_name = request.form.get("last_name", "").strip() or None
        user.first_name = request.form.get("first_name", "").strip()
        user.middle_name = request.form.get("middle_name", "").strip()
        user.role_id = request.form.get("role_id") or None

        try:
            db.session.commit()
            flash("Пользователь обновлен.", "success")
            return redirect(url_for("main.index"))
        except IntegrityError:
            db.session.rollback()
            flash("Не удалось обновить пользователя.", "danger")

    roles = Role.query.order_by(Role.name).all()
    return render_template("user_form.html", user=user, roles=roles)


@main_bp.route("/users/<int:user_id>/password", methods=["GET", "POST"])
@login_required
def change_password(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        flash("Пользователь не найден.", "warning")
        return redirect(url_for("main.users"))

    if request.method == "POST":
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")

        if password != password_confirm:
            flash("Пароли не совпадают.", "danger")
            return render_template("change_password.html", user=user)

        user.set_password(password)
        db.session.commit()
        flash("Пароль изменен.", "success")
        return redirect(url_for("main.user_detail", user_id=user.id))

    return render_template("change_password.html", user=user)


@main_bp.post("/users/<int:user_id>/delete")
@login_required
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        flash("Пользователь не найден.", "warning")
        return redirect(url_for("main.users"))

    if user.id == current_user.id:
        flash("Нельзя удалить собственную учетную запись.", "warning")
        return redirect(url_for("main.users"))

    db.session.delete(user)
    db.session.commit()
    flash("Пользователь удален.", "success")
    return redirect(url_for("main.users"))
