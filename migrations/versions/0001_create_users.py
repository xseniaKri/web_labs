"""create users and roles tables

Revision ID: 0001_create_users
Revises:
Create Date: 2026-04-27 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from werkzeug.security import generate_password_hash


revision = "0001_create_users"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_roles_name"), "roles", ["name"], unique=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("login", sa.String(length=80), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("last_name", sa.String(length=120), nullable=True),
        sa.Column("first_name", sa.String(length=120), nullable=False),
        sa.Column("middle_name", sa.String(length=120), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_login"), "users", ["login"], unique=True)

    op.create_table(
        "visit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("path", sa.String(length=100), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_visit_logs_user_id"), "visit_logs", ["user_id"], unique=False)

    users_table = sa.table(
        "users",
        sa.column("login", sa.String),
        sa.column("password_hash", sa.String),
        sa.column("last_name", sa.String),
        sa.column("first_name", sa.String),
        sa.column("middle_name", sa.String),
        sa.column("role_id", sa.Integer),
    )
    roles_table = sa.table(
        "roles",
        sa.column("name", sa.String(length=80)),
        sa.column("description", sa.Text()),
    )
    op.bulk_insert(
        roles_table,
        [
            {
                "name": "Администратор",
                "description": "роль админа",
            },
            {
                "name": "Пользователь",
                "description": "роль пользователя",
            },
        ]
    )
    op.bulk_insert(
        users_table,
        [
            {
                "login": "user",
                "password_hash": generate_password_hash("qwerty"),
                "last_name": None,
                "first_name": "Иван",
                "middle_name": "Иванович",
                "role_id": 1,
            },
            {
                "login": "user2",
                "password_hash": generate_password_hash("qwerty"),
                "last_name": None,
                "first_name": "Сергей",
                "middle_name": "Сергеевич",
                "role_id": 2,
            },
        ],
    )


def downgrade():
    op.drop_index(op.f("ix_visit_logs_user_id"), table_name="visit_logs")
    op.drop_table("visit_logs")
    op.drop_index(op.f("ix_users_login"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_roles_name"), table_name="roles")
    op.drop_table("roles")
