import requests
from flask import Blueprint, request, Response, current_app
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
from server import storage

twilio_bp = Blueprint("twilio", __name__)

_active_calls = {}

def get_client():
    return Client(
        current_app.config["TWILIO_SID"],
        current_app.config["TWILIO_TOKEN"]
    )


@twilio_bp.route("/incoming", methods=["POST"])
def incoming():
    caller   = request.form.get("From", "unknown")
    call_sid = request.form.get("CallSid")
    safe_id  = storage.safe_caller_id(caller)

    if call_sid:
        _active_calls[call_sid] = caller

    response = VoiceResponse()

    pending = storage.get_pending_replies(safe_id)

    for reply in pending:
        if reply.get("filename"):
            url = request.url_root + f"public/audio/{reply['filename']}"
            response.play(url)

    response.record(
        action                           = request.url_root + "twilio/recording-done",
        method                           = "POST",
        max_length                       = 120,
        play_beep                        = True,
        recording_status_callback        = request.url_root + "twilio/recording-ready",
        recording_status_callback_method = "POST",
    )

    return Response(str(response), mimetype="text/xml")


@twilio_bp.route("/recording-done", methods=["POST"])
def recording_done():
    caller  = request.form.get("From", "unknown")
    safe_id = storage.safe_caller_id(caller)
    storage.mark_replies_played(safe_id)
    response = VoiceResponse()
    response.hangup()
    return Response(str(response), mimetype="text/xml")


@twilio_bp.route("/recording-ready", methods=["POST"])
def recording_ready():
    call_sid      = request.form.get("CallSid")
    recording_url = request.form.get("RecordingUrl")
    recording_sid = request.form.get("RecordingSid")

    caller = _active_calls.pop(call_sid, "unknown")

    if not recording_url:
        return ("", 204)

    audio = requests.get(
        recording_url + ".wav",
        auth    = (current_app.config["TWILIO_SID"], current_app.config["TWILIO_TOKEN"]),
        timeout = 30,
    )

    if audio.status_code == 200:
        storage.save_incoming(audio.content, caller, recording_sid)

    return ("", 204)
