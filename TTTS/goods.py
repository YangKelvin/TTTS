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
    return redirect(url_for('user.login'))
