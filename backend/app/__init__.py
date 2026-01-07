from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "bytt-meg-senere"

    # Ruter importeres her for å unngå sirkulære imports
    from .routes import bp
    app.register_blueprint(bp)

    return app