from flask import Blueprint, request
from flask_jwt_extended import (jwt_required, get_jwt_identity)
from flasgger import swag_from
from app.models.product import Product
from app.modules import response
from app.modules.transform import transform_data
from app.modules.upload_r2 import delete_image, upload_image
from app.modules.time import get_wib_time
from app.modules.swagger_utils import get_doc_path
from app import db
from app.models.user import User

product_bp = Blueprint('product', __name__, url_prefix='/products')


@product_bp.route('/', methods=['GET'], strict_slashes=False)
@swag_from(get_doc_path('product/get_list.yml'))
def get_products():
    try:
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 10, type=int)

        pagination = Product.query\
            .filter(Product.deleted_at.is_(None)) \
            .paginate(page=page, per_page=limit, error_out=False)

        data = transform_data(pagination.items)

        return response.ok({
            "data": data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": pagination.total
            }
        }, "Successfully retrieved products")

    except Exception:
        return response.internal_server_error("Internal server error")


@product_bp.route('/<string:product_id>', methods=['GET'], strict_slashes=False)
@swag_from(get_doc_path('product/get_detail.yml'))
def get_product_by_id(product_id):
    try:
        product = Product.query.get(product_id)
        if not product:
            return response.not_found("Product not found")

        return response.ok(
            product.to_dict(),
            "Successfully retrieved product"
        )

    except Exception:
        return response.internal_server_error("Internal server error")


@product_bp.route('/', methods=['POST'], strict_slashes=False)
@jwt_required()
@swag_from(get_doc_path('product/create.yml'))
def create_product():
    try:
        uid = get_jwt_identity()
        current_user = User.query.get(uid)
        if current_user.role != 'admin':
            return response.unauthorized("Admin access required")
        
        name = request.form.get("name")
        price = request.form.get("price")
        description = request.form.get("description")
        stock = request.form.get("stock", 0)
        image = request.files.get("image")

        if not name or not price:
            return response.bad_request("Name and price are required")

        upload_result = upload_image(name, image, "products")
        if not upload_result:
            return response.bad_request("Image upload failed")

        image_url = upload_result["url"]
        image_key = upload_result["key"]

        new_product = Product(
            name=name,
            description=description,
            price=float(price),
            image_url=image_url,
            image_key=image_key,
            stock=int(stock)
        )

        try:
            db.session.add(new_product)
            db.session.commit()
        except Exception:
            delete_image(image_key)
            raise

        return response.created(
            new_product.to_dict(),
            "Product created successfully"
        )

    except Exception:
        db.session.rollback()
        return response.internal_server_error("Internal server error")


@product_bp.route('/<string:product_id>', methods=['PUT'], strict_slashes=False)
@jwt_required()
@swag_from(get_doc_path('product/update.yml'))
def update_product(product_id):
    try:
        uid = get_jwt_identity()
        current_user = User.query.get(uid)
        if current_user.role != 'admin':
            return response.unauthorized("Admin access required")
        
        product_data = request.form.to_dict()
        if not product_data and not request.files:
            return response.bad_request("Request body is empty")
        
        product = Product.query.get(product_id)
        if not product:
            return response.not_found("Product not found")

        name = product_data.get("name", product.name)
        price_raw = product_data.get("price", product.price)
        price = float(price_raw)
        
        description = product_data.get("description", product.description)
        image = request.files.get("image")
        
        stock_raw = product_data.get("stock", product.stock)
        stock = int(stock_raw)

        if image:
            upload_result = upload_image(name, image, "products")
            
            if not upload_result:
                return response.bad_request("Image upload failed")

            new_image_url = upload_result["url"]
            new_image_key = upload_result["key"]

            delete_image(product.image_key)
            product.image_url = new_image_url
            product.image_key = new_image_key

        product.name = name
        product.price = price
        product.description = description
        product.stock = stock

        db.session.commit()

        return response.ok(
            product.to_dict(),
            "Product updated successfully"
        )

    except Exception:
        db.session.rollback()
        return response.internal_server_error("Internal server error")


@product_bp.route('/<string:product_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
@swag_from(get_doc_path('product/delete_soft.yml'))
def delete_product(product_id):
    try:
        uid = get_jwt_identity()
        current_user = User.query.get(uid)
        if current_user.role != 'admin':
            return response.unauthorized("Admin access required")
        
        product = Product.query.get(product_id)
        if not product:
            return response.not_found("Product not found")

        product.deleted_at = get_wib_time()
        db.session.commit()

        return response.ok({}, "Product deleted successfully")

    except Exception:
        db.session.rollback()
        return response.internal_server_error("Internal server error")


@product_bp.route('/hard/<string:product_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
@swag_from(get_doc_path('product/delete_hard.yml'))
def hard_delete_product(product_id):
    try:
        uid = get_jwt_identity()
        current_user = User.query.get(uid)
        if current_user.role != 'admin':
            return response.unauthorized("Admin access required")
        
        product = Product.query.get(product_id)
        if not product:
            return response.not_found("Product not found")

        delete_image(product.image_key)

        db.session.delete(product)
        db.session.commit()

        return response.ok({}, "Product deleted successfully")

    except Exception:
        db.session.rollback()
        return response.internal_server_error("Internal server error")