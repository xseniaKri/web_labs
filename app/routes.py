from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Role, User


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    users_count = User.query.count()
    return render_template("index.html", users_count=users_count)


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
            return redirect(url_for("main.users"))

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


@main_bp.route("/users", methods=["GET", "POST"])
@login_required
def users():
    if request.method == "POST":
        user = User(
            login=request.form.get("login", "").strip(),
            last_name=request.form.get("last_name", "").strip() or None,
            first_name=request.form.get("first_name", "").strip(),
            middle_name=request.form.get("middle_name", "").strip(),
            role_id=request.form.get("role_id") or None,
        )
        user.set_password(request.form.get("password", ""))
        db.session.add(user)

        try:
            db.session.commit()
            flash("Пользователь создан.", "success")
        except IntegrityError:
            db.session.rollback()
            flash("Пользователь с таким логином уже существует.", "danger")

        return redirect(url_for("main.users"))

    users_list = User.query.order_by(User.id).all()
    roles = Role.query.order_by(Role.name).all()
    return render_template("users.html", users=users_list, roles=roles)


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
