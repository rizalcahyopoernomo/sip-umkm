import os
from datetime import timedelta


# =========================================
# BASE DIRECTORY
# =========================================
BASE_DIR = os.path.abspath(
    os.path.dirname(__file__)
)


# =========================================
# DATA DIRECTORY
# =========================================
DATA_DIR = os.path.join(
    BASE_DIR,
    'data'
)

os.makedirs(
    DATA_DIR,
    exist_ok=True
)


# =========================================
# DATABASE FILE
# =========================================
DATABASE_FILE = os.path.join(
    DATA_DIR,
    'tps_umkm.db'
)


# =========================================
# UPLOAD DIRECTORY
# =========================================
UPLOAD_DIR = os.path.join(
    BASE_DIR,
    'static',
    'products'
)

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


# =========================================
# MAIN CONFIG
# =========================================
class Config:

    # =====================================
    # FLASK CORE
    # =====================================
    SECRET_KEY = (
        os.environ.get(
            'SECRET_KEY'
        )
        or
        '8c4f2d91b7a34ef6c0d8fa521ab93e7d2f84c6a1b95e73fd4a0b2e1c9f6d8ab3'
    )

    DEBUG = False


    # =====================================
    # DATABASE
    # =====================================
    SQLALCHEMY_DATABASE_URI = (
        f"sqlite:///{DATABASE_FILE}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # =====================================
    # SESSION
    # =====================================
    SESSION_PERMANENT = False

    REMEMBER_COOKIE_DURATION = timedelta(days=1)

    REMEMBER_COOKIE_SECURE = False

    REMEMBER_COOKIE_HTTPONLY = True

    SESSION_COOKIE_HTTPONLY = True

    SESSION_COOKIE_SAMESITE = 'Lax'


    # =====================================
    # FILE UPLOAD
    # =====================================
    UPLOAD_FOLDER = UPLOAD_DIR

    MAX_CONTENT_LENGTH = (
        5 * 1024 * 1024
    )


    # =====================================
    # STATIC CACHE
    # =====================================
    SEND_FILE_MAX_AGE_DEFAULT = 0


    # =====================================
    # OPTIONAL INIT
    # =====================================
    @staticmethod
    def init_app(app):

        pass