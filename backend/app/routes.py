from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from .db import (
    init_db,
    add_ticket, get_tickets, close_ticket,
    user_exists, create_user, get_user
)

bp = Blueprint("main", __name__)

def current_user():
    return session.get("user")

def current_role():
    return session.get("role")

@bp.before_app_request
def ensure_db():
    init_db()

@bp.route("/")
def home():
    if not current_user():
        return redirect(url_for("main.login"))
    return redirect(url_for("main.kb"))

@bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        u = get_user(username)
        if u and check_password_hash(u["pw_hash"], password):
            session["user"] = u["username"]
            session["role"] = u["role"]
            return redirect(url_for("main.kb"))

        error = "Feil brukernavn eller passord."
    return render_template("login.html", error=error)

@bp.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
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
            flash("Bruker opprettet. Du kan logge inn nå.")
            return redirect(url_for("main.login"))

    return render_template("register.html", error=error)

@bp.route("/logout")
def logout():
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
        title = request.form.get("title", "").strip()
        desc = request.form.get("desc", "").strip()
        category = request.form.get("category", "Annet").strip()
        priority = request.form.get("priority", "Middels").strip()
        device = request.form.get("device", "").strip()

        if title and desc:
            add_ticket(owner=user, title=title, desc=desc,
                       category=category, priority=priority, device=device)
            flash("Saken er sendt til support. Du finner den i oversikten under.")
        else:
            flash("Du må fylle ut tittel og beskrivelse.")

        return redirect(url_for("main.tickets"))

    visible = get_tickets() if role == "support" else get_tickets(owner=user)
    return render_template("_tickets.html", tickets=visible, role=role)

@bp.route("/tickets/<int:ticket_id>/close", methods=["POST"])
def close_ticket_view(ticket_id):
    user = current_user()
    role = current_role()

    if not user or role != "support":
        return redirect(url_for("main.tickets"))

    close_ticket(ticket_id)
    flash(f"Sak #{ticket_id} er lukket.")
    return redirect(url_for("main.tickets"))


# --------------------------------------------------
# Chatbot-innhold (regelbasert, støtter setninger)
# --------------------------------------------------

FAQ = [
    {
        "tags": ["feide", "innlogging", "login", "passord", "konto"],
        "answer": (
            "Feide-problemer (Nivå 1):\n"
            "1) Sjekk brukernavn/passord\n"
            "2) Velg riktig skole/organisasjon\n"
            "3) Prøv inkognito/privat vindu\n"
            "4) Tøm cache/cookies\n"
            "Hvis det fortsatt feiler: noter feilmelding og tidspunkt."
        ),
    },
    {
        "tags": ["wifi", "nett", "internett", "nettverk"],
        "answer": (
            "Wi-Fi-problemer (Nivå 1):\n"
            "1) Slå Wi-Fi av/på\n"
            "2) Koble til riktig nettverk\n"
            "3) Restart enheten\n"
            "Hvis det feiler videre: gå til nivå 2 eller opprett sak."
        ),
    },
    {
        "tags": ["utskrift", "printer", "skriver"],
        "answer": (
            "Utskrift (Nivå 1):\n"
            "1) Velg riktig skriver\n"
            "2) Sjekk papir/toner\n"
            "3) Restart skriver og PC"
        ),
    },
]

def chatbot_reply(message: str) -> str:
    import re
    text = (message or "").lower()
    words = set(re.findall(r"\w+", text))

    for item in FAQ:
        if any(tag in words or tag in text for tag in item["tags"]):
            return item["answer"]

    return (
        "Jeg er ikke helt sikker på problemet ennå.\n"
        "Prøv å beskrive:\n"
        "- hvilken tjeneste\n"
        "- feilmelding\n"
        "- tidspunkt\n"
        "- enhet/OS\n"
        "Eller opprett en sak under «Mine saker»."
    )

@bp.route("/chat", methods=["POST"])
def chat():
    if not current_user():
        return jsonify({"reply": "Du må være innlogget for å bruke chat."}), 401

    data = request.get_json(silent=True) or {}
    msg = data.get("message", "")
    return jsonify({"reply": chatbot_reply(msg)})