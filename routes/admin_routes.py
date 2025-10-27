from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db, User, Query, Response

admin_bp = Blueprint('admin_bp', __name__)

# --------------------------
# 🔐 Role Check Helper
# --------------------------
def is_admin():
    claims = get_jwt()
    return claims.get('role') == 'admin'

# --------------------------
# 📊 Admin Dashboard Overview
# --------------------------
@admin_bp.route('/overview', methods=['GET'])
@jwt_required()
def admin_overview():
    if not is_admin():
        return jsonify({'error': 'Access forbidden: Admins only'}), 403

    user_count = User.query.count()
    query_count = Query.query.count()
    response_count = Response.query.count()
    answered_count = Query.query.filter_by(answered=True).count()
    pending_count = query_count - answered_count

    stats = {
        'total_users': user_count,
        'total_queries': query_count,
        'total_responses': response_count,
        'answered_queries': answered_count,
        'pending_queries': pending_count
    }
    return jsonify(stats), 200

# --------------------------
# 👥 View All Users
# --------------------------
@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def view_users():
    if not is_admin():
        return jsonify({'error': 'Access forbidden: Admins only'}), 403

    users = User.query.all()
    data = [{'id': u.id, 'username': u.username, 'role': u.role} for u in users]
    return jsonify(data), 200

# --------------------------
# 🔄 Promote or Demote User
# --------------------------
@admin_bp.route('/user/<int:user_id>/role', methods=['PUT'])
@jwt_required()
def update_user_role(user_id):
    if not is_admin():
        return jsonify({'error': 'Access forbidden: Admins only'}), 403

    data = request.get_json()
    new_role = data.get('role')

    if new_role not in ['student', 'faculty', 'admin']:
        return jsonify({'error': 'Invalid role specified'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user.role = new_role
    db.session.commit()
    return jsonify({'message': f"User '{user.username}' role updated to {new_role}"}), 200

# --------------------------
# ❌ Delete User
# --------------------------
@admin_bp.route('/user/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    if not is_admin():
        return jsonify({'error': 'Access forbidden: Admins only'}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': f"User '{user.username}' deleted successfully"}), 200