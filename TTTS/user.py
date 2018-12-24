import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort

from TTTS.db import get_db
from . import functions

# 查看是否登入
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('user.login'))

        return view(**kwargs)

    return wrapped_view
    
# blueprint name='user'
bp = Blueprint('user', __name__, url_prefix='/user')

# 取得某個顧客的shopping cart 中的商品內容和金額
def getShoppingCart(AccountID, check_author=True):
    user = g.user
    myShoppingCart = get_db().execute(
        'Select B.Account, C.GoodsID, C.GoodsName, C.ImageName, C.CountryOfOrigin, C.StockQuantity, C.Price, A.Amount, C.Price*A.Amount AS totalPrice '
        'FROM SHOPPINGCART AS A, ACCOUNT AS B, GOODS AS C '
        'WHERE (A.AccountID=B.AccountID) and (A.GoodsID = C.GoodsID) and '
        'A.AccountID = ?',
        (user['AccountID'],)
    ).fetchall()
    return myShoppingCart

# 取得 user 資訊
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

# login
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

# 查看當前使用者的購物車
@bp.route('/shoppingCart', methods=('GET', 'POST'))
def shoppingcart():
    user = g.user
    myShoppingCart = functions.get_all_shopping_cart_goods(user['AccountID'])
    totalPrice = 0
    for goods in myShoppingCart:
        totalPrice += int(goods['total'])
    return render_template('user/shoppingcart.html', shoppingcart=myShoppingCart, total=totalPrice)

# 購買購物車中所有的商品(未完成)
@bp.route('/buyAllGoodsInShoppingCart', methods=('GET', 'POST'))
def buyAllGoodsInShoppingCart():
    print('購買購物車中的商品')
    user = g.user
    myShoppingCart = functions.get_all_shopping_cart_goods(user['AccountID'])

    # myShoppingCart=getShoppingCart(user['AccountID'])
    totalPrice = 0
    for goods in myShoppingCart:
        totalPrice += int(goods['total'])

    if totalPrice == 0:
        return redirect(url_for('goods.index'))

    if request.method == 'POST':
        print('post')
        address = request.form['addresss']
        ShippingMethodID = request.form['shippingMethod']
        paymentID = request.form['payment']
        discountStr = request.form['discount']
        # 如果有足夠的庫存(判斷部分沒完成)
        if (True):
            print('訂購成功')
            db = get_db()
            # 設定折扣
            discount = functions.get_discount(discountStr)
            resultPrice = int(totalPrice) * discount['DiscountPercentage']

            # 新增訂單資料（ORDERS）
            functions.add_new_order(user['AccountID'], address, ShippingMethodID, paymentID, discount['DiscountID'], resultPrice)

            # 取得最新 OrderID
            newOrder = db.execute(
                'SELECT MAX(OrderID) AS ID FROM ORDERS'
            ).fetchone()
            OrderID = newOrder['ID']
        
            for goods in myShoppingCart:
                # 新增訂單資料（SALES_ON）
                functions.add_new_sales_on(OrderID, goods['GoodsID'], goods['Amount'])

                # 更新商品庫存
                newAmount = goods['StockQuantity'] - goods['Amount']
                functions.update_goods_stock_quantity(goods['GoodsID'], newAmount)

            # 刪除購物車的內容
            functions.delete_all_goods_from_shopping_cart(user['AccountID'])

            return redirect(url_for('goods.index'))
    return render_template('user/buyAllGoodsInShoppingCart.html', shoppingCart=myShoppingCart, total=totalPrice)

# 查看當前使用者的購買紀錄
@bp.route('/buyHistory', methods=('GET','POST'))
def buyHistory():
    user = g.user
    # print('current user id:' + str(user['AccountID']))
    orders = functions.get_orders(user['AccountID'])
    myHistory = functions.get_user_buy_history(user['AccountID'])

    return render_template('user/buyHistory.html', orders = orders, myHistory = myHistory)

# 取得 g.user
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM ACCOUNT WHERE AccountID = ?', (user_id,)
        ).fetchone()

# 登出
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

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
        
        password = request.form['password']
        confirmPassword = request.form['confirmPassword']
        permission = request.form['permission']
        name = request.form['username']
        identificationNumber = request.form['identification']
        gender = request.form['gender']
        cellphone = request.form['cellphone']
        email = request.form['email']

        if password is None:
            error = 'Password is required.'
        elif confirmPassword is None:
            error = 'Confirm Password is required.'
        elif (not permission.isdigit()) or (int(permission) not in [1, 2, 3]):
            error = 'Permission error.'
        elif len(cellphone) != 10 or (not cellphone.isdigit()):
            error = 'cellphone error.'
        elif password != confirmPassword:
            error = 'Confirm Password error.'

        if error is None:
            db.execute('UPDATE ACCOUNT SET Password = ?, PermissionID = ?, UserName = ?, IdentificationNumber = ?,'
            ' Gender = ?, CellphoneNumber = ?, Email = ?'
            ' WHERE AccountID = ?', 
            (generate_password_hash(password), permission, name, identificationNumber, gender, cellphone, email, user_id))
            db.commit()
            # 待修改
            return redirect(url_for('user.userList'))

        flash(error)
    
    # 待修改
    return render_template('user/editUserInfo.html', user=user)

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

@bp.route('/<int:user_id>/deleteAccount', methods=('GET', 'POST'))
def deleteAccount(user_id):
    db = get_db()
    db.execute(
        'DELETE FROM ACCOUNT WHERE ACCOUNT.AccountID = ?',
        (user_id,)
    )
    db.commit()
    return redirect(url_for('user.userList'))
