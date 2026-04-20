from flask import Blueprint, jsonify, request, session
from models.printer import Printer
from models.record import Record
from models.stock import Stock
from models.toner import Toner
from models.equipment import Equipment
from services.auth_service import AuthService
from models.user import User
from services.compatibility_service import CompatibilityService

bp = Blueprint("api", __name__)


@bp.route("/api/health")
def health():
    """Проверка работоспособности API"""
    return jsonify({"status": "ok", "data": "CartridgeApp API is running"})


@bp.route("/api/printers")
def api_printers():
    """Получить список всех активных принтеров"""
    try:
        printers = Printer.get_all(active_only=True)
        return jsonify([{
            "id": p["id"],
            "floor": p["floor"],
            "dept": p["dept"],
            "model": p["model"],
            "cartridge": p["cartridge"],
            "monthly_rate": p["monthly_rate"],
            "price": p["price"],
            "note": p["note"]
        } for p in printers])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/toners")
def api_toners():
    """Получить список всех тонеров"""
    try:
        toners = Toner.get_all()
        return jsonify([{
            "id": t["id"],
            "name": t["name"],
            "capacity_pages": t["capacity_pages"],
            "color": t["color"],
            "compatible_printers": t["compatible_printers"],
            "supplier": t["supplier"],
            "price": t["price"],
            "last_updated": t["last_updated"]
        } for t in toners])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/stock")
def api_stock():
    """Получить складские позиции"""
    try:
        items = Stock.get_all()
        return jsonify([{
            "id": s["id"],
            "item_name": s["item_name"],
            "category": s["category"],
            "quantity": s["quantity"],
            "unit_price": s["unit_price"],
            "total_price": s["total_price"],
            "note": s["note"]
        } for s in items])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/equipment")
def api_equipment():
    """Получить оборудование"""
    try:
        items = Equipment.get_all()
        return jsonify([{
            "id": e["id"],
            "type": e["type"],
            "model": e["model"],
            "serial_number": e["serial_number"],
            "assigned_to": e["assigned_to"],
            "purchase_date": e["purchase_date"],
            "warranty_until": e["warranty_until"],
            "status": e["status"],
            "note": e["note"]
        } for e in items])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/recent-records")
def api_recent_records():
    """Последние 10 записей о заправках"""
    try:
        records = Record.get_all_with_printers()[:10]
        return jsonify([{
            "id": r["id"],
            "date": r["date"],
            "printer_model": r["printer_model"],
            "department": r["department"],
            "cartridge_type": r["cartridge_type"],
            "toner_used": r["toner_used"],
            "pages_printed": r["pages_printed"]
        } for r in records])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Защищённые маршруты (только для админов)
@bp.route("/api/users")
def api_users():
    """Только для администраторов — получить список пользователей"""
    if not AuthService.is_admin():
        return jsonify({"error": "Доступ запрещён"}), 403
    try:
        users = User.get_all()
        return jsonify([{
            "id": u["id"],
            "username": u["username"],
            "role": u["role"]
        } for u in users])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route("/api/compatible-toners/<int:printer_id>")
def compatible_toners(printer_id):
    toners = CompatibilityService.get_compatible_toners(printer_id)
    return jsonify([{
        "id": t["id"],
        "name": t["name"],
        "cartridge": t["compatible_printers"]
    } for t in toners])

@bp.route("/api/events")
def api_events():
    return jsonify([])

@bp.route("/api/stats")
def api_stats():
    year = request.args.get("year", datetime.now().year)
    # Ваша логика статистики
    return jsonify({"total": 0})

@bp.route("/api/floors")
def api_floors():
    floors = [1, 2, 3]  # пример
    return jsonify(floors)

@bp.route("/api/stock/alerts")
def stock_alerts():
    return jsonify([])
