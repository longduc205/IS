import os
import pymysql
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

login_manager = LoginManager()
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "insecure-dev-key")
    app.config["DATABASE_HOST"] = os.environ.get("DATABASE_HOST", "localhost")
    app.config["DATABASE_PORT"] = int(os.environ.get("DATABASE_PORT", 3306))
    app.config["DATABASE_USER"] = os.environ.get("DATABASE_USER", "vulnlab")
    app.config["DATABASE_PASSWORD"] = os.environ.get("DATABASE_PASSWORD", "vulnlab_secret")
    app.config["DATABASE_NAME"] = os.environ.get("DATABASE_NAME", "vulnlab")
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # CSRFProtect initialized but we selectively exempt vulnerable routes
    csrf.init_app(app)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(int(user_id))

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.sqli import sqli_bp
    from app.routes.xss import xss_bp
    from app.routes.csrf_demo import csrf_bp
    from app.routes.upload import upload_bp
    from app.routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(sqli_bp, url_prefix="/sqli")
    app.register_blueprint(xss_bp, url_prefix="/xss")
    app.register_blueprint(csrf_bp, url_prefix="/csrf")
    app.register_blueprint(upload_bp, url_prefix="/upload")

    # Initialize database
    with app.app_context():
        from app.db_init import init_db
        init_db(app)

    return app
