from flask import Blueprint, render_template, request, redirect, url_for, session
from models.equipment import Equipment

bp = Blueprint("equipment", __name__)


@bp.route("/equipment")
def list_equipment():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    items = Equipment.get_all()
    return render_template("equipment.html", items=items)


@bp.route("/equipment/add", methods=["GET", "POST"])
def add_equipment():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        try:
            type = request.form["type"].strip()
            model = request.form["model"].strip()
            serial_number = request.form["serial_number"].strip()
            assigned_to = request.form.get("assigned_to", "").strip()
            purchase_date = request.form["purchase_date"]
            warranty_until = request.form["warranty_until"]
            status = request.form["status"]
            note = request.form.get("note", "").strip()

            Equipment.add(
                type=type,
                model=model,
                serial_number=serial_number,
                assigned_to=assigned_to,
                purchase_date=purchase_date,
                warranty_until=warranty_until,
                status=status,
                note=note
            )
            return redirect(url_for("equipment.list_equipment"))
        except Exception as e:
            return f"Ошибка при добавлении оборудования: {str(e)}", 400

    return render_template("equipment_add.html")


@bp.route("/equipment/edit/<int:eid>", methods=["GET", "POST"])
def edit_equipment(eid):
    item = Equipment.get_by_id(eid)
    if not item:
        return "Оборудование не найдено", 404

    if request.method == "POST":
        updates = {
            "type": request.form["type"].strip(),
            "model": request.form["model"].strip(),
            "serial_number": request.form["serial_number"].strip(),
            "assigned_to": request.form.get("assigned_to", "").strip(),
            "purchase_date": request.form["purchase_date"],
            "warranty_until": request.form["warranty_until"],
            "status": request.form["status"],
            "note": request.form.get("note", "").strip(),
        }
        Equipment.update(eid, **updates)
        return redirect(url_for("equipment.list_equipment"))

    return render_template("equipment_edit.html", item=item)


@bp.route("/equipment/delete/<int:eid>")
def delete_equipment(eid):
    Equipment.delete(eid)
    return redirect(url_for("equipment.list_equipment"))
