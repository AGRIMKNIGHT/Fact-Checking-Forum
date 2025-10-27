from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db, Query, Response, User
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

query_bp = Blueprint('query_bp', __name__)


# Safe JWT identity helper
def get_current_username():
    identity = get_jwt_identity()
    if isinstance(identity, dict):
        return identity.get("username")
    return identity

# Helper functions for role-based access
def is_student():
    claims = get_jwt()
    return claims.get('role') == 'student'

def is_faculty():
    claims = get_jwt()
    return claims.get('role') == 'faculty'



# Get all queries (for all users)
@query_bp.route('/', methods=['GET'])
@jwt_required(optional=True)
def get_all_queries():
    queries = db.session.query(Query).all()
    data = []
    for q in queries:
        responses = [
            {
                'id': r.id,
                'content': r.content,
                'faculty_id': r.faculty_id,
                'created_at': r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else None,
            }
            for r in q.responses
        ]
        data.append({
            'id': q.id,
            'title': q.title,
            'description': q.description,
            'student_id': q.student_id,
            'created_at': q.created_at.strftime("%Y-%m-%d %H:%M:%S") if q.created_at else None,
            'answered': q.answered,
            'responses': responses
        })
    return jsonify(data), 200


# Admin view: Get all queries with responses and allow deletion
@query_bp.route('/admin/queries', methods=['GET'])
@jwt_required()
def admin_view_queries():
    try:
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({'error': 'Access forbidden: Admin only'}), 403

        queries = db.session.query(Query).all()
        data = []
        for q in queries:
            responses = [
                {
                    'id': r.id,
                    'content': r.content,
                    'faculty_id': r.faculty_id,
                    'created_at': r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else None,
                }
                for r in q.responses
            ]
            data.append({
                'id': q.id,
                'title': q.title,
                'description': q.description,
                'student_id': q.student_id,
                'created_at': q.created_at.strftime("%Y-%m-%d %H:%M:%S") if q.created_at else None,
                'answered': q.answered,
                'responses': responses
            })
        return jsonify(data), 200
    except Exception as e:
        print("❌ Error loading admin queries:", str(e))
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


# Get logged-in student's queries
@query_bp.route('/my', methods=['GET'])
@jwt_required()
def get_my_queries():
    if not is_student():
        return jsonify({'error': 'Access forbidden: Students only'}), 403

    current_username = get_current_username()
    student = db.session.query(User).filter_by(username=current_username).first()
    if not student:
        return jsonify({'error': 'User not found'}), 404

    my_queries = db.session.query(Query).filter_by(student_id=student.id).all()
    result = []
    for q in my_queries:
        responses = [
            {
                'id': r.id,
                'content': r.content,
                'faculty_id': r.faculty_id,
                'created_at': r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else None,
            }
            for r in q.responses
        ]
        result.append({
            'id': q.id,
            'title': q.title,
            'description': q.description,
            'created_at': q.created_at.strftime("%Y-%m-%d %H:%M:%S") if q.created_at else None,
            'answered': q.answered,
            'responses': responses
        })
    return jsonify(result), 200


# Post a new query (Students only)
@query_bp.route('/new', methods=['POST'])
@jwt_required()
def create_query():
    try:
        if not is_student():
            return jsonify({'error': 'Access forbidden: Students only'}), 403

        data = request.get_json()
        title = data.get('title')
        description = data.get('description')

        if not title or not description:
            return jsonify({'error': 'Title and description are required'}), 400

        current_username = get_current_username()
        student = db.session.query(User).filter_by(username=current_username).first()
        if not student:
            return jsonify({'error': 'User not found'}), 404

        new_query = Query(title=title, description=description, student_id=student.id, answered=False, created_at=datetime.now(timezone.utc))
        db.session.add(new_query)
        db.session.commit()

        return jsonify({'message': 'Query posted successfully', 'query_id': new_query.id}), 201

    except Exception as e:
        print("❌ Error posting query:", str(e))
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

# Faculty respond to a query (Allow multiple responses)
@query_bp.route('/respond/<int:query_id>', methods=['POST'])
@jwt_required()
def respond_to_query(query_id):
    try:
        if not is_faculty():
            return jsonify({'error': 'Access forbidden: Faculty only'}), 403

        query = db.session.query(Query).get(query_id)
        if not query:
            return jsonify({'error': 'Query not found'}), 404

        data = request.get_json()
        content = data.get('content')

        if not content:
            return jsonify({'error': 'Response content is required'}), 400

        current_username = get_current_username()
        faculty = db.session.query(User).filter_by(username=current_username).first()
        if not faculty:
            return jsonify({'error': 'User not found'}), 404

        # Allow multiple responses; just mark answered once
        new_response = Response(content=content, query_id=query.id, faculty_id=faculty.id, created_at=datetime.now(timezone.utc))
        if not query.answered:
            query.answered = True

        db.session.add(new_response)
        db.session.commit()

        return jsonify({'message': 'Response added successfully', 'response_id': new_response.id}), 201

    except Exception as e:
        print("❌ Error adding faculty response:", str(e))
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


# Get a specific query with its responses
@query_bp.route('/<int:query_id>', methods=['GET'])
@jwt_required(optional=True)
def get_query(query_id):
    query = db.session.query(Query).get(query_id)
    if not query:
        return jsonify({'error': 'Query not found'}), 404

    responses = [
        {
            'id': r.id,
            'content': r.content,
            'faculty_id': r.faculty_id,
            'created_at': r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else None,
        }
        for r in query.responses
    ]

    result = {
        'id': query.id,
        'title': query.title,
        'description': query.description,
        'student_id': query.student_id,
        'created_at': query.created_at.strftime("%Y-%m-%d %H:%M:%S") if query.created_at else None,
        'answered': query.answered,
        'responses': responses
    }
    return jsonify(result), 200


# Get logged-in faculty's responses
@query_bp.route('/responses/my', methods=['GET'])
@jwt_required()
def get_my_responses():
    try:
        claims = get_jwt() or {}
        role = claims.get("role", None)

        if role != "faculty":
            return jsonify({'error': 'Access forbidden: Faculty only'}), 403

        current_username = get_current_username()
        faculty = db.session.query(User).filter_by(username=current_username).first()
        if not faculty:
            return jsonify({'error': 'User not found'}), 404

        # ✅ Fixed query syntax for SQLAlchemy
        responses = db.session.query(Response).filter(Response.faculty_id == faculty.id).all()

        result = []
        for r in responses:
            query = db.session.query(Query).get(r.query_id)
            result.append({
                'response_id': r.id,
                'content': r.content,
                'query_title': query.title if query else "Unknown Query",
                'query_description': query.description if query else "No description",
                'created_at': r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else None,
            })
        return jsonify(result), 200

    except Exception as e:
        print("❌ Error loading faculty responses:", str(e))
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


# Get system statistics for Admin Dashboard
@query_bp.route('/admin/stats', methods=['GET'])
@jwt_required()
def get_admin_stats():
    try:
        claims = get_jwt() or {}
        role = claims.get("role")
        if role != "admin":
            return jsonify({'error': 'Access forbidden: Admin only'}), 403

        users = db.session.query(User).all()
        queries = db.session.query(Query).all()
        responses = db.session.query(Response).all()

        student_count = sum(1 for u in users if u.role == 'student')
        faculty_count = sum(1 for u in users if u.role == 'faculty')
        admin_count = sum(1 for u in users if u.role == 'admin')

        # Safe count of answered queries
        query_ids_with_responses = {r.query_id for r in responses}
        answered_queries = len(query_ids_with_responses)
        unanswered_queries = len(queries) - answered_queries

        stats = {
            'total_users': len(users),
            'students': student_count,
            'faculty': faculty_count,
            'admins': admin_count,
            'total_queries': len(queries),
            'answered_queries': answered_queries,
            'unanswered_queries': unanswered_queries,
            'total_responses': len(responses)
        }

        return jsonify(stats), 200

    except Exception as e:
        print("❌ Error loading admin stats:", str(e))
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500



# Delete a query (Admin only)
@query_bp.route('/admin/delete_query/<int:query_id>', methods=['DELETE'])
@jwt_required()
def delete_query(query_id):
    try:
        claims = get_jwt() or {}
        if claims.get("role") != "admin":
            return jsonify({'error': 'Access forbidden: Admin only'}), 403

        query = db.session.query(Query).get(query_id)
        if not query:
            return jsonify({'error': 'Query not found'}), 404

        # Delete all responses linked to this query first
        responses = db.session.query(Response).filter_by(query_id=query.id).all()
        for r in responses:
            db.session.delete(r)

        # Then delete the query itself
        db.session.delete(query)
        db.session.commit()

        return jsonify({'message': f'Query {query_id} and all associated responses deleted successfully'}), 200
    except Exception as e:
        print("❌ Error deleting query:", str(e))
        db.session.rollback()
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


# Delete a response (Admin only)
@query_bp.route('/admin/delete_response/<int:response_id>', methods=['DELETE'])
@jwt_required()
def delete_response(response_id):
    try:
        claims = get_jwt() or {}
        if claims.get("role") != "admin":
            return jsonify({'error': 'Access forbidden: Admin only'}), 403

        response = db.session.query(Response).get(response_id)
        if not response:
            return jsonify({'error': 'Response not found'}), 404

        db.session.delete(response)
        db.session.commit()
        return jsonify({'message': f'Response {response_id} deleted successfully'}), 200
    except Exception as e:
        print("❌ Error deleting response:", str(e))
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


# Get all users (Admin only)
@query_bp.route('/admin/users', methods=['GET'])
@jwt_required()
def get_all_users():
    try:
        claims = get_jwt() or {}
        if claims.get("role") != "admin":
            return jsonify({'error': 'Access forbidden: Admin only'}), 403

        users = db.session.query(User).all()
        data = [
            {
                'id': u.id,
                'username': u.username,
                'role': u.role,
                'active': u.active
            }
            for u in users
        ]
        return jsonify(data), 200
    except Exception as e:
        print("❌ Error loading users:", str(e))
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500



# Suspend user (Admin only)
@query_bp.route('/admin/suspend_user/<int:user_id>', methods=['PATCH'])
@jwt_required()
def suspend_user(user_id):
    try:
        claims = get_jwt() or {}
        if claims.get("role") != "admin":
            return jsonify({'error': 'Access forbidden: Admin only'}), 403

        user = db.session.query(User).get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        user.active = False
        db.session.commit()
        return jsonify({'message': f'User {user.username} suspended successfully'}), 200
    except Exception as e:
        print("❌ Error suspending user:", str(e))
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


# Unsuspend user (Admin only)
@query_bp.route('/admin/unsuspend_user/<int:user_id>', methods=['PATCH'])
@jwt_required()
def unsuspend_user(user_id):
    try:
        claims = get_jwt() or {}
        if claims.get("role") != "admin":
            return jsonify({'error': 'Access forbidden: Admin only'}), 403

        user = db.session.query(User).get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        user.active = True
        db.session.commit()
        return jsonify({'message': f'User {user.username} unsuspended successfully'}), 200
    except Exception as e:
        print("❌ Error unsuspending user:", str(e))
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


# Delete user (Admin only)
@query_bp.route('/admin/delete_user/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    try:
        claims = get_jwt() or {}
        if claims.get("role") != "admin":
            return jsonify({'error': 'Access forbidden: Admin only'}), 403

        user = db.session.query(User).get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': f'User {user.username} deleted successfully'}), 200
    except Exception as e:
        print("❌ Error deleting user:", str(e))
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500



# Add new user (Admin only) — can add Student, Faculty, or Admin
@query_bp.route('/admin/add_user', methods=['POST'])
@jwt_required()
def add_user():
    try:
        claims = get_jwt() or {}
        if claims.get("role") != "admin":
            return jsonify({'error': 'Access forbidden: Admin only'}), 403

        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', '').lower().strip()

        if not username or not password or not role:
            return jsonify({'error': 'Username, password, and role are required'}), 400

        if role not in ['student', 'faculty', 'admin']:
            return jsonify({'error': 'Invalid role. Must be student, faculty, or admin'}), 400

        if db.session.query(User).filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400

        password_hash = generate_password_hash(password)
        new_user = User(username=username, password_hash=password_hash, role=role, active=True)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': f'{role.capitalize()} added successfully', 'user': {
            'id': new_user.id,
            'username': new_user.username,
            'role': new_user.role
        }}), 201

    except Exception as e:
        print("❌ Error adding user:", str(e))
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
