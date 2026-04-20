from datetime import datetime
from models.database import Database


class Toner:
    @staticmethod
    def get_all():
        """Получить все типы тонеров"""
        with Database.get_connection() as db:
            return db.execute(
                "SELECT * FROM toners ORDER BY name"
            ).fetchall()

    @staticmethod
    def get_by_id(tid):
        """Получить тонер по ID"""
        with Database.get_connection() as db:
            return db.execute(
                "SELECT * FROM toners WHERE id = ?", (tid,)
            ).fetchone()

    @staticmethod
    def add(name, capacity_pages, color, compatible_printers, supplier, price):
        """Добавить новый тип тонера"""
        with Database.get_connection() as db:
            db.execute("""
                INSERT INTO toners 
                (name, capacity_pages, color, compatible_printers, supplier, price, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, capacity_pages, color, compatible_printers, supplier, price, datetime.now().strftime("%Y-%m-%d")))

    @staticmethod
    def update(tid, **kwargs):
        """Обновить данные о тонере"""
        with Database.get_connection() as db:
            # Добавляем обновление даты
            kwargs["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            fields = ", ".join(f"{k}=?" for k in kwargs.keys())
            values = list(kwargs.values()) + [tid]
            db.execute(f"UPDATE toners SET {fields} WHERE id=?", values)

    @staticmethod
    def delete(tid):
        """Удалить тип тонера"""
        with Database.get_connection() as db:
            db.execute("DELETE FROM toners WHERE id=?", (tid,))
