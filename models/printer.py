# models/printer.py
from models.database import Database


class Printer:
    @staticmethod
    def get_all(active_only=True):
        query = "SELECT * FROM printers"
        if active_only:
            query += " WHERE active=1"
        query += " ORDER BY floor, id"
        with Database.get_connection() as db:
            return db.execute(query).fetchall()

    @staticmethod
    def get_by_id(pid):
        with Database.get_connection() as db:
            return db.execute(
                "SELECT * FROM printers WHERE id = ?", (pid,)
            ).fetchone()

    @staticmethod
    def add(floor, dept, model, cartridge, monthly_rate, price, note=""):
        with Database.get_connection() as db:
            db.execute("""
                INSERT INTO printers (floor,dept,model,cartridge,monthly_rate,price,note)
                VALUES (?,?,?,?,?,?,?)
            """, (floor, dept, model, cartridge, monthly_rate, price, note))

    @staticmethod
    def update(pid, **kwargs):
        with Database.get_connection() as db:
            fields = ", ".join(f"{k}=?" for k in kwargs.keys())
            values = list(kwargs.values()) + [pid]
            db.execute(f"UPDATE printers SET {fields} WHERE id=?", values)

    @staticmethod
    def delete(pid):
        with Database.get_connection() as db:
            db.execute("UPDATE printers SET active=0 WHERE id=?", (pid,))
