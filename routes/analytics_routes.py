from flask import Blueprint, render_template, session, jsonify, request, redirect, url_for
from config import Config
import os
import shutil
from datetime import datetime

bp = Blueprint("analytics", __name__)


@bp.route("/analytics")
def analytics():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("analytics.html")


# API: Получить список бэкапов
@bp.route("/api/backups")
def api_backups():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    if not session.get("role") == "admin":
        return jsonify({"error": "Доступ запрещён"}), 403


    backups = []
    if os.path.exists(Config.BACKUP_DIR):
        for f in sorted(os.listdir(Config.BACKUP_DIR), reverse=True):
            path = os.path.join(Config.BACKUP_DIR, f)
            if f.startswith("data_") and f.endswith(".db"):
                stat = os.stat(path)
                backups.append({
                    "name": f,
                    "date": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                    "size": f"{stat.st_size / (1024*1024):.1f} MB",
                    "path": f"/backups/{f}"
                })
    return jsonify(backups)


# API: Создать новый бэкап
@bp.route("/api/backup", methods=["POST"])
def create_backup():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    if not session.get("role") == "admin":
        return jsonify({"error": "Доступ запрещён"}), 403

    try:
        # Убедимся, что папка существует
        os.makedirs(Config.BACKUP_DIR, exist_ok=True)

        # Имя файла с датой и временем
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"data_{timestamp}.db"
        backup_path = os.path.join(Config.BACKUP_DIR, backup_filename)

        # Копируем текущую базу данных
        shutil.copy2(Config.DATABASE_PATH, backup_path)

        return jsonify({
            "status": "success",
            "message": "Резервная копия создана",
            "backup": {
                "name": backup_filename,
                "date": timestamp.replace("_", " "),
                "path": f"/backups/{backup_filename}"
            }
        }), 201

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Ошибка при создании резервной копии: {str(e)}"
        }), 500


# API: Статистика для графиков
@bp.route("/api/stats")
def api_stats():
    year = request.args.get("year", type=int) or datetime.now().year
    # Здесь можно подключить реальную статистику из records
    return jsonify({
        "months": Config.MONTHS_SHORT,
        "toner_usage": [50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160],
        "pages_printed": [1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300]
    })
