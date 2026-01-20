from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import logging

from .db import (
    init_db,
    add_ticket, get_tickets, close_ticket,
    user_exists, create_user, get_user
)

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
        logger.info(f"User logged out: {user}")
    session.clear()
    return redirect(url_for("main.login"))

@bp.route("/kb")
def kb():
    if not current_user():
        return redirect(url_for("main.login"))
    return render_template("kb.html")

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
                ticket_id = add_ticket(owner=user, title=title, desc=desc,
                           category=category, priority=priority, device=device)
                logger.info(f"Ticket created: #{ticket_id} by {user}")
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
def close_ticket_view(ticket_id):
    user = current_user()
    role = current_role()

    if not user:
        return redirect(url_for("main.login"))
    
    if role != "support":
        flash("Du har ikke tilgang til å lukke saker.")
        return redirect(url_for("main.tickets"))

    try:
        close_ticket(ticket_id)
        logger.info(f"Ticket #{ticket_id} closed by {user}")
        flash(f"Sak #{ticket_id} er lukket.")
    except Exception as e:
        logger.error(f"Error closing ticket {ticket_id}: {e}")
        flash("Kunne ikke lukke saken. Prøv igjen.")
    
    return redirect(url_for("main.tickets"))


# -------------------------------------------------------------------
# Chatbot (lokal AI-opplevelse)
# -------------------------------------------------------------------

def _norm(s: str) -> str:
    return (s or "").strip().lower()

def _detect_topic(text: str) -> str:
    t = _norm(text)
    if any(k in t for k in ["feide", "innlogging", "login", "logge inn", "pålogging"]):
        return "feide"
    if any(k in t for k in ["wifi", "wi-fi", "nett", "internett", "nettverk", "tilkobling"]):
        return "wifi"
    if any(k in t for k in ["utskrift", "skriver", "printer", "print", "skrive ut"]):
        return "utskrift"
    if any(k in t for k in ["passord", "glemt", "låst", "reset", "tilbakestill"]):
        return "passord"
    if any(k in t for k in ["teams", "office", "word", "excel", "onedrive", "m365", "365"]):
        return "m365"
    if any(k in t for k in ["chrome", "edge", "safari", "firefox", "nettleser", "cache", "cookies"]):
        return "nettleser"
    return "ukjent"

def _extract_context(text: str) -> dict:
    t = _norm(text)
    ctx = {"os": None, "browser": None, "error": None}

    # OS
    if any(k in t for k in ["windows", "win10", "win11"]):
        ctx["os"] = "Windows"
    elif any(k in t for k in ["mac", "macos", "osx", "macbook"]):
        ctx["os"] = "macOS"
    elif any(k in t for k in ["iphone", "ios"]):
        ctx["os"] = "iOS"
    elif "android" in t:
        ctx["os"] = "Android"

    # Browser
    if "chrome" in t:
        ctx["browser"] = "Chrome"
    elif "edge" in t:
        ctx["browser"] = "Edge"
    elif "safari" in t:
        ctx["browser"] = "Safari"
    elif "firefox" in t:
        ctx["browser"] = "Firefox"

    # Feilmelding i anførselstegn
    if '"' in text:
        parts = text.split('"')
        if len(parts) >= 3:
            maybe = parts[1].strip()
            if 3 <= len(maybe) <= 180:
                ctx["error"] = maybe

    return ctx

def _topic_steps(topic: str) -> str:
    if topic == "feide":
        return (
            "Nivå 1 – Feide/innlogging:\n"
            "1. Sjekk brukernavn/passord (Caps Lock).\n"
            "2. Velg riktig skole/organisasjon i Feide.\n"
            "3. Prøv inkognito/privat vindu.\n"
            "4. Tøm cache/cookies og prøv igjen.\n\n"
            "Nivå 2 – hvis fortsatt feil:\n"
            "1. Noter tidspunkt og nøyaktig feilmelding.\n"
            "2. Test i en annen nettleser.\n\n"
            "Nivå 3:\n"
            "Opprett sak hvis det fortsatt ikke fungerer."
        )

    if topic == "wifi":
        return (
            "Nivå 1 – Wi-Fi/Nett:\n"
            "1. Slå Wi-Fi av og på.\n"
            "2. Koble til riktig nettverk.\n"
            "3. Start enheten på nytt.\n\n"
            "Nivå 2 – hvis fortsatt feil:\n"
            "1. Sjekk IP-adresse (ipconfig/ifconfig).\n"
            "2. Test ping mot gateway/ruter hvis du kan.\n\n"
            "Nivå 3:\n"
            "Opprett sak hvis problemet gjelder flere eller ikke lar seg løse."
        )

    if topic == "utskrift":
        return (
            "Nivå 1 – Utskrift:\n"
            "1. Velg riktig skriver.\n"
            "2. Sjekk papir/toner.\n"
            "3. Restart skriver og PC.\n\n"
            "Nivå 2 – hvis fortsatt feil:\n"
            "1. Sjekk utskriftskø og drivere.\n"
            "2. Test fra en annen enhet.\n\n"
            "Nivå 3:\n"
            "Opprett sak og legg ved feilkode/skjermbilde."
        )

    if topic == "passord":
        return (
            "Nivå 1 – Passord:\n"
            "1. Bruk 'Glemt passord' dersom tilgjengelig.\n"
            "2. Vent litt etter passordbytte (synk kan ta tid).\n"
            "3. Sjekk Caps Lock.\n\n"
            "Nivå 2 – hvis fortsatt feil:\n"
            "1. Prøv på en annen enhet eller nettleser.\n\n"
            "Nivå 3:\n"
            "Opprett sak hvis kontoen er låst eller du ikke får reset."
        )

    if topic == "m365":
        return (
            "Nivå 1 – Teams/Office/OneDrive:\n"
            "1. Logg ut og inn igjen.\n"
            "2. Sjekk nettforbindelsen.\n"
            "3. Prøv web-versjon i nettleser.\n\n"
            "Nivå 2 – hvis fortsatt feil:\n"
            "1. Tøm cache/cookies for tjenesten.\n"
            "2. Test på en annen enhet.\n\n"
            "Nivå 3:\n"
            "Opprett sak hvis flere har problemet eller konto/tilgang mistenkes."
        )

    if topic == "nettleser":
        return (
            "Nivå 1 – Nettleser:\n"
            "1. Oppdater siden (Ctrl/Cmd+R).\n"
            "2. Prøv inkognito/privat vindu.\n"
            "3. Tøm cache/cookies.\n"
            "4. Prøv en annen nettleser.\n\n"
            "Nivå 2 – hvis fortsatt feil:\n"
            "1. Deaktiver utvidelser midlertidig.\n\n"
            "Nivå 3:\n"
            "Opprett sak hvis feilen er konsekvent og du har feilmelding/skjermbilde."
        )

    return (
        "Jeg kan hjelpe, men trenger litt mer info.\n"
        "Skriv hva du har problemer med (Feide, Wi-Fi, utskrift, passord eller Teams/Office), "
        "og gjerne feilmelding i anførselstegn (\"...)."
    )

def local_helpdesk_bot(user_msg: str) -> str:
    topic = _detect_topic(user_msg)
    ctx = _extract_context(user_msg)

    # Husk sist tema for mer "samtale"
    last_topic = session.get("chat_topic")
    if topic == "ukjent" and last_topic:
        topic = last_topic
    session["chat_topic"] = topic

    # Still maks 1–2 oppfølgingsspørsmål hvis info mangler
    missing = []
    if topic in {"feide", "nettleser", "m365"} and not ctx.get("browser"):
        missing.append("Hvilken nettleser bruker du (Chrome/Edge/Safari/Firefox)?")
    if not ctx.get("os"):
        missing.append("Hvilken enhet/OS bruker du (Windows/macOS/iOS/Android)?")
    if topic in {"feide", "m365"} and not ctx.get("error"):
        missing.append("Har du en feilmelding? Hvis ja, skriv den i anførselstegn (\"...).")

    response = _topic_steps(topic)

    if missing:
        followup = "\n".join([f"{i+1}. {q}" for i, q in enumerate(missing[:2])])
        response += "\n\nFor at jeg skal treffe bedre, svar på:\n" + followup
        return response

    extras = []
    if ctx.get("os"):
        extras.append(f"OS: {ctx['os']}")
    if ctx.get("browser"):
        extras.append(f"Nettleser: {ctx['browser']}")
    if ctx.get("error"):
        extras.append(f"Feilmelding: {ctx['error']}")

    if extras:
        response += "\n\n" + "\n".join(extras)

    return response

@bp.route("/chat", methods=["POST"])
def chat():
    if not current_user():
        return jsonify({"reply": "Du må være innlogget for å bruke chat."}), 401

    try:
        data = request.get_json(silent=True) or {}
        user_msg = (data.get("message") or "").strip()

        if not user_msg:
            return jsonify({"reply": "Skriv hva du trenger hjelp med."})

        history = session.get("chat_history", [])
        reply = local_helpdesk_bot(user_msg)

        history.append({"role": "user", "content": user_msg})
        history.append({"role": "assistant", "content": reply})
        session["chat_history"] = history

        return jsonify({"reply": reply})
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({"reply": "En feil oppstod. Prøv igjen senere."}), 500