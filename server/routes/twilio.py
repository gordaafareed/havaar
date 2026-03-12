import requests
from flask import Blueprint, request, Response, current_app
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from server import storage, notify
from datetime import datetime

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

    elif digit == "9":
        response = VoiceResponse()
        gather   = response.gather(
            num_digits = 2,
            timeout    = 5,
            action     = base_url() + "twilio/panic-confirm",
            method     = "POST",
        )
        out = storage.recordings_out()
        if (out / "panic_prompt.wav").exists():
            gather.play(audio_url("panic_prompt.wav"))
        response.hangup()
        return twiml(response)

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

    if not recording_url:
        return ("", 204)

    audio = requests.get(
        recording_url + ".wav",
        auth    = (current_app.config["TWILIO_SID"], current_app.config["TWILIO_TOKEN"]),
        timeout = 30,
    )

    if audio.status_code == 200:
        filename   = storage.save_incoming(audio.content, caller, recording_sid)
        audio_path = str(storage.incoming_path(filename))
        notify.new_message(
            caller,
            datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            audio_path=audio_path,
        )

    return ("", 204)

@twilio_bp.route("/panic-confirm", methods=["POST"])
def panic_confirm():
    digits   = request.form.get("Digits", "")
    call_sid = request.form.get("CallSid")
    caller   = _active_calls.get(call_sid, request.form.get("From", "unknown"))
    response = VoiceResponse()

    if digits == "99":
        from datetime import datetime
        notify.panic(caller, datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"))
        storage.log_panic(caller)
        out = storage.recordings_out()
        if (out / "panic_confirmed.wav").exists():
            response.play(audio_url("panic_confirmed.wav"))

    response.hangup()
    return twiml(response)
