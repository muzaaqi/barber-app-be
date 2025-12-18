from flask import Blueprint, request
from flask_jwt_extended import (jwt_required, get_jwt_identity)
from sqlalchemy.orm import joinedload
from datetime import datetime
from app import db
from app.models.product_transactions import ProductTransaction
from app.models.product import Product
from app.modules import response
from app.modules.transform import transform_data

product_transaction_bp = Blueprint('product_transaction', __name__, url_prefix='/product-transactions')

@product_transaction_bp.route('/', methods=['GET'])
def get_product_transactions():
    try:
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 10, type=int)

        pagination = ProductTransaction.query \
            .options(joinedload(ProductTransaction.user), joinedload(ProductTransaction.product)) \
            .order_by(ProductTransaction.created_at.desc()) \
            .paginate(page=page, per_page=limit, error_out=False)

        data = transform_data(pagination.items, relations={"product": ['name', 'image_url', 'price'], "user": ['name', 'email']})
        
        return response.ok({
            "data": data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": pagination.total
            }
        }, "Successfully retrieved product transactions")

    except Exception:
        return response.internal_server_error("Internal server error")

@product_transaction_bp.route('/<string:transaction_id>', methods=['GET'])
def get_product_transaction_by_id(transaction_id):
    try:
        product_transaction = ProductTransaction.query \
            .options(joinedload(ProductTransaction.product)) \
            .get(transaction_id)
        
        if not product_transaction:
            return response.not_found("Product transaction not found")

        data = transform_data([product_transaction], relations={"product": ['name', 'image_url', 'price']})[0]
        
        return response.ok(
            data,
            "Successfully retrieved product transaction"
        )

    except Exception:
        return response.internal_server_error("Internal server error")

@product_transaction_bp.route('/', methods=['GET'])
def get_product_transactions_by_user_id():
    try:
        user_id = request.args.get("user_id", type=str)
        if not user_id:
            return response.bad_request("User ID is required")

        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 10, type=int)

        pagination = ProductTransaction.query \
            .options(joinedload(ProductTransaction.user), joinedload(ProductTransaction.product)) \
            .filter(ProductTransaction.user_id == user_id) \
            .order_by(ProductTransaction.created_at.desc()) \
            .paginate(page=page, per_page=limit, error_out=False)

        data = transform_data(pagination.items, relations={"product": ['name', 'image_url', 'price'], "user": ['name', 'email']})

        return response.ok({
            "data": data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": pagination.total
            }
        }, "Successfully retrieved product transactions for user")

    except Exception:
        return response.internal_server_error("Internal server error")

@product_transaction_bp.route('/', methods=['POST'])
def create_product_transaction():
    try:
        data = request.get_json()
        if not data:
            return response.bad_request("Request body is empty")

        required_fields = ["transaction_id", "product_id", "quantity"]
        if not all(field in data for field in required_fields):
            return response.bad_request("Missing required fields")

        transaction_id = data["transaction_id"]
        product_id = data["product_id"]
        quantity = data["quantity"]
        
        product = Product.query.get(product_id)
        if not product:
            return response.not_found("Product not found")

        if product.stock < quantity:
            return response.bad_request("Insufficient product stock")

        product.stock -= quantity

        new_product_transaction = ProductTransaction(
            transaction_id=transaction_id,
            product_id=product_id,
            quantity=quantity,
        )

        db.session.add(new_product_transaction)
        db.session.commit()

        return response.created(
            new_product_transaction.to_dict(),
            "Product transaction created successfully"
        )

    except Exception:
        db.session.rollback()
        return response.internal_server_error("Internal server error")

@product_transaction_bp.route('/<string:transaction_id>', methods=['PUT'])
def update_product_transaction(transaction_id):
    try:
        product_transaction = ProductTransaction.query.get(transaction_id)
        if not product_transaction:
            return response.not_found("Product transaction not found")

        data = request.get_json()
        if not data:
            return response.bad_request("Request body is empty")

        quantity = data.get("quantity", product_transaction.quantity)

        product_transaction.quantity = quantity
        product_transaction.updated_at = datetime.utcnow()

        db.session.commit()

        return response.ok(
            product_transaction.to_dict(),
            "Product transaction updated successfully"
        )
    except Exception:
        db.session.rollback()
        return response.internal_server_error("Internal server error")

@product_transaction_bp.route('/<string:transaction_id>', methods=['DELETE'])
def delete_product_transaction(transaction_id):
    try:
        product_transaction = ProductTransaction.query.get(transaction_id)
        if not product_transaction:
            return response.not_found("Product transaction not found")

        db.session.delete(product_transaction)
        db.session.commit()

        return response.ok(
            {},
            "Product transaction deleted successfully"
        )
    except Exception:
        db.session.rollback()
        return response.internal_server_error("Internal server error")