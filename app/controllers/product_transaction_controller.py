from flask import Blueprint, request
from flask_jwt_extended import (jwt_required, get_jwt_identity)
from sqlalchemy.orm import joinedload
from datetime import datetime
from app import db
from app.models.product_transactions import ProductTransaction, TransactionItem, CartItem
from app.models.user import User
from app.models.product import Product
from app.modules import response
from app.modules.transform import transform_data

product_transaction_bp = Blueprint('product_transaction', __name__, url_prefix='/product-transactions')


@product_transaction_bp.route('/', methods=['GET'])
@jwt_required()
def get_product_transactions():
    try:
        user_id = get_jwt_identity()
        current_user = User.query.get(user_id)
        if not current_user or current_user.role != 'admin':
            return response.unauthorized("You are not allowed to access this resource")
        
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 10, type=int)
        
        filter_user_id = request.args.get("user_id")

        query = ProductTransaction.query \
            .options(
                joinedload(ProductTransaction.user),
                joinedload(ProductTransaction.items).joinedload(TransactionItem.product)
            ) \
            .order_by(ProductTransaction.created_at.desc())

        if filter_user_id:
            query = query.filter(ProductTransaction.user_id == filter_user_id)

        pagination = query.paginate(page=page, per_page=limit, error_out=False)

        data = transform_data(pagination.items, relations={
            "user": ['name', 'email'], 
            "items": [] 
        })
        
        return response.ok({
            "data": data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": pagination.total
            }
        }, "Successfully retrieved product transactions")

    except Exception as e:
        print(e)
        return response.internal_server_error("Internal server error")


@product_transaction_bp.route('/<string:transaction_id>', methods=['GET'])
@jwt_required()
def get_product_transaction_by_id(transaction_id):
    try:
        user_id = get_jwt_identity()
        current_user = User.query.get(user_id)
        
        product_transaction = ProductTransaction.query \
            .options(joinedload(ProductTransaction.items).joinedload(TransactionItem.product)) \
            .get(transaction_id)
        
        if not product_transaction:
            return response.not_found("Product transaction not found")

        if product_transaction.user_id != current_user.id and current_user.role != 'admin':
            return response.unauthorized("You are not allowed to view this transaction")

        data = transform_data([product_transaction], relations={
            "items": [],
            "user": ['name', 'email']
        })[0]
        
        return response.ok(
            data,
            "Successfully retrieved product transaction"
        )

    except Exception as e:
        print(e)
        return response.internal_server_error("Internal server error")

@product_transaction_bp.route('/me', methods=['GET'])
@jwt_required()
def get_my_transactions():
    try:
        user_id = get_jwt_identity()

        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 10, type=int)

        pagination = ProductTransaction.query \
            .options(joinedload(ProductTransaction.items).joinedload(TransactionItem.product)) \
            .filter(ProductTransaction.user_id == user_id) \
            .order_by(ProductTransaction.created_at.desc()) \
            .paginate(page=page, per_page=limit, error_out=False)

        data = transform_data(pagination.items, relations={"items": []})

        return response.ok({
            "data": data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": pagination.total
            }
        }, "Successfully retrieved your transactions")

    except Exception as e:
        print(e)
        return response.internal_server_error("Internal server error")


@product_transaction_bp.route('/checkout', methods=['POST'])
@jwt_required()
def create_product_transaction():
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        checkout_items = [] 
        grand_total = 0
        is_direct_buy = False

        if 'product_id' in data and 'quantity' in data:
            is_direct_buy = True
            product_id = data['product_id']
            quantity = int(data['quantity'])

            if quantity < 1:
                return response.bad_request("Quantity must be at least 1")

            product = Product.query.get(product_id)
            if not product:
                return response.not_found("Product not found")
            
            if product.stock < quantity:
                return response.bad_request(f"Insufficient stock for '{product.name}'")

            checkout_items.append({
                'product': product,
                'quantity': quantity,
                'cart_item_obj': None 
            })

            grand_total = product.price * quantity

        else:
            cart_items_db = CartItem.query.filter_by(user_id=user_id).all()
            
            if not cart_items_db:
                return response.bad_request("Cart is empty and no direct product specified.")

            for item in cart_items_db:
                if not item.product: continue
                
                if item.product.stock < item.quantity:
                    return response.bad_request(f"Insufficient stock for '{item.product.name}'")

                checkout_items.append({
                    'product': item.product,
                    'quantity': item.quantity,
                    'cart_item_obj': item 
                })
                
                grand_total += item.product.price * item.quantity


        new_transaction = ProductTransaction(
            user_id=user_id,
            total_price=grand_total,
            expedition_service=data.get("expedition_service", "JNE"),
            payment_method=data.get("payment_method", "cod"),
            payment_status=data.get("payment_status", "unpaid"),
            shipping_address=data.get("shipping_address"),
            expedition_status="pending"
        )

        db.session.add(new_transaction)
        db.session.flush()

        for item_data in checkout_items:
            prod = item_data['product']
            qty = item_data['quantity']
            cart_obj = item_data['cart_item_obj']

            prod.stock -= qty
            
            new_item = TransactionItem(
                transaction_id=new_transaction.id,
                product_id=prod.id,
                quantity=qty,
                price_at_purchase=prod.price
            )
            db.session.add(new_item)

            if cart_obj:
                db.session.delete(cart_obj)

        db.session.commit()

        result = new_transaction.to_dict()
        
        return response.created(
            result,
            "Transaction created successfully"
        )

    except Exception as e:
        db.session.rollback()
        print(f"Checkout Error: {e}")
        return response.internal_server_error("Internal server error")


@product_transaction_bp.route('/<string:transaction_id>', methods=['PUT'])
@jwt_required()
def update_transaction_status(transaction_id):
    try:
        product_transaction = ProductTransaction.query.get(transaction_id)
        if not product_transaction:
            return response.not_found("Product transaction not found")

        data = request.get_json()
        if not data:
            return response.bad_request("Request body is empty")

        if 'payment_status' in data:
            product_transaction.payment_status = data['payment_status']
        
        if 'expedition_status' in data:
            product_transaction.expedition_status = data['expedition_status']

        product_transaction.updated_at = datetime.utcnow()
        db.session.commit()

        return response.ok(
            product_transaction.to_dict(),
            "Transaction status updated successfully"
        )
    except Exception as e:
        db.session.rollback()
        return response.internal_server_error("Internal server error")


@product_transaction_bp.route('/<string:transaction_id>', methods=['DELETE'])
@jwt_required()
def delete_product_transaction(transaction_id):
    try:
        product_transaction = ProductTransaction.query \
            .options(joinedload(ProductTransaction.items).joinedload(TransactionItem.product)) \
            .get(transaction_id)
            
        if not product_transaction:
            return response.not_found("Product transaction not found")

        for item in product_transaction.items:
            item.product.stock += item.quantity

        db.session.delete(product_transaction)
        db.session.commit()

        return response.ok(
            {},
            "Product transaction deleted successfully"
        )
    except Exception as e:
        db.session.rollback()
        return response.internal_server_error("Internal server error")