from flask_mail import Message, Mail
import logging

from .config import Config

logger = logging.getLogger(__name__)
mail = Mail()

def init_mail(app):
    """Initialize Flask-Mail"""
    mail.init_app(app)

def send_email(subject: str, recipients: list, text_body: str, html_body: str):
    """Send email with error handling"""
    try:
        msg = Message(
            subject=subject,
            recipients=recipients,
            body=text_body,
            html=html_body
        )
        mail.send(msg)
        logger.info(f"E-post sendt til {recipients}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Kunne ikke sende e-post til {recipients}: {e}")
        return False

def send_ticket_created_email(ticket: dict, user_email: str):
    subject = f"[{Config.SITE_NAME}] Sak #{ticket['id']} opprettet: {ticket['title']}"

    text_body = f"""
Hei,

Din support-sak har blitt opprettet.

Saksnummer: #{ticket['id']}
Tittel: {ticket['title']}
Kategori: {ticket.get('category','')}
Prioritet: {ticket.get('priority','')}

Følg saken din her: {Config.BASE_URL}/tickets/{ticket['id']}

Med vennlig hilsen,
{Config.SITE_NAME}
""".strip()

    html_body = f"""
<html><body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
<div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
  <h2 style="color: #2563eb;">Support-sak opprettet</h2>
  <p>Hei,</p>
  <p>Din support-sak har blitt opprettet.</p>
  <div style="background:#f3f4f6; padding:15px; border-radius:5px; margin:20px 0;">
    <p><strong>Saksnummer:</strong> #{ticket['id']}</p>
    <p><strong>Tittel:</strong> {ticket['title']}</p>
    <p><strong>Kategori:</strong> {ticket.get('category','')}</p>
    <p><strong>Prioritet:</strong> {ticket.get('priority','')}</p>
  </div>
  <p><a href="{Config.BASE_URL}/tickets/{ticket['id']}" style="display:inline-block; padding:10px 20px; background:#2563eb; color:white; text-decoration:none; border-radius:5px;">Se sak</a></p>
  <p style="margin-top: 30px; font-size: 12px; color: #666;">Med vennlig hilsen,<br>{Config.SITE_NAME}</p>
</div>
</body></html>
""".strip()

    if user_email:
        send_email(subject, [user_email], text_body, html_body)

def notify_support_new_ticket(ticket: dict):
    subject = f"[{Config.SITE_NAME}] Ny support-sak #{ticket['id']}"

    text_body = f"""
Ny support-sak opprettet:

Saksnummer: #{ticket['id']}
Fra: {ticket.get('owner','')}
Tittel: {ticket.get('title','')}

Behandle saken: {Config.BASE_URL}/tickets/{ticket['id']}
""".strip()

    html_body = f"""
<html><body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
<div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
  <h2 style="color:#dc2626;">Ny support-sak</h2>
  <p><strong>Saksnummer:</strong> #{ticket['id']}</p>
  <p><strong>Fra:</strong> {ticket.get('owner','')}</p>
  <p><strong>Tittel:</strong> {ticket.get('title','')}</p>
  <p><a href="{Config.BASE_URL}/tickets/{ticket['id']}" style="display:inline-block; padding:10px 20px; background:#2563eb; color:white; text-decoration:none; border-radius:5px;">Behandle sak</a></p>
</div>
</body></html>
""".strip()

    send_email(subject, [Config.ADMIN_EMAIL], text_body, html_body)