from flask import Flask
import os
import secrets

def create_app():
    app = Flask(__name__)
    
    # Secure secret key - use environment variable or generate random
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", secrets.token_hex(32))
    
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