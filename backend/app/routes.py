from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint("main", __name__)

# Enkelt demo-oppsett (MVP)
# Senere flytter vi dette til database.
USERS = {
    "bruker": {
        "pw": generate_password_hash("passord123", method="pbkdf2:sha256"),
        "role": "user",
    },
    "support": {
        "pw": generate_password_hash("support123", method="pbkdf2:sha256"),
        "role": "support",
    },
}

TICKETS = []  # {"title": "...", "desc": "...", "owner": "...", "status": "Åpen"}


def current_user():
    return session.get("user")


def current_role():
    return session.get("role")


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

        if username in USERS and check_password_hash(USERS[username]["pw"], password):
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

        if title and desc:
            TICKETS.append(
                {"title": title, "desc": desc, "owner": user, "status": "Åpen"}
            )

        return redirect(url_for("main.tickets"))

    if role == "support":
        visible = TICKETS
    else:
        visible = [t for t in TICKETS if t["owner"] == user]

    return render_template("_tickets.html", user=user, role=role, tickets=visible)