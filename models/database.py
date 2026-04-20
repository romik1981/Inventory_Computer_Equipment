# models/database.py
# models/database.py
import sqlite3
import os
from datetime import datetime
from config import Config


class Database:
    @staticmethod
    def get_connection():
        conn = sqlite3.connect(Config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def init_db():
        """Создаёт таблицы, но НЕ создаёт администратора"""
        os.makedirs(Config.BACKUP_DIR, exist_ok=True)

        with Database.get_connection() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user'
                );

                CREATE TABLE IF NOT EXISTS printers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    floor INTEGER NOT NULL,
                    dept TEXT NOT NULL,
                    model TEXT NOT NULL,
                    cartridge TEXT NOT NULL,
                    monthly_rate INTEGER NOT NULL DEFAULT 0,
                    price REAL NOT NULL DEFAULT 0,
                    note TEXT,
                    active INTEGER DEFAULT 1
                );

                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    printer_id INTEGER,
                    cartridge_type TEXT NOT NULL,
                    toner_used REAL NOT NULL DEFAULT 0,
                    pages_printed INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY (printer_id) REFERENCES printers(id)
                );

                CREATE TABLE IF NOT EXISTS stock (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    unit_price REAL,
                    total_price REAL,
                    note TEXT
                );

                CREATE TABLE IF NOT EXISTS equipment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    model TEXT NOT NULL,
                    serial_number TEXT UNIQUE,
                    assigned_to TEXT,
                    purchase_date TEXT,
                    warranty_until TEXT,
                    status TEXT DEFAULT 'active',
                    note TEXT
                );

                CREATE TABLE IF NOT EXISTS toners (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    capacity_pages INTEGER,
                    color TEXT,
                    compatible_printers TEXT,
                    supplier TEXT,
                    price REAL,
                    last_updated TEXT
                );
            """)

            # --- Миграция: добавление колонки date в records ---
            try:
                db.execute("ALTER TABLE records ADD COLUMN date TEXT")
                db.execute("UPDATE records SET date = ? WHERE date IS NULL", (datetime.now().strftime("%Y-%m-%d"),))
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e):
                    print(f"Ошибка при миграции: {e}")
