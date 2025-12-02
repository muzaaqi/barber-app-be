from flask import Blueprint
from app.controller.haircut_models_controller import get_models, get_model_by_id

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/')
@bp.route('/index')
def index():
    return "Welcome to the Barber App API"

@bp.route('/haircut-models', methods=['GET'])
def get_haircut_models():
    return get_models()

@bp.route('/haircut-models/<int:model_id>', methods=['GET'])
def get_haircut_model_by_id(model_id):
    return get_model_by_id(model_id)