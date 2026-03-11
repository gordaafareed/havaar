import os
import hashlib
import pathlib
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = pathlib.Path(__file__).parent.parent

class Config:
    DASHBOARD_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "changeme")
    SECRET_KEY         = os.environ.get(
                             "DASHBOARD_SECRET_KEY",
                             hashlib.sha256(
                                 DASHBOARD_PASSWORD.encode()
                             ).hexdigest()
                         )
    TWILIO_SID         = os.environ.get("TWILIO_ACCOUNT_SID")
    TWILIO_TOKEN       = os.environ.get("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE       = os.environ.get("TWILIO_PHONE_NUMBER")
    PORT               = int(os.environ.get("PORT", 5050))
    RECORDINGS_DIR = pathlib.Path(
        os.environ.get("RECORDINGS_DIR", str(BASE_DIR / "recordings"))
    ).resolve()
    RECORDINGS_IN      = RECORDINGS_DIR / "incoming"
    RECORDINGS_OUT     = RECORDINGS_DIR / "outbound"
