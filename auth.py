from flask import Blueprint, render_template, request, redirect, flash, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from model import db, User

auth = Blueprint('auth', __name__)

# Registration route
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash('Email already registered.', 'error')
            return redirect(url_for('auth.register'))
        
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')  # ✅ Recommended
        new_user = User(email=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


# Login route
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Welcome back!', 'success')
            return redirect(url_for('tasks.dashboard'))
        else:
            flash('Invalid email or password.', 'error')
            return redirect(url_for('auth.login'))

    return render_template('login.html')


# Logout route
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
