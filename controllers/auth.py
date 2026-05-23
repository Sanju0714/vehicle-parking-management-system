from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, User
from werkzeug.security import check_password_hash, generate_password_hash

auth_bp = Blueprint('auth', __name__)

# Hardcoded Admin Credentials
ADMIN_EMAIL = 'admin1051@gmail.com'
ADMIN_PASSWORD = 'admin@1051'

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Admin login check
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['username'] = 'Admin'
            session['role'] = 'admin'
            return redirect(url_for('admin.dashboard_admin'))

        # Check for registered user
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['username'] = user.full_name
            session['user_id'] = user.id
            session['role'] = 'user'
            return redirect(url_for('user.user_dashboard'))

        flash('Invalid credentials. Please try again.', 'danger')
        return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        address = request.form.get('address')
        pin_code = request.form.get('pin_code')
        phone = request.form.get('phone')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please login.', 'warning')
            return redirect(url_for('auth.login'))

        new_user = User(
            full_name=full_name,
            email=email,
            password=generate_password_hash(password),
            address=address,
            pin_code=pin_code,
            phone=phone,
            role='user'
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

