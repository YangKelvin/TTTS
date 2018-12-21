import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort

from TTTS.db import get_db

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

# test
# register
@bp.route('/init', methods=('GET', 'POST'))
def init():
    db = get_db()
    db.execute(
        'INSERT INTO ACCOUNT (Account, Password, PermissionID, UserName, IdentificationNumber, Gender, CellphoneNumber, Email) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        ('105590045', generate_password_hash('123'), '1', 'kelvin', 'N123456789', 'M', '0975107900', 't105590045@ntut.org.tw')
    )
    db.execute(
        'INSERT INTO ACCOUNT (Account, Password, PermissionID, UserName, IdentificationNumber, Gender, CellphoneNumber, Email) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        ('105590023', generate_password_hash('234'), '2', 'james', 'N123098765', 'M', '0978700387', 't105590023@ntut.org.tw')
    )
    db.execute(
        'INSERT INTO ACCOUNT (Account, Password, PermissionID, UserName, IdentificationNumber, Gender, CellphoneNumber, Email) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        ('105590021', generate_password_hash('345'), '2', 'kelvin', 'N123098764', 'M', '0912345678', 't105590021@ntut.org.tw')
    )
    db.execute(
        'INSERT INTO ACCOUNT (Account, Password, PermissionID, UserName, IdentificationNumber, Gender, CellphoneNumber, Email) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        ('105590014', generate_password_hash('456'), '3', 'kelvin', 'N123098765', 'M', '0987654321', 't105590014@ntut.org.tw')
    )
    db.execute(
        'INSERT INTO ACCOUNT (Account, Password, PermissionID, UserName, IdentificationNumber, Gender, CellphoneNumber, Email) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        ('105590000', generate_password_hash('567'), '3', 'kelvin', 'N000000000', 'M', '0900000000', 't105590000@ntut.org.tw')
    )
    db.commit()
    return redirect(url_for('user.login'))

def get_shoppingcart(GoodsID, check_author=True):
    post = get_db().execute(
        'SELECT GoodsID, GoodsName, GoodsType, Price, StockQuantity, Introduction, ImageName, CountryOfOrigin'
        ' FROM GOODS'
        ' WHERE GoodsID = ?',
        (GoodsID,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    return post

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

@bp.route('/shoppingCart', methods=('GET', 'POST'))
def shoppingcart():
    user = g.user
    db = get_db()
    myShoppingcart = db.execute(
        'Select B.Account, C.GoodsName, A.Ammount '
        'FROM SHOPPINGCART AS A, ACCOUNT AS B, GOODS AS C '
        'WHERE (A.AccountID=B.AccountID) and (A.GoodsID = C.GoodsID) and '
        'A.AccountID = ?',
        (user['AccountID'],)
    ).fetchall()
    return render_template('user/shoppingcart.html', shoppingcart=myShoppingcart)

# 待修改
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM ACCOUNT WHERE AccountID = ?', (user_id,)
        ).fetchone()

# 待修改
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# 未測試
def get_user(uid):
    db = get_db()
    user = db.execute(
        'SELECT * FROM ACCOUNT AS A'
        ' WHERE A.AccountID = ?',
        (uid,)
    ).fetchone()

    if user is None:
        abort(404, "User id {0} doesn't exist.".format(id))

    return user

@bp.route('/userList', methods=('GET', 'POST'))
def userList():
    db = get_db()
    user = db.execute('SELECT * FROM ACCOUNT')
    return render_template('user/userList.html', user = user)

# 修改帳號資料
@bp.route('/<int:user_id>/editUser', methods=('GET', 'POST'))
def edit(user_id):
    user = get_user(user_id)

    if request.method == 'POST':
        error = None
        db = get_db()
        account = request.form['account']
        password = request.form['password']
        permission = request.form['permission']
        name = request.form['username']
        identificationNumber = request.form['identification']
        gender = request.form['gender']
        cellphone = request.form['cellphone']
        email = request.form['email']

        if account is None:
            error = 'Account is required.'
        elif password is None:
            error = 'Password is required.'
        elif (not permission.isdigit()) or (int(permission) not in [1, 2, 3]):
            error = 'Permission error.'
        elif db.execute(
            'SELECT AccountID FROM ACCOUNT WHERE Account = ?', (account,)
        ).fetchone()['AccountID'] is not user['AccountID']:
            error = 'Account {} is already registered.'.format(account)

        if error is None:
            db.execute('UPDATE ACCOUNT SET Account = ?, Password = ?, PermissionID = ?, UserName = ?, IdentificationNumber = ?,'
            ' Gender = ?, CellphoneNumber = ?, Email = ?'
            ' WHERE AccountID = ?', 
            (account, generate_password_hash(password), permission, name, identificationNumber, gender, cellphone, email, user_id))
            db.commit()
            # 待修改
            return redirect(url_for('user.userList'))

        flash(error)
    
    # 待修改
    return render_template('user/editUseInfo.html', user=user)

# admin創建帳號
@bp.route('/create', methods=('GET', 'POST'))
def create():
    if g.user['PermissionID'] is not 1:
        return redirect(url_for('user.login'))

    if request.method == 'POST':
        account = request.form['account']
        password = request.form['password']
        permission = request.form['permission']
        username = request.form['username']
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
        elif (not permission.isdigit()) or (int(permission) not in [1, 2, 3]):
            error = 'Permission error.'
        elif db.execute(
            'SELECT AccountID FROM ACCOUNT WHERE Account = ?', (account,)
        ).fetchone() is not None:
            error = 'Account {} is already registered.'.format(account)

        # 待修改
        if error is None:
            db.execute(
                'INSERT INTO ACCOUNT (Account, Password, PermissionID, UserName, IdentificationNumber, Gender, CellphoneNumber, Email) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (account, generate_password_hash(password), permission, username, id, gender, cellphone, email)
            )
            db.commit()
            # 待修改
            return redirect(url_for('user.login'))

        flash(error)
    # 待修改
    return render_template('user/create.html')