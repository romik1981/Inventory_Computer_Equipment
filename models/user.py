from models.database import Database


class User:
    @staticmethod
    def find_by_username(username):
        """Найти пользователя по логину"""
        with Database.get_connection() as db:
            return db.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()

    @staticmethod
    def get_all():
        """Получить всех пользователей (без паролей)"""
        with Database.get_connection() as db:
            return db.execute(
                "SELECT id, username, role FROM users ORDER BY username"
            ).fetchall()

    @staticmethod
    def create(username, password_hash, role="user"):
        """Создать нового пользователя"""
        with Database.get_connection() as db:
            db.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, password_hash, role)
            )

    @staticmethod
    def update_role(user_id, new_role):
        """Обновить роль пользователя"""
        with Database.get_connection() as db:
            db.execute(
                "UPDATE users SET role = ? WHERE id = ?",
                (new_role, user_id)
            )

    @staticmethod
    def delete(user_id):
        """Удалить пользователя по ID"""
        with Database.get_connection() as db:
            db.execute("DELETE FROM users WHERE id = ?", (user_id,))