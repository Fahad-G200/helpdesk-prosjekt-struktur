from __future__ import annotations

from flask import (
    Blueprint, render_template, request, redirect, url_for, session,
    flash, jsonify, abort, send_from_directory
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

import logging
import os
import re
import uuid
from datetime import datetime
from typing import Dict, Tuple, Optional
from .email_service import send_email
from .sms_service import send_sms
from .db import create_reset_code, verify_reset_code, consume_reset_code, set_password_hash

from .config import Config
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
    # Attachments
    add_attachment, get_attachments, get_attachment,
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


# -----------------------------
# Upload helpers
# -----------------------------
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def save_upload(file_storage, ticket_id: int) -> tuple[str, str]:
    """
    Lagrer fil på disk med unikt navn.
    Returnerer (stored_filename, original_filename)
    """
    original_filename = secure_filename(file_storage.filename or "")
    if not original_filename:
        raise ValueError("Tomt filnavn")

    if not allowed_file(original_filename):
        raise ValueError("Ugyldig filtype")

    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

    ext = original_filename.rsplit(".", 1)[1].lower()
    stored_filename = f"ticket_{ticket_id}_{uuid.uuid4().hex}.{ext}"
    path = os.path.join(Config.UPLOAD_FOLDER, stored_filename)

    file_storage.save(path)
    return stored_filename, original_filename


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
        email = request.form.get("email", "").strip() or None

        try:
            update_preferences(
                user,
                notify_email,
                notify_inapp,
                notify_sms,
                phone
            )
            # Update email separately if provided
            if email:
                try:
                    from .db import _conn
                    conn = _conn()
                    cur = conn.cursor()
                    cur.execute("UPDATE users SET email = ? WHERE username = ?", (email, user))
                    conn.commit()
                    conn.close()
                except Exception as e:
                    logger.error(f"Email update error: {e}")
            
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


# Chatbot page (dedicated chat interface)
@bp.route("/chatbot")
def chatbot_page():
    if not current_user():
        return redirect(url_for("main.login"))
    
    return render_template("chatbot.html")


# -----------------------------
# Tickets
# -----------------------------
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
                logger.info(f"Ticket created: #{ticket_id} by {user} (owner field should be: {user})")
                try:
                    log_activity(user, f"Opprettet sak #{ticket_id} – '{title}'")
                except Exception:
                    pass

                # --- NYTT: håndter vedlegg ---
                try:
                    files = request.files.getlist("files")
                except Exception:
                    files = []

                for f in files:
                    if not f or not getattr(f, "filename", ""):
                        continue
                    try:
                        stored_name, original_name = save_upload(f, ticket_id)
                        add_attachment(ticket_id, stored_name, original_name, user)
                    except Exception as e:
                        logger.error(f"File upload error (ticket #{ticket_id}): {e}")
                        flash(f"Kunne ikke laste opp fil '{getattr(f, 'filename', '')}'.", "danger")

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
        if role == "support":
            visible = get_tickets()
            logger.info(f"Support user {user} fetched all tickets: {len(visible)} total")
        else:
            visible = get_tickets(owner=user)
            logger.info(f"User {user} fetched their own tickets: {len(visible)} visible")
    except Exception as e:
        logger.error(f"Error fetching tickets for {user} (role={role}): {e}")
        visible = []
        flash("Kunne ikke hente saker. Prøv igjen senere.")

    # --- NYTT: legg ved vedlegg på hver ticket for visning i template ---
    for t in visible:
        try:
            t["attachments"] = get_attachments(t["id"])
        except Exception:
            t["attachments"] = []
    
    # DEBUG: log owner field på første sak hvis det finnes
    if visible and len(visible) > 0:
        first_ticket = visible[0]
        logger.debug(f"First ticket keys: {list(first_ticket.keys())} | owner={first_ticket.get('owner', 'MISSING')}")

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


# -----------------------------
# Attachments download
# -----------------------------
@bp.route("/attachments/<int:attachment_id>/download")
def download_attachment(attachment_id: int):
    user = current_user()
    role = current_role()
    if not user:
        return redirect(url_for("main.login"))

    att = get_attachment(attachment_id)
    if not att:
        abort(404)

    t = get_ticket(att["ticket_id"])
    if not t:
        abort(404)

    # tilgangskontroll: eier eller support
    if role != "support" and t["owner"] != user:
        abort(403)

    return send_from_directory(
        Config.UPLOAD_FOLDER,
        att["stored_filename"],
        as_attachment=True,
        download_name=att["original_filename"],
    )


# Vis vedlegg inline (for bilder)
@bp.route("/attachments/<int:attachment_id>/view")
def view_attachment(attachment_id: int):
    user = current_user()
    role = current_role()
    if not user:
        return redirect(url_for("main.login"))

    att = get_attachment(attachment_id)
    if not att:
        abort(404)

    t = get_ticket(att["ticket_id"])
    if not t:
        abort(404)

    # tilgangskontroll: eier eller support
    if role != "support" and t["owner"] != user:
        abort(403)

    # Bestem mimetype basert på filendelse
    filename = att["original_filename"].lower()
    if filename.endswith(('.jpg', '.jpeg')):
        mimetype = 'image/jpeg'
    elif filename.endswith('.png'):
        mimetype = 'image/png'
    elif filename.endswith('.gif'):
        mimetype = 'image/gif'
    elif filename.endswith('.webp'):
        mimetype = 'image/webp'
    else:
        # Ikke et bilde - redirect til download
        return redirect(url_for("main.download_attachment", attachment_id=attachment_id))

    return send_from_directory(
        Config.UPLOAD_FOLDER,
        att["stored_filename"],
        mimetype=mimetype,
        as_attachment=False,
    )


# -----------------------------
# (Beholder din gamle upload-route urørt)
# -----------------------------
@bp.route("/tickets/<int:ticket_id>/upload", methods=["POST"])
def upload_attachment(ticket_id: int):
    user = current_user()
    if not user:
        return redirect(url_for("main.login"))

    # Sjekk at brukeren har tilgang til saken
    t = get_ticket(ticket_id)
    if not t:
        abort(404)
    if current_role() != "support" and t["owner"] != user:
        abort(403)

    if "file" not in request.files:
        flash("Ingen fil valgt")
        return redirect(url_for("main.tickets"))

    file = request.files["file"]

    if file.filename == "":
        flash("Ingen fil valgt")
        return redirect(url_for("main.tickets"))

    if not allowed_file(file.filename):
        flash("Ugyldig filtype")
        return redirect(url_for("main.tickets"))

    try:
        stored_name, original_name = save_upload(file, ticket_id)
        add_attachment(ticket_id, stored_name, original_name, user)
        log_activity(user, f"Lastet opp vedlegg til sak #{ticket_id}")
        flash("Vedlegg lastet opp")
    except Exception as e:
        logger.error(f"Upload error for ticket #{ticket_id}: {e}")
        flash("Kunne ikke laste opp vedlegg. Prøv igjen.")

    return redirect(url_for("main.tickets"))


@bp.route("/dashboard")
def dashboard():
    if not current_user():
        return redirect(url_for("main.login"))

    # Hent saker fra DB (for support: alle, for user: egne)
    role = current_role()
    user = current_user()
    visible = get_tickets() if role == "support" else get_tickets(owner=user)

    # Enkle “stats” (demo). Kan forbedres senere.
    total_active = sum(1 for t in visible if (t.get("status") or "").lower() != "lukket")
    critical = sum(1 for t in visible if (t.get("priority") or "").lower() in ["kritisk", "critical", "høy", "high"])
    closed_today = 0
    avg_time = "2.4t"

    stats = {
        "total_active": total_active,
        "critical": critical,
        "closed_today": closed_today,
        "avg_time": avg_time,
    }

    return render_template("dashboard.html", tickets=visible, stats=stats)



# ============================================================================
# LEGG TIL DISSE RUTENE I routes.py (etter dashboard-ruten)
# ============================================================================

# -----------------------------
# ADMIN: User Management
# -----------------------------
@bp.route("/admin/users")
def admin_users():
    user = current_user()
    if not user or current_role() != "support":
        abort(403)

    from .db import get_all_users
    try:
        users = get_all_users()
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        users = []

    return render_template("admin_users.html", users=users)


@bp.route("/admin/users/<username>/promote", methods=["POST"])
def promote_user(username: str):
    user = current_user()
    if not user or current_role() != "support":
        abort(403)

    if username == "admin":
        flash("Kan ikke endre admin-bruker.")
        return redirect(url_for("main.admin_users"))

    from .db import change_user_role
    try:
        change_user_role(username, "support")
        log_activity(user, f"Promoterte {username} til support")
        flash(f"{username} er nå support.")
    except Exception as e:
        logger.error(f"Error promoting user: {e}")
        flash("Kunne ikke endre rolle.")

    return redirect(url_for("main.admin_users"))


@bp.route("/admin/users/<username>/demote", methods=["POST"])
def demote_user(username: str):
    user = current_user()
    if not user or current_role() != "support":
        abort(403)

    if username == "admin":
        flash("Kan ikke endre admin-bruker.")
        return redirect(url_for("main.admin_users"))

    from .db import change_user_role
    try:
        change_user_role(username, "user")
        log_activity(user, f"Degraderte {username} til user")
        flash(f"{username} er nå vanlig bruker.")
    except Exception as e:
        logger.error(f"Error demoting user: {e}")
        flash("Kunne ikke endre rolle.")

    return redirect(url_for("main.admin_users"))


@bp.route("/admin/users/<username>/reset-password", methods=["POST"])
def admin_reset_password(username: str):
    user = current_user()
    if not user or current_role() != "support":
        abort(403)

    # Admin kan ikke resette sitt eget passord
    if username == user:
        flash("Du kan ikke resette ditt eget passord.")
        return redirect(url_for("main.admin_users"))

    # Generer tilfeldig passord (12-16 tegn, bokstaver + tall)
    import secrets
    import string
    
    alphabet = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
    new_password = ''.join(secrets.choice(alphabet) for _ in range(14))
    
    # Hash og lagre
    from werkzeug.security import generate_password_hash
    from .db import _conn
    
    try:
        new_hash = generate_password_hash(new_password, method="pbkdf2:sha256")
        conn = _conn()
        cur = conn.cursor()
        cur.execute("UPDATE users SET pw_hash = ? WHERE username = ?", (new_hash, username))
        conn.commit()
        conn.close()
        
        log_activity(user, f"Resatte passord for bruker {username}")
        
        # Flash passordet KUN denne gangen (ikke i log, ikke i response)
        flash(f"Nytt passord for {username} er: {new_password} – Gi dette direkte til brukeren.", category="success")
    except Exception as e:
        logger.error(f"Error resetting password for {username}: {e}")
        flash("Kunne ikke resette passord.")

    return redirect(url_for("main.admin_users"))


@bp.route("/admin/users/<username>/delete", methods=["POST"])
def delete_user(username: str):
    user = current_user()
    if not user or current_role() != "support":
        abort(403)

    if username == "admin" or username == user:
        flash("Kan ikke slette denne brukeren.")
        return redirect(url_for("main.admin_users"))

    from .db import delete_user_db
    try:
        delete_user_db(username)
        log_activity(user, f"Slettet bruker {username}")
        flash(f"Bruker {username} slettet.")
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        flash("Kunne ikke slette bruker.")

    return redirect(url_for("main.admin_users"))

# -------------------------
# ADMIN-VERKTØY (placeholder-ruter)
# -------------------------
# Disse finnes for at admin-menyen ikke skal gi 500 (BuildError) når base.html
# bruker url_for(...) til admin-sider som ikke er implementert ennå.
# Ingen UI-endringer – vi bare sørger for at lenkene fungerer.


@bp.route("/admin/system")
def admin_system():
    user = current_user()
    if not user:
        return redirect(url_for("main.login"))
    if current_role() != "support":
        abort(403)

    return redirect(url_for("main.admin_settings"))


# Alias-navn (i tilfelle base.html bruker andre url_for-navn/URL-er)
@bp.route("/admin/system-settings")
def admin_system_settings():
    return admin_system()


@bp.route("/admin/kb-admin")
def kb_admin():
    return admin_kb()


@bp.route("/admin/users-admin")
def users_admin():
    return admin_users()


@bp.route("/admin/saker")
def admin_saker():
    return admin_tickets()


@bp.route("/admin/systeminnstillinger")
def systeminnstillinger():
    return admin_system()
# -----------------------------
# ADMIN: Ticket Management
# -----------------------------
@bp.route("/admin/tickets")
def admin_tickets():
    user = current_user()
    if not user or current_role() != "support":
        abort(403)

    try:
        all_tickets = get_tickets()
    except Exception as e:
        logger.error(f"Error fetching tickets: {e}")
        all_tickets = []

    return render_template("admin_tickets.html", tickets=all_tickets)


@bp.route("/tickets/<int:ticket_id>/assign", methods=["POST"])
def assign_ticket_to_support(ticket_id: int):
    user = current_user()
    if not user or current_role() != "support":
        abort(403)

    assigned_to = request.form.get("assigned_to", user).strip()

    from .db import assign_ticket
    try:
        assign_ticket(ticket_id, assigned_to)
        log_activity(user, f"Tildelte sak #{ticket_id} til {assigned_to}")

        t = get_ticket(ticket_id)
        if t:
            add_notification(
                t["owner"],
                f"Sak #{ticket_id} er tildelt {assigned_to}",
                url_for("main.tickets")
            )

        flash(f"Sak #{ticket_id} tildelt {assigned_to}.")
    except Exception as e:
        logger.error(f"Error assigning ticket: {e}")
        flash("Kunne ikke tildele sak.")

    return redirect(url_for("main.admin_tickets"))


@bp.route("/tickets/<int:ticket_id>/priority", methods=["POST"])
def change_ticket_priority(ticket_id: int):
    user = current_user()
    if not user or current_role() != "support":
        abort(403)

    new_priority = request.form.get("priority", "Middels")

    from .db import update_ticket_priority
    try:
        update_ticket_priority(ticket_id, new_priority)
        log_activity(user, f"Endret prioritet på sak #{ticket_id} til {new_priority}")
        flash(f"Prioritet endret til {new_priority}.")
    except Exception as e:
        logger.error(f"Error changing priority: {e}")
        flash("Kunne ikke endre prioritet.")

    return redirect(url_for("main.admin_tickets"))


@bp.route("/tickets/<int:ticket_id>/delete", methods=["POST"])
def delete_ticket_permanently(ticket_id: int):
    user = current_user()
    if not user or current_role() != "support":
        abort(403)

    from .db import delete_ticket_db
    try:
        delete_ticket_db(ticket_id)
        log_activity(user, f"Slettet sak #{ticket_id} permanent")
        flash(f"Sak #{ticket_id} slettet permanent.")
    except Exception as e:
        logger.error(f"Error deleting ticket: {e}")
        flash("Kunne ikke slette sak.")

    return redirect(url_for("main.admin_tickets"))


@bp.route("/tickets/<int:ticket_id>")
def ticket_detail(ticket_id: int):
    user = current_user()
    if not user:
        return redirect(url_for("main.login"))

    t = get_ticket(ticket_id)
    if not t:
        abort(404)

    role = current_role()
    if role != "support" and t["owner"] != user:
        abort(403)

    attachments = get_attachments(ticket_id)

    return render_template(
        "ticket_detail.html",
        ticket=t,
        attachments=attachments
    )

# -----------------------------
# ADMIN: Knowledge Base Management
# -----------------------------
@bp.route("/admin/kb")
def admin_kb():
    user = current_user()
    if not user or current_role() != "support":
        abort(403)

    try:
        articles = get_articles()
    except Exception:
        articles = []

    return render_template("admin_kb.html", articles=articles)


@bp.route("/admin/kb/new", methods=["GET", "POST"])
def create_article_view():
    user = current_user()
    if not user or current_role() != "support":
        abort(403)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = (request.form.get("content") or request.form.get("body") or "").strip()
        cover_url = request.form.get("cover_url", "").strip()

        if not title or not content:
            flash("Tittel og innhold er påkrevd.")
        else:
            try:
                article_id = create_article(title, content, user, cover_url or None)
                log_activity(user, f"Opprettet KB-artikkel #{article_id}: {title}")
                flash("Artikkel opprettet.")
                return redirect(url_for("main.view_article", article_id=article_id))
            except Exception as e:
                logger.error(f"Error creating article: {e}")
                flash("Kunne ikke opprette artikkel.")

    return render_template("create_article.html")


@bp.route("/kb/<int:article_id>")
def view_article(article_id: int):
    if not current_user():
        return redirect(url_for("main.login"))

    try:
        article = get_article(article_id)
        if not article:
            flash("Artikkelen finnes ikke.")
            return redirect(url_for("main.kb"))
    except Exception as e:
        logger.error(f"Error viewing article: {e}")
        flash("Kunne ikke hente artikkel.")
        return redirect(url_for("main.kb"))

    return render_template("view_article.html", article=article, role=current_role())


@bp.route("/kb/<int:article_id>/edit", methods=["GET", "POST"])
def edit_article_view(article_id: int):
    user = current_user()
    if not user or current_role() != "support":
        abort(403)

    try:
        article = get_article(article_id)
        if not article:
            flash("Artikkelen finnes ikke.")
            return redirect(url_for("main.admin_kb"))
    except Exception as e:
        logger.error(f"Error fetching article: {e}")
        flash("Kunne ikke hente artikkel.")
        return redirect(url_for("main.admin_kb"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        cover_url = request.form.get("cover_url", "").strip()

        if not title or not content:
            flash("Tittel og innhold er påkrevd.")
        else:
            try:
                update_article(article_id, title, content, cover_url or None)
                log_activity(user, f"Redigerte KB-artikkel #{article_id}")
                flash("Artikkel oppdatert.")
                return redirect(url_for("main.view_article", article_id=article_id))
            except Exception as e:
                logger.error(f"Error updating article: {e}")
                flash("Kunne ikke oppdatere artikkel.")

    return render_template("edit_article.html", article=article)


@bp.route("/kb/<int:article_id>/delete", methods=["POST"])
def delete_article(article_id: int):
    user = current_user()
    if not user or current_role() != "support":
        abort(403)

    try:
        delete_article_db(article_id)
        log_activity(user, f"Slettet KB-artikkel #{article_id}")
        flash("Artikkel slettet.")
    except Exception as e:
        logger.error(f"Error deleting article: {e}")
        flash("Kunne ikke slette artikkel.")

    return redirect(url_for("main.admin_kb"))


# -----------------------------
# ADMIN: System Settings
# -----------------------------
@bp.route("/admin/settings", methods=["GET", "POST"])
def admin_settings():
    user = current_user()
    if not user or current_role() != "support":
        abort(403)

    from .db import get_system_settings, set_system_settings

    if request.method == "POST":
        system_name = (request.form.get("system_name") or "").strip() or "IT Helpdesk"
        support_email = (request.form.get("support_email") or "").strip() or "support@helpdesk.no"
        max_file_size = (request.form.get("max_file_size") or "").strip() or "16"

        try:
            set_system_settings(system_name, support_email, max_file_size)
            flash("Innstillinger lagret.")
            try:
                log_activity(user, "Endret systeminnstillinger")
            except Exception:
                pass
            return redirect(url_for("main.admin_settings"))
        except Exception as e:
            logger.error(f"Error saving system settings: {e}")
            flash("Kunne ikke lagre innstillinger.")

    try:
        settings = get_system_settings()
    except Exception as e:
        logger.error(f"Error loading system settings: {e}")
        settings = {
            "system_name": "IT Helpdesk",
            "support_email": "support@helpdesk.no",
            "max_file_size": "16",
        }
    
    return render_template("admin_settings.html", settings=settings) 


# -----------------------------
# ADMIN: Bulk Actions
# -----------------------------
@bp.route("/admin/tickets/bulk-close", methods=["POST"])
def bulk_close_tickets():
    user = current_user()
    if not user or current_role() != "support":
        abort(403)

    ticket_ids = request.form.getlist("ticket_ids[]")

    closed_count = 0
    for tid in ticket_ids:
        try:
            close_ticket(int(tid))
            closed_count += 1
        except Exception:
            pass

    log_activity(user, f"Lukket {closed_count} saker samtidig (bulk)")
    flash(f"{closed_count} saker lukket.")

    return redirect(url_for("main.admin_tickets"))


@bp.route("/admin/tickets/bulk-delete", methods=["POST"])
def bulk_delete_tickets():
    user = current_user()
    if not user or current_role() != "support":
        abort(403)

    ticket_ids = request.form.getlist("ticket_ids[]")

    from .db import delete_ticket_db
    deleted_count = 0
    for tid in ticket_ids:
        try:
            delete_ticket_db(int(tid))
            deleted_count += 1
        except Exception:
            pass

    log_activity(user, f"Slettet {deleted_count} saker permanent (bulk)")
    flash(f"{deleted_count} saker slettet.")

    return redirect(url_for("main.admin_tickets"))


# -----------------------------
# Alias-ruter (norske sidebar-lenker)
# -----------------------------
@bp.route("/admin/systeminnstillinger")
def admin_systeminnstillinger_alias():
    return redirect(url_for("main.admin_settings"))


@bp.route("/admin/saker")
def admin_saker_alias():
    return redirect(url_for("main.admin_tickets"))


@bp.route("/admin/kb-admin")
def admin_kb_alias():
    return redirect(url_for("main.admin_kb"))


@bp.route("/admin/users-admin")
def admin_users_alias():
    return redirect(url_for("main.admin_users"))


# -----------------------------
# Chat (NY: AI-bot)
# -----------------------------

import json
from typing import List

class IntelligentHelpdeskAI:
    """
    Advanced AI chatbot that understands natural language,
    learns from context, and thinks like a real support agent.
    """

    def __init__(self):
        self.knowledge_base = self._init_knowledge_base()
        self.conversation_patterns = self._init_conversation_patterns()
        self.intent_classifiers = self._init_intent_classifiers()

    def _init_knowledge_base(self) -> Dict:
        """Comprehensive knowledge with real-world understanding"""
        return {
            "feide": {
                "description": "Feide authentication and login system",
                "keywords": ["feide", "innlogging", "login", "autentisering", "bruker", "konto"],
                "natural_phrases": [
                    "kan ikke logge inn", "får ikke tilgang", "innlogging fungerer ikke",
                    "kommer ikke inn", "kan ikke få tilgang", "login problem",
                    "får ikke logget meg inn", "klarer ikke å komme inn"
                ],
                "error_patterns": [
                    (r"timeout|time out|tidsavbrudd", "Feide-tjenesten bruker for lang tid. Dette kan skyldes høy trafikk eller nettverksproblemer."),
                    (r"feil brukernavn|wrong username|ugyldig bruker", "Brukernavnet er ikke riktig. Sjekk at du bruker formatet: fornavn.etternavn@skole.no"),
                    (r"feil passord|wrong password|incorrect password", "Passordet er feil. Husk at passord er case-sensitive (store/små bokstaver betyr noe)."),
                    (r"session.*utløpt|session expired|økten.*utløpt", "Innloggingsøkten har utløpt. Dette skjer etter 30 minutter med inaktivitet."),
                    (r"ingen tilgang|no access|access denied", "Du mangler tilgang. Kontakt support for å sjekke brukerrettigheter."),
                    (r"organisasjon|institution|skole", "Feil organisasjon valgt. Velg riktig skole/institusjon fra nedtrekksmenyen."),
                ],
                "solutions": {
                    "basic": [
                        "Sjekk at brukernavn er riktig format: fornavn.etternavn@skole.no",
                        "Kontroller at passordet er riktig (Caps Lock av)",
                        "Velg riktig organisasjon/skole fra nedtrekksmenyen",
                        "Prøv i et inkognito-vindu (Ctrl+Shift+N)"
                    ],
                    "intermediate": [
                        "Tøm nettleserens cache og cookies (Ctrl+Shift+Del)",
                        "Prøv en annen nettleser (Chrome, Firefox, Edge)",
                        "Sjekk at system-klokken er riktig (viktig for Feide-autentisering)",
                        "Deaktiver VPN hvis du har det påslått"
                    ],
                    "advanced": [
                        "Test med mobil data i stedet for Wi-Fi (isolerer nettverksproblemer)",
                        "Sjekk status.feide.no for driftsmeldinger",
                        "Kontroller at nettleseren er oppdatert til siste versjon",
                        "Prøv å logge inn fra en annen enhet for å teste om problemet følger deg"
                    ]
                },
                "questions": [
                    "Får du en feilmelding? I så fall, hva står det?",
                    "Hvilken nettleser bruker du?",
                    "Skjer dette på flere enheter eller bare én?",
                    "Har du prøvd i et inkognito-vindu?"
                ]
            },
            "wifi": {
                "description": "Wireless network connectivity issues",
                "keywords": ["wifi", "wi-fi", "nett", "internett", "nettverk", "tilkobling", "trådløst"],
                "natural_phrases": [
                    "får ikke nett", "ingen internett", "nettverket fungerer ikke",
                    "kan ikke koble til", "wifi virker ikke", "internett er nede",
                    "kommer ikke på nett", "nettverket er tregt"
                ],
                "error_patterns": [
                    (r"ingen internett|no internet|not connected", "Du er koblet til Wi-Fi, men har ingen internett-tilgang. Dette kan være DNS-problem eller ISP-problem."),
                    (r"begrensa.*tilkobling|limited connectivity|begrenset", "Windows melder 'Begrenset tilkobling' som betyr at du er koblet til Wi-Fi, men ikke kan nå internett."),
                    (r"finner ikke|cannot find|not found", "Nettverket vises ikke i listen. Dette kan skyldes at du er for langt unna, eller at nettverket er skjult."),
                    (r"feil passord|wrong password|incorrect password", "Wi-Fi-passordet er feil. Dobbeltsjekk passordet, spesielt spesialtegn."),
                    (r"ip.*adresse|ip.*address|dhcp", "Kan ikke få IP-adresse fra nettverket. Dette er et DHCP-problem på ruteren."),
                ],
                "solutions": {
                    "basic": [
                        "Slå Wi-Fi av og på igjen på enheten",
                        "Start enheten på nytt",
                        "Flytt nærmere Wi-Fi-routeren",
                        "Sjekk at du kobler til riktig nettverk (ikke naboen sitt)"
                    ],
                    "intermediate": [
                        "Start routeren på nytt (trekk ut strømmen i 30 sekunder)",
                        "Glem nettverket og koble til på nytt",
                        "Test på en annen enhet - fungerer det der? (isolerer om det er enheten eller nettverket)",
                        "Sjekk at flymodus ikke er på"
                    ],
                    "advanced": [
                        "Sjekk IP-innstillinger - sørg for at DHCP er aktivert",
                        "Prøv å sette DNS manuelt til 8.8.8.8 og 8.8.4.4 (Google DNS)",
                        "Sjekk om MAC-filtrering er aktivert på routeren",
                        "Test med Ethernet-kabel hvis mulig (isolerer Wi-Fi-problemet)"
                    ]
                },
                "questions": [
                    "Ser du nettverket i listen over tilgjengelige nettverk?",
                    "Er du koblet til, men uten internett? Eller kan du ikke koble til i det hele tatt?",
                    "Fungerer det på andre enheter (mobil, PC)?",
                    "Er signalstyrken god (full stripe)?"
                ]
            },
            "utskrift": {
                "description": "Printer and printing problems",
                "keywords": ["utskrift", "skriver", "printer", "print", "skrive ut"],
                "natural_phrases": [
                    "kan ikke skrive ut", "skriveren fungerer ikke", "får ikke printet",
                    "printer ikke", "utskrift virker ikke", "skriveren svarer ikke"
                ],
                "error_patterns": [
                    (r"ikke funnet|not found|cannot find", "Skriveren finnes ikke i systemet. Driver mangler eller skriver er ikke på nettverket."),
                    (r"offline|ikke.*tilkoblet|disconnected", "Skriveren viser som offline. Sjekk tilkobling og strøm."),
                    (r"papir|paper.*jam|papirstopp", "Papirstopp i skriveren. Åpne skriveren og fjern papir forsiktig."),
                    (r"toner|blekk|ink|cartridge", "Toner/blekk er tom eller lav. Bytt patron."),
                    (r"kø|queue|venter", "Utskriftskøen er blokkert. Gamle dokumenter hindrer nye utskrifter."),
                    (r"driver|drivere", "Skriverdriver er korrupt eller utdatert."),
                ],
                "solutions": {
                    "basic": [
                        "Sjekk at skriveren er slått på og koblet til strøm",
                        "Kontroller at riktig skriver er valgt i utskriftsdialogen",
                        "Sjekk papir - er det papir i skuffen?",
                        "Start både skriver og PC på nytt"
                    ],
                    "intermediate": [
                        "Åpne utskriftskøen og slett gamle/ventende dokumenter",
                        "Sjekk at skriveren ikke viser feilmodus (blinkende lys/feilmelding)",
                        "Test å printe en testside direkte fra skriveren",
                        "Prøv å skrive ut fra et annet program (f.eks. Notisblokk)"
                    ],
                    "advanced": [
                        "Reinstaller skriverdriver fra produsentens nettside",
                        "For nettverksskriver: ping skriverens IP-adresse",
                        "Sjekk Windows Print Spooler-tjenesten (services.msc)",
                        "Opprett ny skriver med samme driver (fjern gammel først)"
                    ]
                },
                "questions": [
                    "Skjer det noe når du trykker print? Kommer dokumentet i køen?",
                    "Er det en lokal skriver (USB) eller nettverksskriver?",
                    "Viser skriveren noen feilmeldinger eller blinkende lys?",
                    "Har det fungert før, eller er dette første gang?"
                ]
            },
            "passord": {
                "description": "Password and account access issues",
                "keywords": ["passord", "password", "glemt", "reset", "låst", "konto"],
                "natural_phrases": [
                    "har glemt passordet", "kan ikke huske passordet", "passord fungerer ikke",
                    "kontoen er låst", "må bytte passord", "feil passord"
                ],
                "error_patterns": [
                    (r"låst|locked|blocked", "Kontoen din er låst etter flere feilede innloggingsforsøk. Den låses vanligvis opp automatisk etter 30 minutter."),
                    (r"utløpt|expired|gamle", "Passordet har utløpt. De fleste systemer krever passordbytte hver 90-180 dag."),
                    (r"kompleksitet|complexity|krav|requirements", "Det nye passordet oppfyller ikke sikkerhetskrav (lengde, tegn, etc)."),
                    (r"brukt før|used before|previously used", "Du kan ikke gjenbruke gamle passord."),
                    (r"ikke synk|not sync|forskjellig", "Passordet er ikke synkronisert mellom systemer ennå. Vent 5-10 minutter."),
                ],
                "solutions": {
                    "basic": [
                        "Sjekk at Caps Lock er AV (passord er case-sensitive)",
                        "Kontroller tastaturspråk (norsk vs engelsk layout)",
                        "Bruk 'Glemt passord'-lenken hvis tilgjengelig",
                        "Vent 5-10 minutter hvis du nettopp har byttet passord (synkronisering)"
                    ],
                    "intermediate": [
                        "Prøv å logge inn på en annen enhet (isolerer om problemet er lokalt)",
                        "Sjekk at du bruker riktig brukernavn-format",
                        "For låst konto: vent 30 minutter for automatisk opplåsing",
                        "Test passordet i Notisblokk først (for å se hva du faktisk skriver)"
                    ],
                    "advanced": [
                        "Husk passordkrav: Minimum 8-12 tegn, store og små bokstaver, tall, spesialtegn",
                        "Bruk en passordbehandler (LastPass, 1Password, Bitwarden)",
                        "For AD/domenekonto: prøv å låse og låse opp PC (Ctrl+Alt+Del)",
                        "Kontakt support hvis kontoen fortsatt er låst etter 30 min"
                    ]
                },
                "questions": [
                    "Er kontoen låst, eller er det bare feil passord?",
                    "Har du byttet passord nylig (siste 10 minutter)?",
                    "Virker passordet på andre systemer/tjenester?",
                    "Får du en spesifikk feilmelding?"
                ]
            },
            "m365": {
                "description": "Microsoft 365 applications and services",
                "keywords": ["teams", "outlook", "onedrive", "word", "excel", "powerpoint", "office", "m365", "365"],
                "natural_phrases": [
                    "teams fungerer ikke", "outlook krasjer", "kan ikke åpne word",
                    "onedrive synkroniserer ikke", "kan ikke sende epost", "teams-møte virker ikke"
                ],
                "error_patterns": [
                    (r"synk.*ikke|not sync|synkronisering", "OneDrive synkroniserer ikke filer. Dette kan skyldes nettverksproblemer eller konflikt."),
                    (r"kan ikke.*åpne|cannot open|won't open", "Kan ikke åpne Office-filer. Dette kan være lisens-, tilgangs- eller fil-problem."),
                    (r"teams.*krasj|teams.*crash|teams freeze", "Teams krasjer eller fryser. Ofte cache-relatert."),
                    (r"mikrofon|kamera|audio|video|lyd|bilde", "Lyd/video fungerer ikke i Teams. Dette er vanligvis en tillatelse- eller driver-issue."),
                    (r"lisens|license|activation", "Office er ikke aktivert eller lisens mangler."),
                    (r"epost|email|mail.*send|kan ikke sende", "Kan ikke sende/motta e-post i Outlook."),
                ],
                "solutions": {
                    "basic": [
                        "Logg helt ut og inn igjen i programmet/appen",
                        "Start programmet på nytt",
                        "Sjekk internettforbindelsen",
                        "Prøv web-versjonen (office.com) - fungerer det der?"
                    ],
                    "intermediate": [
                        "For Teams: Tøm cache (%appdata%\\Microsoft\\Teams\\Cache)",
                        "For OneDrive: Pause og fortsett synkronisering",
                        "For Outlook: Kjør i safe mode (outlook.exe /safe)",
                        "Sjekk at du har siste versjon (Fil > Konto > Oppdateringsalternativer)"
                    ],
                    "advanced": [
                        "Reparer Office-installasjonen (Kontrollpanel > Programmer)",
                        "Tilbakestill Teams: Avinstaller fullstendig og installer på nytt",
                        "Sjekk OneDrive-status: høyreklikk OneDrive-ikon > Innstillinger",
                        "For Teams lyd/video: Sjekk nettleser-tillatelser og Windows personvern"
                    ]
                },
                "questions": [
                    "Hvilket program har du problemer med (Teams/Outlook/Word/etc)?",
                    "Får du en feilmelding? Hva står det?",
                    "Fungerer det i web-versjonen (office.com)?",
                    "Er dette et nytt problem eller har det vært lenge?"
                ]
            },
            "nettleser": {
                "description": "Web browser issues and problems",
                "keywords": ["chrome", "edge", "safari", "firefox", "nettleser", "browser", "nettside", "webside"],
                "natural_phrases": [
                    "nettleseren krasjer", "siden laster ikke", "nettleser er treg",
                    "nettsider fungerer ikke", "browser virker ikke"
                ],
                "error_patterns": [
                    (r"laster ikke|won't load|not loading", "Nettsider laster ikke. Dette kan være cache, DNS, eller nettverksproblem."),
                    (r"treg|slow|langsom", "Nettleseren er veldig treg. Sannsynligvis for mange åpne faner eller utvidelser."),
                    (r"krasj|crash|frys|freeze", "Nettleseren krasjer. Dette kan være korrupt cache, dårlig utvidelse, eller minne-problem."),
                    (r"err_|dns|ssl|certificate|sertifikat", "Nettverksfeil i nettleseren (DNS, SSL, eller tilkoblingsproblem)."),
                    (r"cookies|cache", "Cache/cookie-problemer som hindrer riktig lasting."),
                ],
                "solutions": {
                    "basic": [
                        "Oppdater siden (Ctrl+R eller F5)",
                        "Hard refresh: Ctrl+Shift+R (tømmer cache for den siden)",
                        "Prøv inkognito-modus (Ctrl+Shift+N)",
                        "Test en annen nettside - er problemet generelt eller spesifikt?"
                    ],
                    "intermediate": [
                        "Tøm cache og cookies: Ctrl+Shift+Del > velg 'All tid'",
                        "Deaktiver alle utvidelser midlertidig (sjekk om én av dem er problemet)",
                        "Test i en annen nettleser - fungerer det der?",
                        "Oppdater nettleseren til siste versjon"
                    ],
                    "advanced": [
                        "Opprett ny nettleserprofil (for å teste om profilen er korrupt)",
                        "Tøm DNS-cache: åpne CMD og kjør 'ipconfig /flushdns'",
                        "Deaktiver hardware-akselerasjon (Innstillinger > System)",
                        "Reset nettleserinnstillinger til standard"
                    ]
                },
                "questions": [
                    "Hvilken nettleser bruker du?",
                    "Er det alle nettsider eller bare én bestemt?",
                    "Fungerer det i inkognito-modus?",
                    "Har du mange utvidelser installert?"
                ]
            }
        }

    def _init_conversation_patterns(self) -> Dict:
        """Patterns that indicate user intent and emotion"""
        return {
            "urgency": {
                "high": ["haster", "akutt", "kritisk", "nå", "umiddelbart", "snarest", "raskt",
                         "deadline", "eksamen", "presentasjon", "møte om", "fort", "emergency"],
                "frustrated": ["irritert", "frustrert", "lei", "gir opp", "funker aldri",
                               "dritt", "faen", "pokker", "ugh", "argh"],
                "confused": ["forstår ikke", "skjønner ikke", "confused", "forvirret",
                             "hva mener du", "hva betyr", "hvordan"]
            },
            "progress": {
                "tried": ["har prøvd", "prøvd", "forsøkt", "tested", "gjort"],
                "not_working": ["fungerer ikke", "virker ikke", "hjelper ikke", "samme feil",
                                "fortsatt problem", "fremdeles"],
                "worked": ["fungerte", "virket", "løst", "fikset", "fixed", "takk", "tusen takk"]
            },
            "questions": {
                "how": ["hvordan", "how", "how do i"],
                "why": ["hvorfor", "why", "how come"],
                "what": ["hva", "what", "what is"],
                "where": ["hvor", "where"]
            }
        }

    def _init_intent_classifiers(self) -> Dict:
        """AI intent classification rules"""
        return {
            "needs_immediate_help": lambda text: any(w in text for w in ["haster", "akutt", "nå", "raskt"]),
            "frustrated": lambda text: any(w in text for w in ["irritert", "lei", "gir opp", "funker aldri"]),
            "follow_up": lambda text: any(w in text for w in ["nei", "fortsatt", "samme", "virker ikke"]),
            "positive_feedback": lambda text: any(w in text for w in ["takk", "fungerte", "løst", "bra"]),
            "needs_clarification": lambda text: len(text.split()) < 4,
            "has_error_message": lambda text: '"' in text or "feilmelding" in text.lower()
        }

    def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze user's emotional state and urgency"""
        text_lower = text.lower()

        sentiment = {
            "urgency": "normal",
            "emotion": "neutral",
            "frustration_level": 0
        }

        if any(word in text_lower for word in self.conversation_patterns["urgency"]["high"]):
            sentiment["urgency"] = "high"

        frustrated_words = [w for w in self.conversation_patterns["urgency"]["frustrated"] if w in text_lower]
        if frustrated_words:
            sentiment["emotion"] = "frustrated"
            sentiment["frustration_level"] = len(frustrated_words)

        if any(word in text_lower for word in self.conversation_patterns["urgency"]["confused"]):
            sentiment["emotion"] = "confused"

        return sentiment

    def _extract_entities(self, text: str) -> Dict:
        """Extract key information from user message (NER-like)"""
        entities = {
            "os": None,
            "browser": None,
            "application": None,
            "device": None,
            "error_message": None,
            "actions_tried": []
        }

        text_lower = text.lower()

        os_map = {
            "windows": ["windows", "win10", "win11", "pc", "laptop"],
            "macos": ["mac", "macos", "macbook", "imac", "apple"],
            "ios": ["iphone", "ipad", "ios"],
            "android": ["android", "samsung", "pixel"],
            "linux": ["linux", "ubuntu"]
        }
        for os_name, keywords in os_map.items():
            if any(k in text_lower for k in keywords):
                entities["os"] = os_name
                break

        browser_map = {
            "Chrome": ["chrome", "google chrome"],
            "Edge": ["edge", "microsoft edge"],
            "Safari": ["safari"],
            "Firefox": ["firefox", "mozilla"]
        }
        for browser, keywords in browser_map.items():
            if any(k in text_lower for k in keywords):
                entities["browser"] = browser
                break

        app_map = {
            "Teams": ["teams", "microsoft teams"],
            "Outlook": ["outlook"],
            "Word": ["word", "word document"],
            "Excel": ["excel", "spreadsheet"],
            "PowerPoint": ["powerpoint", "ppt", "presentasjon"],
            "OneDrive": ["onedrive"]
        }
        for app, keywords in app_map.items():
            if any(k in text_lower for k in keywords):
                entities["application"] = app
                break

        error_patterns = [
            r'"([^"]+)"',
            r'feilmelding[:\s]+([^\n\.]+)',
            r'får[:\s]+([^\n\.]+)',
            r'sier[:\s]+([^\n\.]+)'
        ]
        for pattern in error_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                entities["error_message"] = match.group(1).strip()
                break

        action_keywords = ["prøvd", "forsøkt", "restartet", "startet på nytt", "tømt cache",
                          "logget ut", "reinstallert", "sjekket", "testet"]
        entities["actions_tried"] = [k for k in action_keywords if k in text_lower]

        return entities

    def _classify_topic(self, text: str, entities: Dict) -> Tuple[str, float]:
        text_lower = text.lower()
        scores = {}

        noise_words = ["jeg", "du", "det", "har", "er", "på", "med", "til", "og", "i"]
        words = [w for w in text_lower.split() if w not in noise_words and len(w) > 2]

        for topic, data in self.knowledge_base.items():
            score = 0

            for keyword in data["keywords"]:
                if keyword in text_lower:
                    score += 3

            for phrase in data["natural_phrases"]:
                if phrase in text_lower:
                    score += 5

            for keyword in data["keywords"]:
                if any(keyword in word or word in keyword for word in words):
                    score += 1

            if topic == "m365" and entities.get("application"):
                score += 4
            if topic == "nettleser" and entities.get("browser"):
                score += 4

            for error_pattern, _ in data.get("error_patterns", []):
                if re.search(error_pattern, text_lower):
                    score += 6

            if score > 0:
                scores[topic] = score

        if not scores:
            return "unknown", 0.0

        best_topic = max(scores.items(), key=lambda x: x[1])
        confidence = min(best_topic[1] / 10.0, 1.0)

        return best_topic[0], confidence

    def _find_matching_error(self, error_msg: str, topic: str) -> Optional[str]:
        if not error_msg or topic not in self.knowledge_base:
            return None

        topic_data = self.knowledge_base[topic]
        error_lower = error_msg.lower()

        for pattern, explanation in topic_data.get("error_patterns", []):
            if re.search(pattern, error_lower):
                return explanation

        return None

    def _generate_ai_response(
        self,
        topic: str,
        confidence: float,
        entities: Dict,
        sentiment: Dict,
        conversation_state: Dict
    ) -> str:
        response_parts = []

        if confidence < 0.3:
            return self._generate_clarification_request(entities, sentiment)

        topic_data = self.knowledge_base.get(topic, {})

        opening = self._generate_opening(topic, sentiment, entities)
        response_parts.append(opening)
        response_parts.append("")

        if entities.get("error_message"):
            error_explanation = self._find_matching_error(entities["error_message"], topic)
            if error_explanation:
                response_parts.append(" **Jeg forstår problemet:**")
                response_parts.append(f"Feilmeldingen '{entities['error_message']}' betyr: {error_explanation}")
                response_parts.append("")

        if entities.get("actions_tried"):
            response_parts.append(f" Jeg ser du allerede har prøvd: {', '.join(entities['actions_tried'])}")
            response_parts.append("La meg gi deg neste steg basert på det.")
            response_parts.append("")

        context_parts = []
        if entities.get("os"):
            context_parts.append(f" {entities['os']}")
        if entities.get("browser"):
            context_parts.append(f" {entities['browser']}")
        if entities.get("application"):
            context_parts.append(f" {entities['application']}")

        if context_parts:
            response_parts.append(f"**System:** {' | '.join(context_parts)}")
            response_parts.append("")

        message_count = conversation_state.get("message_count", 1)

        if message_count == 1 or not conversation_state.get("solutions_given"):
            response_parts.append("** Her er hva jeg anbefaler å prøve:**")
            response_parts.append("")
            for i, solution in enumerate(topic_data["solutions"]["basic"], 1):
                response_parts.append(f"{i}. {solution}")
            conversation_state["solutions_given"] = "basic"

        elif conversation_state.get("solutions_given") == "basic":
            response_parts.append("** La oss prøve mer avanserte løsninger:**")
            response_parts.append("")
            for i, solution in enumerate(topic_data["solutions"]["intermediate"], 1):
                response_parts.append(f"{i}. {solution}")
            conversation_state["solutions_given"] = "intermediate"

        else:
            response_parts.append("**⚙️ Dette er mer avanserte løsninger:**")
            response_parts.append("")
            for i, solution in enumerate(topic_data["solutions"]["advanced"], 1):
                response_parts.append(f"{i}. {solution}")
            conversation_state["solutions_given"] = "advanced"

        response_parts.append("")

        if message_count == 1:
            response_parts.append("**❓ For å hjelpe deg bedre:**")
            questions = topic_data.get("questions", [])[:2]
            for q in questions:
                response_parts.append(f"• {q}")
            response_parts.append("")

        if message_count >= 3:
            response_parts.append("** Hvis dette fortsatt ikke løser problemet:**")
            response_parts.append("Jeg anbefaler at du oppretter en support-sak så kan vårt team hjelpe deg direkte.")
            response_parts.append("De har tilgang til flere verktøy og kan feilsøke mer detaljert.")
        else:
            response_parts.append("** Fungerte det?**")
            response_parts.append("• Hvis ja: Fantastisk! Glad jeg kunne hjelpe! ")
            response_parts.append("• Hvis nei: Fortell meg hva som skjedde, så går vi videre.")

        return "\n".join(response_parts)

    def _generate_opening(self, topic: str, sentiment: Dict, entities: Dict) -> str:
        if sentiment["urgency"] == "high":
            urgency_openers = [
                "⚡ **Jeg ser dette haster!** La meg hjelpe deg raskt.",
                " **Forstår at dette er viktig.** La oss løse det nå.",
                "⏰ **OK, dette må fikses fort.** Jeg skal hjelpe deg umiddelbart."
            ]
            import random
            return random.choice(urgency_openers)

        if sentiment["emotion"] == "frustrated":
            if sentiment["frustration_level"] > 1:
                return " **Jeg forstår at dette er frustrerende.** La meg hjelpe deg å løse dette en gang for alle."
            return " **Jeg forstår at dette er irriterende.** La oss finne en løsning sammen."

        if sentiment["emotion"] == "confused":
            return " **Jeg skal forklare dette enkelt.** Ikke bekymre deg, vi tar det steg for steg."

        topic_openings = {
            "feide": " **Feide-innlogging kan være tricky!** Jeg hjelper deg å komme inn.",
            "wifi": " **Nettverksproblemer er kjedelige!** La meg hjelpe deg å få nettet til å virke.",
            "utskrift": "️ **Skriverproblemer er ofte enkle å fikse!** La meg guide deg.",
            "passord": " **Passordproblemer? Helt normalt!** Jeg hjelper deg tilbake på rett spor.",
            "m365": " **Microsoft 365 kan ha sine utfordringer.** La meg hjelpe deg.",
            "nettleser": " **Nettleserproblemer? Jeg har løsningen!**"
        }
        return topic_openings.get(topic, " **Hei! Jeg er her for å hjelpe deg.**")

    def _generate_clarification_request(self, entities: Dict, sentiment: Dict) -> str:
        parts = []

        if sentiment["emotion"] == "frustrated":
            parts.append(" **Jeg merker at dette er frustrerende for deg.**")
            parts.append("La meg hjelpe - jeg trenger bare litt mer info for å gi deg best mulig hjelp.")
            parts.append("")
        else:
            parts.append(" **Jeg vil gjerne hjelpe deg, men trenger litt mer informasjon.**")
            parts.append("")

        understood = []
        if entities.get("os"):
            understood.append(f" System: {entities['os']}")
        if entities.get("browser"):
            understood.append(f" Nettleser: {entities['browser']}")
        if entities.get("application"):
            understood.append(f" Program: {entities['application']}")

        if understood:
            parts.append("**Dette har jeg forstått:**")
            parts.extend(understood)
            parts.append("")

        parts.append("**Jeg kan hjelpe med:**")
        parts.append("•  **Feide/Innlogging** - 'Kan ikke logge inn på Feide'")
        parts.append("•  **Wi-Fi/Nettverk** - 'Får ikke internett på PC-en'")
        parts.append("• ️ **Utskrift** - 'Skriveren vil ikke printe'")
        parts.append("•  **Passord** - 'Har glemt passordet mitt'")
        parts.append("•  **Microsoft 365** - 'Teams krasjer hele tiden'")
        parts.append("•  **Nettleser** - 'Chrome laster ikke nettsider'")
        parts.append("")
        parts.append("** Tips for best hjelp:**")
        parts.append("• Beskriv problemet: 'Jeg kan ikke logge inn på Feide på PC-en min'")
        parts.append("• Inkluder feilmelding: 'Får feilmelding \"timeout\"'")
        parts.append("• Fortell hva du har prøvd: 'Har startet på nytt, men hjelper ikke'")
        parts.append("")
        parts.append("**Prøv å beskrive problemet ditt med noen flere ord, så hjelper jeg deg! **")

        return "\n".join(parts)

    def _should_escalate(self, conversation_state: Dict) -> bool:
        message_count = conversation_state.get("message_count", 0)
        solutions_level = conversation_state.get("solutions_given", "")
        return (
            message_count >= 4
            or solutions_level == "advanced"
            or conversation_state.get("user_requested_human", False)
        )

    def process_message(self, user_msg: str, conversation_state: Dict = None) -> Tuple[str, Dict]:
        if conversation_state is None:
            conversation_state = {
                "message_count": 0,
                "last_topic": None,
                "solutions_given": None,
                "context_entities": {},
                "user_requested_human": False
            }

        conversation_state["message_count"] += 1

        human_request_phrases = ["snakke med", "menneske", "ekte person", "support", "menneskelig"]
        if any(phrase in user_msg.lower() for phrase in human_request_phrases):
            conversation_state["user_requested_human"] = True
            return self._generate_human_escalation_message(), conversation_state

        positive_phrases = ["takk", "fungerte", "virket", "løst", "fikset", "bra", "perfekt"]
        if any(phrase in user_msg.lower() for phrase in positive_phrases) and conversation_state["message_count"] > 1:
            return self._generate_success_message(), conversation_state

        sentiment = self._analyze_sentiment(user_msg)
        entities = self._extract_entities(user_msg)

        previous_entities = conversation_state.get("context_entities", {})
        for key, value in entities.items():
            if value:
                previous_entities[key] = value
        conversation_state["context_entities"] = previous_entities

        topic, confidence = self._classify_topic(user_msg, previous_entities)

        follow_up_phrases = ["nei", "fungerer ikke", "virker ikke", "fortsatt", "samme problem", "hjelper ikke"]
        if (topic == "unknown" or confidence < 0.3) and conversation_state.get("last_topic"):
            if any(phrase in user_msg.lower() for phrase in follow_up_phrases):
                topic = conversation_state["last_topic"]
                confidence = 0.8

        if topic != "unknown":
            conversation_state["last_topic"] = topic

        if self._should_escalate(conversation_state):
            return self._generate_escalation_message(topic, previous_entities), conversation_state

        response = self._generate_ai_response(
            topic,
            confidence,
            previous_entities,
            sentiment,
            conversation_state
        )

        return response, conversation_state

    def _generate_success_message(self) -> str:
        import random
        messages = [
            " **Fantastisk!** Jeg er så glad jeg kunne hjelpe deg!\n\nHvis du får andre problemer, er jeg her. Ha en fin dag! ",
            " **Perfekt!** Det var akkurat det jeg håpet på!\n\nHusk at jeg alltid er her hvis du trenger hjelp igjen. Lykke til! ",
            " **Supert!** Kjempe bra at det virket!\n\nFøl deg fri til å spørre meg igjen hvis du trenger noe. God dag videre! "
        ]
        return random.choice(messages)

    def _generate_escalation_message(self, topic: str, entities: Dict) -> str:
        parts = []
        parts.append(" **Jeg tror det er best at vårt support-team tar over herfra.**")
        parts.append("")
        parts.append("De har tilgang til flere verktøy og kan:")
        parts.append("• Se direkte på systemet ditt")
        parts.append("• Sjekke logger og feilmeldinger")
        parts.append("• Gjøre mer avanserte endringer")
        parts.append("• Gi deg personlig oppfølging")
        parts.append("")
        parts.append("** Når du oppretter en support-sak, inkluder:**")

        if entities.get("error_message"):
            parts.append(f"• Feilmelding: '{entities['error_message']}'")
        if entities.get("os"):
            parts.append(f"• System: {entities['os']}")
        if entities.get("browser"):
            parts.append(f"• Nettleser: {entities['browser']}")
        if entities.get("application"):
            parts.append(f"• Program: {entities['application']}")
        if entities.get("actions_tried"):
            parts.append(f"• Hva du har prøvd: {', '.join(entities['actions_tried'])}")

        parts.append("")
        parts.append("Du kan opprette en sak ved å klikke på 'Saker' i menyen. ")
        parts.append("")
        parts.append("Vårt team svarer vanligvis innen 1-2 timer! ")
        return "\n".join(parts)

    def _generate_human_escalation_message(self) -> str:
        return (
            " **Selvfølgelig! La meg sette deg i kontakt med vårt support-team.**\n\n"
            "De er ekte mennesker som har mer erfaring og tilgang til flere verktøy enn meg.\n\n"
            "** Opprett en support-sak her:**\n"
            "Klikk på 'Saker' i menyen, og teamet vårt tar kontakt med deg så fort som mulig!\n\n"
            "Gjennomsnittlig responstid: 1-2 timer ⏰\n\n"
            "Jeg håper de kan hjelpe deg bedre enn jeg kunne! "
        )


# Global bot instance
_bot_instance = None


def get_bot() -> IntelligentHelpdeskAI:
    """Get or create AI bot instance"""
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = IntelligentHelpdeskAI()
    return _bot_instance


def sanitize_chat_reply(text: str) -> str:
    """Remove markdown formatting from chat reply"""
    # Remove bold: ** text ** → text
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    # Remove italic: _ text _ or * text * → text
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    # Remove backticks/code: `text` → text
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # Remove heading markers (###, ##, #) at start of line
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    return text


@bp.route("/chat", methods=["POST"])
def chat():
    """AI-powered chat endpoint"""
    if not current_user():
        return jsonify({"reply": "Du må være innlogget for å bruke chat."}), 401

    try:
        data = request.get_json(silent=True) or {}
        user_msg = (data.get("message") or "").strip()

        if not user_msg:
            return jsonify({"reply": "Skriv hva du trenger hjelp med, så hjelper jeg deg!"})

        if "ai_chat_state" not in session:
            session["ai_chat_state"] = {
                "message_count": 0,
                "last_topic": None,
                "solutions_given": None,
                "context_entities": {},
                "user_requested_human": False
            }

        conversation_state = session["ai_chat_state"]

        bot = get_bot()
        reply, updated_state = bot.process_message(user_msg, conversation_state)

        # Remove markdown from reply
        reply = sanitize_chat_reply(reply)

        session["ai_chat_state"] = updated_state
        session.modified = True

        try:
            log_activity(
                current_user(),
                f"Chat: {user_msg[:50]}... -> Topic: {updated_state.get('last_topic', 'unknown')}"
            )
        except Exception:
            pass

        return jsonify({
            "reply": reply,
            "topic": updated_state.get("last_topic"),
            "message_count": updated_state.get("message_count", 1),
            "confidence": "high" if updated_state.get("last_topic") != "unknown" else "low"
        })

    except Exception as e:
        logger.error(f"Chat AI error: {e}")
        return jsonify({
            "reply": "Oops! Noe gikk galt i mitt AI-hode. Prøv igjen, eller opprett en support-sak hvis problemet fortsetter."
        }), 500



@bp.route("/chat/reset", methods=["POST"])
def reset_chat():
    """Reset AI conversation state"""
    if not current_user():
        return jsonify({"status": "error"}), 401

    session.pop("ai_chat_state", None)
    session.pop("chat_history", None)
    session.modified = True

    try:
        log_activity(current_user(), "Reset chat-samtale")
    except Exception:
        pass

    return jsonify({
        "status": "ok",
        "message": "Samtalen er tilbakestilt. Jeg husker ikke vår tidligere dialog nå! "
    })

@bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        u = get_user(username) if username else None

        # Sikkerhet: ikke avslør om bruker finnes
        if not u:
            flash("Hvis brukeren finnes, vil IT-support hjelpe deg med nytt passord.")
            return redirect(url_for("main.login"))

        # Admin styrer nå passordreset - ingen automatisk SMS/e-post
        try:
            # Logg at bruker forsøkte å bruke glemt-passord siden
            log_activity(username, "Forsøkte å endre passord via glemt passord-siden")
        except:
            pass
        
        flash("Hvis brukeren finnes, vil IT-support hjelpe deg med nytt passord.")
        return redirect(url_for("main.login"))

    return render_template("forgot_password.html")


@bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        code = (request.form.get("code") or "").strip()
        password = request.form.get("password") or ""
        password2 = request.form.get("password2") or ""

        if not username or not code or not password or not password2:
            flash("Alle feltene må fylles ut.")
            return redirect(url_for("main.reset_password"))

        if len(password) < 8:
            flash("Passord må være minst 8 tegn.")
            return redirect(url_for("main.reset_password"))

        if password != password2:
            flash("Passordene er ikke like.")
            return redirect(url_for("main.reset_password"))

        try:
            if not verify_reset_code(username, code):
                flash("Ugyldig eller utløpt kode.")
                return redirect(url_for("main.reset_password"))

            new_hash = generate_password_hash(password, method="pbkdf2:sha256")
            set_password_hash(username, new_hash)
            consume_reset_code(username, code)

            flash("Passordet er oppdatert. Du kan logge inn nå.")
            return redirect(url_for("main.login"))
        
        except Exception as e:
            logger.error(f"Reset password error: {e}")
            flash("Noe gikk galt ved passordbytte. Prøv igjen eller kontakt support.")
            return redirect(url_for("main.reset_password"))

    return render_template("reset_password.html")