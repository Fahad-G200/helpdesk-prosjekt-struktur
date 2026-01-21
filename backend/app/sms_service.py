import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Twilio er VALGFRITT.
# Appen skal IKKE krasje hvis twilio ikke er installert.
try:
    from twilio.rest import Client
except Exception:  # pragma: no cover
    Client = None  # type: ignore


def _get_client() -> Optional["Client"]:
    """
    Returnerer Twilio Client hvis SMS kan brukes, ellers None.
    SMS kan brukes kun hvis:
    - twilio er installert
    - TWILIO_ACCOUNT_SID og TWILIO_AUTH_TOKEN er satt
    """
    if Client is None:
        logger.warning("Twilio er ikke installert (pip install twilio). SMS sendes ikke.")
        return None

    sid = os.environ.get("TWILIO_ACCOUNT_SID")
    token = os.environ.get("TWILIO_AUTH_TOKEN")
    if not sid or not token:
        logger.warning("Twilio env vars mangler (TWILIO_ACCOUNT_SID/TWILIO_AUTH_TOKEN). SMS sendes ikke.")
        return None

    return Client(sid, token)


def send_sms(to_phone: str, body: str) -> bool:
    """
    Sender SMS via Twilio.
    Returnerer True hvis sendt, False hvis ikke sendt/feilet.
    """
    if not to_phone:
        return False

    from_phone = os.environ.get("TWILIO_FROM_NUMBER")
    if not from_phone:
        logger.warning("TWILIO_FROM_NUMBER mangler. SMS sendes ikke.")
        return False

    client = _get_client()
    if not client:
        return False

    try:
        client.messages.create(
            from_=from_phone,
            to=to_phone,
            body=(body or "").strip(),
        )
        logger.info(f"SMS sendt til {to_phone}")
        return True
    except Exception as e:
        logger.error(f"Kunne ikke sende SMS til {to_phone}: {e}")
        return False