# routes/stock_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session
from models.stock import Stock

bp = Blueprint("stock", __name__)


@bp.route("/stock")
def list_stock():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    items = Stock.get_all()
    return render_template("stock.html", items=items)


@bp.route("/stock/add", methods=["GET", "POST"])
def add_stock():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        try:
            item_name = request.form["item_name"].strip()
            category = request.form["category"].strip()
            quantity = int(request.form["quantity"])
            unit_price = float(request.form.get("unit_price") or 0)
            total_price = float(request.form.get("total_price") or 0)
            note = request.form.get("note", "").strip()

            # Если не указана общая цена — вычисляем
            if total_price == 0 and unit_price and quantity:
                total_price = unit_price * quantity

            Stock.add(item_name, category, quantity, unit_price, total_price, note)
            return redirect(url_for("stock.list_stock"))
        except (ValueError, KeyError) as e:
            return f"Ошибка в данных: {str(e)}", 400

    return render_template("stock_add.html")


@bp.route("/stock/edit/<int:sid>", methods=["GET", "POST"])
def edit_stock(sid):
    item = Stock.get_by_id(sid)
    if not item:
        return "Элемент не найден", 404

    if request.method == "POST":
        updates = {
            "item_name": request.form["item_name"].strip(),
            "category": request.form["category"].strip(),
            "quantity": int(request.form["quantity"]),
            "unit_price": float(request.form.get("unit_price") or 0),
            "total_price": float(request.form.get("total_price") or 0),
            "note": request.form.get("note", "").strip(),
        }
        # Пересчёт общей цены, если нужно
        if updates["total_price"] == 0 and updates["unit_price"] > 0 and updates["quantity"] > 0:
            updates["total_price"] = updates["unit_price"] * updates["quantity"]

        Stock.update(sid, **updates)
        return redirect(url_for("stock.list_stock"))

    return render_template("stock_edit.html", item=item)


@bp.route("/stock/delete/<int:sid>")
def delete_stock(sid):
    Stock.delete(sid)
    return redirect(url_for("stock.list_stock"))
