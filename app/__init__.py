from flask import Flask, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.extensions import db, migrate, socketio, swagger
from config import Config
from app import models
from app.routes import api
from app.controllers.main_controller import main_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app, resources={r"/*": {"origins": Config.CORS_ALLOWED_ORIGINS}})
    JWTManager(app)

    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)
    swagger.init_app(app)
    
    @app.route('/')
    def index():
        return render_template ('index.html')

    app.register_blueprint(api)
    app.register_blueprint(main_bp)
    
    with app.app_context():
        from app import events

    return app
