from __future__ import annotations

import os
import logging
from typing import Any, Dict, Optional, List

logger = logging.getLogger(__name__)

# Flask-Mail er valgfritt. Appen skal ikke krasje om det mangler.
try:
    from flask_mail import Mail, Message  # type: ignore
except Exception:  # pragma: no cover
    Mail = None  # type: ignore
    Message = None  # type: ignore

mail = Mail() if Mail is not None else None


def init_mail(app) -> None:
    """
    Initialiserer Flask-Mail hvis det er installert.
    Hvis flask_mail ikke finnes, gjør vi ingenting (app krasjer ikke).
    """
    global mail
    if Mail is None:
        logger.warning("flask_mail er ikke installert. E-post blir deaktivert.")
        return

    if mail is None:
        mail = Mail()  # type: ignore

    try:
        mail.init_app(app)  # type: ignore[union-attr]
    except Exception as e:
        logger.error(f"Kunne ikke initialisere Flask-Mail: {e}")


def _support_recipients(app=None) -> List[str]:
    """
    Henter liste over support-mottakere fra config eller env.
    Forventet format: "a@x.no,b@y.no"
    """
    raw = None
    if app is not None:
        try:
            raw = app.config.get("MAIL_SUPPORT_RECIPIENTS")
        except Exception:
            raw = None

    if not raw:
        raw = os.environ.get("MAIL_SUPPORT_RECIPIENTS")

    if not raw:
        return []

    return [r.strip() for r in str(raw).split(",") if r.strip()]


def _mail_configured(app=None) -> bool:
    """
    Best-effort sjekk på om MAIL_* er satt opp.
    """
    if app is not None:
        try:
            return bool(app.config.get("MAIL_SERVER") and app.config.get("MAIL_DEFAULT_SENDER"))
        except Exception:
            return False

    return bool(os.environ.get("MAIL_SERVER") and os.environ.get("MAIL_DEFAULT_SENDER"))


def _send_message(app, subject: str, recipients: List[str], body: str) -> bool:
    """
    Sender e-post. Returnerer True hvis sendt, ellers False.
    """
    if Mail is None or Message is None or mail is None:
        logger.warning("E-post kan ikke sendes (flask_mail mangler eller er ikke init).")
        return False

    if not recipients:
        return False

    try:
        with app.app_context():
            msg = Message(subject=subject, recipients=recipients, body=body)
            mail.send(msg)  # type: ignore[union-attr]
        return True
    except Exception as e:
        logger.error(f"Kunne ikke sende e-post: {e}")
        return False


def send_ticket_created_email(ticket: Dict[str, Any], user_email: Optional[str] = None, app=None) -> bool:
    """
    Sender bekreftelse til bruker hvis user_email finnes.
    Hvis ikke konfigurert -> gjør ingenting og returnerer False.
    """
    if not user_email:
        return False

    if app is None:
        try:
            from flask import current_app
            app = current_app
        except Exception:
            app = None

    if app is None or not _mail_configured(app):
        logger.warning("E-post er ikke konfigurert. Ticket-epost sendes ikke.")
        return False

    subject = f"Helpdesk: Sak #{ticket.get('id')} opprettet"
    body = (
        "Hei!\n\n"
        "Saken din er opprettet.\n\n"
        f"ID: {ticket.get('id')}\n"
        f"Tittel: {ticket.get('title')}\n"
        f"Kategori: {ticket.get('category')}\n"
        f"Prioritet: {ticket.get('priority')}\n\n"
        "Beskrivelse:\n"
        f"{ticket.get('description') or ticket.get('desc') or ''}\n\n"
        "Hilsen\nHelpdesk\n"
    )

    return _send_message(app, subject, [user_email], body)


def notify_support_new_ticket(ticket: Dict[str, Any], app=None) -> bool:
    """
    Sender e-post til support når ny sak opprettes.
    Krever MAIL_SUPPORT_RECIPIENTS (comma-separated) i config eller env.
    """
    if app is None:
        try:
            from flask import current_app
            app = current_app
        except Exception:
            app = None

    if app is None or not _mail_configured(app):
        logger.warning("E-post er ikke konfigurert. Support-varsling sendes ikke.")
        return False

    recipients = _support_recipients(app)
    if not recipients:
        logger.warning("MAIL_SUPPORT_RECIPIENTS mangler. Support-varsling sendes ikke.")
        return False

    subject = f"Helpdesk: Ny sak #{ticket.get('id')}"
    body = (
        "Ny sak opprettet.\n\n"
        f"ID: {ticket.get('id')}\n"
        f"Tittel: {ticket.get('title')}\n"
        f"Eier: {ticket.get('owner')}\n"
        f"Kategori: {ticket.get('category')}\n"
        f"Prioritet: {ticket.get('priority')}\n\n"
        "Beskrivelse:\n"
        f"{ticket.get('description') or ticket.get('desc') or ''}\n"
    )

    return _send_message(app, subject, recipients, body)

def send_email(subject: str, body: str, to_email: str, app=None) -> bool:
    """
    Backwards-compatible helper for older code paths.

    Some parts of the project import `send_email` directly.
    This function sends a plain-text email to a single recipient.

    Returns True if sent, otherwise False.
    """
    if not to_email:
        return False

    if app is None:
        try:
            from flask import current_app
            app = current_app
        except Exception:
            app = None

    if app is None or not _mail_configured(app):
        logger.warning("E-post er ikke konfigurert. send_email() sendes ikke.")
        return False

    return _send_message(app, subject, [to_email], body)