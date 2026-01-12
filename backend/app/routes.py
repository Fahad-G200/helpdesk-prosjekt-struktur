import os
from openai import OpenAI

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from .db import (
    init_db,
    add_ticket, get_tickets, close_ticket,
    user_exists, create_user, get_user
)

# OpenAI-klient (API key leses fra miljøvariabelen OPENAI_API_KEY)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"

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
# Chatbot (AI via OpenAI) – ingen UI-endringer nødvendig
# --------------------------------------------------

@bp.route("/chat", methods=["POST"])
def chat():
    if not current_user():
        return jsonify({"reply": "Du må være innlogget for å bruke chat."}), 401

    data = request.get_json(silent=True) or {}
    user_msg = (data.get("message") or "").strip()

    if not user_msg:
        return jsonify({"reply": "Skriv hva du trenger hjelp med."})

    # historikk per bruker (i session)
    history = session.get("chat_history", [])

    system_prompt = (
        "Du er en profesjonell helpdesk-assistent for en skole. "
        "Svar alltid på norsk. "
        "Du skal kun hjelpe med IT-support (Feide/innlogging, Wi-Fi, utskrift, passord, Teams/Office, nettleserproblemer). "
        "Gi konkrete steg i riktig rekkefølge (nivå 1, nivå 2, nivå 3). "
        "Hvis du mangler informasjon, still 1-2 korte oppfølgingsspørsmål. "
        "Hvis problemet krever systemtilgang eller virker avansert, anbefal å opprette en sak og si hva som må inkluderes: "
        "feilmelding, tidspunkt, enhet/OS, nettleser og hva som er prøvd."
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history[-10:])  # begrens historikk for kostnad/stabilitet
    messages.append({"role": "user", "content": user_msg})

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.4,
            max_tokens=250
        )
        reply = resp.choices[0].message.content.strip()
    except Exception:
        reply = "Beklager, jeg klarte ikke å kontakte AI-tjenesten akkurat nå. Prøv igjen om litt."

    history.append({"role": "user", "content": user_msg})
    history.append({"role": "assistant", "content": reply})
    session["chat_history"] = history

    return jsonify({"reply": reply})