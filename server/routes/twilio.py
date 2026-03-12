import requests
from flask import Blueprint, request, Response, current_app
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from server import storage

twilio_bp    = Blueprint("twilio", __name__)
_active_calls = {}


def get_client():
    return Client(
        current_app.config["TWILIO_SID"],
        current_app.config["TWILIO_TOKEN"]
    )


def base_url():
    return request.url_root


def audio_url(filename):
    return base_url() + f"public/audio/{filename}"


def twiml(response):
    return Response(str(response), mimetype="text/xml")


@twilio_bp.route("/incoming", methods=["POST"])
def incoming():
    caller   = request.form.get("From", "unknown")
    call_sid = request.form.get("CallSid")
    safe_id  = storage.safe_caller_id(caller)

    if call_sid:
        _active_calls[call_sid] = caller

    response = VoiceResponse()
    out      = storage.recordings_out()
    pending  = storage.get_pending_replies(safe_id)

    if (out / "greeting.wav").exists():
        response.play(audio_url("greeting.wav"))

    if pending and (out / "you_have_messages.wav").exists():
        response.play(audio_url("you_have_messages.wav"))

    for reply in pending:
        if reply.get("filename"):
            response.play(audio_url(reply["filename"]))

    _append_menu(response)

    return twiml(response)


def _append_menu(response):
    out = storage.recordings_out()
    gather = response.gather(
        num_digits = 1,
        timeout    = 8,
        action     = base_url() + "twilio/menu",
        method     = "POST",
    )
    if (out / "menu.wav").exists():
        gather.play(audio_url("menu.wav"))

    _append_menu_repeat(response)


def _append_menu_repeat(response):
    out = storage.recordings_out()
    gather = response.gather(
        num_digits = 1,
        timeout    = 8,
        action     = base_url() + "twilio/menu",
        method     = "POST",
    )
    if (out / "menu.wav").exists():
        gather.play(audio_url("menu.wav"))
    response.hangup()


@twilio_bp.route("/menu", methods=["POST"])
def menu():
    digit    = request.form.get("Digits", "")
    response = VoiceResponse()
    out      = storage.recordings_out()

    if digit == "1":
        if (out / "leave_message.wav").exists():
            response.play(audio_url("leave_message.wav"))
        response.record(
            action                           = base_url() + "twilio/recording-done",
            method                           = "POST",
            max_length                       = 120,
            play_beep                        = True,
            recording_status_callback        = base_url() + "twilio/recording-ready",
            recording_status_callback_method = "POST",
        )

    elif digit == "2":
        if storage.broadcast_live_exists():
            response.play(audio_url("broadcast_live.wav"))
            gather = response.gather(
                num_digits = 1,
                timeout    = 8,
                action     = base_url() + "twilio/after-broadcast",
                method     = "POST",
            )
            if (out / "after_broadcast.wav").exists():
                gather.play(audio_url("after_broadcast.wav"))
            response.hangup()
        else:
            if (out / "no_broadcast.wav").exists():
                response.play(audio_url("no_broadcast.wav"))
            _append_menu(response)

    elif digit == "3":
        if (out / "image_instruction.wav").exists():
            response.play(audio_url("image_instruction.wav"))
        gather = response.gather(
            num_digits = 1,
            timeout    = 30,
            action     = base_url() + "twilio/image-ready",
            method     = "POST",
        )
        response.hangup()

    else:
        _append_menu(response)

    return twiml(response)


@twilio_bp.route("/after-broadcast", methods=["POST"])
def after_broadcast():
    digit    = request.form.get("Digits", "")
    response = VoiceResponse()
    out      = storage.recordings_out()

    if digit == "1":
        if (out / "leave_message.wav").exists():
            response.play(audio_url("leave_message.wav"))
        response.record(
            action                           = base_url() + "twilio/recording-done",
            method                           = "POST",
            max_length                       = 120,
            play_beep                        = True,
            recording_status_callback        = base_url() + "twilio/recording-ready",
            recording_status_callback_method = "POST",
        )
    elif digit == "2":
        # hear broadcast again — redirect back to broadcast
        response.play(audio_url("broadcast_live.wav"))
        gather = response.gather(
            num_digits = 1,
            timeout    = 8,
            action     = base_url() + "twilio/after-broadcast",
            method     = "POST",
        )
        if (out / "after_broadcast.wav").exists():
            gather.play(audio_url("after_broadcast.wav"))
        response.hangup()
    else:
        response.hangup()

    return twiml(response)


@twilio_bp.route("/image-ready", methods=["POST"])
def image_ready():
    caller   = request.form.get("From", "unknown")
    call_sid = request.form.get("CallSid")
    safe_id  = storage.safe_caller_id(caller)
    response = VoiceResponse()
    out      = storage.recordings_out()

    if call_sid:
        _active_calls[call_sid] = caller
        _active_calls[f"{call_sid}_type"] = "image"

    if (out / "image_ready.wav").exists():
        response.play(audio_url("image_ready.wav"))

    response.record(
        action                           = base_url() + "twilio/recording-done",
        method                           = "POST",
        max_length                       = 30,
        play_beep                        = False,
        recording_status_callback        = base_url() + "twilio/recording-ready",
        recording_status_callback_method = "POST",
    )

    return twiml(response)


@twilio_bp.route("/recording-done", methods=["POST"])
def recording_done():
    caller   = request.form.get("From", "unknown")
    call_sid = request.form.get("CallSid")
    safe_id  = storage.safe_caller_id(
        _active_calls.get(call_sid, caller)
    )
    storage.mark_replies_played(safe_id)
    response = VoiceResponse()
    response.hangup()
    return twiml(response)


@twilio_bp.route("/recording-ready", methods=["POST"])
def recording_ready():
    call_sid      = request.form.get("CallSid")
    recording_url = request.form.get("RecordingUrl")
    recording_sid = request.form.get("RecordingSid")

    caller   = _active_calls.pop(call_sid, "unknown")
    subtype  = _active_calls.pop(f"{call_sid}_type", "voice")

    if not recording_url:
        return ("", 204)

    audio = requests.get(
        recording_url + ".wav",
        auth    = (current_app.config["TWILIO_SID"], current_app.config["TWILIO_TOKEN"]),
        timeout = 30,
    )

    if audio.status_code == 200:
        storage.save_incoming(audio.content, caller, recording_sid, subtype=subtype)

    return ("", 204)