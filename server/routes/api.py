from flask import Blueprint, request, jsonify, send_from_directory, session, current_app
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


# ── threads ────────────────────────────────────────────────────────────────────

@api_bp.route("/threads")
@login_required
def get_threads():
    meta = storage.load_meta()
    return jsonify({
        "threads":  storage.get_all_threads(meta),
        "contacts": meta["contacts"],
    })


@api_bp.route("/threads/<safe_id>")
@login_required
def get_thread(safe_id):
    return jsonify(storage.get_thread(safe_id))


@api_bp.route("/threads/<entry_id>/listened", methods=["POST"])
@login_required
def mark_listened(entry_id):
    found = storage.mark_incoming_listened(entry_id)
    if not found:
        return jsonify({"error": "not found"}), 404
    return jsonify({"ok": True})


@api_bp.route("/threads/<entry_id>", methods=["DELETE"])
@login_required
def delete_incoming(entry_id):
    storage.delete_incoming(entry_id)
    return jsonify({"ok": True})


# ── contacts ───────────────────────────────────────────────────────────────────

@api_bp.route("/contacts/<safe_id>/label", methods=["POST"])
@login_required
def set_label(safe_id):
    data = request.get_json()
    if not data or "label" not in data:
        return jsonify({"error": "missing label"}), 400
    found = storage.set_contact_label(safe_id, data.get("label", ""))
    if not found:
        return jsonify({"error": "not found"}), 404
    return jsonify({"ok": True})


# ── audio — incoming ───────────────────────────────────────────────────────────

@api_bp.route("/audio/incoming/<filename>")
@login_required
def serve_incoming(filename):
    return send_from_directory(current_app.config["RECORDINGS_IN"], filename)


# ── audio — outgoing ────────────────────────────────

@api_bp.route("/audio/outgoing/<filename>")
@login_required
def serve_outgoing(filename):
    return send_from_directory(current_app.config["RECORDINGS_OUT"], filename)

@api_bp.route("/reply/<entry_id>", methods=["DELETE"])
@login_required
def delete_reply(entry_id):
    storage.delete_outgoing(entry_id)
    return jsonify({"ok": True})

@api_bp.route("/reply/<safe_id>", methods=["POST"])
@login_required
def upload_reply(safe_id):
    if "audio" not in request.files:
        return jsonify({"error": "no audio"}), 400
    filename = storage.save_outgoing(request.files["audio"].read(), safe_id)
    return jsonify({"ok": True, "filename": filename})


# ── default greeting ───────────────────────────────────────────────────────────

@api_bp.route("/outbound/default", methods=["POST"])
@login_required
def upload_default():
    if "audio" not in request.files:
        return jsonify({"error": "no audio"}), 400
    storage.save_default(request.files["audio"].read())
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
        "default_exists": storage.default_exists(),
    })
