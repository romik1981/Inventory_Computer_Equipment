from flask import Blueprint, render_template, session, redirect, url_for
from config import Config

bp = Blueprint("analytics", __name__)

@bp.route("/analytics")
def analytics():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("analytics.html", months=Config.MONTHS)
