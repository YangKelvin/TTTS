from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
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
        'SELECT GoodsName, GoodsType, Price, StockQuantity, Introduction, ImageName, CountryOfOrigin'
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

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
# @login_required
def update(id):
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
                'UPDATE GOODS SET GoodsName = ?, GoodsType = ?, Price = ?, StockQuantity = ?, Intorduction = ?, ImageName = ?, CountryOfOrigin = ?'
                ' WHERE id = ?',
                (goodsName, goodsType, price, stockQuantity, introduction, imageName, countryOfOrigin, id)
            )
            db.commit()
            return redirect(url_for('goods.index'))

    return render_template('goods/updateGoods.html', post=post)