from flask import Blueprint, request, jsonify, url_for
from ..models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from ..extensions import db, mail
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)

s = URLSafeTimedSerializer('mysecretkey')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], email=data['email'], password=hashed_password, is_active=False)
    db.session.add(new_user)
    db.session.commit()

    token = s.dumps(data['email'], salt='email-confirm')
    link = url_for('auth.confirm_email', token=token, _external=True)

    msg = Message('Confirm Your Email', recipients=[data['email']])
    msg.body = f'Please click the link to confirm your email (Valid for 10 minutes): {link}'
    mail.send(msg)

    return jsonify({'message': 'User registered successfully. Please check your email to confirm your account.'})

@auth_bp.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=600)  # 600 ثانية = 10 دقائق
    except SignatureExpired:
        return jsonify({'message': 'The token has expired.'}), 400

    user = User.query.filter_by(email=email).first_or_404()
    
    if not user.is_active:
        user.is_active = True
        db.session.commit()
        return jsonify({'message': 'Email confirmed, your account has been activated!'})
    else:
        return jsonify({'message': 'Account already activated.'}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    
    if not user.is_active:
        return jsonify({'message': 'Please confirm your email first.'}), 400

    if user and check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(minutes=30)) 
        return jsonify({'access_token': access_token})
    return jsonify({'message': 'Invalid credentials'}), 401

@auth_bp.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()

    if not user:
        return jsonify({'message': 'Invalid email address'}), 400

    token = s.dumps(user.email, salt='password-reset')
    link = url_for('auth.reset_password_token', token=token, _external=True)

    msg = Message('Reset Your Password', recipients=[user.email])
    msg.body = f'Please click the link to reset your password (Valid for 10 minutes): {link}'
    mail.send(msg)

    return jsonify({'message': 'A password reset link has been sent to your email address.'})

@auth_bp.route('/reset_password/<token>', methods=['POST'])
def reset_password_token(token):
    try:
        email = s.loads(token, salt='password-reset', max_age=600)  
    except SignatureExpired:
        return jsonify({'message': 'The token has expired.'}), 400

    data = request.get_json()
    user = User.query.filter_by(email=email).first_or_404()

    hashed_password = generate_password_hash(data['password'], method='sha256')
    user.password = hashed_password
    db.session.commit()

    access_token = create_access_token(identity=user.id, expires_delta=timedelta(minutes=30))

    return jsonify({'message': 'Password has been updated successfully.', 'access_token': access_token})
