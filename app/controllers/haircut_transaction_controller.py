from flask import Blueprint, request
from app.models.haircut_transactions import HaircutTransaction
from app.models.transactions import Transaction
from app.models.haircut import Haircut
from app.modules import response
from app.modules.transform import transform
from app import db

haircut_transaction_bp = Blueprint('haircut_transaction', __name__, url_prefix='/haircut-transactions')

@haircut_transaction_bp.route('/', methods=['GET'])
def get_haircut_transactions():
    try:
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 10, type=int)

        pagination = HaircutTransaction.query \
            .order_by(HaircutTransaction.created_at.desc()) \
            .paginate(page=page, per_page=limit, error_out=False)

        data = transform(pagination.items)

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
def get_haircut_transaction_by_id(transaction_id):
    try:
        haircut_transaction = HaircutTransaction.query.get(transaction_id)
        if not haircut_transaction:
            return response.not_found("Haircut transaction not found")

        return response.ok(
            haircut_transaction.to_dict(),
            "Successfully retrieved haircut transaction"
        )

    except Exception:
        return response.internal_server_error("Internal server error")

@haircut_transaction_bp.route('/', methods=['GET'])
def get_haircut_transactions_by_user_id():
    try:
        user_id = request.args.get("user_id", type=str)
        if not user_id:
            return response.bad_request("User ID is required")

        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 10, type=int)

        pagination = HaircutTransaction.query \
            .join(Transaction, HaircutTransaction.transaction_id == Transaction.id) \
            .filter(Transaction.user_id == user_id) \
            .order_by(HaircutTransaction.created_at.desc()) \
            .paginate(page=page, per_page=limit, error_out=False)

        data = transform(pagination.items)

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
def create_haircut_transaction():
    try:
        data = request.get_json()
        if not data:
            return response.bad_request("Request body is empty")

        required_fields = ["user_id", "haircut_id", "hairwash", "total_price"]
        if not all(field in data for field in required_fields):
            return response.bad_request("Missing required fields")

        new_transaction = HaircutTransaction(
            user_id=data["user_id"],
            haircut_id=data["haircut_id"],
            hairwash=data["hairwash"],
            total_price=data["total_price"]
        )
        
        new_transaction = Transaction(
            user_id=data["user_id"],
            transaction_id=new_transaction.id,
        )
        
        Haircut.choosen_count += 1

        db.session.add(new_transaction)
        db.session.commit()

        return response.created(
            new_transaction.to_dict(),
            "Haircut transaction created successfully"
        )
    except Exception:
        db.session.rollback()
        return response.internal_server_error("Internal server error")

@haircut_transaction_bp.route('/<string:transaction_id>', methods=['DELETE'])
def delete_haircut_transaction(transaction_id):
    try:
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

@haircut_transaction_bp.route('/<string:transaction_id>', methods=['PUT'])
def update_haircut_transaction_status(transaction_id):
    try:
        haircut_transaction = HaircutTransaction.query.get(transaction_id)
        if not haircut_transaction:
            return response.not_found("Haircut transaction not found")

        db.session.commit()

        return response.ok(
            haircut_transaction.to_dict(),
            "Haircut transaction updated successfully"
        )

    except Exception:
        db.session.rollback()
        return response.internal_server_error("Internal server error")