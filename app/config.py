import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://lab_user:lab_password@localhost:5432/lab_db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False