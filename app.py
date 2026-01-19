from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect

import os
import pymysql
from datetime import datetime

# Configure PyMySQL to be used with SQLAlchemy
pymysql.install_as_MySQLdb()

# Initialize Flask app
app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')

# MySQL Database Configuration
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', '')
db_host = os.environ.get('DB_HOST', 'localhost')
db_name = os.environ.get('DB_NAME', 'university_chatbot')

# MySQL connection string
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Import routes after app initialization to avoid circular imports
from routes import *

# Ensure database tables are created
with app.app_context():
    db.create_all()
    print("Database tables created or verified.")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Import and initialize AI model
        from ai_model import initialize_model
        print("Training AI model...")
        initialize_model()
        print("AI model training complete.")
    app.run(debug=True)
    