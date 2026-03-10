import os
import pathlib
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = pathlib.Path(__file__).parent.parent

class Config:
    SECRET_KEY         = os.environ.get("DASHBOARD_SECRET_KEY", os.urandom(24).hex())
    DASHBOARD_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "changeme")
    TWILIO_SID         = os.environ.get("TWILIO_ACCOUNT_SID")
    TWILIO_TOKEN       = os.environ.get("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE       = os.environ.get("TWILIO_PHONE_NUMBER")
    PORT               = int(os.environ.get("PORT", 5050))
    RECORDINGS_DIR     = pathlib.Path(os.environ.get("RECORDINGS_DIR", BASE_DIR / "recordings"))
    RECORDINGS_IN      = RECORDINGS_DIR / "incoming"
    RECORDINGS_OUT     = RECORDINGS_DIR / "outbound"
