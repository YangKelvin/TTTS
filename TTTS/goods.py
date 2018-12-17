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
    return redirect(url_for('goods.addNewGoods'))

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