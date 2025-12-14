from flask import Blueprint, request
from app.models.haircut import HaircutModels
from app.modules import response
from app.modules.transform import transform
from app.modules.upload_r2 import delete_image, upload_image

haircut_bp = Blueprint('haircut', __name__, url_prefix='/haircuts')

@haircut_bp.route('/', methods=['GET'])
def get_models():
    try:
        haircut_models = HaircutModels.query.order_by(HaircutModels.choosen_count.desc()).all()
        data = transform(haircut_models)
        return response.ok(data, "Successfully retrieved haircut models")
    except Exception as e:
        return response.internal_server_error(str(e))

@haircut_bp.route('/<int:model_id>', methods=['GET'])
def get_model_by_id(model_id):
    try:
        haircut_model = HaircutModels.query.get(model_id)
        if not haircut_model:
            return response.not_found("Haircut model not found")
        data = haircut_model.to_dict()
        return response.ok(data, "Successfully retrieved haircut model")
    except Exception as e:
        return response.internal_server_error(str(e))

@haircut_bp.route('/', methods=['POST'])
def create_model():
    try:
        model_data = request.get_json()
        res = upload_image(model_data.get("name"), "haircut-models")
        if res == None or res[1] != 200:
            return response.bad_request("Image upload failed")
        
        new_model = HaircutModels(**model_data, image_url=res[0]['url'])
        new_model.insert()
        data = new_model.to_dict()
        return response.created(data, "Successfully created haircut model")
    except Exception as e:
        return response.internal_server_error(str(e))

@haircut_bp.route('/<int:model_id>', methods=['PUT'])
def update_model(model_id):
    try:
        model_data = request.get_json()
        if not model_data:
            return response.bad_request("Request body is empty")

        haircut_model = HaircutModels.query.get(model_id)
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

            delete_image(haircut_model.image_url)
            haircut_model.image_url = upload_result[0]

        for field in allowed_fields:
            if field in model_data:
                setattr(haircut_model, field, model_data[field])

        haircut_model.update()
        return response.ok(
            haircut_model.to_dict(),
            "Successfully updated haircut model"
        )

    except Exception as e:
        return response.internal_server_error(str(e))
