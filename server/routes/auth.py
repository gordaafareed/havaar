from flask import Blueprint, request, session, jsonify, redirect, url_for, current_app

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if data and data.get("password") == current_app.config["DASHBOARD_PASSWORD"]:
        session["authenticated"] = True
        return jsonify({"ok": True})
    return jsonify({"error": "wrong password"}), 401


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})
