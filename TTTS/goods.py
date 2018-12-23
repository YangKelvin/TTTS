from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from TTTS.user import login_required
from TTTS.db import get_db

# bp = Blueprint('goods', __name__)
bp = Blueprint('goods', __name__, url_prefix='/goods')

# goods index
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
            return redirect(url_for('goods.index'))

    return render_template('goods/addNewGoods.html')

# 取得商品資訊
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

# 取得購物車內的商品(?)
def get_shoppingCart_goods(AccountID, check_author=True):
    post = get_db().execute(
        'SELECT G.GoodsID, G.GoodsName, G.GoodsType, G.Price, G.ImageName, G.CountryOfOrigin, CART.Amount'
        ' FROM GOODS AS G,'
        ' (SELECT S.GoodsID, S.Amount FROM SHOPPINGCART AS S WHERE S.AccountID = ?) CART'
        ' WHERE G.GoodsID = CART.GoodsID',
        (AccountID,)
    ).fetchall()

    return post

# 修改商品資訊
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
    
    return render_template('goods/updateGoods.html', posts=post)

# 刪除特定商品
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
# 查看商品資訊
@bp.route('/<int:GoodsID>/viewGoods', methods=('GET', 'POST'))
def viewGoods(GoodsID):
    print ('view')
    goods = get_goods(GoodsID)

    if (request.method == 'POST'):
        print("go to buy goods page")
        buyGoods(GoodsID)

        # amount = request.form['amount']

        # db = get_db()

        # 判斷庫存數量是否大於購買數量
        # originAmount = goods['StockQuantity']
        # resutlAmount = int(originAmount) - int(amount)

        # 若送出的訂單數量合法
        # if (resutlAmount >= 0):
            # 新增訂單（SALES_ON）
            # db.execute(
            #     'INSERT INTO SALES_ON (AccountID, GoodsID, Amount) '
            #     'VALUES (?, ?, ?)', 
            #     (session.get('user_id'), goods['GoodsID'], amount,)
            # )

            # 新增訂單（ORDERS）
            
            # 更新商品庫存
            # db.execute(
            #     'UPDATE GOODS SET StockQuantity = ?'
            #     ' WHERE GoodsID = ?',
            #     (resutlAmount, goods['GoodsID'])
            # )
            # return redirect(url_for('goods.index'))
    temp = '台灣'
    return render_template('goods/viewGoods.html', post=goods, temp=temp)

@bp.route('/<int:GoodsID>/buyGoods', methods=('GET', 'POST'))
def buyGoods(GoodsID):
    print('buy page')

    # 取得購買的商品
    buyGoods=get_goods(GoodsID)
    print('--------goods--------')
    print('GoodsID='+str(buyGoods['GoodsID']))
    print('GoodsName='+str(buyGoods['GoodsName']))
    print('GoodsType='+str(buyGoods['GoodsType']))
    print('GoodsPrice='+str(buyGoods['Price']))
    print('GoodsStockQuantity='+str(buyGoods['StockQuantity']))
    print('ImageName='+str(buyGoods['ImageName']))
    print('CountryOfOrigin='+str(buyGoods['CountryOfOrigin']))
    print('---------------------')

    if request.method == 'POST':
        print('post')
        address = request.form['addresss']
        ShippingMethodID = request.form['shippingMethod']
        paymentID = request.form['payment']
        discount = request.form['discount']
        orderAmount = request.form['orderAmount']

        print('--------訂購資訊--------')
        print('address:' + address)
        print('shipping method id:' + ShippingMethodID)
        print('payment id:' + paymentID)
        print('discount:' + discount)
        print('order amount:' + orderAmount)
        print('---------------------')
        # 如果有足夠的庫存
        if (int(orderAmount) <= int(buyGoods['StockQuantity'])):
            print('訂購成功')
            db = get_db()

            # 查詢折扣是否存在
            goodsDiscount = db.execute(
                'SELECT DiscountID, DiscountName, DiscountString, DiscountPercentage, DiscountTypeID FROM DISCOUNT WHERE DiscountString = ?',
                ('shipping1',)
            ).fetchone()
            print(goodsDiscount['DiscountName'])

            # 查詢折扣是否存在
            # 新增訂單資料（ORDERS）
            totalPrice=int(orderAmount) * int(buyGoods['Price'])
            db.execute(
                'INSERT INTO ORDERS (AccountID, Address, ShippingMethodID, StatusID, PaymentID, DiscountID, TotalPrice) '
                'VALUES (?, ?, ?, ?, ?, ?, ?)', 
                (session.get('user_id'), address, ShippingMethodID, '1',paymentID, goodsDiscount['DiscountID'], totalPrice,)
            )

            # 取得最新 OrderID
            newOrder = db.execute(
                'SELECT MAX(OrderID) AS ID FROM ORDERS'
            ).fetchone()
            OrderID = newOrder['ID']
            print('OrderID:' + str(OrderID))
            
            # 新增訂單資料（SALES_ON）
            db.execute(
                'INSERT INTO SALES_ON (OrderID, GoodsID, Amount) '
                'VALUES (?, ?, ?)', 
                (OrderID, GoodsID, orderAmount,)
            )

            # 更新商品庫存
            originAmount = buyGoods['StockQuantity']
            db.execute(
                'UPDATE GOODS SET StockQuantity = ? WHERE GOODSID = ? ',
                (int(originAmount)-int(orderAmount), GoodsID)
            )
            db.commit()
            return redirect(url_for('goods.index'))
    return render_template('goods/buyGoods.html', goods=buyGoods)

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
                'INSERT INTO SHOPPINGCART (AccountID, GoodsID, Amount) '
                'VALUES (?, ?, ?)', 
                (session.get('user_id'), goods['GoodsID'], amount,)
            )
            db.commit()

            return redirect(url_for('goods.index'))
        else:
            print('庫存不夠')
    temp = '台灣'
    return render_template('goods/viewGoods.html', post=goods, temp=temp)

# 購買購物車裡面的商品

# 購買單個商品

@bp.route('/<int:GoodsID>/deleteShoppingCartGoods', methods=('GET', 'POST'))
@login_required
def delete_shoppingCart_goods(GoodsID):
    # 取得SHOPPINGCART的商品
    deleteGoods = get_goods(GoodsID)
    deleteGoodsID = deleteGoods['GoodsID']
    print('delete goods id:' + str(deleteGoods['GoodsID']))
    print('current user id:' + str(session.get('user_id')))
    # 刪除
    db = get_db()
    db.execute('DELETE FROM SHOPPINGCART WHERE SHOPPINGCART.GoodsID = ? AND SHOPPINGCART.AccountID = ?', (int(deleteGoodsID),int(session.get('user_id')),))
    db.commit()
    # 待修改
    return redirect(url_for('goods.index'))