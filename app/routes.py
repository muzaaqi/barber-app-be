from flask import Blueprint
from app.controller.haircut_models_controller import get_haircut_models, get_haircut_model_by_id

bp = Blueprint('api', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    return "Welcome to the Barber App API"

@bp.route('/api/haircut-models')
def get_haircut_models():
    return get_haircut_models()

@bp.route('/api/haircut-models/<int:model_id>')
def get_haircut_model_by_id(model_id):
    return get_haircut_model_by_id(model_id)