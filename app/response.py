from flask import jsonify, make_response

def ok(data, message):
    res = {
        'status': 'success',
        'message': message,
        'data': data
    }
    return make_response(jsonify(res), 200)

def created(data, message):
    res = {
        'status': 'success',
        'message': message,
        'data': data
    }
    return make_response(jsonify(res), 201)

def bad_request(message):
    res = {
        'status': 'fail',
        'message': message
    }
    return make_response(jsonify(res), 400)

def not_found(message):
    res = {
        'status': 'fail',
        'message': message
    }
    return make_response(jsonify(res), 404)

def internal_server_error(message):
    res = {
        'status': 'error',
        'message': message
    }
    return make_response(jsonify(res), 500)

def unauthorized(message):
    res = {
        'status': 'fail',
        'message': message
    }
    return make_response(jsonify(res), 401)

def forbidden(message):
    res = {
        'status': 'fail',
        'message': message
    }
    return make_response(jsonify(res), 403)

def conflict(message):
    res = {
        'status': 'fail',
        'message': message
    }
    return make_response(jsonify(res), 409)