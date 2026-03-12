import requests
from flask import current_app


def _token_chat():
    token   = current_app.config.get("TELEGRAM_TOKEN", "")
    chat_id = current_app.config.get("TELEGRAM_CHAT_ID", "")
    return token, chat_id


def _send(text: str) -> None:
    token, chat_id = _token_chat()
    if not token or not chat_id:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json    = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout = 5,
        )
    except Exception:
        pass


def new_message(caller: str, timestamp: str, audio_path: str = None) -> None:
    token, chat_id = _token_chat()
    if not token or not chat_id:
        return

    _send(f"📩 <b>new message</b>\ncaller: <code>{caller}</code>\n{timestamp}")

    if audio_path:
        try:
            with open(audio_path, "rb") as f:
                res = requests.post(
                    f"https://api.telegram.org/bot{token}/sendVoice",
                    data    = {"chat_id": chat_id},
                    files   = {"voice": f},
                    timeout = 30,
                )
        except Exception as e:
            print(f"  telegram audio error: {e}")


def panic(caller: str, timestamp: str) -> None:
    _send(f"🚨 <b>PANIC</b>\ncaller: <code>{caller}</code>\n{timestamp}")
