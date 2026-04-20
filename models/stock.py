# models/stock.py
from models.database import Database


class Stock:
    @staticmethod
    def get_all():
        with Database.get_connection() as db:
            return db.execute("SELECT * FROM stock ORDER BY category, item_name").fetchall()

    @staticmethod
    def add(item_name, category, quantity, unit_price, total_price, note=""):
        with Database.get_connection() as db:
            db.execute("""
                INSERT INTO stock (item_name, category, quantity, unit_price, total_price, note)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (item_name, category, quantity, unit_price, total_price, note))

    @staticmethod
    def get_by_id(sid):
        with Database.get_connection() as db:
            return db.execute("SELECT * FROM stock WHERE id = ?", (sid,)).fetchone()

    @staticmethod
    def update(sid, **kwargs):
        with Database.get_connection() as db:
            fields = ", ".join(f"{k}=?" for k in kwargs.keys())
            values = list(kwargs.values()) + [sid]
            db.execute(f"UPDATE stock SET {fields} WHERE id=?", values)

    @staticmethod
    def delete(sid):
        with Database.get_connection() as db:
            db.execute("DELETE FROM stock WHERE id=?", (sid,))