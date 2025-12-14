from flask import Blueprint
from app.controllers.haircut_controller import haircut_bp
from app.controllers.user_controller import user_bp

api = Blueprint('api', __name__, url_prefix='/api')

api.register_blueprint(haircut_bp)
api.register_blueprint(user_bp)