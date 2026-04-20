from flask import Blueprint, render_template, redirect, url_for, session, flash
from services.auth_service import AuthService
from models.user import User

bp = Blueprint("admin", __name__)


@bp.route("/admin")
def admin_panel():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    if not AuthService.is_admin():
        flash("Доступ запрещён: требуется роль администратора.")
        return redirect(url_for("dashboard.dashboard"))

    users = User.get_all()
    return render_template("admin.html", users=users)


@bp.route("/admin/user/delete/<int:user_id>")
def delete_user(user_id):
    if not AuthService.is_admin():
        return "Доступ запрещён", 403
    if user_id == session["user_id"]:
        flash("Нельзя удалить самого себя.")
        return redirect(url_for("admin.admin_panel"))

    User.delete(user_id)
    flash("Пользователь удалён.")
    return redirect(url_for("admin.admin_panel"))


@bp.route("/admin/user/promote/<int:user_id>")
def promote_user(user_id):
    if not AuthService.is_admin():
        return "Доступ запрещён", 403
    User.update_role(user_id, "admin")
    flash("Пользователь повышен до администратора.")
    return redirect(url_for("admin.admin_panel"))


@bp.route("/admin/user/demote/<int:user_id>")
def demote_user(user_id):
    if not AuthService.is_admin():
        return "Доступ запрещён", 403
    User.update_role(user_id, "user")
    flash("Пользователь понижен до обычного пользователя.")
    return redirect(url_for("admin.admin_panel"))
