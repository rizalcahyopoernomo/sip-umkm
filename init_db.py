from app import app
from models.entities import db


# =========================================
# INIT DATABASE
# =========================================
def initialize_database():

    with app.app_context():

        # =========================================
        # CREATE ALL TABLES
        # =========================================
        db.create_all()

        print("\n===================================")
        print("DATABASE BERHASIL DIINITIALISASI")
        print("===================================\n")


# =========================================
# MAIN
# =========================================
if __name__ == "__main__":

    initialize_database()