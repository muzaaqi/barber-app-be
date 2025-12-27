from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
from flasgger import swag_from

from app import db
from app.modules import response
from app.models.product_transactions import CartItem
from app.models.product import Product

cart_bp = Blueprint('cart', __name__, url_prefix='/carts')


@cart_bp.route('/', methods=['GET'])
@jwt_required()
@swag_from('app/docs/cart/get.yml')
def get_my_cart():
    try:
        user_id = get_jwt_identity()

        cart_items = CartItem.query \
            .options(joinedload(CartItem.product)) \
            .filter_by(user_id=user_id) \
            .all()

        data = []
        grand_total = 0
        total_items = 0

        for item in cart_items:
            if not item.product:
                continue

            subtotal = item.product.price * item.quantity
            grand_total += subtotal
            total_items += item.quantity

            data.append({
                "cart_id": item.id,
                "product_id": item.product_id,
                "product_name": item.product.name,
                "product_image": item.product.image_url,
                "price": item.product.price,
                "quantity": item.quantity,
                "subtotal": subtotal,
                "max_stock": item.product.stock
            })

        return response.ok({
            "items": data,
            "summary": {
                "total_items": total_items,
                "grand_total": grand_total
            }
        }, "Successfully retrieved cart")

    except Exception:
        return response.internal_server_error("Internal server error")

@cart_bp.route('/', methods=['POST'])
@jwt_required()
@swag_from('app/docs/cart/add.yml')
def add_to_cart():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))

        if not product_id:
            return response.bad_request("Product ID is required")
        
        if quantity < 1:
            return response.bad_request("Quantity must be at least 1")

        product = Product.query.get(product_id)
        if not product:
            return response.not_found("Product not found")

        existing_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()

        if existing_item:
            new_quantity = existing_item.quantity + quantity
            
            if new_quantity > product.stock:
                return response.bad_request(f"Stock insufficient. Max available: {product.stock}")
            
            existing_item.quantity = new_quantity
            message = "Cart updated successfully"
            
            db.session.commit()
            return response.ok(existing_item.to_dict(), message)

        else:
            if quantity > product.stock:
                return response.bad_request(f"Stock insufficient. Max available: {product.stock}")

            new_item = CartItem(
                user_id=user_id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(new_item)
            message = "Product added to cart"
            
            db.session.commit()
            return response.ok(new_item.to_dict(), message)

    except Exception:
        db.session.rollback()
        return response.internal_server_error("Internal server error")


@cart_bp.route('/<string:cart_id>', methods=['PUT'])
@jwt_required()
@swag_from('app/docs/cart/update.yml')
def update_cart_item(cart_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        new_quantity = int(data.get('quantity'))

        cart_item = CartItem.query.filter_by(id=cart_id, user_id=user_id).first()
        
        if not cart_item:
            return response.not_found("Cart item not found")

        if new_quantity < 1:
            return response.bad_request("Quantity must be at least 1")

        if new_quantity > cart_item.product.stock:
            return response.bad_request(f"Stock insufficient. Max available: {cart_item.product.stock}")

        cart_item.quantity = new_quantity
        db.session.commit()

        return response.ok(cart_item.to_dict(), "Cart quantity updated")

    except Exception:
        db.session.rollback()
        return response.internal_server_error("Internal server error")

@cart_bp.route('/<string:cart_id>', methods=['DELETE'])
@jwt_required()
@swag_from('app/docs/cart/delete.yml')
def delete_cart_item(cart_id):
    try:
        user_id = get_jwt_identity()
        
        cart_item = CartItem.query.filter_by(id=cart_id, user_id=user_id).first()

        if not cart_item:
            return response.not_found("Cart item not found")

        db.session.delete(cart_item)
        db.session.commit()

        return response.ok(None, "Item removed from cart")

    except Exception:
        db.session.rollback()
        return response.internal_server_error("Internal server error")