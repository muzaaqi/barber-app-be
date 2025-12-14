from flask import Blueprint, request
from app.models.haircut import Haircut
from app.modules import response
from app.modules.transform import transform
from app.modules.upload_r2 import delete_image, upload_image
from app import db

haircut_bp = Blueprint('haircut', __name__, url_prefix='/haircuts')


@haircut_bp.route('/', methods=['GET'])
def get_models():
    try:
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 10, type=int)

        pagination = Haircut.query \
            .order_by(Haircut.choosen_count.desc()) \
            .paginate(page=page, per_page=limit, error_out=False)

        data = transform(pagination.items)

        return response.ok({
            "data": data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": pagination.total
            }
        }, "Successfully retrieved haircut models")

    except Exception:
        return response.internal_server_error("Internal server error")


@haircut_bp.route('/<string:model_id>', methods=['GET'])
def get_model_by_id(model_id):
    try:
        haircut_model = Haircut.query.get(model_id)
        if not haircut_model:
            return response.not_found("Haircut model not found")

        return response.ok(
            haircut_model.to_dict(),
            "Successfully retrieved haircut model"
        )

    except Exception:
        return response.internal_server_error("Internal server error")


@haircut_bp.route('/', methods=['POST'])
def create_model():
    try:
        model_data = request.get_json()
        if not model_data:
            return response.bad_request("Request body is empty")

        required_fields = ["name", "description", "price"]
        if not all(field in model_data for field in required_fields):
            return response.bad_request("Missing required fields")

        upload_result = upload_image(model_data["name"], "haircut-models")
        if not upload_result or upload_result[1] != 200:
            return response.bad_request("Image upload failed")

        image_url = upload_result[0]["url"]

        new_model = Haircut(
            name=model_data["name"],
            description=model_data["description"],
            price=model_data["price"],
            image_url=image_url
        )

        try:
            new_model.insert()
        except Exception:
            delete_image(image_url)
            raise

        return response.created(
            new_model.to_dict(),
            "Successfully created haircut model"
        )

    except Exception:
        db.session.rollback()
        return response.internal_server_error("Internal server error")


@haircut_bp.route('/<string:model_id>', methods=['PUT'])
def update_model(model_id):
    try:
        model_data = request.get_json()
        if not model_data:
            return response.bad_request("Request body is empty")

        haircut_model = Haircut.query.get(model_id)
        if not haircut_model:
            return response.not_found("Haircut model not found")

        allowed_fields = ["name", "description", "price"]

        if model_data.get("image"):
            upload_result = upload_image(
                model_data.get("name", haircut_model.name),
                "haircut-models"
            )

            if not upload_result or upload_result[1] != 200:
                return response.bad_request("Image upload failed")

            new_image_url = upload_result[0]["url"]

            delete_image(haircut_model.image_url)
            haircut_model.image_url = new_image_url

        for field in allowed_fields:
            if field in model_data:
                setattr(haircut_model, field, model_data[field])

        haircut_model.update()

        return response.ok(
            haircut_model.to_dict(),
            "Successfully updated haircut model"
        )

    except Exception:
        db.session.rollback()
        return response.internal_server_error("Internal server error")
    
@haircut_bp.route('/<string:model_id>', methods=['DELETE'])
def delete_model(model_id):
    try:
        haircut_model = Haircut.query.get(model_id)
        if not haircut_model:
            return response.not_found("Haircut model not found")

        delete_image(haircut_model.image_url)
        haircut_model.delete()

        return response.ok(
            {},
            "Successfully deleted haircut model"
        )

    except Exception:
        db.session.rollback()
        return response.internal_server_error("Internal server error")