from __future__ import annotations

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
import logging
import re
from datetime import datetime
from typing import Dict, Tuple, Optional

from .db import (
    init_db,
    # Users
    user_exists, create_user, get_user, update_last_login, update_preferences, get_support_users,
    # Tickets
    add_ticket, get_tickets, get_ticket, close_ticket,
    # Notifications
    add_notification, get_notifications, mark_all_notifications_read, count_notifications,
    # Ratings
    add_rating, get_rating,
    # Activity
    log_activity, get_activity,
    # Knowledge base
    get_articles, get_article, create_article, update_article, delete_article_db,
)

# E-postvarsling
from .email_service import send_ticket_created_email, notify_support_new_ticket

bp = Blueprint("main", __name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def current_user():
    return session.get("user")


def current_role():
    return session.get("role")


@bp.before_app_request
def ensure_db():
    try:
        init_db()
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")


@bp.context_processor
def inject_notification_count():
    """
    Gjør at base.html kan vise notif_count uten at alle routes må sende det inn manuelt.
    """
    if current_user():
        try:
            return {"notif_count": count_notifications(current_user())}
        except Exception:
            return {"notif_count": 0}
    return {"notif_count": 0}


@bp.route("/")
def home():
    if not current_user():
        return redirect(url_for("main.login"))
    return redirect(url_for("main.kb"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        try:
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            if not username or not password:
                error = "Brukernavn og passord er påkrevd."
            else:
                u = get_user(username)
                if u and check_password_hash(u["pw_hash"], password):
                    session["user"] = u["username"]
                    session["role"] = u["role"]
                    session.permanent = True

                    try:
                        update_last_login(username)
                    except Exception:
                        pass

                    try:
                        log_activity(username, "Logget inn")
                    except Exception:
                        pass

                    logger.info(f"User logged in: {username}")
                    return redirect(url_for("main.kb"))

                error = "Feil brukernavn eller passord."
        except Exception as e:
            logger.error(f"Login error: {e}")
            error = "En feil oppstod. Prøv igjen senere."

    return render_template("login.html", error=error)


@bp.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        try:
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            password2 = request.form.get("password2", "")

            if len(username) < 3:
                error = "Brukernavn må være minst 3 tegn."
            elif len(password) < 8:
                error = "Passord må være minst 8 tegn."
            elif password != password2:
                error = "Passordene er ikke like."
            elif user_exists(username):
                error = "Brukernavnet er allerede i bruk."
            else:
                pw_hash = generate_password_hash(password, method="pbkdf2:sha256")
                create_user(username=username, pw_hash=pw_hash, role="user")
                try:
                    log_activity(username, "Opprettet ny brukerkonto")
                except Exception:
                    pass

                logger.info(f"New user registered: {username}")
                flash("Bruker opprettet. Du kan logge inn nå.")
                return redirect(url_for("main.login"))
        except Exception as e:
            logger.error(f"Registration error: {e}")
            error = "En feil oppstod ved registrering. Prøv igjen."

    return render_template("register.html", error=error)


@bp.route("/logout")
def logout():
    user = current_user()
    if user:
        try:
            log_activity(user, "Logget ut")
        except Exception:
            pass
        logger.info(f"User logged out: {user}")
    session.clear()
    return redirect(url_for("main.login"))


@bp.route("/kb")
def kb():
    if not current_user():
        return redirect(url_for("main.login"))

    try:
        articles = get_articles()
    except Exception:
        articles = []

    return render_template("kb.html", articles=articles, role=current_role())


@bp.route("/notifications")
def notifications_page():
    user = current_user()
    if not user:
        return redirect(url_for("main.login"))

    try:
        notifs = get_notifications(user)
        mark_all_notifications_read(user)
    except Exception as e:
        logger.error(f"Notifications error: {e}")
        notifs = []

    return render_template("notifications.html", notifications=notifs)


@bp.route("/settings", methods=["GET", "POST"])
def settings():
    user = current_user()
    if not user:
        return redirect(url_for("main.login"))

    u = get_user(user) or {}

    if request.method == "POST":
        notify_email = 1 if request.form.get("notify_email") else 0
        notify_inapp = 1 if request.form.get("notify_inapp") else 0
        notify_sms = 1 if request.form.get("notify_sms") else 0
        phone = request.form.get("phone", "").strip() or None

        try:
            update_preferences(
                user,
                notify_email,
                notify_inapp,
                notify_sms,
                phone
            )
            log_activity(user, "Endret varselinnstillinger")
            flash("Innstillinger oppdatert.")
        except Exception as e:
            logger.error(f"Settings update error: {e}")
            flash("Kunne ikke lagre innstillinger. Prøv igjen.")

        return redirect(url_for("main.settings"))

    return render_template("settings.html", preferences=u)


@bp.route("/admin/activity")
def activity_log():
    user = current_user()
    if not user:
        return redirect(url_for("main.login"))
    if current_role() != "support":
        abort(403)

    try:
        entries = get_activity(200)
    except Exception as e:
        logger.error(f"Activity log error: {e}")
        entries = []

    return render_template("logs.html", log_entries=entries)


@bp.route("/tickets", methods=["GET", "POST"])
def tickets():
    user = current_user()
    if not user:
        return redirect(url_for("main.login"))

    role = current_role()

    if request.method == "POST":
        try:
            title = request.form.get("title", "").strip()
            desc = request.form.get("desc", "").strip()
            category = request.form.get("category", "Annet").strip()
            priority = request.form.get("priority", "Middels").strip()
            device = request.form.get("device", "").strip()

            if not title or not desc:
                flash("Du må fylle ut tittel og beskrivelse.")
            else:
                ticket_id = add_ticket(
                    owner=user,
                    title=title,
                    desc=desc,
                    category=category,
                    priority=priority,
                    device=device
                )
                logger.info(f"Ticket created: #{ticket_id} by {user}")
                try:
                    log_activity(user, f"Opprettet sak #{ticket_id} – '{title}'")
                except Exception:
                    pass

                try:
                    for sup in get_support_users():
                        add_notification(
                            sup["username"],
                            f"Ny sak opprettet av {user}: {title}",
                            url_for("main.tickets")
                        )
                except Exception:
                    pass

                ticket = {
                    "id": ticket_id,
                    "title": title,
                    "owner": user,
                    "category": category,
                    "priority": priority,
                    "description": desc,
                }
                try:
                    send_ticket_created_email(ticket, user_email=None)
                    notify_support_new_ticket(ticket)
                except Exception:
                    pass

                flash("Saken er sendt til support. Du finner den i oversikten under.")

        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            flash("En feil oppstod ved opprettelse av sak. Prøv igjen.")

        return redirect(url_for("main.tickets"))

    try:
        visible = get_tickets() if role == "support" else get_tickets(owner=user)
    except Exception as e:
        logger.error(f"Error fetching tickets: {e}")
        visible = []
        flash("Kunne ikke hente saker. Prøv igjen senere.")

    return render_template("_tickets.html", tickets=visible, role=role)


@bp.route("/tickets/<int:ticket_id>/close", methods=["POST"])
def close_ticket_view(ticket_id: int):
    user = current_user()
    role = current_role()

    if not user:
        return redirect(url_for("main.login"))
    if role != "support":
        flash("Du har ikke tilgang til å lukke saker.")
        return redirect(url_for("main.tickets"))

    try:
        t = get_ticket(ticket_id)
        close_ticket(ticket_id)

        try:
            log_activity(user, f"Lukket sak #{ticket_id}")
        except Exception:
            pass

        if t:
            try:
                add_notification(
                    t["owner"],
                    f"Sak #{ticket_id} ble lukket av support ({user}).",
                    url_for("main.tickets")
                )
            except Exception:
                pass

        logger.info(f"Ticket #{ticket_id} closed by {user}")
        flash(f"Sak #{ticket_id} er lukket.")
    except Exception as e:
        logger.error(f"Error closing ticket {ticket_id}: {e}")
        flash("Kunne ikke lukke saken. Prøv igjen.")

    return redirect(url_for("main.tickets"))


@bp.route("/tickets/<int:ticket_id>/rate", methods=["POST"])
def rate_ticket(ticket_id: int):
    user = current_user()
    if not user:
        return redirect(url_for("main.login"))

    t = get_ticket(ticket_id)
    if not t or t["owner"] != user or t["status"] != "Lukket":
        abort(403)

    if t.get("rating") is not None or get_rating(ticket_id) is not None:
        flash("Denne saken er allerede vurdert.")
        return redirect(url_for("main.tickets"))

    try:
        stars = int(request.form.get("stars", "0"))
    except ValueError:
        stars = 0

    feedback = (request.form.get("feedback") or "").strip()

    if stars < 1 or stars > 5:
        flash("Ugyldig vurdering. Velg 1–5.")
        return redirect(url_for("main.tickets"))

    try:
        add_rating(ticket_id, user, stars, feedback)
        log_activity(user, f"Ga {stars}★ til sak #{ticket_id}")
    except Exception as e:
        logger.error(f"Rating error: {e}")
        flash("Kunne ikke lagre vurdering. Prøv igjen.")
        return redirect(url_for("main.tickets"))

    try:
        for sup in get_support_users():
            add_notification(
                sup["username"],
                f"Sak #{ticket_id} fikk {stars}★ fra {user}",
                url_for("main.tickets")
            )
    except Exception:
        pass

    flash("Takk for din tilbakemelding!")
    return redirect(url_for("main.tickets"))


class HelpdeskBot:
    def __init__(self):
        self.knowledge_base = self._init_knowledge_base()

    def _init_knowledge_base(self) -> Dict:
        return {
            "feide": {"keywords": ["feide", "innlogging", "login", "logge inn", "pålogging"]},
            "wifi": {"keywords": ["wifi", "wi-fi", "nett", "internett", "nettverk"]},
            "utskrift": {"keywords": ["utskrift", "skriver", "printer", "print"]},
            "passord": {"keywords": ["passord", "glemt", "låst", "reset"]},
        }

    def process_message(self, message: str) -> str:
        ml = message.lower()
        for topic, data in self.knowledge_base.items():
            if any(k in ml for k in data["keywords"]):
                return f"Jeg ser du spør om {topic}. Prøv: start på nytt, sjekk nett, og beskriv feilmelding."
        return "Beskriv problemet litt mer (Feide / Wi-Fi / utskrift / passord), så hjelper jeg deg."


_bot_instance = None

def get_bot() -> HelpdeskBot:
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = HelpdeskBot()
    return _bot_instance


@bp.route("/chat", methods=["POST"])
def chat():
    if not current_user():
        return jsonify({"reply": "Du må være innlogget for å bruke chat."}), 401

    try:
        data = request.get_json(silent=True) or {}
        user_msg = (data.get("message") or "").strip()

        if not user_msg:
            return jsonify({"reply": "Skriv hva du trenger hjelp med."})

        bot = get_bot()
        reply = bot.process_message(user_msg)

        return jsonify({"reply": reply})
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({"reply": "En feil oppstod. Prøv igjen senere."}), 500


@bp.route("/chat/reset", methods=["POST"])
def reset_chat():
    if not current_user():
        return jsonify({"status": "error"}), 401
    session.pop("chat_history", None)
    return jsonify({"status": "ok", "message": "Samtalen er tilbakestilt."})