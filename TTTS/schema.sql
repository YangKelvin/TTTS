DROP TABLE IF EXISTS COUNTRY;
DROP TABLE IF EXISTS AREA;
DROP TABLE IF EXISTS COUNTY;
DROP TABLE IF EXISTS DETAIL_ADDRESS;
DROP TABLE IF EXISTS ADDRESS;
DROP TABLE IF EXISTS GOODS;
DROP TABLE IF EXISTS PERMISSION;
DROP TABLE IF EXISTS ACCOUNT;
DROP TABLE IF EXISTS SHOPPINGCART;
DROP TABLE IF EXISTS DISCOUNTTYPE;
DROP TABLE IF EXISTS DISCOUNT;
DROP TABLE IF EXISTS SHIPPINGMETHOD;
DROP TABLE IF EXISTS STATUS;
DROP TABLE IF EXISTS PAYMENT;
DROP TABLE IF EXISTS ORDERS;
DROP TABLE IF EXISTS BLOCKLIST;
DROP TABLE IF EXISTS SALES_ON;

CREATE TABLE COUNTRY (
    CountryID INTEGER PRIMARY KEY AUTOINCREMENT,
    CountryName VARCHAR(20)
);

CREATE TABLE AREA (
    AreaID INTEGER PRIMARY KEY AUTOINCREMENT,
    AreaName VARCHAR(20)
);

CREATE TABLE COUNTY (
    CountyID INTEGER PRIMARY KEY AUTOINCREMENT,
    CountyName VARCHAR(20)
);

CREATE TABLE DETAIL_ADDRESS (
    DAddressID INTEGER PRIMARY KEY AUTOINCREMENT,
    DetailAddress VARCHAR(200)
);

CREATE TABLE ADDRESS (
    AddressID INTEGER PRIMARY KEY AUTOINCREMENT,
    CountryID INTEGER,
    AreaID INTEGER,
    CountyID INTEGER,
    DAddressID INTEGER,
    FOREIGN KEY(CountryID) REFERENCES COUNTRY(CountryID),
    FOREIGN KEY(AreaID) REFERENCES AREA(AreaID),
    FOREIGN KEY(CountyID) REFERENCES COUNTY(CountyID),
    FOREIGN KEY(DAddressID) REFERENCES DETAIL_ADDRESS(DAddressID)
);

CREATE TABLE GOODS (
    GoodsID INTEGER PRIMARY KEY AUTOINCREMENT,
    GoodsName VARCHAR(20),
    GoodsType VARCHAR(20),
    Price INTEGER,
    StockQuantity INTEGER,
    Introduction VARCHAR(255),
    ImageName VARCHAR(255),
    CountryOfOrigin INTEGER,
    FOREIGN KEY(CountryOfOrigin) REFERENCES COUNTRY(CountryID)
);

CREATE TABLE PERMISSION (
    PermissionID INTEGER PRIMARY KEY AUTOINCREMENT,
    PermissionName VARCHAR(20)
);

CREATE TABLE ACCOUNT (
    AccountID INTEGER PRIMARY KEY AUTOINCREMENT,
    Account VARCHAR(20),
    Password VARCHAR(20),
    PermissionID INTEGER,
    UserName VARCHAR(20),
    IdentificationNumber VARCHAR(20),
    Gender VARCHAR(2),
    CellphoneNumber VARCHAR(10),
    Email VARCHAR(50),
    FOREIGN KEY(PermissionID) REFERENCES PERMISSION(PermissionID)
);

CREATE TABLE SHOPPINGCART (
    AccountID INTEGER,
    GoodsID INTEGER,
    Amount INTEGER,
    PRIMARY KEY(AccountID, GoodsID),
    FOREIGN KEY(AccountID) REFERENCES ACCOUNT(AccountID),
    FOREIGN KEY(GoodsID) REFERENCES GOODS(GoodsID)
);

CREATE TABLE DISCOUNTTYPE (
    DiscountTypeID INTEGER PRIMARY KEY AUTOINCREMENT,
    DiscountTypeName VARCHAR(20)
);

CREATE TABLE DISCOUNT (
    DiscountID INTEGER PRIMARY KEY AUTOINCREMENT,
    DiscountName VARCHAR(20),
    DiscountString VARCHAR(255),
    DiscountTypeID INTEGER,
    DiscountPercentage FLOAT,
    FOREIGN KEY(DiscountTypeID) REFERENCES DISCOUNTTYPE(DiscountTypeID)
);

CREATE TABLE SHIPPINGMETHOD (
    ShippingMethodID INTEGER PRIMARY KEY AUTOINCREMENT,
    ShippingMethodName VARCHAR(20)
);

CREATE TABLE STATUS (
    StatusID INTEGER PRIMARY KEY AUTOINCREMENT,
    StatusName VARCHAR(20)
);

CREATE TABLE PAYMENT (
    PaymentID INTEGER PRIMARY KEY AUTOINCREMENT,
    PaymentName VARCHAR(20)
);

CREATE TABLE ORDERS (
    OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
    AccountID INTEGER,
    Address TEXT,
    ShippingMethodID INTEGER,
    StatusID INTEGER,
    DATE TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    DiscountID INTEGER,
    PaymentID INTEGER,
    TotalPrice INTEGER,
    FOREIGN KEY(AccountID) REFERENCES ACCOUNT(AccountID),
    FOREIGN KEY(ShippingMethodID) REFERENCES SHIPPINGMETHOD(ShippingMethodID),
    FOREIGN KEY(StatusID) REFERENCES STATUS(StatusID),
    FOREIGN KEY(DiscountID) REFERENCES DISCOUNT(DiscountID),
    FOREIGN KEY(PaymentID) REFERENCES PAYMENT(PaymentID)
);

-- CREATE TABLE BLOCKLIST (
--     BlockID INTEGER PRIMARY KEY AUTOINCREMENT,
--     AccountID INTEGER,
--     FOREIGN KEY(AccountID) REFERENCES ACCOUNT(AccountID)
-- );

CREATE TABLE SALES_ON (
    OrderID INTEGER,
    GoodsID INTEGER,
    Amount INTEGER,
    PRIMARY KEY(OrderID, GoodsID),
    FOREIGN KEY(OrderID) REFERENCES ORDERS(OrderID),
    FOREIGN KEY(GoodsID) REFERENCES GOODS(GoodsID)
);

-- INSERT INTO PERMISSION VALUES (1, 'Admin');
-- INSERT INTO PERMISSION VALUES (2, 'Staff');
-- INSERT INTO PERMISSION VALUES (3, 'Customer');

-- INSERT INTO DISCOUNTTYPE VALUES (1, 'Shipping');
-- INSERT INTO DISCOUNTTYPE VALUES (2, 'Season');
-- INSERT INTO DISCOUNTTYPE VALUES (3, 'Special');

-- INSERT INTO DISCOUNT VALUES (1, 'shipping discount 1', 'shipping1', 1, 0.9);
-- INSERT INTO DISCOUNT VALUES (2, 'shipping discount 2', 'shipping2', 1, 0.8);
-- INSERT INTO DISCOUNT VALUES (3, 'season discount 1', 'season1', 2, 0.9);
-- INSERT INTO DISCOUNT VALUES (4, 'special discount 1', 'special1', 3, 0.6);