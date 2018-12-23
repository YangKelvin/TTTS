from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from TTTS.user import login_required
from TTTS.db import get_db

bp = Blueprint('coupon', __name__, url_prefix='/coupon')

@bp.route('/addNewCoupon', methods=('GET', 'POST'))
def addNewCoupon():
    if request.method == 'POST':
        db = get_db()
        error = None

        discountType = request.form['discountType']
        discountName = request.form['discountName']
        discountString = request.form['discountString']
        discountPercentage = request.form['discountPercentage']

        if db.execute(
            'SELECT * FROM DISCOUNT WHERE DISCOUNT.DiscountString = ?',
            (discountString,)
        ).fetchone() is not None:
            error = '折扣碼不可重複'
        
        discountTypeID = db.execute(
            'SELECT DiscountTypeID FROM DISCOUNTTYPE WHERE DISCOUNTTYPE.DiscountTypeName = ?', (discountType, )
        ).fetchone()

        if error is None:
            db.execute(
                'INSERT INTO DISCOUNT (DiscountName, DiscountString, DiscountTypeID, DiscountPercentage) VALUES (?, ?, ?, ?)',
                (discountName, discountString, discountTypeID['DiscountTypeID'], discountPercentage,)
            )
            db.commit()

        return redirect(url_for('coupon.couponList'))

    return render_template('coupon/addCoupon.html')

@bp.route('/<int:coupon_id>/Edit', methods=('GET', 'POST'))
def edit(coupon_id):
    db = get_db()
    coupon = db.execute(
        'SELECT DiscountID, DiscountName, DiscountString, DiscountPercentage, DiscountTypeName'
        ' FROM DISCOUNT, DISCOUNTTYPE'
        ' WHERE DISCOUNT.DiscountTypeID = DISCOUNTTYPE.DiscountTypeID AND DISCOUNT.DiscountID = ?',
        (coupon_id,)
    ).fetchone()

    if request.method == 'POST':
        error = None

        discountType = request.form['discountType']
        discountName = request.form['discountName']
        discountString = request.form['discountString']
        discountPercentage = request.form['discountPercentage']
        
        if db.execute(
            'SELECT discountString FROM DISCOUNT WHERE DISCOUNT.DiscountString = ?',
            (discountString,)
        ).fetchone() is not None and (discountString != coupon['DiscountString']):
            error = '折扣碼重複!'
        
        discountTypeID = db.execute(
            'SELECT DiscountTypeID FROM DISCOUNTTYPE WHERE DISCOUNTTYPE.DiscountTypeName = ?', (discountType, )
        ).fetchone()

        if error is None:
            db.execute(
                'UPDATE DISCOUNT SET DiscountName = ?, DiscountString = ?, DiscountTypeID = ?, DiscountPercentage = ?'
                ' WHERE DiscountID = ?',
                (discountName, discountString, discountTypeID['DiscountTypeID'], discountPercentage, coupon['DiscountID'])
            )
            db.commit()
            return redirect(url_for('coupon.couponList'))

        flash(error)

    return render_template('coupon/editCouponInfo.html', coupon=coupon)

@bp.route('/<int:coupon_id>/deleteCoupon', methods=('POST',))
def deleteCoupon(coupon_id):
    if request.method == 'POST':
        db = get_db()
        db.execute(
            'DELETE FROM DISCOUNT WHERE DISCOUNT.DiscountID = ?', (coupon_id,)
        )
        return redirect(url_for('coupon.couponList'))
    
    return render_template('coupon/couponList.html')

@bp.route('/couponList', methods=('GET', 'POST'))
def couponList():
    db = get_db()
    coupon = db.execute(
        'SELECT DiscountID, DiscountName, DiscountString, DiscountPercentage, DiscountTypeName'
        ' FROM DISCOUNT, DISCOUNTTYPE'
        ' WHERE DISCOUNT.DiscountTypeID = DISCOUNTTYPE.DiscountTypeID'
    )
    return render_template('coupon/couponList.html', coupons=coupon)