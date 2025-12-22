from flask import Flask, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from app import models

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app, resources={r"/*": {"origins": Config.CORS_ALLOWED_ORIGINS}})
    JWTManager(app)

    db.init_app(app)
    migrate.init_app(app, db)
    
    @app.route('/')
    def index():
        return render_template ('index.html')

    from app.routes import api
    app.register_blueprint(api)

    return app
