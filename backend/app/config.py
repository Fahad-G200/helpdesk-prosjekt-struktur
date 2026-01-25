import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'helpdesk.db')

    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf', 'txt', 'doc', 'docx', 'log'}

    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@helpdesk.no'

    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@helpdesk.no'
    SITE_NAME = 'IT Helpdesk'
    BASE_URL = os.environ.get('BASE_URL') or 'http://localhost:5000'

    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    SLA_CRITICAL = 2
    SLA_HIGH = 8
    SLA_MEDIUM = 24
    SLA_LOW = 72