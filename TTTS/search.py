from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from TTTS.db import get_db

bp = Blueprint('search', __name__, url_prefix='/search')

@bp.route('/', methods=('GET', 'POST'))
def search():
    if request.method == 'POST':
        db = get_db()
        name = request.form['searchName']
        goods = db.execute(
            'SELECT * FROM GOODS'
            ' WHERE GoodsName LIKE ?',
            ('%' + name + '%',)
        ).fetchall()
        # 要改
        return render_template('search/searchResult.html', posts=goods)
    # 要改
    return render_template('search/search.html')
