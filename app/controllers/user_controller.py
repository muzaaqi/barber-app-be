from flask import Blueprint, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app.models.user import User
from app.modules import response
from app import db

user_bp = Blueprint("user", __name__, url_prefix="/user")


@user_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if User.query.filter_by(email=email).first():
        return response.bad_request("Email already exists")

    new_user = User(
        name=name,
        email=email,
        password=generate_password_hash(password)
    )
    db.session.add(new_user)
    db.session.commit()

    return response.created({"email": email}, "Register success")


@user_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return response.unauthorized("Invalid email or password")

    token = create_access_token(identity=str(user.id))

    return response.ok({"token": token}, "Login success")


@user_bp.route("/me", methods=["GET"])
@jwt_required()
def get_profile():
    uid = get_jwt_identity()
    user = User.query.get(uid)

    if not user:
        return response.not_found("User not found")

    return response.ok({
        "id": user.id,
        "email": user.email,
        "name": user.name
    }, "")
