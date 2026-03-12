import json
import pathlib
import re
import subprocess
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
    return {"contacts": {}, "threads": {}}


def save_meta(meta: dict) -> None:
    meta_file().write_text(json.dumps(meta, indent=2))


# ── contacts ───────────────────────────────────────────────────────────────────

def get_contacts() -> dict:
    return load_meta()["contacts"]


def ensure_contact(meta: dict, caller: str, safe_id: str) -> None:
    if safe_id not in meta["contacts"]:
        meta["contacts"][safe_id] = {"caller": caller, "label": ""}


def set_contact_label(safe_id: str, label: str) -> bool:
    meta = load_meta()
    if safe_id not in meta["contacts"]:
        return False
    meta["contacts"][safe_id]["label"] = label
    save_meta(meta)
    return True


# ── thread ─────────────────────────────────────────────────────────────────────

def get_thread(safe_id: str) -> list:
    return load_meta()["threads"].get(safe_id, [])


def get_all_threads(meta: dict) -> dict:
    return meta.get("threads", {})


def add_incoming(caller: str, recording_sid: str, filename: str) -> dict:
    meta    = load_meta()
    safe_id = safe_caller_id(caller)
    ensure_contact(meta, caller, safe_id)

    entry = {
        "id":        recording_sid,
        "type":      "incoming",
        "caller":    caller,
        "safe_id":   safe_id,
        "timestamp": datetime.utcnow().isoformat(),
        "filename":  filename,
        "listened":  False,
    }

    if safe_id not in meta["threads"]:
        meta["threads"][safe_id] = []
    meta["threads"][safe_id].append(entry)
    save_meta(meta)
    return entry


def add_outgoing(safe_id: str, filename: str) -> dict:
    meta  = load_meta()
    entry = {
        "id":        f"out_{safe_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "type":      "outgoing",
        "safe_id":   safe_id,
        "timestamp": datetime.utcnow().isoformat(),
        "filename":  filename,
        "pending":   True,
        "played":    False,
    }
    if safe_id not in meta["threads"]:
        meta["threads"][safe_id] = []
    meta["threads"][safe_id].append(entry)
    save_meta(meta)
    return entry


def get_pending_replies(safe_id: str) -> list:
    meta = load_meta()
    thread = meta["threads"].get(safe_id, [])
    result = [e for e in thread if e["type"] == "outgoing" and e.get("pending")]
    return result


def mark_replies_played(safe_id: str) -> None:
    """Mark pending replies as played and delete their audio files."""
    meta   = load_meta()
    thread = meta["threads"].get(safe_id, [])
    for entry in thread:
        if entry["type"] == "outgoing" and entry.get("pending"):
            if entry.get("filename"):
                path = recordings_out() / entry["filename"]
                if path.exists():
                    path.unlink()
            entry["pending"]  = False
            entry["played"]   = True
            entry["filename"] = None
    save_meta(meta)


def mark_incoming_listened(entry_id: str) -> bool:
    meta = load_meta()
    for thread in meta["threads"].values():
        for entry in thread:
            if entry["id"] == entry_id and entry["type"] == "incoming":
                entry["listened"] = True
                save_meta(meta)
                return True
    return False


def delete_incoming(entry_id: str) -> bool:
    meta = load_meta()
    for safe_id, thread in meta["threads"].items():
        for i, entry in enumerate(thread):
            if entry["id"] == entry_id and entry["type"] == "incoming":
                if entry.get("filename"):
                    path = recordings_in() / entry["filename"]
                    if path.exists():
                        path.unlink()
                meta["threads"][safe_id].pop(i)
                save_meta(meta)
                return True
    return False


def delete_outgoing(entry_id: str) -> bool:
    meta = load_meta()
    for safe_id, thread in meta["threads"].items():
        for i, entry in enumerate(thread):
            if entry["id"] == entry_id and entry["type"] == "outgoing":
                if entry.get("filename"):
                    path = outgoing_path(entry["filename"])
                    if path.exists():
                        path.unlink()
                meta["threads"][safe_id].pop(i)
                save_meta(meta)
                return True
    return False


# ── audio files ────────────────────────────────────────────────────────────────

def incoming_path(filename: str) -> pathlib.Path:
    return recordings_in() / filename


def outgoing_path(filename: str) -> pathlib.Path:
    return recordings_out() / filename


def save_incoming(data: bytes, caller: str, recording_sid: str) -> str:
    safe_id   = safe_caller_id(caller)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename  = f"{safe_id}_{timestamp}.wav"
    incoming_path(filename).write_bytes(data)
    add_incoming(caller, recording_sid, filename)
    return filename


def save_outgoing(data: bytes, safe_id: str) -> str:
    timestamp   = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    webm_path   = outgoing_path(f"{safe_id}_{timestamp}_tmp.webm")
    wav_filename = f"{safe_id}_{timestamp}.wav"
    wav_path    = outgoing_path(wav_filename)

    webm_path.write_bytes(data)
    subprocess.run([
        "ffmpeg", "-i", str(webm_path),
        "-ar", "8000",      # 8kHz
        "-ac", "1",         # mono
        "-y", str(wav_path)
    ], check=True, capture_output=True)
    webm_path.unlink()

    add_outgoing(safe_id, wav_filename)
    return wav_filename


def delete_default() -> bool:
    path = recordings_out() / "default.wav"
    if path.exists():
        path.unlink()
        return True
    return False


def save_default(data: bytes) -> None:
    (recordings_out() / "default.wav").write_bytes(data)


def default_exists() -> bool:
    return (recordings_out() / "default.wav").exists()


# ── broadcast ────────────────────────────────────────────────────────────────

def broadcast_live_path() -> pathlib.Path:
    return recordings_out() / "broadcast_live.wav"

def broadcast_draft_path() -> pathlib.Path:
    return recordings_out() / "broadcast_draft.wav"

def broadcast_live_exists() -> bool:
    return broadcast_live_path().exists()

def broadcast_draft_exists() -> bool:
    return broadcast_draft_path().exists()

def save_broadcast_draft(data: bytes) -> None:
    tmp  = recordings_out() / "broadcast_draft_tmp.webm"
    path = broadcast_draft_path()
    tmp.write_bytes(data)
    subprocess.run([
        "ffmpeg", "-i", str(tmp),
        "-ar", "8000", "-ac", "1",
        "-y", str(path)
    ], check=True, capture_output=True)
    tmp.unlink()

def publish_broadcast(title: str) -> None:
    draft = broadcast_draft_path()
    if not draft.exists():
        raise FileNotFoundError("no draft to publish")
    draft.rename(broadcast_live_path())
    meta = load_meta()
    meta["broadcast"] = {
        "title":     title,
        "published": datetime.utcnow().isoformat(),
    }
    save_meta(meta)

def unpublish_broadcast() -> None:
    path = broadcast_live_path()
    if path.exists():
        path.unlink()
    meta = load_meta()
    meta.pop("broadcast", None)
    save_meta(meta)

def get_broadcast_meta() -> dict:
    return load_meta().get("broadcast", None)

def delete_broadcast_draft() -> None:
    path = broadcast_draft_path()
    if path.exists():
        path.unlink()

# ── panic ────────────────────────────────────────────────────────────────

def log_panic(caller: str) -> None:
    meta    = load_meta()
    safe_id = safe_caller_id(caller)
    ensure_contact(meta, caller, safe_id)
    entry = {
        "id":        f"panic_{safe_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "type":      "panic",
        "caller":    caller,
        "safe_id":   safe_id,
        "timestamp": datetime.utcnow().isoformat(),
    }
    if safe_id not in meta["threads"]:
        meta["threads"][safe_id] = []
    meta["threads"][safe_id].append(entry)
    save_meta(meta)
