from flask import Flask
import os

from .config import Config
from .email_service import init_mail


def create_app():
    app = Flask(__name__)

    # Last inn config.py (MAIL_*, DATABASE_PATH, osv.)
    app.config.from_object(Config)

    # Init Flask-Mail
    init_mail(app)

    # Security headers
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    # Import routes
    from .routes import bp
    app.register_blueprint(bp)

    return app