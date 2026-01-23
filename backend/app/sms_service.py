import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from twilio.rest import Client  # type: ignore
except Exception:
    Client = None  # type: ignore


def _get_client() -> Optional["Client"]:
    if Client is None:
        logger.warning("Twilio er ikke installert (pip install twilio). SMS sendes ikke.")
        return None

    sid = os.environ.get("TWILIO_ACCOUNT_SID")
    token = os.environ.get("TWILIO_AUTH_TOKEN")
    if not sid or not token:
        logger.warning("Twilio env vars mangler. SMS sendes ikke.")
        return None

    return Client(sid, token)


def send_sms(to_phone: str, body: str) -> bool:
    """
    Sender SMS via Twilio.
    Krever:
      TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER
    """
    from_phone = os.environ.get("TWILIO_FROM_NUMBER")
    if not from_phone:
        logger.warning("TWILIO_FROM_NUMBER mangler. SMS sendes ikke.")
        return False

    client = _get_client()
    if not client:
        return False

    if not to_phone:
        return False

    try:
        client.messages.create(from_=from_phone, to=to_phone, body=body.strip())
        return True
    except Exception as e:
        logger.error(f"Kunne ikke sende SMS: {e}")
        return False