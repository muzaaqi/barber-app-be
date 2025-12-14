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
        products = Product.query.order_by(Product.choosen.desc()).all()
        data = transform(products)
        return response.ok(data, "Successfully retrieved products")
    except Exception as e:
        return response.internal_server_error(str(e))

@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product_by_id(product_id):
    try:
        product = Product.query.get(product_id)
        if not product:
            return response.not_found("Product not found")
        data = product.to_dict()
        return response.ok(data, "Successfully retrieved product")
    except Exception as e:
        return response.internal_server_error(str(e))

@product_bp.route('/', methods=['POST'])
def create_product():
    try:
        name = request.form.get('name')
        price = request.form.get('price')
        description = request.form.get('description')
        image = request.files.get('image')

        if not all([name, price, description, image]):
            return response.bad_request("All fields are required")

        image_url = upload_image(name, "products")

        new_product = Product(
            name=name,
            price=price,
            description=description,
            image=image_url
        )
        db.session.add(new_product)
        db.session.commit()

        data = new_product.to_dict()
        return response.created(data, "Product created successfully")
    except Exception as e:
        return response.internal_server_error(str(e))

@product_bp.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        product = Product.query.get(product_id)
        if not product:
            return response.not_found("Product not found")

        name = request.form.get('name', product.name)
        price = request.form.get('price', product.price)
        description = request.form.get('description', product.description)
        image = request.files.get('image')

        if image:
            delete_image(product.image_url)
            image_url = upload_image(name, "products")
            product.image_url = image_url

        product.name = name
        product.price = price
        product.description = description

        db.session.commit()

        data = product.to_dict()
        return response.ok(data, "Product updated successfully")
    except Exception as e:
        return response.internal_server_error(str(e))

@product_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        product = Product.query.get(product_id)
        if not product:
            return response.not_found("Product not found")

        delete_image(product.image_url)

        db.session.delete(product)
        db.session.commit()

        return response.ok({}, "Product deleted successfully")
    except Exception as e:
        return response.internal_server_error(str(e))