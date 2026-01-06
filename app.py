from flask import Flask
from models import db
from config import Config
import os

from utils import get_current_user


def create_app():
    app = Flask(__name__)

    @app.context_processor
    def inject_user():
        return {"user": get_current_user()}

    app.config.from_object(Config)

    # Initialiser la base de données
    db.init_app(app)

    # Importer et enregistrer les blueprints
    from routes.main import bp as main_bp
    from routes.auth import bp as auth_bp
    from routes.devinette import bp as devinette_bp
    from routes.devinetteSansAlcool import bp as devinette_sans_alcool_bp
    from routes.scoreboard import bp as scoreboard_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(devinette_bp)
    app.register_blueprint(devinette_sans_alcool_bp)
    app.register_blueprint(scoreboard_bp)

    # Gestionnaires d'erreurs
    from utils import page_not_found, internal_error
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_error)

    # Commande CLI pour initialiser la DB
    from argon2 import PasswordHasher
    from models import User

    @app.cli.command('init-db')
    def init_db():
        """Créer la base de données et un utilisateur exemple."""
        db.create_all()
        ph = PasswordHasher()
        if not User.query.filter_by(username='alice').first():
            try:
                demo = User(
                    username='alice',
                    email='alice@example.com',
                    password_hash=ph.hash('password123'),
                    wins=0
                )
                db.session.add(demo)
                db.session.commit()
                print('Utilisateur de démo créé: alice / password123')
            except Exception as e:
                print('Erreur lors de la création de l\'utilisateur:', e)
        print('Base de données initialisée.')

    return app


if __name__ == '__main__':
    flask_app = create_app()
    # Créer la DB si elle n'existe pas
    if not os.path.exists('app.db'):
        with flask_app.app_context():
            db.create_all()
    flask_app.run(debug=True)
