from flask import Flask

from app.config import Config
from app.extensions import db, login_manager
from app.models import User
from app.routes import main_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "main.login"
    login_manager.login_message = "Для доступа к странице необходимо войти."
    login_manager.login_message_category = "warning"

    app.register_blueprint(main_bp)
    register_cli_commands(app)

    return app


def register_cli_commands(app):
    @app.cli.command("create-admin")
    def create_admin():
        username = app.config["ADMIN_USERNAME"]
        email = app.config["ADMIN_EMAIL"]
        password = app.config["ADMIN_PASSWORD"]

        user = User.query.filter_by(username=username).first()
        if user is None:
            user = User(username=username, email=email, is_admin=True)
            user.set_password(password)
            db.session.add(user)
        else:
            user.email = email
            user.is_admin = True
            user.is_active_account = True
            user.set_password(password)

        db.session.commit()
        print(f"Admin user is ready: {username}")
