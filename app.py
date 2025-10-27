from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db
from routes.auth_routes import auth_bp
from routes.query_routes import query_bp
from routes.admin_routes import admin_bp
from sqlalchemy import text

# Initialize Flask App
app = Flask(__name__)

# ------------------------------
# App Configuration
# ------------------------------
class Config:
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'postgresql://gokul:yourpassword@localhost/fact_forum'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'your_jwt_secret_key'

app.config.from_object(Config)

# ------------------------------
# Initialize Extensions
# ------------------------------
CORS(app)
db.init_app(app)
jwt = JWTManager(app)

# ------------------------------
# Register Blueprints
# ------------------------------
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(query_bp, url_prefix="/api/queries")
app.register_blueprint(admin_bp, url_prefix="/api/admin")

# ------------------------------
# Routes
# ------------------------------
@app.route('/')
def home():
    return "✅ Fact Checking Forum backend is running!"

@app.route('/pgtest')
def test_pg():
    try:
        with db.engine.connect() as connection:
            version = connection.execute(text("SELECT version();")).scalar()
            return f"✅ PostgreSQL database connection is working!<br><br>Version: {version}"
    except Exception as e:
        return f"❌ PostgreSQL database connection error: {str(e)}"

# ------------------------------
# Error Handler Example
# ------------------------------
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

# ------------------------------
# Run App
# ------------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5051)