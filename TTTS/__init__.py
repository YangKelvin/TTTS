import os

from flask import Flask, render_template, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'TTTS.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import user
    app.register_blueprint(user.bp)

    from . import search
    app.register_blueprint(search.bp)

    from . import goods
    app.register_blueprint(goods.bp)
    app.add_url_rule('/goods', endpoint='index')

    @app.route('/initDatabase')
    def initDataBase():
        database=db.get_db()
        print('init PERMISSION')
        database.execute(
            'INSERT INTO PERMISSION (PermissionName) VALUES(?)',
            ('Admin',)
        )  
        database.execute(
            'INSERT INTO PERMISSION (PermissionName) VALUES(?)',
            ('Staff',)
        )  
        database.execute(
            'INSERT INTO PERMISSION (PermissionName) VALUES(?)',
            ('Customer',)
        )  

        print('init ACCOUNT')
        database.execute(
        'INSERT INTO ACCOUNT (Account, Password, PermissionID, UserName, IdentificationNumber, Gender, CellphoneNumber, Email) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        ('admin', generate_password_hash('123'), '1', 'AdminA', 'A000000000', 'M', '0000000000', 'admin@ntut.org.tw')
        )
        database.execute(
        'INSERT INTO ACCOUNT (Account, Password, PermissionID, UserName, IdentificationNumber, Gender, CellphoneNumber, Email) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        ('staff', generate_password_hash('123'), '2', 'StaffA', 'A000000001', 'M', '0000000001', 'staff@ntut.org.tw')
        )
        database.execute(
        'INSERT INTO ACCOUNT (Account, Password, PermissionID, UserName, IdentificationNumber, Gender, CellphoneNumber, Email) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        ('customer', generate_password_hash('123'), '3', 'CustomerA', 'A000000002', 'M', '0000000002', 'customer@ntut.org.tw')
        )
        database.execute(
        'INSERT INTO ACCOUNT (Account, Password, PermissionID, UserName, IdentificationNumber, Gender, CellphoneNumber, Email) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        ('105590045', generate_password_hash('123'), '1', 'kelvin', 'N123456789', 'M', '0975107900', 't105590045@ntut.org.tw')
        )
        database.execute(
            'INSERT INTO ACCOUNT (Account, Password, PermissionID, UserName, IdentificationNumber, Gender, CellphoneNumber, Email) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            ('105590023', generate_password_hash('234'), '2', 'james', 'N123098765', 'M', '0978700387', 't105590023@ntut.org.tw')
        )
        database.execute(
            'INSERT INTO ACCOUNT (Account, Password, PermissionID, UserName, IdentificationNumber, Gender, CellphoneNumber, Email) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            ('105590021', generate_password_hash('345'), '2', 'kelvin', 'N123098764', 'M', '0912345678', 't105590021@ntut.org.tw')
        )
        database.execute(
            'INSERT INTO ACCOUNT (Account, Password, PermissionID, UserName, IdentificationNumber, Gender, CellphoneNumber, Email) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            ('105590014', generate_password_hash('456'), '3', 'kelvin', 'N123098765', 'M', '0987654321', 't105590014@ntut.org.tw')
        )
        database.execute(
            'INSERT INTO ACCOUNT (Account, Password, PermissionID, UserName, IdentificationNumber, Gender, CellphoneNumber, Email) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            ('105590000', generate_password_hash('567'), '3', 'kelvin', 'N000000000', 'M', '0900000000', 't105590000@ntut.org.tw')
        )

        print('init GOODS')
        database.execute(
        'INSERT INTO GOODS (GoodsName, GoodsType, Price, StockQuantity, Introduction, ImageName, CountryOfOrigin) VALUES (?, ?, ?, ?, ?, ?, ?)',
        ('好好喝綠茶', '綠茶', '100', '500', '好喝的綠茶喔', 'goodGreenTea.png', '1')
        )
        database.execute(
            'INSERT INTO GOODS (GoodsName, GoodsType, Price, StockQuantity, Introduction, ImageName, CountryOfOrigin) VALUES (?, ?, ?, ?, ?, ?, ?)',
            ('好好喝紅茶', '紅茶', '100', '500', '好喝的紅茶喔', 'goodBlackTea.png', '1')
        )
        database.execute(
            'INSERT INTO GOODS (GoodsName, GoodsType, Price, StockQuantity, Introduction, ImageName, CountryOfOrigin) VALUES (?, ?, ?, ?, ?, ?, ?)',
            ('好好喝烏龍茶', '烏龍茶', '100', '500', '好喝的綠茶喔', 'goodGreenTea.png', '1')
        )

        print('init DISCOUNTTYPE')
        database.execute(
            'INSERT INTO DISCOUNTTYPE (DiscountTypeName) VALUES(?)',
            ('Shipping',)
        )  
        database.execute(
            'INSERT INTO DISCOUNTTYPE (DiscountTypeName) VALUES(?)',
            ('Season',)
        ) 
        database.execute(
            'INSERT INTO DISCOUNTTYPE (DiscountTypeName) VALUES(?)',
            ('Special',)
        )

        print('init DISCOUNT')  
        database.execute(
            'INSERT INTO DISCOUNT (DiscountName, DiscountString, DiscountTypeID, DiscountPercentage) VALUES(?, ?, ?, ?)',
            ('shipping discount 1', 'shipping1', 1, 0.9)
        )
        database.execute(
            'INSERT INTO DISCOUNT (DiscountName, DiscountString, DiscountTypeID, DiscountPercentage) VALUES(?, ?, ?, ?)',
            ('shipping discount 2', 'shipping2', 1, 0.9)
        )
        database.execute(
            'INSERT INTO DISCOUNT (DiscountName, DiscountString, DiscountTypeID, DiscountPercentage) VALUES(?, ?, ?, ?)',
            ('season discount 1', 'season1', 2, 0.9)
        )
        database.execute(
            'INSERT INTO DISCOUNT (DiscountName, DiscountString, DiscountTypeID, DiscountPercentage) VALUES(?, ?, ?, ?)',
            ('special discount 1', 'special', 3, 0.6)
        )

        print ('init SHIPPINGMETHOD')
        database.execute(
            'INSERT INTO SHIPPINGMETHOD (ShippingMethodName) VALUES(?)',
            ('超商取貨',)
        )
        database.execute(
            'INSERT INTO SHIPPINGMETHOD (ShippingMethodName) VALUES(?)',
            ('宅配到府',)
        )

        print ('init PAYMENT')
        database.execute(
            'INSERT INTO PAYMENT (PaymentName) VALUES(?)',
            ('現金',)
        )
        database.execute(
            'INSERT INTO PAYMENT (PaymentName) VALUES(?)',
            ('信用卡',)
        )

        print ('init STATUS')
        database.execute(
            'INSERT INTO STATUS (StatusName) VALUES(?)',
            ('Process',)
        )
        database.execute(
            'INSERT INTO STATUS (StatusName) VALUES(?)',
            ('Transportation',)
        )
        database.execute(
            'INSERT INTO STATUS (StatusName) VALUES(?)',
            ('Arrival',)
        )
        database.execute(
            'INSERT INTO STATUS (StatusName) VALUES(?)',
            ('Carry out',)
        )
        database.execute(
            'INSERT INTO STATUS (StatusName) VALUES(?)',
            ('Fail',)
        )
        database.execute(
            'INSERT INTO STATUS (StatusName) VALUES(?)',
            ('Apply',)
        )
        database.execute(
            'INSERT INTO STATUS (StatusName) VALUES(?)',
            ('Cancel',)
        )
        database.commit()


        return redirect(url_for('goods.index'))
    return app