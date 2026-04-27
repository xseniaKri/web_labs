from flask import Flask

from app.config import Config
from app.extensions import db, login_manager
from app.models import Role, User
from app.routes import main_bp


def create_app(config_class=Config):
    flask_app = Flask(__name__)
    flask_app.config.from_object(config_class)

    db.init_app(flask_app)
    login_manager.init_app(flask_app)
    login_manager.login_view = "main.login"
    login_manager.login_message = "Для доступа к странице необходимо войти."
    login_manager.login_message_category = "warning"

    flask_app.register_blueprint(main_bp)
    register_cli_commands(flask_app)

    return flask_app


def register_cli_commands(flask_app):
    @flask_app.cli.command("create-admin")
    def create_admin():
        login = flask_app.config["ADMIN_USERNAME"]
        password = flask_app.config["ADMIN_PASSWORD"]

        role = Role.query.filter_by(name="Администратор").first()
        if role is None:
            role = Role(
                name="Администратор",
                description="Полный доступ к управлению учетными записями.",
            )
            db.session.add(role)
            db.session.flush()

        user = User.query.filter_by(login=login).first()
        if user is None:
            user = User(
                login=login,
                first_name="Администратор",
                middle_name="Системы",
                role_id=role.id,
            )
            user.set_password(password)
            db.session.add(user)
        else:
            user.role_id = role.id
            user.set_password(password)

        db.session.commit()
        print(f"Admin user is ready: {login}")
