import csv
from io import StringIO

from flask import Blueprint, Response, render_template, request
from flask_login import current_user
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import User, VisitLog
from app.routes import check_rights, is_admin, can


reports_bp = Blueprint("reports", __name__, url_prefix="/visits")
PER_PAGE = 10
ANONYMOUS_USER = "Неаутентифицированный пользователь"


def user_full_name(user):
    if user is None:
        return ANONYMOUS_USER

    return " ".join(
        part for part in (user.last_name, user.first_name, user.middle_name) if part
    )


def reports_query():
    return VisitLog.query.outerjoin(User)


def pages_report_rows():
    query = db.session.query(
        VisitLog.path,
        func.count(VisitLog.id).label("visits_count"),
    )
    if not is_admin():
        query = query.filter(VisitLog.user_id == current_user.id)

    return (
        query.group_by(VisitLog.path)
        .order_by(func.count(VisitLog.id).desc(), VisitLog.path)
        .all()
    )


def users_report_rows():
    query = (
        db.session.query(User, func.count(VisitLog.id).label("visits_count"))
        .select_from(VisitLog)
        .outerjoin(User)
    )
    if not is_admin():
        query = query.filter(VisitLog.user_id == current_user.id)

    return (
        query.group_by(User.id)
        .order_by(func.count(VisitLog.id).desc(), User.last_name, User.first_name)
        .all()
    )


def csv_response(filename, headers, rows):
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(headers)
    writer.writerows(rows)

    return Response(
        buffer.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@reports_bp.before_app_request
def log_visit():
    if request.endpoint == "static":
        return

    visit = VisitLog(
        user_id=current_user.id if current_user.is_authenticated else None,
        path=request.path[:100],
    )
    db.session.add(visit)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()


@reports_bp.context_processor
def inject_permissions():
    return {"can": can, "is_admin": is_admin}


@reports_bp.get("/")
@check_rights("view_visit_log")
def visit_log():
    page = request.args.get("page", 1, type=int)
    query = reports_query().order_by(VisitLog.created_at.desc(), VisitLog.id.desc())
    if not is_admin():
        query = query.filter(VisitLog.user_id == current_user.id)

    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    return render_template(
        "visit_log.html",
        pagination=pagination,
        visits=pagination.items,
        title="Журнал посещений",
        user_full_name=user_full_name,
    )


@reports_bp.get("/pages")
@check_rights("view_visit_reports")
def pages_report():
    rows = pages_report_rows()
    return render_template(
        "visits_pages_report.html",
        rows=rows,
        title="Отчет по страницам",
    )


@reports_bp.get("/pages.csv")
@check_rights("view_visit_reports")
def pages_report_csv():
    rows = ((row.path, row.visits_count) for row in pages_report_rows())
    return csv_response("visits_by_pages.csv", ["Страница", "Количество посещений"], rows)


@reports_bp.get("/users")
@check_rights("view_visit_reports")
def users_report():
    rows = users_report_rows()
    return render_template(
        "visits_users_report.html",
        rows=rows,
        title="Отчет по пользователям",
        user_full_name=user_full_name,
    )


@reports_bp.get("/users.csv")
@check_rights("view_visit_reports")
def users_report_csv():
    rows = (
        (user_full_name(user), visits_count)
        for user, visits_count in users_report_rows()
    )
    return csv_response("visits_by_users.csv", ["Пользователь", "Количество посещений"], rows)
