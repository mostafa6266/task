from flask import Flask
from .extensions import db, jwt, mail, migrate
from .auth.routes import auth_bp
from .books.routes import books_bp
from dotenv import load_dotenv


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth_bp)
    app.register_blueprint(books_bp)

    return app