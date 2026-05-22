from flask import Flask, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# Setup Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# Define database path and ensure the directory exists
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_FOLDER = os.path.join(BASE_DIR, 'database')
DB_PATH = os.path.join(DB_FOLDER, 'parking.db')

os.makedirs(DB_FOLDER, exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import db from models and initialize with app
from models import db
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

# Import and register blueprints
from controllers.auth import auth_bp as auth_blueprint
from controllers.admin import admin_bp as admin_blueprint
from controllers.user import user_bp as user_blueprint

app.register_blueprint(auth_blueprint)
app.register_blueprint(admin_blueprint, url_prefix='/admin')
app.register_blueprint(user_blueprint, url_prefix='/user')

# Import User model for login manager
from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Default route
@app.route('/')
def home():
    return redirect(url_for('auth.login'))

# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

