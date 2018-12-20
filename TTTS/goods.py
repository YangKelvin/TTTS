from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from TTTS.user import login_required
from TTTS.db import get_db

# bp = Blueprint('goods', __name__)
bp = Blueprint('goods', __name__, url_prefix='/goods')

# 初始化
@bp.route('/init', methods=('GET', 'POST'))
def init():
    print ('init goods')
    db = get_db()
    db.execute(
        'INSERT INTO GOODS (GoodsName, GoodsType, Price, StockQuantity, Introduction, ImageName, CountryOfOrigin) VALUES (?, ?, ?, ?, ?, ?, ?)',
        ('好好喝綠茶', '綠茶', '100', '5', '好喝的綠茶喔', 'goodGreenTea.png', '1')
    )
    db.execute(
        'INSERT INTO GOODS (GoodsName, GoodsType, Price, StockQuantity, Introduction, ImageName, CountryOfOrigin) VALUES (?, ?, ?, ?, ?, ?, ?)',
        ('好好喝紅茶', '紅茶', '100', '5', '好喝的紅茶喔', 'goodBlackTea.png', '1')
    )
    db.execute(
        'INSERT INTO GOODS (GoodsName, GoodsType, Price, StockQuantity, Introduction, ImageName, CountryOfOrigin) VALUES (?, ?, ?, ?, ?, ?, ?)',
        ('好好喝烏龍茶', '烏龍茶', '100', '5', '好喝的綠茶喔', 'goodGreenTea.png', '1')
    )
    db.commit()
    return redirect(url_for('index'))

# index
@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT GoodsID, GoodsName, GoodsType, Price, StockQuantity, Introduction, ImageName, CountryOfOrigin'
        ' FROM GOODS'
        ' ORDER BY GoodsID DESC'
    ).fetchall()
    return render_template('goods/index.html', posts=posts)

# 新增產品
@bp.route('/addNewGoods', methods=('GET', 'POST'))
# @login_required
def addNewGoods():
    if request.method == 'POST':
        goodsName = request.form['goodsName']
        goodsType = request.form['goodsType']
        price = request.form['price']
        stockQuantity = request.form['stockQuantity']
        introduction = request.form['introduction']
        imageName = request.form['imageName']
        countryOfOrigin = request.form['countryOfOrigin']

        error = None

        if not goodsName:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO GOODS (GoodsName, GoodsType, Price, StockQuantity, Introduction, ImageName, CountryOfOrigin)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?)',
                (goodsName, goodsType, price, stockQuantity, introduction, imageName, countryOfOrigin)
            )
            db.commit()
            return redirect(url_for('goods.addNewGoods'))

    return render_template('goods/addNewGoods.html')

def get_goods(GoodsID, check_author=True):
    post = get_db().execute(
        'SELECT GoodsID, GoodsName, GoodsType, Price, StockQuantity, Introduction, ImageName, CountryOfOrigin'
        ' FROM GOODS'
        ' WHERE GoodsID = ?',
        (GoodsID,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    return post

def get_shoppingCart_goods(AccountID, check_author=True):
    post = get_db().execute(
        'SELECT G.GoodsID, G.GoodsName, G.GoodsType, G.Price, G.ImageName, G.CountryOfOrigin, CART.Amount'
        ' FROM GOODS AS G,'
        ' (SELECT S.GoodsID, S.Amount FROM SHOPPINGCART AS S WHERE S.AccountID = ?) CART'
        ' WHERE G.GoodsID = CART.GoodsID',
        (AccountID,)
    ).fetchall()

    return post

# 修改商品
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
# @login_required
def updateGoods(id):
    print ('update')
    post = get_goods(id)

    if request.method == 'POST':
        goodsName = request.form['goodsName']
        goodsType = request.form['goodsType']
        price = request.form['price']
        stockQuantity = request.form['stockQuantity']
        introduction = request.form['introduction']
        imageName = request.form['imageName']
        countryOfOrigin = request.form['countryOfOrigin']

        error = None

        if not goodsName:
            error = 'GoodsName is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE GOODS SET GoodsName = ?, GoodsType = ?, Price = ?, StockQuantity = ?, Introduction = ?, ImageName = ?, CountryOfOrigin = ?'
                ' WHERE GoodsID = ?',
                (goodsName, goodsType, price, stockQuantity, introduction, imageName, countryOfOrigin, id)
            )
            db.commit()
            return redirect(url_for('goods.index'))
    
    return render_template('goods/updateGoods.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
def deleteGoods(id):
    print('delete1')
    get_goods(id)
    db = get_db()
    db.execute('DELETE FROM GOODS WHERE GoodsID = ?', (id,))
    db.commit()
    print('delete')
    return redirect(url_for('goods.index'))
# --------------------------------
    
# 顧客
@bp.route('/<int:GoodsID>/buyGoods', methods=('GET', 'POST'))
def buyGoods(GoodsID):
    print ('buy')
    goods = get_goods(GoodsID)

    if (request.method == 'POST'):
        amount = request.form['amount']

        db = get_db()

        # 判斷庫存數量是否大於購買數量
        originAmount = goods['StockQuantity']
        resutlAmount = int(originAmount) - int(amount)

        # 若送出的訂單數量合法
        if (resutlAmount >= 0):
            # 新增訂單（SALES_ON）
            db.execute(
                'INSERT INTO SALES_ON (AccountID, GoodsID, Amount) '
                'VALUES (?, ?, ?)', 
                (session.get('user_id'), goods['GoodsID'], amount,)
            )

            # 新增訂單（ORDERS）
            
            # 更新商品庫存
            db.execute(
                'UPDATE GOODS SET StockQuantity = ?'
                ' WHERE GoodsID = ?',
                (resutlAmount, goods['GoodsID'])
            )
            return redirect(url_for('goods.index'))
    temp = '台灣'
    return render_template('goods/buyGoods.html', post=goods, temp=temp)

# 加到購物車
@bp.route('/<int:GoodsID>/addGoodsToShoppingCart', methods=('GET', 'POST'))
def addToShoppingCart(GoodsID):
    print ('Add')
    goods = get_goods(GoodsID)

    if (request.method == 'POST'):
        amount = request.form['amount2']

        db = get_db()

        # 判斷庫存數量是否大於購買數量
        originAmount = goods['StockQuantity']
        resutlAmount = int(originAmount) - int(amount)

        # 若送出的訂單數量合法
        if (resutlAmount >= 0):
            # 新增訂單（SALES_ON）
            db.execute(
                'INSERT INTO SHOPPINGCART (AccountID, GoodsID, Ammount) '
                'VALUES (?, ?, ?)', 
                (session.get('user_id'), goods['GoodsID'], amount,)
            )
            db.commit()

            return redirect(url_for('goods.index'))
        else:
            print('庫存不夠')
    temp = '台灣'
    return render_template('goods/buyGoods.html', post=goods, temp=temp)


@bp.route('/<int:id>/deleteShoppingCartGoods', methods=('GET', 'POST'))
@login_required
def delete_shoppingCart_goods(id):
    # 取得SHOPPINGCART的商品
    post = get_shoppingCart_goods(id)

    if request.method == 'POST':
        db = get_db()
        # 永健大大來幫我
        # 永健大大來幫我
        # 永健大大來幫我
        db.execute('DELETE FROM SHOPPINGCART WHERE SHOPPINGCART.GoodsID = ?', (id,))
        db.commit()
        # 待修改
        return redirect(url_for('goods.index'))

    # 待修改
    return render_template('goods/index.html', post=post)
    
# 未測試
@bp.route('/<int:id>/view', methods=('GET', 'POST'))
@login_required
def view_goods(id):
    post = get_goods(id)

    if request.method == 'POST':
        db = get_db()
        amount = request.form['goodsAmount']
        # 從GOODS中取得所選商品
        selectedGoods = db.execute(
            'SELECT G.Amount'
            ' FROM GOODS AS G'
            ' WHERE G.GoodsID = ?',
            (id,)
        ).fetchone()

        # 從SHOPPINGCART中取得所選商品
        selectedShoppingCartGoods = db.execute(
            'SELECT S.Amount'
            ' FROM SHOPPINGCART AS S'
            ' WHERE AccountID = ? AND S.GoodsID = ?',
            (session.get['user_id'], id,)
        ).fetchone()

        # 修改SHOPPINGCART內的資訊
        if selectedShoppingCartGoods is None:
            db.execute('INSERT INTO SHOPPINGCART (AccountID, GoodsID, Amount) VALUES (?, ?, ?)', (session.get('user_id'), id, amount,))
        else:
            db.execute(
                'UPDATE SHOPPINGCART SET Amount = ?'
                ' WHERE AccountID = ? AND GoodsID = ?',
                # selectedShoppingCartGoods[0] 不確定
                (selectedShoppingCartGoods['Amount'] + amount, session.get('user_id'), id,)
            )

        # 修改GOODS中的StockQuantity
        db.execute(
            'UPDATE GOODS SET StockQuantity = ?'
            ' WHERE GoodsID = ?',
            # selectedGoods[0] 不確定
            (selectedGoods['Amount'] - amount, id,)
        )
        db.commit()
        # 待修改
        return redirect(url_for('goods.index'))

    # 待修改
    return render_template('goods/index.html', post=post)
