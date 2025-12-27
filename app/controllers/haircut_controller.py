from flask import Blueprint, request
from flask_jwt_extended import (jwt_required , get_jwt_identity)
from flasgger import swag_from
from app.models.haircut import Haircut
from app.modules import response
from app.modules.transform import transform_data
from app.modules.upload_r2 import delete_image, upload_image
from app.modules.time import get_wib_time
from app.modules.swagger_utils import get_doc_path
from app import db
from app.models.user import User

haircut_bp = Blueprint('haircut', __name__, url_prefix='/haircuts')


@haircut_bp.route('/', methods=['GET'])
@swag_from(get_doc_path('haircut/get_list.yml'))
def get_models():
    try:
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 10, type=int)

        pagination = Haircut.query \
            .filter(Haircut.deleted_at.is_(None)) \
            .order_by(Haircut.choosen_count.desc()) \
            .paginate(page=page, per_page=limit, error_out=False)

        data = transform_data(pagination.items)

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
@swag_from(get_doc_path('haircut/get_detail.yml'))
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
@jwt_required()
@swag_from(get_doc_path('haircut/create.yml'))
def create_model():
    try:
        uid = get_jwt_identity()
        current_user = User.query.get(uid)
        if current_user.role != 'admin':
            return response.unauthorized("Admin access required")
        
        name = request.form.get("name")
        description = request.form.get("description")
        image = request.files.get("image")

        if not name or not description:
            return response.bad_request("Name and description are required")

        if not image or image.filename == "":
            return response.bad_request("Image is required")

        upload_result = upload_image(name, image, "haircut-models")
        if not upload_result:
            return response.bad_request("Image upload failed")
        
        image_url = upload_result["url"]
        image_key = upload_result["key"]

        new_model = Haircut(
            name=name,
            description=description,
            image_url=image_url,
            image_key=image_key
        )

        try:
            db.session.add(new_model)
            db.session.commit()
        except Exception:
            delete_image(image_key)
            raise

        return response.created(
            new_model.to_dict(),
            "Successfully created haircut model"
        )

    except Exception:
        db.session.rollback()
        return response.internal_server_error("Internal server error")


@haircut_bp.route('/<string:model_id>', methods=['PUT'])
@jwt_required()
@swag_from(get_doc_path('haircut/update.yml'))
def update_model(model_id):
    try:
        uid = get_jwt_identity()
        current_user = User.query.get(uid)
        if current_user.role != 'admin':
            return response.unauthorized("Admin access required")
        
        model_data = request.form.to_dict()
        
        haircut_model = Haircut.query.get(model_id)
        if not haircut_model:
            return response.not_found("Haircut model not found")

        name = model_data.get("name", haircut_model.name)
        description = model_data.get("description", haircut_model.description)
        image = request.files.get("image")
        choosen_count = int(haircut_model.choosen_count)

        if image:
            upload_result = upload_image(name, image, "haircut-models")

            if not upload_result:
                return response.bad_request("Image upload failed")

            new_image_url = upload_result["url"]
            new_image_key = upload_result["key"]

            delete_image(haircut_model.image_key)
            haircut_model.image_url = new_image_url
            haircut_model.image_key = new_image_key

        haircut_model.name = name
        haircut_model.description = description
        haircut_model.choosen_count = int(choosen_count)

        db.session.commit()

        return response.ok(
            haircut_model.to_dict(),
            "Successfully updated haircut model"
        )

    except Exception:
        db.session.rollback()
        return response.internal_server_error("Internal server error")
    

@haircut_bp.route('/<string:haircut_id>', methods=['DELETE'])
@jwt_required()
@swag_from(get_doc_path('haircut/delete_soft.yml'))
def delete_haircut(haircut_id):
    try:
        uid = get_jwt_identity()
        current_user = User.query.get(uid)
        if current_user.role != 'admin':
            return response.unauthorized("Admin access required")
        
        haircut = Haircut.query.get(haircut_id)
        if not haircut:
            return response.not_found("Haircut not found")

        haircut.deleted_at = get_wib_time()
        db.session.commit()

        return response.ok({}, "Haircut deleted successfully")

    except Exception:
        db.session.rollback()
        return response.internal_server_error("Internal server error")

@haircut_bp.route('/hard/<string:model_id>', methods=['DELETE'])
@jwt_required()
@swag_from(get_doc_path('haircut/delete_hard.yml'))
def hard_delete_model(model_id):
    try:
        uid = get_jwt_identity()
        current_user = User.query.get(uid)
        if current_user.role != 'admin':
            return response.unauthorized("Admin access required")
        
        haircut_model = Haircut.query.get(model_id)
        if not haircut_model:
            return response.not_found("Haircut model not found")

        delete_image(haircut_model.image_key)
        db.session.delete(haircut_model)
        db.session.commit()

        return response.ok(
            {},
            "Successfully deleted haircut model"
        )

    except Exception as e:
        print(e)
        db.session.rollback()
        return response.internal_server_error("Internal server error")