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
def update_goods(name, goods_type, price, stockQuantity, introduction, imageName, countryOfOrigin, id):
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
        (discount_str,)
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
    db.execute(
        'DELETE FROM SHOPPINGCART' 
        'WHERE SHOPPINGCART.GoodsID = ? AND SHOPPINGCART.AccountID = ?', 
        (goods_id, account_id),
        )
    db.commit()

def delete_all_goods_from_shopping_cart(account_id):
    db = get_db()
    db.execute(
        'DELETE FROM SHOPPINGCART WHERE SHOPPINGCART.AccountID = ?', 
        (account_id,),
        )
    db.commit()

def get_all_shopping_cart_goods(account_id):
    db = get_db()
    my_shopping_cart = db.execute(
        'SELECT B.Account, B.UserNAme, C.GoodsID, C.GoodsName, C.StockQuantity, C.Price, A.Amount, C.Price * A.Amount AS total '
        'FROM SHOPPINGCART AS A, ACCOUNT AS B, GOODS AS C '
        'WHERE A.AccountID = B.AccountID and '
        'A.GoodsID = C.GoodsID and '
        'A.AccountID = ?',
        (account_id,)
    ).fetchall()
    return my_shopping_cart

def get_discount(discount_str):
    db = get_db()
    discount = db.execute(
        'SELECT A.DiscountID, A.DiscountName, B.DiscountTypeName, A.DiscountString, DiscountPercentage '
        'FROM DISCOUNT AS A, DISCOUNTTYPE AS B '
        'WHERE A.DiscountTypeID = B.DiscountTypeID and '
        'A.DiscountString = ?',
        (discount_str,)
    ).fetchone()
    
    return discount

def get_orders(account_id):
    db = get_db()
    orders = db.execute(
        'SELECT A.OrderID, A.Date, A.Address, B.ShippingMethodName, C.StatusName, D.PaymentName, A.TotalPrice, E.DiscountName, E.DiscountPercentage '
        'FROM ORDERS AS A, SHIPPINGMETHOD AS B, STATUS AS C, PAYMENT AS D, DISCOUNT AS E '
        'WHERE A.ShippingMethodID = B.ShippingMethodID and '
        'A.StatusID = C.StatusID and '
        'A.PaymentID = D.PaymentID and '
        'A.DiscountID = E.DiscountID and '
        'A.AccountID = ?',
        (account_id,)
    ).fetchall()
    return orders

def get_user_buy_history(account_id):
    db = get_db()
    my_order_history = db.execute(
        'SELECT A.OrderID, A.Date, B.GoodsName, B.Price, B.Introduction, C.Amount, B.Price * C.Amount AS total1, A.TotalPrice, A.DiscountID '
        'FROM ORDERS AS A, GOODS AS B, SALES_ON AS C, Discount AS D '
        'WHERE A.OrderID = C.OrderID and '
        'C.GoodsID = B.GoodsID and '
        'A.DiscountID = D.DiscountID and '
        'A.AccountID = ?',
        (account_id,)
    ).fetchall()
    return my_order_history

def get_user_information(account_id):
    db = get_db()
    userInformation = db.execute(
        'SELECT Account, UserName, CellphoneNumber, Gender, Email, PermissionName FROM ACCOUNT, PERMISSION'
        ' WHERE ACCOUNT.AccountID = ? AND PERMISSION.PermissionID = ACCOUNT.PermissionID',
        (account_id,)
    ).fetchone()
    return userInformation

#not use
def get_user_buy_history_in_order(account_id, current_order_id):
    db = get_db()
    my_order_history = db.execute(
        'SELECT A.OrderID, A.Date, B.GoodsName, B.Price, C.Amount, B.Price * C.Amount AS total1, A.TotalPrice, A.DiscountID '
        'FROM ORDERS AS A, GOODS AS B, SALES_ON AS C, Discount AS D '
        'WHERE A.OrderID = C.OrderID and '
        'C.GoodsID = B.GoodsID and '
        'A.DicountID = C.DiscountID and '
        'A.AccountID = ? and A.OrderID = ?',
        (account_id, current_order_id,)
    ).fetchall()
    return my_order_history

# 產品分析
def get_goods_statistics_list(id):
    db = get_db()
    goods_statistics_list = db.execute(
        'SELECT D.UserName, C.GoodsName, B.Amount, B.Amount * C.Price AS Earn '
        'FROM ORDERS AS A, SALES_ON AS B, GOODS AS C, ACCOUNT AS D '
        'WHERE A.OrderID = B.OrderID and '
        'B.GoodsID = C.GoodsID and '
        'A.AccountID = D.AccountID and '
        'B.GoodsID = ?',
        (id,)
    ).fetchall()
    return goods_statistics_list

def get_all_goods_statistics_list():
    db = get_db()
    goods_statistics_list = db.execute(
        'SELECT D.UserName, C.GoodsName, B.Amount, B.Amount * C.Price AS Earn '
        'FROM ORDERS AS A, SALES_ON AS B, GOODS AS C, ACCOUNT AS D '
        'WHERE A.OrderID = B.OrderID and '
        'B.GoodsID = C.GoodsID and '
        'A.AccountID = D.AccountID',
    ).fetchall()
    return goods_statistics_list

def get_all_goods_statistics():
    db = get_db()
    goods_statistics = db.execute(
        'SELECT C.GoodsID, C.GoodsName, C.Price, SUM(B.Amount) AS Amount, SUM(B.Amount * C.Price) AS TotalPrice '
        'FROM ORDERS AS A, SALES_ON AS B, GOODS AS C, ACCOUNT AS D '
        'WHERE A.OrderID = B.OrderID and '
        'B.GoodsID = C.GoodsID and '
        'A.AccountID = D.AccountID '
        'GROUP BY C.GoodsName '
        'ORDER BY C.GoodsID ASC',
    ).fetchall()
    return goods_statistics

def get_all_orders():
    db = get_db()
    orders = db.execute(
        'SELECT  A.OrderID, B.Account, B.UserName, A.Address, C.ShippingMethodName, D.StatusName, E.PaymentName, F.DiscountName, F.DiscountPercentage, A.TotalPrice '
        'FROM ORDERS AS A, ACCOUNT AS B, SHIPPINGMETHOD AS C, STATUS AS D, PAYMENT AS E, DISCOUNT AS F '
        'WHERE A.AccountID = B.AccountID and '
        'A.ShippingMethodID = C.ShippingMethodID and '
        'A.StatusID = D.StatusID and '
        'A.PaymentID = E.PaymentID and '
        'A.DiscountID = F.DiscountID',
    ).fetchall()
    return orders

def update_order_status(order_id, status_id):
    db = get_db()
    db.execute(
        'UPDATE ORDERS SET StatusID = ? WHERE OrderID = ? ',
        (status_id, order_id)
    )
    db.commit()