from flask import Blueprint, request
from flask_jwt_extended import (jwt_required, get_jwt_identity)
from sqlalchemy.orm import joinedload
from flasgger import swag_from
from app.extensions import socketio
from app.models.haircut_transactions import HaircutTransaction
from app.models.user import User
from app.modules import response
from app.modules.transform import transform_data
from app.modules.upload_r2 import upload_image
from app import db

haircut_transaction_bp = Blueprint('haircut_transaction', __name__, url_prefix='/haircut-transactions')

@haircut_transaction_bp.route('/', methods=['GET'])
@jwt_required()
@swag_from('../docs/haircut_transaction/get_list.yml')
def get_haircut_transactions():
    try:
        uid = get_jwt_identity()
        current_user = User.query.get(uid)
        if current_user.role != "admin":
            return response.unauthorized("Admin access required")
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 10, type=int)

        pagination = HaircutTransaction.query \
            .options(joinedload(HaircutTransaction.user), joinedload(HaircutTransaction.haircut)) \
            .order_by(HaircutTransaction.created_at.desc()) \
            .paginate(page=page, per_page=limit, error_out=False)

        data = transform_data(pagination.items, relations={"user": ['name', 'email'], "haircut": ['name', 'image_url']})
        return response.ok({
            "data": data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": pagination.total
            }
        }, "Successfully retrieved haircut transactions")

    except Exception:
        return response.internal_server_error("Internal server error")

@haircut_transaction_bp.route('/<string:transaction_id>', methods=['GET'])
@jwt_required()
@swag_from('../docs/haircut_transaction/get_detail.yml')
def get_haircut_transaction_by_id(transaction_id):
    try:
        haircut_transaction = HaircutTransaction.query \
            .options(joinedload(HaircutTransaction.haircut)) \
            .get(transaction_id)
        if not haircut_transaction:
            return response.not_found("Haircut transaction not found")
        
        data = transform_data([haircut_transaction], relations={"haircut": ['name', 'image_url']})[0]

        return response.ok(
            data,
            "Successfully retrieved haircut transaction"
        )

    except Exception:
        return response.internal_server_error("Internal server error")

@haircut_transaction_bp.route('/user', methods=['GET'])
@jwt_required()
@swag_from('../docs/haircut_transaction/get_user_list.yml')
def get_haircut_transactions_by_user_id():
    try:
        user_id = get_jwt_identity()
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 10, type=int)

        pagination = HaircutTransaction.query \
            .options(joinedload(HaircutTransaction.haircut)) \
            .filter(HaircutTransaction.user_id == user_id) \
            .order_by(HaircutTransaction.created_at.desc()) \
            .paginate(page=page, per_page=limit, error_out=False)

        data = transform_data(pagination.items, relations={"haircut": ['name', 'image_url']})

        return response.ok({
            "data": data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": pagination.total
            }
        }, "Successfully retrieved haircut transactions for user")

    except Exception:
        return response.internal_server_error("Internal server error")

@haircut_transaction_bp.route('/', methods=['POST'])
@jwt_required()
@swag_from('../docs/haircut_transaction/create.yml')
def create_haircut_transaction():
    try:
        user_id = get_jwt_identity()
        
        data = request.get_json()
        if not data:
            return response.bad_request("Request body is empty")

        required_fields = ["haircut_id", "hairwash", "total_price", "reservation_time", "payment_method"]
        if not all(field in data for field in required_fields):
            return response.bad_request("Missing required fields")

        new_transaction = HaircutTransaction(
            user_id=user_id,
            haircut_id=data["haircut_id"],
            hairwash=True if data["hairwash"] == "True" else False,
            reservation_time=data.get("reservation_time"),
            payment_method=data.get("payment_method", "cash"),
            payment_status=data.get("payment_status", "unpaid"),
            total_price=data["total_price"]
        )

        db.session.add(new_transaction)
        db.session.commit()
        
        emit_payload = {
            "id": new_transaction.id,
            "user_id": new_transaction.user_id,
        }
        
        socketio.emit('new_haircut_transaction_created', emit_payload, to='admin_room')

        return response.created(
            new_transaction.to_dict(),
            "Haircut transaction created successfully"
        )
    except Exception as e:
        print(e)
        db.session.rollback()
        return response.internal_server_error("Internal server error")

@haircut_transaction_bp.route('/<string:transaction_id>', methods=['PUT'])
@jwt_required()
@swag_from('../docs/haircut_transaction/update_status.yml')
def update_haircut_transaction_status(transaction_id):
    try:
        haircut_transaction = HaircutTransaction.query.get(transaction_id)
        if not haircut_transaction:
            return response.not_found("Haircut transaction not found")
        
        transaction_data = request.get_json()
        if not transaction_data:
            return response.bad_request("Request body is empty")
        
        haircut_transaction.reservation_status = transaction_data.get("reservation_status", haircut_transaction.reservation_status)
        haircut_transaction.payment_status = transaction_data.get("payment_status", haircut_transaction.payment_status)

        db.session.commit()
        
        if transaction_data.get("reservation_status") == "completed":
            emit_payload = {
                "id": haircut_transaction.id,
                "status": haircut_transaction.reservation_status
            }
            socketio.emit('haircut_transaction_completed', emit_payload, to='admin_room')

        return response.ok(
            haircut_transaction.to_dict(),
            "Haircut transaction updated successfully"
        )

    except Exception:
        db.session.rollback()
        return response.internal_server_error("Internal server error")

@haircut_transaction_bp.route('/receipt/<string:transaction_id>', methods=['POST'])
@jwt_required()
@swag_from('../docs/haircut_transaction/upload_receipt.yml')
def upload_receipt(transaction_id):
    try:
        user_id = get_jwt_identity()
        
        haircut_transaction = HaircutTransaction.query.get(transaction_id)
        if not haircut_transaction:
            return response.not_found("Haircut transaction not found")
        
        if haircut_transaction.user_id != user_id:
            return response.unauthorized("You are not authorized to upload receipt for this transaction")

        file = request.files.get('receipt')
        if not file:
            return response.bad_request("No receipt file provided")
        
        result = upload_image(name=f"receipt-{transaction_id}", file=file, folder="receipts")
        if not result:
            return response.internal_server_error("Failed to upload receipt")
        
        haircut_transaction.receipt_url = result['url']
        haircut_transaction.receipt_key = result['key']
        haircut_transaction.payment_status = "received"
        
        db.session.commit()

        return response.ok(
            haircut_transaction.to_dict(),
            "Receipt uploaded successfully"
        )

    except Exception:
        db.session.rollback()
        return response.internal_server_error("Internal server error")

@haircut_transaction_bp.route('/<string:transaction_id>', methods=['DELETE'])
@jwt_required()
@swag_from('../docs/haircut_transaction/delete.yml')
def delete_haircut_transaction(transaction_id):
    try:
        user_id = get_jwt_identity()
        current_user = User.query.get(user_id)
        if current_user.role != "admin":
            return response.unauthorized("Admin access required")
        
        haircut_transaction = HaircutTransaction.query.get(transaction_id)
        if not haircut_transaction:
            return response.not_found("Haircut transaction not found")

        db.session.delete(haircut_transaction)
        db.session.commit()

        return response.ok(
            {},
            "Haircut transaction deleted successfully"
        )

    except Exception:
        db.session.rollback()
        return response.internal_server_error("Internal server error")