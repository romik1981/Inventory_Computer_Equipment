# routes/auth_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session
from services.auth_service import AuthService

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()  # ← важно!
        password = request.form.get("password", "").strip()  # ← и здесь
        if AuthService.login(username, password):
            return redirect(url_for("dashboard.dashboard"))
        error = "Неверный логин или пароль"
    return render_template("login.html", error=error)


@bp.route("/logout")
def logout():
    AuthService.logout()
    return redirect(url_for("auth.login"))
