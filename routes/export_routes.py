from flask import Blueprint, send_file, session, redirect, url_for
from services.export_service import ExportService

bp = Blueprint("export", __name__)


@bp.route("/export/printers")
def export_printers():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    path = ExportService.export_printers()
    return send_file(path, as_attachment=True)


@bp.route("/export/records")
def export_records():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    path = ExportService.export_records()
    return send_file(path, as_attachment=True)


@bp.route("/export/stock")
def export_stock():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    path = ExportService.export_stock()
    return send_file(path, as_attachment=True)