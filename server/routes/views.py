from flask import Blueprint, session, redirect, url_for, send_from_directory, current_app
import pathlib

views_bp = Blueprint("views", __name__)

STATIC_DIR = pathlib.Path(__file__).parent.parent / "static"

@views_bp.route("/")
def dashboard():
    if not session.get("authenticated"):
        return redirect(url_for("views.login_page"))
    return send_from_directory(STATIC_DIR, "dashboard.html")

@views_bp.route("/login")
def login_page():
    return send_from_directory(STATIC_DIR, "login.html")

@views_bp.route("/public/audio/<filename>")
def public_audio(filename):
    path = pathlib.Path(current_app.config["RECORDINGS_OUT"]) / filename
    if not path.exists():
        return ("", 404)
    return send_from_directory(current_app.config["RECORDINGS_OUT"], filename)
