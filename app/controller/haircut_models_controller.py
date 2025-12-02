from app.model.haircut_models import HaircutModels
from app.modules import response
from app.modules.transform import transform

def get_models():
    try:
        haircut_models = HaircutModels.query.all()
        data = transform(haircut_models)
        return response.ok(data, "Successfully retrieved haircut models")
    except Exception as e:
        return response.internal_server_error(str(e))

def get_model_by_id(model_id):
    try:
        haircut_model = HaircutModels.query.get(model_id)
        if not haircut_model:
            return response.not_found("Haircut model not found")
        data = haircut_model.to_dict()
        return response.ok(data, "Successfully retrieved haircut model")
    except Exception as e:
        return response.internal_server_error(str(e))

def create_model(model_data):
    try:
        new_model = HaircutModels(**model_data)
        new_model.save()
        data = new_model.to_dict()
        return response.created(data, "Successfully created haircut model")
    except Exception as e:
        return response.internal_server_error(str(e))