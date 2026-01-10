from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

# import databasefunksjoner
from .db import add_ticket, get_tickets, close_ticket

bp = Blueprint("main", __name__)

# fortsatt definisjon av USERS …

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
            add_ticket(owner=user, title=title, desc=desc)
        return redirect(url_for("main.tickets"))

    # Hent saker fra DB
    visible = get_tickets() if role == "support" else get_tickets(owner=user)
    return render_template("_tickets.html", user=user, role=role, tickets=visible)

@bp.route("/tickets/<int:ticket_id>/close", methods=["POST"])
def close_ticket_view(ticket_id: int):
    """Lukk en sak (kun support)."""
    user = current_user()
    role = current_role()
    if not user or role != "support":
        return redirect(url_for("main.tickets"))
    close_ticket(ticket_id)
    return redirect(url_for("main.tickets"))
