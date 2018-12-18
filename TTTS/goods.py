from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from TTTS.user import login_required
from TTTS.db import get_db

# bp = Blueprint('goods', __name__)
bp = Blueprint('goods', __name__, url_prefix='/goods')

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

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT GoodsID, GoodsName, GoodsType, Price, StockQuantity, Introduction, ImageName, CountryOfOrigin'
        ' FROM GOODS'
        ' ORDER BY GoodsID DESC'
    ).fetchall()
    return render_template('goods/index.html', posts=posts)


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

def get_goods(id, check_author=True):
    post = get_db().execute(
        'SELECT GoodsID, GoodsName, GoodsType, Price, StockQuantity, Introduction, ImageName, CountryOfOrigin'
        ' FROM GOODS'
        ' WHERE GoodsID = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
# @login_required
def updateGoods(id):
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
                (selectedShoppingCartGoods[0] + amount, session.get('user_id'), id,)
            )

        # 修改GOODS中的StockQuantity
        db.execute(
            'UPDATE GOODS SET StockQuantity = ?'
            ' WHERE GoodsID = ?',
            # selectedGoods[0] 不確定
            (selectedGoods[0] - amount, id,)
        )
        db.commit()
        # 待修改
        return redirect(url_for('goods.index'))

    # 待修改
    return render_template('goods/index.html', post=post)

