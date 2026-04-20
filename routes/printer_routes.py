# routes/printer_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session
from models.printer import Printer

bp = Blueprint("printer", __name__)


@bp.route("/printers")
def list_printers():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    printers = Printer.get_all(active_only=True)
    return render_template("printers.html", printers=printers)


@bp.route("/printer/add", methods=["GET", "POST"])
def add_printer():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        try:
            floor = int(request.form["floor"])
            dept = request.form["dept"].strip()
            model = request.form["model"].strip()
            cartridge = request.form["cartridge"].strip()
            monthly_rate = int(request.form["monthly_rate"])
            price = float(request.form["price"])
            note = request.form.get("note", "").strip()

            Printer.add(floor, dept, model, cartridge, monthly_rate, price, note)
            return redirect(url_for("printer.list_printers"))
        except (ValueError, KeyError) as e:
            return "Ошибка в данных формы", 400

    return render_template("printer_add.html")


@bp.route("/printer/edit/<int:pid>", methods=["GET", "POST"])
def edit_printer(pid):
    printer = dict(Printer.get_by_id(pid))
    if not printer:
        return "Принтер не найден", 404

    if request.method == "POST":
        updates = {
            "floor": int(request.form["floor"]),
            "dept": request.form["dept"].strip(),
            "model": request.form["model"].strip(),
            "cartridge": request.form["cartridge"].strip(),
            "monthly_rate": int(request.form["monthly_rate"]),
            "price": float(request.form["price"]),
            "note": request.form.get("note", "").strip(),
        }
        Printer.update(pid, **updates)
        return redirect(url_for("printer.list_printers"))

    return render_template("printer_edit.html", printer=printer)


@bp.route("/printer/delete/<int:pid>")
def delete_printer(pid):
    Printer.delete(pid)
    return redirect(url_for("printer.list_printers"))

# Добавим метод в модель
# models/printer.py — дополнение