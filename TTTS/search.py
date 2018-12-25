from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from TTTS.db import get_db

bp = Blueprint('search', __name__, url_prefix='/search')

@bp.route('/', methods=('POST',))
def search():
    db = get_db()
    name = request.form['searchName']
    goods = db.execute(
        'SELECT * FROM GOODS'
        ' WHERE GoodsName LIKE ?',
        ('%' + name + '%',)
    ).fetchall()

    return render_template('search/searchResult.html', posts=goods)