# routes/dashboard_routes.py
from flask import Blueprint, render_template, session, redirect, url_for
from models.record import Record
from models.stock import Stock
from models.printer import Printer
from config import Config

bp = Blueprint("dashboard", __name__)


@bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    # Последние записи
    recent_records = Record.get_all_with_printers()[:10]

    # Статистика
    total_printers = len(Printer.get_all())
    total_records = len(Record.get_all_with_printers())
    total_stock_items = len(Stock.get_all())

    return render_template(
        "dashboard.html",
        recent_records=recent_records,
        total_printers=total_printers,
        total_records=total_records,
        total_stock_items=total_stock_items,
        months=Config.MONTHS
    )
