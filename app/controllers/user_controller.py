from flask import Blueprint, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from flasgger import swag_from
from app.models.user import User
from app.modules import response
from app.modules.swagger_utils import get_doc_path
from app import db

user_bp = Blueprint("user", __name__, url_prefix="/user")


@user_bp.route("/register", methods=["POST"])
@swag_from(get_doc_path('user/register.yml'))
def register():
    try:
        data = request.get_json()
        if not data:
            return response.bad_request("Request body is empty")

        required_fields = ["name", "email", "password"]
        if not all(field in data for field in required_fields):
            return response.bad_request("Missing required fields")

        name = data["name"].strip()
        email = data["email"].strip().lower()
        password = data["password"]

        if len(password) < 6:
            return response.bad_request("Password must be at least 6 characters")

        if User.query.filter_by(email=email).first():
            return response.bad_request("Email already exists")

        new_user = User(
            name=name,
            email=email,
            password=generate_password_hash(password)
        )

        db.session.add(new_user)
        db.session.commit()

        return response.created(
            {
                "id": new_user.id,
                "email": new_user.email,
                "name": new_user.name
            },
            "Register success"
        )

    except Exception:
        db.session.rollback()
        return response.internal_server_error("Internal server error")


@user_bp.route("/login", methods=["POST"])
@swag_from(get_doc_path('user/login.yml'))
def login():
    try:
        data = request.get_json()
        if not data:
            return response.bad_request("Request body is empty")

        required_fields = ["email", "password"]
        if not all(field in data for field in required_fields):
            return response.bad_request("Missing email or password")

        email = data["email"].strip().lower()
        password = data["password"]

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            return response.unauthorized("Invalid email or password")

        access_token = create_access_token(identity=str(user.id))

        return response.ok(
            {"token": access_token},
            "Login success"
        )

    except Exception:
        return response.internal_server_error("Internal server error")


@user_bp.route("/me", methods=["GET"])
@jwt_required()
@swag_from(get_doc_path('user/profile_get.yml'))
def get_profile():
    try:
        uid = get_jwt_identity()
        user = User.query.get(uid)

        if not user:
            return response.not_found("User not found")

        return response.ok(
            {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role
            },
            "Successfully retrieved profile"
        )

    except Exception:
        return response.internal_server_error("Internal server error")

@user_bp.route("/me", methods=["PUT"])
@jwt_required()
@swag_from(get_doc_path('user/profile_update.yml'))
def update_profile():
    try:
        uid = get_jwt_identity()
        user = User.query.get(uid)

        if not user:
            return response.not_found("User not found")

        data = request.get_json()
        if not data:
            return response.bad_request("Request body is empty")

        name = data.get("name", user.name)
        email = data.get("email", user.email).strip().lower()

        if email != user.email and User.query.filter_by(email=email).first():
            return response.bad_request("Email already exists")

        user.name = name
        user.email = email

        db.session.commit()

        return response.ok(
            {
                "id": user.id,
                "email": user.email,
                "name": user.name
            },
            "Profile updated successfully"
        )

    except Exception:
        db.session.rollback()
        return response.internal_server_error("Internal server error")

@user_bp.route("/me/password", methods=["PUT"])
@jwt_required()
@swag_from(get_doc_path('user/password_update.yml'))
def change_password():
    try:
        uid = get_jwt_identity()
        user = User.query.get(uid)

        if not user:
            return response.not_found("User not found")

        data = request.get_json()
        if not data:
            return response.bad_request("Request body is empty")

        required_fields = ["current_password", "new_password"]
        if not all(field in data for field in required_fields):
            return response.bad_request("Missing required fields")

        current_password = data["current_password"]
        new_password = data["new_password"]

        if not check_password_hash(user.password, current_password):
            return response.unauthorized("Current password is incorrect")

        if len(new_password) < 6:
            return response.bad_request("New password must be at least 6 characters")

        user.password = generate_password_hash(new_password)
        db.session.commit()

        return response.ok(
            {},
            "Password changed successfully"
        )

    except Exception:
        db.session.rollback()
        return response.internal_server_error("Internal server error")