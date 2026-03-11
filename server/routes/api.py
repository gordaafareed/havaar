from flask import Blueprint, request, jsonify, send_from_directory, session, redirect, url_for, current_app
from functools import wraps
from server import storage

api_bp = Blueprint("api", __name__)


# ── auth guard ─────────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("authenticated"):
            return jsonify({"error": "unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


# ── calls ──────────────────────────────────────────────────────────────────────

@api_bp.route("/calls")
@login_required
def get_calls():
    return jsonify(storage.get_calls())


@api_bp.route("/calls/<recording_sid>/listened", methods=["POST"])
@login_required
def mark_listened(recording_sid):
    found = storage.mark_call_listened(recording_sid)
    if not found:
        return jsonify({"error": "not found"}), 404
    return jsonify({"ok": True})


# ── contacts ───────────────────────────────────────────────────────────────────

@api_bp.route("/contacts")
@login_required
def get_contacts():
    return jsonify(storage.get_contacts())


@api_bp.route("/contacts/<safe_id>/label", methods=["POST"])
@login_required
def set_label(safe_id):
    data = request.get_json()
    if not data or "label" not in data:
        return jsonify({"error": "missing label"}), 400
    found = storage.set_contact_label(safe_id, data["label"])
    if not found:
        return jsonify({"error": "contact not found"}), 404
    return jsonify({"ok": True})


# ── audio ─────────────────────────────────────────────────

@api_bp.route("/audio/incoming/<filename>")
@login_required
def serve_incoming(filename):
    return send_from_directory(current_app.config["RECORDINGS_IN"], filename)

@api_bp.route("/audio/outbound/<filename>")
@login_required
def serve_outbound(filename):
    return send_from_directory(current_app.config["RECORDINGS_OUT"], filename)


# ── outbound message ───────────────────────────────────────────────

@api_bp.route("/outbound/<safe_id>", methods=["POST"])
@login_required
def upload_outbound(safe_id):
    if "audio" not in request.files:
        return jsonify({"error": "no audio file"}), 400
    storage.save_outbound(request.files["audio"].read(), safe_id)
    return jsonify({"ok": True})


@api_bp.route("/outbound/default", methods=["POST"])
@login_required
def upload_default():
    if "audio" not in request.files:
        return jsonify({"error": "no audio file"}), 400
    storage.save_default(request.files["audio"].read())
    return jsonify({"ok": True})


@api_bp.route("/outbound/<safe_id>", methods=["DELETE"])
@login_required
def delete_outbound(safe_id):
    storage.delete_outbound(safe_id)
    return jsonify({"ok": True})


@api_bp.route("/outbound/default", methods=["DELETE"])
@login_required
def delete_default():
    storage.delete_default()
    return jsonify({"ok": True})


# ── status ─────────────────────────────────────────────────────────────────────

@api_bp.route("/status")
def status():
    return jsonify({
        "ok":             True,
        "twilio_sid_set": bool(current_app.config["TWILIO_SID"]),
        "twilio_token_set": bool(current_app.config["TWILIO_TOKEN"]),
        "default_greeting": storage.default_exists(),
    })
