from flask import Flask, redirect, url_for
from config import Config
from models.database import Database
from services.auth_service import AuthService  # ← только здесь!
from models.user import User


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # --- Регистрация Blueprint'ов ---
    from routes.auth_routes import bp as auth_bp
    from routes.dashboard_routes import bp as dashboard_bp
    from routes.printer_routes import bp as printer_bp
    from routes.record_routes import bp as record_bp
    from routes.stock_routes import bp as stock_bp
    from routes.equipment_routes import bp as equipment_bp
    from routes.toner_routes import bp as toner_bp
    from routes.admin_routes import bp as admin_bp
    from routes.api_routes import bp as api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(printer_bp)
    app.register_blueprint(record_bp)
    app.register_blueprint(stock_bp)
    app.register_blueprint(equipment_bp)
    app.register_blueprint(toner_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # Главная страница
    @app.route("/")
    def index():
        return redirect(url_for("dashboard.dashboard"))

    return app


if __name__ == "__main__":
    # === Инициализация базы данных ===
    Database.init_db()

    # === Создание администратора при старте ===
    with Database.get_connection() as db:
        user = db.execute("SELECT * FROM users WHERE username = ?", ("admin",)).fetchone()
        if not user:
            password_hash = AuthService.hash_password("admin123")
            db.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ("admin", password_hash, "admin")
            )
            print("✅ Администратор 'admin' создан с паролем 'admin123'")
        else:
            print("ℹ️ Администратор уже существует")

    # === Запуск приложения ===
    app = create_app()

    print("\n" + "=" * 55)
    print("  CartridgeApp запущено!")
    print("  Откройте в браузере: http://localhost:5000")
    print("  Логин: admin | Пароль: admin123")
    print("=" * 55 + "\n")

    try:
        from waitress import serve
        serve(app, host="0.0.0.0", port=5000, threads=4)
    except ImportError:
        app.run(host="0.0.0.0", port=5000, debug=False)
