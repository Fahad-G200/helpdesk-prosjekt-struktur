from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

# databasefunksjoner
from .db import add_ticket, get_tickets, close_ticket

bp = Blueprint("main", __name__)

# --- DEMO-BRUKERE ---
USERS = {
    "bruker": {
        "pw": generate_password_hash("passord123"),
        "role": "user",
    },
    "support": {
        "pw": generate_password_hash("support123"),
        "role": "support",
    },
}

# --- HJELPEFUNKSJONER ---
def current_user():
    return session.get("user")

def current_role():
    return session.get("role")


# --- ROUTES ---

@bp.route("/")
def home():
    if not current_user():
        return redirect(url_for("main.login"))
    return redirect(url_for("main.tickets"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if (
            username in USERS
            and check_password_hash(USERS[username]["pw"], password)
        ):
            session["user"] = username
            session["role"] = USERS[username]["role"]
            return redirect(url_for("main.tickets"))

        error = "Feil brukernavn eller passord."

    return render_template("login.html", error=error)


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))


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
            add_ticket(
                owner=user,
                title=title,
                desc=desc,
                category=category,
                priority=priority,
                device=device,
            )

        return redirect(url_for("main.tickets"))

    # support ser alle, bruker ser egne
    visible = get_tickets() if role == "support" else get_tickets(owner=user)

    return render_template("_tickets.html", tickets=visible, role=role)


@bp.route("/tickets/<int:ticket_id>/close", methods=["POST"])
def close_ticket_view(ticket_id):
    user = current_user()
    role = current_role()

    if not user or role != "support":
        return redirect(url_for("main.tickets"))

    close_ticket(ticket_id)
    return redirect(url_for("main.tickets"))

