from app import app

from models.entities import (
    db,
    User,
    Product,
    Category
)

from services.auth_service import AuthService


# =========================================
# SEED DEFAULT USERS
# =========================================
def seed_users():

    # =========================
    # DEFAULT OWNER
    # =========================
    if not User.query.filter_by(
        username='admin'
    ).first():

        AuthService.create_user(

            'admin',

            'admin123',

            'owner'
        )

        print("✔ Owner default berhasil dibuat")

    else:

        print("⚠ Owner default sudah ada")

    # =========================
    # DEFAULT CASHIER
    # =========================
    if not User.query.filter_by(
        username='kasir1'
    ).first():

        AuthService.create_user(

            'kasir1',

            'kasir123',

            'cashier'
        )

        print("✔ Cashier default berhasil dibuat")

    else:

        print("⚠ Cashier default sudah ada")


# =========================================
# SEED CATEGORY
# =========================================
def seed_categories():

    if not Category.query.first():

        categories = [

            Category(
                name='Makanan'
            ),

            Category(
                name='Minuman'
            ),

            Category(
                name='Rokok'
            )
        ]

        db.session.add_all(categories)

        db.session.commit()

        print("✔ Category berhasil dibuat")

    else:

        print("⚠ Category sudah tersedia")


# =========================================
# SEED PRODUCTS
# =========================================
def seed_products():

    if Product.query.first():

        print("⚠ Product sudah tersedia")

        return

    kategori = Category.query.all()

    if len(kategori) < 3:

        print("❌ Category belum lengkap")

        return

    products = [

        Product(

            name='Indomie Goreng',

            price=3500,

            stock=100,

            category_id=kategori[0].id,

            image='indomie.jpg',

            cost=2500
        ),

        Product(

            name='Aqua 600ml',

            price=5000,

            stock=50,

            category_id=kategori[1].id,

            image='aqua.jpg',

            cost=3500
        ),

        Product(

            name='Teh Botol Sosro',

            price=3500,

            stock=30,

            category_id=kategori[1].id,

            image='teh_botol.jpg',

            cost=2500
        )
    ]

    db.session.add_all(products)

    db.session.commit()

    print("✔ Product berhasil dibuat")


# =========================================
# RUN ALL SEED
# =========================================
def run_seed():

    with app.app_context():

        print("\n===================================")
        print("START SEED DATABASE")
        print("===================================\n")

        seed_users()

        seed_categories()

        seed_products()

        print("\n===================================")
        print("SEED DATABASE SELESAI")
        print("===================================\n")


# =========================================
# MAIN
# =========================================
if __name__ == "__main__":

    run_seed()