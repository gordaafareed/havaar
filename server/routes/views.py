from flask import Blueprint, session, redirect, url_for, send_from_directory, current_app
import pathlib

views_bp = Blueprint("views", __name__)

STATIC_DIR = pathlib.Path(__file__).parent.parent / "static"


@views_bp.route("/")
def dashboard():
    if not session.get("authenticated"):
        return redirect(url_for("views.login_page"))
    return send_from_directory(STATIC_DIR, "index.html")


@views_bp.route("/login", methods=["GET"])
def login_page():
    return send_from_directory(STATIC_DIR, "login.html")


@views_bp.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(STATIC_DIR, filename)


@views_bp.route("/public/audio/<filename>")
def public_audio(filename):
    return send_from_directory(current_app.config["RECORDINGS_OUT"], filename)
