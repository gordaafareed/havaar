import json
import pathlib
import re
from datetime import datetime
from flask import current_app


# ── helpers ────────────────────────────────────────────────────────────────────

def recordings_in() -> pathlib.Path:
    return current_app.config["RECORDINGS_IN"]


def recordings_out() -> pathlib.Path:
    return current_app.config["RECORDINGS_OUT"]


def meta_file() -> pathlib.Path:
    return current_app.config["RECORDINGS_IN"].parent / "meta.json"


def safe_caller_id(caller: str) -> str:
    return re.sub(r"\W", "", caller)


# ── meta ───────────────────────────────────────────────────────────────────────

def load_meta() -> dict:
    f = meta_file()
    if f.exists():
        return json.loads(f.read_text())
    return {"calls": [], "contacts": {}}


def save_meta(meta: dict) -> None:
    meta_file().write_text(json.dumps(meta, indent=2))


# ── calls ──────────────────────────────────────────────────────────────────────

def add_call(caller: str, recording_sid: str, filename: str) -> dict:
    meta      = load_meta()
    safe_id   = safe_caller_id(caller)
    entry     = {
        "id":        recording_sid,
        "caller":    caller,
        "safe_id":   safe_id,
        "timestamp": datetime.utcnow().isoformat(),
        "filename":  filename,
        "listened":  False,
    }
    meta["calls"].insert(0, entry)

    if safe_id not in meta["contacts"]:
        meta["contacts"][safe_id] = {"caller": caller, "label": ""}

    save_meta(meta)
    return entry


def mark_call_listened(recording_sid: str) -> bool:
    meta = load_meta()
    for call in meta["calls"]:
        if call["id"] == recording_sid:
            call["listened"] = True
            save_meta(meta)
            return True
    return False


def get_calls() -> list:
    return load_meta()["calls"]


# ── contacts ───────────────────────────────────────────────────────────────────

def get_contacts() -> dict:
    return load_meta()["contacts"]


def set_contact_label(safe_id: str, label: str) -> bool:
    meta = load_meta()
    if safe_id not in meta["contacts"]:
        return False
    meta["contacts"][safe_id]["label"] = label
    save_meta(meta)
    return True


# ── audio files ────────────────────────────────────────────────────────────────

def incoming_path(filename: str) -> pathlib.Path:
    return recordings_in() / filename


def outbound_path(safe_id: str) -> pathlib.Path:
    return recordings_out() / f"{safe_id}.wav"


def default_path() -> pathlib.Path:
    return recordings_out() / "default.wav"


def save_incoming(data: bytes, caller: str, recording_sid: str) -> str:
    safe_id   = safe_caller_id(caller)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename  = f"{safe_id}_{timestamp}.wav"
    incoming_path(filename).write_bytes(data)
    add_call(caller, recording_sid, filename)
    return filename


def save_outbound(data: bytes, safe_id: str) -> pathlib.Path:
    path = outbound_path(safe_id)
    path.write_bytes(data)
    return path


def save_default(data: bytes) -> pathlib.Path:
    path = default_path()
    path.write_bytes(data)
    return path


def delete_outbound(safe_id: str) -> bool:
    path = outbound_path(safe_id)
    if path.exists():
        path.unlink()
        return True
    return False


def delete_default() -> bool:
    path = default_path()
    if path.exists():
        path.unlink()
        return True
    return False


def outbound_exists(safe_id: str) -> bool:
    return outbound_path(safe_id).exists()


def default_exists() -> bool:
    return default_path().exists()
