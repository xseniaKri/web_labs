from flask import Flask

from app.config import Config
from app.extensions import db, login_manager
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

    return flask_app
