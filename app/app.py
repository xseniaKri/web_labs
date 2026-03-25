from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user
)

app = Flask(__name__)
app.secret_key = "super_secret_key"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Для доступа необходимо пройти аутентификацию"


class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

users = {
    "user": User(1, "user", "qwerty")
}

@login_manager.user_loader
def load_user(user_id):
    for user in users.values():
        if str(user.id) == user_id:
            return user
    return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/counter")
def counter():
    if "visits" in session:
        session["visits"] += 1
    else:
        session["visits"] = 1

    visits = session["visits"]

    return render_template(
        "counter.html",
        visits=visits
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember = True if request.form.get("remember") else False

        user = users.get(username)

        if user and user.password == password:
            login_user(user, remember=remember)

            flash("Успешный вход")

            next_page = request.args.get("next")

            return redirect(next_page or url_for("index"))

        else:
            flash("Неверный логин или пароль")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы")
    return redirect(url_for("index"))


@app.route("/secret")
@login_required
def secret():
    return render_template("secret.html")


if __name__ == "__main__":
    app.run(debug=True)