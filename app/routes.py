from flask import Blueprint
from app.controllers.haircut_controller import haircut_bp
from app.controllers.user_controller import user_bp
from app.controllers.product_controller import product_bp
from app.controllers.haircut_transaction_controller import haircut_transaction_bp
from app.controllers.product_transaction_controller import product_transaction_bp
from app.controllers.cart_controller import cart_bp

api = Blueprint('api', __name__, url_prefix='/api')

api.register_blueprint(user_bp)
api.register_blueprint(haircut_bp)
api.register_blueprint(product_bp)
api.register_blueprint(haircut_transaction_bp)
api.register_blueprint(product_transaction_bp)
api.register_blueprint(cart_bp)