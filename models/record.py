# models/record.py
from datetime import datetime
from models.database import Database


class Record:
    @staticmethod
    def get_all_with_printers():
        """Получить все записи с информацией о принтерах"""
        query = """
            SELECT r.*, p.model as printer_model, p.dept as department
            FROM records r
            LEFT JOIN printers p ON r.printer_id = p.id
            ORDER BY r.date DESC
        """
        with Database.get_connection() as db:
            return db.execute(query).fetchall()

    @staticmethod
    def add(date, printer_id, cartridge_type, toner_used, pages_printed):
        with Database.get_connection() as db:
            db.execute("""
                INSERT INTO records (date, printer_id, cartridge_type, toner_used, pages_printed)
                VALUES (?, ?, ?, ?, ?)
            """, (date, printer_id, cartridge_type, toner_used, pages_printed))

    @staticmethod
    def get_by_id(rid):
        with Database.get_connection() as db:
            return db.execute("SELECT * FROM records WHERE id = ?", (rid,)).fetchone()

    @staticmethod
    def update(rid, **kwargs):
        with Database.get_connection() as db:
            fields = ", ".join(f"{k}=?" for k in kwargs.keys())
            values = list(kwargs.values()) + [rid]
            db.execute(f"UPDATE records SET {fields} WHERE id=?", values)

    @staticmethod
    def delete(rid):
        with Database.get_connection() as db:
            db.execute("DELETE FROM records WHERE id=?", (rid,))
