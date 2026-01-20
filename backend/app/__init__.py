from flask import Flask
import os
import secrets

from .config import Config
from .email_service import init_mail


def create_app():
    app = Flask(__name__)

    # Last inn config.py (MAIL_*, DATABASE_PATH, osv.)
    app.config.from_object(Config)

    # Secure secret key - use environment variable or generate random
    # (OBS: for vurdering er det best å kreve SECRET_KEY i prod, men du ba ikke endre mer)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", secrets.token_hex(32))

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