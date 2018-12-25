from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from TTTS.user import login_required
from TTTS.db import get_db
# from TTTS.functions import get_all_goods
from . import functions

# bp = Blueprint('goods', __name__)
bp = Blueprint('goods', __name__, url_prefix='/goods')

# goods index
@bp.route('/')
def index():
    posts = functions.get_all_goods()
    user = None
    if g.user is not None:
        user = functions.get_user_information(g.user['AccountID'])
    return render_template('goods/index.html', posts=posts, user=user)

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
            functions.add_new_goods(goodsName, goodsType, price, stockQuantity, introduction, imageName, countryOfOrigin)
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
            functions.update_goods(goodsName, goodsType, price, stockQuantity, introduction, imageName, countryOfOrigin, id)
            return redirect(url_for('goods.index'))
    
    return render_template('goods/updateGoods.html', post=post)

# 刪除特定商品
@bp.route('/<int:id>/delete', methods=('POST',))
def deleteGoods(id):
    functions.delete_goods(id)
    return redirect(url_for('goods.index'))

# 查看商品資訊
@bp.route('/<int:GoodsID>/viewGoods', methods=('GET', 'POST'))
def viewGoods(GoodsID):
    print ('view')
    goods = functions.get_goods(GoodsID)

    if (request.method == 'POST'):
        print("go to buy goods page")
        buyGoods(GoodsID)
    temp = '台灣'
    return render_template('goods/viewGoods.html', post=goods, temp=temp)

@bp.route('/<int:GoodsID>/buyGoods', methods=('GET', 'POST'))
def buyGoods(GoodsID):
    print('buy page')

    # 取得購買的商品
    buyGoods = functions.get_goods(GoodsID)

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
        discountStr = request.form['discount']
        orderAmount = request.form['orderAmount']

        print('--------訂購資訊--------')
        print('address:' + address)
        print('shipping method id:' + ShippingMethodID)
        print('payment id:' + paymentID)
        print('discountStr:' + discountStr)
        print('order amount:' + orderAmount)
        print('---------------------')
        
        # 如果有足夠的庫存
        if (int(orderAmount) <= int(buyGoods['StockQuantity'])):
            print('訂購成功')
            db = get_db()

            # 查詢折扣是否存在
            goodsDiscount = functions.check_discount(discountStr)
            discountID = None
            discount = 1
            if goodsDiscount is None:
                discount = 1
                discountID = 0
            else:
                discount = goodsDiscount['DiscountPercentage']
                discountID = goodsDiscount['DiscountID']
            # print(goodsDiscount)

            # 新增訂單資料（ORDERS）
            totalPrice=int(orderAmount) * int(buyGoods['Price'] * discount) 
            print ("discount:" + str(discount))
            print ("discountID:" + str(discountID))
            print ("total:" + str(totalPrice))
            functions.add_new_order(session.get('user_id'), address, ShippingMethodID, paymentID, discountID, totalPrice)

            # 取得最新 OrderID
            newOrder = db.execute(
                'SELECT MAX(OrderID) AS ID FROM ORDERS'
            ).fetchone()
            OrderID = newOrder['ID']
            print('OrderID:' + str(OrderID))
            
            # 新增訂單資料（SALES_ON）
            functions.add_new_sales_on(OrderID, GoodsID, orderAmount)

            # 更新商品庫存
            originAmount = buyGoods['StockQuantity']
            newStockQuantity = int(originAmount) - int(orderAmount)
            functions.update_goods_stock_quantity(GoodsID, newStockQuantity)

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
            functions.add_new_goods_in_shopping_cart(session.get('user_id'), goods['GoodsID'], amount)

            return redirect(url_for('goods.index'))
        else:
            print('庫存不夠')
    temp = '台灣'
    return render_template('goods/viewGoods.html', post=goods, temp=temp)

# 刪除購物車中的商品
@bp.route('/<int:GoodsID>/deleteShoppingCartGoods', methods=('GET', 'POST'))
@login_required
def delete_shoppingCart_goods(GoodsID):
    # 取得SHOPPINGCART的商品
    deleteGoods = get_goods(GoodsID)
    deleteGoodsID = deleteGoods['GoodsID']
    print('delete goods id:' + str(deleteGoods['GoodsID']))
    print('current user id:' + str(session.get('user_id')))
    # 刪除
    functions.delete_goods_from_shopping_cart(deleteGoodsID, session.get('user_id'))

    # 待修改
    return redirect(url_for('goods.index'))