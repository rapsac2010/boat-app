import functools
import os
import uuid
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from boatapp.db import get_db

bp = Blueprint('auth', __name__, url_prefix = '/auth')

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_filename(original_filename):
    _, file_extension = os.path.splitext(secure_filename(original_filename))
    new_filename = f"{uuid.uuid4()}{file_extension}"
    
    return new_filename

@bp.route('/register', methods = ('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_check = request.form['password2']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        registration_code = request.form['registration']
        email = request.form['email']
        fname = None

        if 'file' in request.files:
            profile_file = request.files['file']
            
            # Check if a file is actually uploaded
            if profile_file.filename != '':
                if profile_file and allowed_file(profile_file.filename):
                    fname = generate_filename(profile_file.filename)
                    profile_file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], fname)) #TODO: compress image to acceptable size
                else:
                    error = 'Unauthorized file extension'

        db = get_db()
        error = None

        # Check for registration code validity
        code_row = db.execute(
            "SELECT * FROM register_codes WHERE code = ?",
            (registration_code,)
        ).fetchone()

        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'
        elif password != password_check:
            error = 'Passwords do not match'

        if code_row is None:
            error = 'Invalid registration code'
        elif code_row['current_uses'] >= code_row['max_uses']:
            error = 'Registration code has reached its maximum uses'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password, first_name, last_name, email, registration_code, profile_fname) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                    (username, generate_password_hash(password), first_name, last_name, email, registration_code, fname)
                )
                db.commit()

                db.execute(
                    "UPDATE register_codes SET current_uses = current_uses + 1 WHERE code = ?",
                    (registration_code,)
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered"
            else:
                return redirect(url_for('auth.login'))
        
        flash(error)
    return render_template('auth/register.html')

@bp.route('/login', methods = ('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        
        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    return wrapped_view