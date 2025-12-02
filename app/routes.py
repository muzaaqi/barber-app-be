from flask import Blueprint

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/')
@bp.route('/index')
def index():
    return "Welcome to the Barber App API"