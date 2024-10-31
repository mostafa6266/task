from flask import Blueprint, request, jsonify
from ..models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from ..extensions import db
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)

# Register a new user
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Check if the username or email is already taken
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already registered'}), 400

    # Hash the password using a more secure method
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')

    # Create a new user
    new_user = User(username=data['username'], email=data['email'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    # Create a JWT token for immediate login
    access_token = create_access_token(identity=new_user.id, expires_delta=timedelta(minutes=30))

    return jsonify({
        'message': 'User registered successfully',
        'access_token': access_token
    }), 201

# User login
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Find the user by username
    user = User.query.filter_by(username=data['username']).first()

    # Verify the password
    if user and check_password_hash(user.password, data['password']):
        # Create a JWT token after successful login
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(minutes=30))
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token
        })
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

# Password reset
@auth_bp.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()

    # Find the user by email
    user = User.query.filter_by(email=data['email']).first()

    if not user:
        return jsonify({'message': 'Invalid email address'}), 400

    # Update the password after verification
    hashed_password = generate_password_hash(data['password'], method='sha256')
    user.password = hashed_password
    db.session.commit()

    # Create a new JWT token after password reset
    access_token = create_access_token(identity=user.id, expires_delta=timedelta(minutes=30))

    return jsonify({'message': 'Password has been updated successfully', 'access_token': access_token}), 200
