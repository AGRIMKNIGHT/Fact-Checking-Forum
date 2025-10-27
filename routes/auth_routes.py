from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from models import db, User

auth_bp = Blueprint('auth_bp', __name__)

# ✅ Register a new user
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Validate fields
    if not all(k in data for k in ('username', 'password', 'role')):
        return jsonify({'error': 'Missing fields (username, password, role)'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400

    hashed_pw = generate_password_hash(data['password'])
    role = data['role'].lower().strip()
    if role not in ['student', 'faculty', 'admin']:
        return jsonify({'error': 'Invalid role. Must be student, faculty, or admin.'}), 400
    new_user = User(username=data['username'], password_hash=hashed_pw, role=role)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': f"User '{data['username']}' registered successfully!"}), 201


# ✅ Login existing user
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True)
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    role_raw = data.get('role') or data.get('Role') or None

    # ✅ Frontend fallback: handle when role is not included in JSON (e.g. dropdown value not sent)
    if role_raw is None or role_raw == '':
        return jsonify({'error': 'Role selection missing from frontend request'}), 400

    role = str(role_raw).strip().lower()

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    if role not in ['student', 'faculty', 'admin']:
        return jsonify({'error': f"Invalid role '{role_raw}'. Must be one of: student, faculty, admin."}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Incorrect password'}), 401

    # ✅ Ensure strict role matching
    if user.role.lower() != role:
        return jsonify({'error': f'Role mismatch. Please login as a {user.role}.'}), 403

    if not user.active:
        return jsonify({'error': 'Account suspended. Contact admin.'}), 403

    # ✅ Generate JWT token
    token = create_access_token(identity=user.username, additional_claims={"role": user.role})

    return jsonify({
        'message': f'{user.role.capitalize()} login successful!',
        'token': token,
        'role': user.role
    }), 200


# ✅ Protected route example (for testing)
@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_username = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")
    return jsonify({
        'message': 'Access granted to protected route!',
        'user': current_username,
        'role': role
    })