from TTTS.db import get_db

# 取的當前所有的商品
def get_all_goods():
    db = get_db()
    goods = db.execute(
        'SELECT GoodsID, GoodsName, GoodsType, Price, StockQuantity, Introduction, ImageName, CountryOfOrigin'
        ' FROM GOODS'
        ' ORDER BY GoodsID DESC'
    ).fetchall()
    return goods

# 取得商品
def get_goods(id):
    goods = get_db().execute(
        'SELECT GoodsID, GoodsName, GoodsType, Price, StockQuantity, Introduction, ImageName, CountryOfOrigin'
        ' FROM GOODS'
        ' WHERE GoodsID = ?',
        (id,)
    ).fetchone()
    return goods

#新增商品
def add_new_goods(name, goods_type, price, stockQuantity, introduction, imageName, countryOfOrigin):
    db = get_db()
    db.execute(
        'INSERT INTO GOODS (GoodsName, GoodsType, Price, StockQuantity, Introduction, ImageName, CountryOfOrigin)'
        ' VALUES (?, ?, ?, ?, ?, ?, ?)',
        (name, goods_type, price, stockQuantity, introduction, imageName, countryOfOrigin)
    )
    db.commit()

# 修改商品
def update_goods(name, goods_type, price, stockQuantity, introduction, imageName, countryOfOrigin):
    db = get_db()
    db.execute(
        'UPDATE GOODS SET GoodsName = ?, GoodsType = ?, Price = ?, StockQuantity = ?, Introduction = ?, ImageName = ?, CountryOfOrigin = ?'
        ' WHERE GoodsID = ?',
        (name, goods_type, price, stockQuantity, introduction, imageName, countryOfOrigin, id)
    )
    db.commit()

# 刪除商品
def delete_goods(id):
    db = get_db()
    db.execute('DELETE FROM GOODS WHERE GoodsID = ?', (id,))
    db.commit()

# 查詢折扣
def check_discount(discount_str):
    db = get_db()
    goodsDiscount = db.execute(
        'SELECT DiscountID, DiscountName, DiscountString, DiscountPercentage, DiscountTypeID FROM DISCOUNT WHERE DiscountString = ?',
        ('shipping1',)
    ).fetchone()
    db.commit()
    return goodsDiscount

# 新增一筆訂單
def add_new_order(account_id, address, shipping_method_id, payment_id, goods_discount, total_price):
    db = get_db()
    db.execute(
        'INSERT INTO ORDERS (AccountID, Address, ShippingMethodID, StatusID, PaymentID, DiscountID, TotalPrice) '
        'VALUES (?, ?, ?, ?, ?, ?, ?)', 
        (account_id, address, shipping_method_id, '1',payment_id, goods_discount, total_price,)
    )
    db.commit()

# 新增一比 sales_on
def add_new_sales_on(order_id, goods_id, amount):
    db = get_db()
    db.execute(
        'INSERT INTO SALES_ON (OrderID, GoodsID, Amount) '
        'VALUES (?, ?, ?)', 
        (order_id, goods_id, amount,)
    )
    db.commit()

def update_goods_stock_quantity(goods_id, new_amount):
    db = get_db()
    db.execute(
        'UPDATE GOODS SET StockQuantity = ? WHERE GOODSID = ? ',
        (new_amount, goods_id)
    )
    db.commit()

def add_new_goods_in_shopping_cart(account_id, goods_id, amount):
    db = get_db()
    db.execute(
        'INSERT INTO SHOPPINGCART (AccountID, GoodsID, Amount) '
        'VALUES (?, ?, ?)', 
        (account_id, goods_id, amount,)
    )
    db.commit()

def delete_goods_from_shopping_cart(account_id, goods_id):
    db = get_db()
    db.execute('DELETE FROM SHOPPINGCART WHERE SHOPPINGCART.GoodsID = ? AND SHOPPINGCART.AccountID = ?', (goods_id, account_id),)
    db.commit()