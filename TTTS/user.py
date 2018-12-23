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

# 判斷購物車中要購買的商品是否有足夠的數量
def IsHasEnoughStock(myShoppingcart):
    return True

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

    if request.method == 'POST':
        print('post')
        address = request.form['addresss']
        ShippingMethodID = request.form['shippingMethod']
        paymentID = request.form['payment']
        discountStr = request.form['discount']
        # 如果有足夠的庫存(判斷部分沒完成)
        if (IsHasEnoughStock(myShoppingCart)):
            print('訂購成功')
            db = get_db()
            # 設定折扣
            discountPercentage = functions.get_discount(discountStr)
            resultPrice = totalPrice * discountPercentage

            # 新增訂單資料（ORDERS）
            functions.add_new_order(user['AccountID'], address, ShippingMethodID, paymentID, discountPercentage, resultPrice)

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
    db = get_db()
    # myHistory = db.execute(
    #     'SELECT S.GoodsID, S.Amount, G.GoodsName, G.GoodsType, G.Price, G.Introduction, G.ImageName, ORDER_TABLE.OrderID, ORDER_TABLE.DATE,'
    #     ' ORDER_TABLE.Address, ORDER_TABLE.ShippingMethodName, ORDER_TABLE.StatusName, ORDER_TABLE.DiscountPercentage'
    #     ' FROM GOODS AS G, SALES_ON AS S,'
    #         ' (SELECT O.OrderID, O.DATE, O.Address, ShippingMethodName, StatusName, DiscountPercentage'
    #         ' FROM ORDERS AS O'
    #         ' LEFT OUTER JOIN SHIPPINGMETHOD ON SHIPPINGMETHOD.ShippingMethodID = O.ShippingMethodID'
    #         ' LEFT OUTER JOIN STATUS ON STATUS.StatusID = O.StatusID'
    #         ' LEFT OUTER JOIN DISCOUNT ON DISCOUNT.DiscountID = O.DiscountID'
    #         ' WHERE O.AccountID LIKE ?) ORDER_TABLE'
    #     ' WHERE S.OrderID = ORDER_TABLE.OrderID AND S.GoodsID = G.GoodsID',
    #     (user['AccountID'],)
    # ).fetchall()
    myHistory = db.execute(
        'SELECT A.OrderID, A.DATE, C.GoodsID, C.GoodsName, C.GoodsType, C.Price, C.Introduction, C.ImageName, B.Amount, D.DiscountPercentage, E.PaymentName, F.ShippingMethodName, A.Address, G.StatusName, A.TotalPrice '
        'FROM ORDERS AS A, SALES_ON AS B, GOODS AS C, DISCOUNT AS D, PAYMENT AS E, SHIPPINGMETHOD AS F, STATUS AS G '
        'WHERE A.OrderID = B.OrderID and '
        'B.GoodsID = C.GoodsID and '
        'A.AccountID=3 and '
        'A.PaymentID = E.PaymentID and '
        'A.ShippingMethodID = F.ShippingMethodID and '
        'A.DiscountID = D.DiscountID and '
        'A.StatusID = G.StatusID and '
        'A.AccountID=?',
        (user['AccountID'],)
    ).fetchall()
    
    # mySalesOn = db.execute(
    #     'SELECT B.GoodsName, B.Price, A.Amount, B.Price*A.Amount AS total '
    #     'FROM SALES_ON AS A, GOODS AS B '
    #     'WHERE A.GoodsID=B.GoodsID and '
    #     'A.OrderID=?'
    # ).fetchall()

    return render_template('user/buyHistory.html', history=myHistory)

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
    user = get_user(user_id)

    if request.method == 'POST':
        db = get_db()

        db.execute(
            'DELETE FROM ACCOUNT WHERE ACCOUNT.AccountID = ?',
            (user_id,)
        )
        db.commit()

        return redirect(url_for('user.userList'))
    
    return render_template('user/editUserInfo.html', user=user)
