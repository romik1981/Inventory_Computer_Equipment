# services/auth_service.py
import hashlib
from flask import session
from models.user import User


class AuthService:
    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def login(username, password):
        user = User.find_by_username(username)
        if user and user["password"] == AuthService.hash_password(password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            return True
        return False

    @staticmethod
    def logout():
        session.clear()

    @staticmethod
    def is_admin():
        return session.get("role") == "admin"

    @staticmethod
    def require_admin(f):
        def wrapper(*args, **kwargs):
            if not AuthService.is_admin():
                return "Доступ запрещён", 403
            return f(*args, **kwargs)
        return wrapper
