from flask import Flask, render_template, request
from flask_socketio import SocketIO
import os

socketio = SocketIO()  # opprett SocketIO-objekt (før create_app)

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "bytt-meg-senere"

    # Initialiser SocketIO med appen
    socketio.init_app(app)

    from .routes import bp
    app.register_blueprint(bp)

    # Feilhåndtering: tilpassede feil-sider for 404, 403, 500
    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("403.html"), 403

    @app.errorhandler(500)
    def server_error(error):
        app.logger.error(f"Uventet serverfeil på {request.path}: {error}")
        return render_template("500.html"), 500

    # Logging til fil (f.eks. helpdesk.log) når app.debug er False
    if not app.debug:
        import logging
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler("helpdesk.log", maxBytes=100_000, backupCount=3)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(module)s:%(lineno)d]"
        ))
        app.logger.addHandler(file_handler)

    return app