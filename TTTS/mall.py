from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from TTTS.user import login_required
from TTTS.db import get_db

bp = Blueprint('mall', __name__)

# @bp.route('/')
# def index():
#     db = get_db()
#     posts = db.execute(
#         'SELECT GoodsName'
#         ' FROM GOODS '
#         ' ORDER BY created DESC'
#     ).fetchall()
#     return render_template('mall/index.html', posts=posts)