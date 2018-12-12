import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

# 待修改
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('user.login'))

        return view(**kwargs)

    return wrapped_view
    
# blueprint name='user'
bp = Blueprint('user', __name__, url_prefix='/user')

# register
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        account = request.form['account']
        password = request.form['password']
        id = request.form['identification']
        gender = request.form['gender']
        cellphone = request.form['cellphone']
        email = request.form['email']
        db = get_db()
        error = None

        if not account:
            error = 'Account is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT AccountID FROM ACCOUNT WHERE Account = ?', (account,)
        ).fetchone() is not None:
            error = 'Account {} is already registered.'.format(account)

        # 待修改
        if error is None:
            db.execute(
                'INSERT INTO ACCOUNT (Account, Password, PermissionID, UserName, IdentificationNumber, Gender, CellphoneNumber, Email) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (account, generate_password_hash(password), 3, username, id, gender, cellphone, email)
            )
            db.commit()
            return redirect(url_for('user.login'))

        flash(error)

    return render_template('user/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        account = request.form['account']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM ACCOUNT WHERE Account = ?', (account,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['AccountID']
            return redirect(url_for('index'))

        flash(error)

    return render_template('user/login.html')

# 待修改
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

# 待修改
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))