from flask import (
    Flask,
    redirect,
    url_for,
    render_template,
    send_from_directory
)

from flask_login import (
    LoginManager,
    current_user
)

from sqlalchemy.exc import (
    SQLAlchemyError,
    IntegrityError
)

from routes.account_routes import (
    account_bp
)

import os


# =========================================
# LOGGER
# =========================================
from utils.logger import (
    logger
)


# =========================================
# CONFIG
# =========================================
from config import Config


# =========================================
# DATABASE & MODELS
# =========================================
from models.entities import (
    db,
    User
)


# =========================================
# SECURITY
# =========================================
from services.auth_service import (
    bcrypt
)


# =========================================
# BLUEPRINTS
# =========================================
from routes.auth_routes import (
    auth_bp
)

from routes.owner_routes import (
    owner_bp
)

from routes.cashier_routes import (
    cashier_bp
)


# =========================================
# INIT FLASK APP
# =========================================
app = Flask(__name__)

app.register_blueprint(
    account_bp
)

app.config['PROPAGATE_EXCEPTIONS'] = False


# =========================================
# APPLICATION STARTUP LOG
# =========================================
logger.info(
    'SIP-UMKM application started'
)


# =========================================
# BASE DIRECTORY
# =========================================
BASE_DIR = os.path.abspath(
    os.path.dirname(__file__)
)


# =========================================
# DATABASE DIRECTORY
# =========================================
data_dir = os.path.join(
    BASE_DIR,
    'data'
)

os.makedirs(
    data_dir,
    exist_ok=True
)


# =========================================
# DATABASE PATH
# =========================================
db_path = os.path.join(
    data_dir,
    'tps_umkm.db'
)


# =========================================
# LOAD CONFIG
# =========================================
app.config.from_object(
    Config
)

Config.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"sqlite:///{db_path}"
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# =========================================
# SESSION & AUTH CONFIG
# =========================================
app.config['SESSION_PERMANENT'] = False

app.config['REMEMBER_COOKIE_DURATION'] = 0

app.config['REMEMBER_COOKIE_SECURE'] = False

app.config['REMEMBER_COOKIE_HTTPONLY'] = True


# =========================================
# JINJA FILTER
# =========================================
def rupiah(value):

    try:

        return (
            "Rp {:,.0f}"
            .format(value)
            .replace(",", ".")
        )

    except Exception:

        logger.error(
            f'RUPIAH FILTER ERROR | {str(value)}'
        )

        return "Rp 0"


app.jinja_env.filters['rupiah'] = rupiah


# =========================================
# INIT DATABASE
# =========================================
db.init_app(app)


# =========================================
# INIT SECURITY
# =========================================
bcrypt.init_app(app)


# =========================================
# LOGIN MANAGER
# =========================================
login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = 'auth.login'

login_manager.login_message = (
    "Silakan login terlebih dahulu"
)

login_manager.login_message_category = (
    "warning"
)

login_manager.session_protection = (
    "strong"
)


# =========================================
# USER LOADER
# =========================================
@login_manager.user_loader
def load_user(user_id):

    try:

        return db.session.get(
            User,
            int(user_id)
        )

    except Exception as error:

        logger.error(
            f'USER LOAD FAILED | {str(error)}'
        )

        return None


# =========================================
# REGISTER BLUEPRINT
# =========================================
app.register_blueprint(
    auth_bp
)

app.register_blueprint(
    owner_bp,
    url_prefix='/owner'
)

app.register_blueprint(
    cashier_bp,
    url_prefix='/cashier'
)


# =========================================
# ROOT ROUTE
# =========================================
@app.route('/')
def index():

    try:

        if not current_user.is_authenticated:

            logger.info(
                'UNAUTHENTICATED ACCESS | Redirect to login'
            )

            return redirect(
                url_for('auth.login')
            )

        if current_user.role == 'owner':

            logger.info(
                f'OWNER ACCESS | USER: {current_user.username}'
            )

            return redirect(
                url_for('owner.dashboard')
            )

        if current_user.role == 'cashier':

            logger.info(
                f'CASHIER ACCESS | USER: {current_user.username}'
            )

            return redirect(
                url_for('cashier.pos')
            )

        logger.warning(
            'UNKNOWN ROLE DETECTED'
        )

        return redirect(
            url_for('auth.login')
        )

    except Exception as error:

        logger.error(
            f'ROOT ROUTE ERROR | {str(error)}'
        )

        return redirect(
            url_for('auth.login')
        )

# =========================================
# FAVICON ROUTE
# =========================================
@app.route('/favicon.ico')
def favicon():

    return send_from_directory(

        os.path.join(
            app.root_path,
            'static'
        ),

        'favicon.ico',

        mimetype='image/vnd.microsoft.icon'
    )

# =========================================
# HEALTH CHECK
# =========================================
@app.route('/health')
def health():

    try:

        logger.info(
            'HEALTH CHECK SUCCESS'
        )

        return {
            "status": "ok",
            "app": "SIP-UMKM"
        }

    except Exception as error:

        logger.error(
            f'HEALTH CHECK ERROR | {str(error)}'
        )

        return {
            "status": "error"
        }, 500


# =========================================
# 404 ERROR HANDLER
# =========================================
@app.errorhandler(404)
def page_not_found(error):

    logger.warning(
        f'404 PAGE NOT FOUND | PATH: {str(error)}'
    )

    return render_template(

        'errors/404.html'

    ), 404


# =========================================
# 500 ERROR HANDLER
# =========================================
@app.errorhandler(500)
def internal_server_error(error):

    try:

        db.session.rollback()

    except Exception as rollback_error:

        logger.error(
            f'ROLLBACK FAILED | {str(rollback_error)}'
        )

    logger.error(
        f'500 INTERNAL SERVER ERROR | {str(error)}'
    )

    return render_template(

        'errors/500.html'

    ), 500


# =========================================
# DATABASE ERROR HANDLER
# =========================================
@app.errorhandler(SQLAlchemyError)
@app.errorhandler(IntegrityError)
def handle_database_error(error):

    try:

        db.session.rollback()

    except Exception as rollback_error:

        logger.error(
            f'DATABASE ROLLBACK FAILED | {str(rollback_error)}'
        )

    logger.error(
        f'DATABASE ERROR | {str(error)}'
    )

    return render_template(

        'errors/500.html'

    ), 500


# =========================================
# GLOBAL AFTER REQUEST
# =========================================
@app.after_request
def add_header(response):

    response.headers["Cache-Control"] = (
        "no-cache, no-store, must-revalidate"
    )

    response.headers["Pragma"] = "no-cache"

    response.headers["Expires"] = "0"

    return response


# =========================================
# RUN APPLICATION
# =========================================
if __name__ == '__main__':

    logger.info(
        'FLASK DEVELOPMENT SERVER STARTED'
    )

    try:

        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False
        )

    except Exception as error:

        logger.error(
            f'FLASK STARTUP ERROR | {str(error)}'
        )