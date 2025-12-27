from flask import Blueprint, render_template, request, session, jsonify, redirect, current_app

main_bp = Blueprint('main', __name__)

@main_bp.before_app_request
def secure_docs():
    if request.path.startswith('/apidocs') or request.path.endswith('apispec_1.json'):
        if not session.get('is_docs_authenticated'):
            if request.path.endswith('json'):
                return jsonify({"message": "Unauthorized docs access. Please login at homepage."}), 401
            
            return redirect('/?auth_required=true')

@main_bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@main_bp.route('/api/auth-docs', methods=['POST'])
def auth_docs():
    data = request.get_json()
    password = data.get('password')
    
    correct_password = current_app.config.get('DOCS_PASSWORD')
    
    if password == correct_password:
        session['is_docs_authenticated'] = True
        return jsonify({"success": True})
    
    return jsonify({"success": False, "message": "Invalid Password"}), 401