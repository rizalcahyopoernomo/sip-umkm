from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


# ==========================================
# 1. USER
# ==========================================
class User(db.Model, UserMixin):

    __tablename__ = 'user'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        index=True
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False
    )

    # ======================================
    # PROFILE IMAGE
    # ======================================
    profile_image = db.Column(

        db.String(255),

        nullable=True,

        default='default.png'
    )

    # ======================================
    # RELATIONSHIP
    # ======================================
    transactions = db.relationship(

        'Transaction',

        backref='cashier',

        lazy=True

        # ⚠ HAPUS cascade delete
        # agar histori transaksi aman
    )

    def __repr__(self):

        return f"<User {self.username}>"


# ==========================================
# 2. CATEGORY
# ==========================================
class Category(db.Model):

    __tablename__ = 'category'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(

        db.String(100),

        unique=True,

        nullable=False,

        index=True
    )

    def __repr__(self):

        return f"<Category {self.name}>"


# ==========================================
# 3. PRODUCT
# ==========================================
class Product(db.Model):

    __tablename__ = 'product'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(

        db.String(100),

        nullable=False,

        index=True
    )

    price = db.Column(

        db.Float,

        nullable=False
    )

    cost = db.Column(

        db.Float,

        default=0,

        nullable=False
    )

    stock = db.Column(

        db.Integer,

        default=0,

        nullable=False
    )

    min_stock = db.Column(

        db.Integer,

        default=5,

        nullable=False
    )

    image = db.Column(

        db.String(100),

        default='default.jpg'
    )

    is_active = db.Column(

        db.Boolean,

        default=True
    )

    # ======================================
    # DSS RESTOCK CONFIG
    # ======================================
    restock_cycle = db.Column(

        db.Integer,

        default=3,

        nullable=False
    )

    category_id = db.Column(

        db.Integer,

        db.ForeignKey(
            'category.id',
            ondelete="CASCADE"
        ),

        nullable=False,

        index=True
    )

    category = db.relationship(

        'Category',

        backref=db.backref(

            'products',

            lazy=True
        )
    )

    def __repr__(self):

        return (
            f"<Product {self.name} | "
            f"Stock {self.stock}>"
        )


# ==========================================
# 4. TRANSACTION
# ==========================================
class Transaction(db.Model):

    __tablename__ = 'transactions'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    invoice_number = db.Column(

        db.String(50),

        unique=True,

        nullable=False,

        index=True
    )

    cashier_id = db.Column(

        db.Integer,

        db.ForeignKey(
            'user.id',
            ondelete="CASCADE"
        ),

        nullable=False,

        index=True
    )

    customer_name = db.Column(

        db.String(100),

        default='Pelanggan Umum',

        nullable=False
    )

    subtotal = db.Column(

        db.Float,

        nullable=False
    )

    discount = db.Column(

        db.Float,

        default=0,

        nullable=False
    )

    total_amount = db.Column(

        db.Float,

        nullable=False
    )

    payment_method = db.Column(

        db.String(50),

        nullable=False
    )

    amount_paid = db.Column(

        db.Float,

        nullable=False
    )

    change_amount = db.Column(

        db.Float,

        nullable=False
    )

    timestamp = db.Column(

        db.DateTime,

        default=datetime.utcnow,

        nullable=False,

        index=True
    )

    items = db.relationship(

        'TransactionItem',

        backref='transaction',

        lazy=True
    )

    def __repr__(self):

        return (
            f"<Transaction "
            f"{self.invoice_number}>"
        )


# ==========================================
# 5. TRANSACTION ITEM
# ==========================================
class TransactionItem(db.Model):

    __tablename__ = 'transaction_items'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    transaction_id = db.Column(

        db.Integer,

        db.ForeignKey(
            'transactions.id',
            ondelete="CASCADE"
        ),

        nullable=False,

        index=True
    )

    product_id = db.Column(

        db.Integer,

        db.ForeignKey('product.id'),

        nullable=False,

        index=True
    )

    product_name = db.Column(

        db.String(100),

        nullable=False
    )

    price_at_time = db.Column(

        db.Float,

        nullable=False
    )

    qty = db.Column(

        db.Integer,

        nullable=False
    )

    subtotal = db.Column(

        db.Float,

        nullable=False
    )

    # ======================================
    # ML / ANALYTICS TIMESTAMP
    # ======================================
    created_at = db.Column(

        db.DateTime,

        default=datetime.utcnow,

        nullable=False,

        index=True
    )

    # ======================================
    # PRODUCT RELATIONSHIP
    # ======================================
    product = db.relationship(

        'Product',

        backref=db.backref(

            'transaction_items',

            lazy=True
        )
    )

    def __repr__(self):

        return (
            f"<Item "
            f"{self.product_name} "
            f"x{self.qty}>"
        )


# ==========================================
# 6. STOCK MOVEMENT
# ==========================================
class StockMovement(db.Model):

    __tablename__ = 'stock_movements'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    product_id = db.Column(

        db.Integer,

        db.ForeignKey(
            'product.id',
            ondelete="CASCADE"
        ),

        nullable=False,

        index=True
    )

    # ======================================
    # TYPE:
    # IN / OUT / ADJUST
    # ======================================
    type = db.Column(

        db.String(20),

        nullable=False,

        index=True
    )

    qty = db.Column(

        db.Integer,

        nullable=False
    )

    note = db.Column(

        db.String(255),

        nullable=True
    )

    created_at = db.Column(

        db.DateTime,

        default=datetime.utcnow,

        nullable=False,

        index=True
    )

    product = db.relationship(

        'Product',

        backref=db.backref(

            'stock_movements',

            lazy=True
        )
    )

    def __repr__(self):

        return (
            f"<StockMovement "
            f"{self.type} "
            f"{self.qty}>"
        )