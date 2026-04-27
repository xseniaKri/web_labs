from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import User


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
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password) and user.is_active_account:
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
            username=request.form.get("username", "").strip(),
            email=request.form.get("email", "").strip(),
            is_admin=request.form.get("is_admin") == "on",
        )
        user.set_password(request.form.get("password", ""))
        db.session.add(user)

        try:
            db.session.commit()
            flash("Пользователь создан.", "success")
        except IntegrityError:
            db.session.rollback()
            flash("Пользователь с таким логином или email уже существует.", "danger")

        return redirect(url_for("main.users"))

    users_list = User.query.order_by(User.id).all()
    return render_template("users.html", users=users_list)


@main_bp.post("/users/<int:user_id>/toggle")
@login_required
def toggle_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        flash("Пользователь не найден.", "warning")
        return redirect(url_for("main.users"))

    if user.id == current_user.id:
        flash("Нельзя отключить собственную учетную запись.", "warning")
        return redirect(url_for("main.users"))

    user.is_active_account = not user.is_active_account
    db.session.commit()
    flash("Статус пользователя обновлен.", "success")
    return redirect(url_for("main.users"))


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
