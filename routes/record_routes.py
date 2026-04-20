# routes/record_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session
from models.record import Record
from models.printer import Printer

bp = Blueprint("record", __name__)


@bp.route("/records")
def list_records():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    records = Record.get_all_with_printers()
    return render_template("records.html", records=records)


@bp.route("/record/add", methods=["GET", "POST"])
def add_record():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    printers = Printer.get_all()

    if request.method == "POST":
        try:
            date = request.form["date"]
            printer_id = int(request.form["printer_id"])
            cartridge_type = request.form["cartridge_type"].strip()
            toner_used = float(request.form["toner_used"])
            pages_printed = int(request.form["pages_printed"])

            Record.add(date, printer_id, cartridge_type, toner_used, pages_printed)
            return redirect(url_for("record.list_records"))
        except (ValueError, KeyError) as e:
            return f"Ошибка в данных: {str(e)}", 400

    return render_template("record_add.html", printers=printers)


@bp.route("/record/edit/<int:rid>", methods=["GET", "POST"])
def edit_record(rid):
    record = Record.get_by_id(rid)
    if not record:
        return "Запись не найдена", 404

    printers = Printer.get_all()

    if request.method == "POST":
        updates = {
            "date": request.form["date"],
            "printer_id": int(request.form["printer_id"]),
            "cartridge_type": request.form["cartridge_type"].strip(),
            "toner_used": float(request.form["toner_used"]),
            "pages_printed": int(request.form["pages_printed"]),
        }
        Record.update(rid, **updates)
        return redirect(url_for("record.list_records"))

    return render_template("record_edit.html", record=record, printers=printers)


@bp.route("/record/delete/<int:rid>")
def delete_record(rid):
    Record.delete(rid)
    return redirect(url_for("record.list_records"))
