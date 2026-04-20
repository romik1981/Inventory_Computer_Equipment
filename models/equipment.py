from models.database import Database


class Equipment:
    @staticmethod
    def get_all():
        """Получить всё оборудование"""
        with Database.get_connection() as db:
            return db.execute(
                "SELECT * FROM equipment ORDER BY type, model"
            ).fetchall()

    @staticmethod
    def get_by_id(eid):
        """Получить оборудование по ID"""
        with Database.get_connection() as db:
            return db.execute(
                "SELECT * FROM equipment WHERE id = ?", (eid,)
            ).fetchone()

    @staticmethod
    def add(type, model, serial_number, assigned_to, purchase_date, warranty_until, status, note=""):
        """Добавить новое оборудование"""
        with Database.get_connection() as db:
            db.execute("""
                INSERT INTO equipment 
                (type, model, serial_number, assigned_to, purchase_date, warranty_until, status, note)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (type, model, serial_number, assigned_to, purchase_date, warranty_until, status, note))

    @staticmethod
    def update(eid, **kwargs):
        """Обновить запись об оборудовании"""
        with Database.get_connection() as db:
            fields = ", ".join(f"{k}=?" for k in kwargs.keys())
            values = list(kwargs.values()) + [eid]
            db.execute(f"UPDATE equipment SET {fields} WHERE id=?", values)

    @staticmethod
    def delete(eid):
        """Удалить оборудование"""
        with Database.get_connection() as db:
            db.execute("DELETE FROM equipment WHERE id=?", (eid,))
