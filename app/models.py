from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db, login_manager


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)

    users = db.relationship("User", back_populates="role")

    def __repr__(self):
        return f"<Role {self.name}>"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(120), nullable=True)
    first_name = db.Column(db.String(120), nullable=False)
    middle_name = db.Column(db.String(120), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=db.func.now(),
    )

    role = db.relationship("Role", back_populates="users")
    visits = db.relationship(
        "VisitLog",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.login}>"


class VisitLog(db.Model):
    __tablename__ = "visit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    path = db.Column(db.String(100), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=db.func.now(),
    )

    user = db.relationship("User", back_populates="visits")

    def __repr__(self):
        return f"<VisitLog {self.path}>"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
