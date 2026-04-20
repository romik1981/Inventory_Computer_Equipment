from flask import Blueprint, render_template, request, redirect, url_for, session
from models.toner import Toner

bp = Blueprint("toner", __name__)


@bp.route("/toners")
def list_toners():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    toners = Toner.get_all()
    return render_template("toners.html", toners=toners)


@bp.route("/toner/add", methods=["GET", "POST"])
def add_toner():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        try:
            name = request.form["name"].strip()
            capacity_pages = int(request.form["capacity_pages"]) if request.form["capacity_pages"] else None
            color = request.form["color"].strip()
            compatible_printers = request.form["compatible_printers"].strip()
            supplier = request.form.get("supplier", "").strip()
            price = float(request.form["price"]) if request.form["price"] else 0.0

            Toner.add(
                name=name,
                capacity_pages=capacity_pages,
                color=color,
                compatible_printers=compatible_printers,
                supplier=supplier,
                price=price
            )
            return redirect(url_for("toner.list_toners"))
        except (ValueError, KeyError) as e:
            return f"Ошибка в данных: {str(e)}", 400

    return render_template("toner_add.html")


@bp.route("/toner/edit/<int:tid>", methods=["GET", "POST"])
def edit_toner(tid):
    toner = Toner.get_by_id(tid)
    if not toner:
        return "Тонер не найден", 404

    if request.method == "POST":
        updates = {
            "name": request.form["name"].strip(),
            "capacity_pages": int(request.form["capacity_pages"]) if request.form["capacity_pages"] else None,
            "color": request.form["color"].strip(),
            "compatible_printers": request.form["compatible_printers"].strip(),
            "supplier": request.form.get("supplier", "").strip(),
            "price": float(request.form["price"]) if request.form["price"] else 0.0,
        }
        Toner.update(tid, **updates)
        return redirect(url_for("toner.list_toners"))

    return render_template("toner_edit.html", toner=toner)


@bp.route("/toner/delete/<int:tid>")
def delete_toner(tid):
    Toner.delete(tid)
    return redirect(url_for("toner.list_toners"))
