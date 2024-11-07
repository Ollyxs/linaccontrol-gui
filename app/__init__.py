import os
import logging
from flask import Flask
from dotenv import load_dotenv

from flask_wtf import CSRFProtect
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5

# from flask_cors import CORS


bootstrap = Bootstrap5()
CSRFP = CSRFProtect()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    load_dotenv()

    app.config["API_URL"] = os.getenv("API_URL")
    app.config["SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    CSRFP.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)

    # CORS(app)

    from app.routes import main, admin, test

    app.register_blueprint(main.main)
    app.register_blueprint(admin.admin)
    app.register_blueprint(test.test)

    return app
