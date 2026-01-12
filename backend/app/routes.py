from flask import Blueprint, render_template, request, redirect, url_for, session, flash
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
            add_ticket(owner=user, title=title, desc=desc, category=category, priority=priority, device=device)
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


    from flask import jsonify

FAQ = [
    {
        "tags": ["feide", "innlogging", "login", "passord", "konto"],
        "answer": (
            "Feide: Prøv dette først (Nivå 1):\n"
            "1) Sjekk brukernavn/passord (Caps Lock)\n"
            "2) Velg riktig skole/organisasjon\n"
            "3) Prøv inkognito/privat vindu\n"
            "4) Tøm cache/cookies\n"
            "Hvis det fortsatt feiler: noter tidspunkt + feilmelding og gå til Nivå 2."
        ),
    },
    {
        "tags": ["wifi", "nett", "internett", "nettverk"],
        "answer": (
            "Wi-Fi/Nett: Prøv dette (Nivå 1):\n"
            "1) Slå Wi-Fi av/på\n"
            "2) Koble til riktig nettverk\n"
            "3) Restart enheten\n"
            "Hvis det fortsatt feiler: sjekk IP/ping på Nivå 2 eller opprett sak (Nivå 3)."
        ),
    },
    {
        "tags": ["utskrift", "printer", "skriver", "print"],
        "answer": (
            "Utskrift: Prøv dette (Nivå 1):\n"
            "1) Velg riktig skriver\n"
            "2) Sjekk papir/toner\n"
            "3) Restart skriver og PC\n"
            "Hvis det fortsatt feiler: noter feilkode og gå til Nivå 2."
        ),
    },
    {
        "tags": ["sak", "ticket", "support", "hjelp", "innmelding"],
        "answer": (
            "Hvis Nivå 1 og 2 ikke løser problemet: Opprett en sak (Nivå 3).\n"
            "Husk å skrive: feilmelding, tidspunkt, enhet/OS, nettleser og hva du har prøvd."
        ),
    },
]

def chatbot_reply(message: str) -> str:
    text = (message or "").lower().strip()
    if not text:
        return "Skriv hva du trenger hjelp med (f.eks. Feide, Wi-Fi, utskrift, passord)."

    # Enkel matching: finn første FAQ der minst én tag finnes i teksten
    for item in FAQ:
        if any(tag in text for tag in item["tags"]):
            return item["answer"]

    # Fallback
    return (
        "Jeg fant ikke en direkte match. Skriv gjerne:\n"
        "- hvilken tjeneste (Feide/Wi-Fi/utskrift)\n"
        "- feilmelding\n"
        "- tidspunkt\n"
        "- enhet og nettleser\n"
        "Hvis du fortsatt står fast: opprett sak under «Mine saker»."
    )

@bp.route("/chat", methods=["POST"])
def chat():
    if not current_user():
        return jsonify({"reply": "Du må være innlogget for å bruke chat."}), 401

    data = request.get_json(silent=True) or {}
    msg = data.get("message", "")
    reply = chatbot_reply(msg)
    return jsonify({"reply": reply})