from flask import Blueprint, request
from app.models.product import Product
from app.modules import response
from app.modules.transform import transform
from app.modules.upload_r2 import delete_image, upload_image
from app import db

product_bp = Blueprint('product', __name__, url_prefix='/products')


@product_bp.route('/', methods=['GET'])
def get_products():
    try:
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 10, type=int)

        pagination = Product.query \
            .order_by(Product.choosen.desc()) \
            .paginate(page=page, per_page=limit, error_out=False)

        data = transform(pagination.items)

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


@product_bp.route('/<string:product_id>', methods=['GET'])
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


@product_bp.route('/', methods=['POST'])
def create_product():
    try:
        name = request.form.get("name")
        price = request.form.get("price")
        description = request.form.get("description")
        image = request.files.get("image")
        stock = request.form.get("stock", 0)

        if not all([name, price, description, image]):
            return response.bad_request("All fields are required")

        upload_result = upload_image(name, "products")
        if not upload_result or upload_result[1] != 200:
            return response.bad_request("Image upload failed")

        image_url = upload_result[0]["url"]

        new_product = Product(
            name=name.strip(),
            price=price,
            description=description.strip(),
            image_url=image_url,
            stock=stock
        )

        try:
            db.session.add(new_product)
            db.session.commit()
        except Exception:
            delete_image(image_url)
            raise

        return response.created(
            new_product.to_dict(),
            "Product created successfully"
        )

    except Exception:
        db.session.rollback()
        return response.internal_server_error("Internal server error")


@product_bp.route('/<string:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        product_data = request.get_json()
        if not product_data:
            return response.bad_request("Request body is empty")
        
        product = Product.query.get(product_id)
        if not product:
            return response.not_found("Product not found")

        name = product_data.get("name", product.name)
        price = product_data.get("price", product.price)
        description = product_data.get("description", product.description)
        image = request.files.get("image")
        stock = int(product_data.get("stock", product.stock))

        if image:
            upload_result = upload_image(name, "products")
            
            if not upload_result or upload_result[1] != 200:
                return response.bad_request("Image upload failed")

            new_image_url = upload_result[0]["url"]

            delete_image(product.image_url)
            product.image_url = new_image_url
        else:
            product.image_url = product.image_url

        product.name = name
        product.price = price
        product.description = description
        product.stock = int(stock)

        db.session.commit()

        return response.ok(
            product.to_dict(),
            "Product updated successfully"
        )

    except Exception:
        db.session.rollback()
        return response.internal_server_error("Internal server error")


@product_bp.route('/<string:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        product = Product.query.get(product_id)
        if not product:
            return response.not_found("Product not found")

        delete_image(product.image_url)

        db.session.delete(product)
        db.session.commit()

        return response.ok({}, "Product deleted successfully")

    except Exception:
        db.session.rollback()
        return response.internal_server_error("Internal server error")
