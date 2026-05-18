from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    session
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from models.entities import (
    User,
    db
)

from services.auth_service import (
    AuthService,
    bcrypt
)

# =========================================
# LOGGER
# =========================================
from utils.logger import (
    logger
)


# =========================================
# AUTH BLUEPRINT
# =========================================
auth_bp = Blueprint(

    'auth',

    __name__,

    template_folder='../templates/auth'
)


# =========================================
# LOGIN
# =========================================
@auth_bp.route(
    '/login',
    methods=['GET', 'POST']
)
def login():
    """
    Login Owner & Cashier
    """

    try:

        # =====================================
        # AUTO REDIRECT IF LOGGED IN
        # =====================================
        if current_user.is_authenticated:

            logger.info(

                f'AUTO REDIRECT | USER: '
                f'{current_user.username} | '
                f'ROLE: {current_user.role}'
            )

            if current_user.role == 'owner':

                return redirect(
                    url_for('owner.dashboard')
                )

            elif current_user.role == 'cashier':

                return redirect(
                    url_for('cashier.pos')
                )

        # =====================================
        # LOGIN PROCESS
        # =====================================
        if request.method == 'POST':

            username = request.form.get(
                'username'
            )

            password = request.form.get(
                'password'
            )

            # =================================
            # VERIFY USER
            # =================================
            user = AuthService.verify_user(

                username,

                password
            )

            # =================================
            # LOGIN SUCCESS
            # =================================
            if user:

                login_user(user)

                logger.info(

                    f'LOGIN SUCCESS | '
                    f'USER: {user.username} | '
                    f'ROLE: {user.role}'
                )

                flash(

                    f'Selamat datang, '
                    f'{user.username}!',

                    'success'
                )

                # =============================
                # ROLE REDIRECT
                # =============================
                if user.role == 'owner':

                    return redirect(

                        url_for(
                            'owner.dashboard'
                        )
                    )

                elif user.role == 'cashier':

                    return redirect(

                        url_for(
                            'cashier.pos'
                        )
                    )

            # =================================
            # LOGIN FAILED
            # =================================
            logger.warning(

                f'LOGIN FAILED | '
                f'USERNAME: {username}'
            )

            flash(

                'Username atau Password salah!',

                'danger'
            )

        return render_template(
            'auth/login.html'
        )

    except Exception as error:

        logger.error(

            f'LOGIN ERROR | '
            f'{str(error)}'
        )

        flash(

            'Terjadi kesalahan saat login.',

            'danger'
        )

        return render_template(
            'auth/login.html'
        )


# =========================================
# LOGOUT
# =========================================
@auth_bp.route('/logout')
@login_required
def logout():
    """
    Logout user & clear session
    """

    try:

        # =====================================
        # SAVE USER BEFORE LOGOUT
        # =====================================
        username = current_user.username

        role = current_user.role

        # =====================================
        # FLASK LOGIN LOGOUT
        # =====================================
        logout_user()

        # =====================================
        # CLEAR SESSION
        # =====================================
        session.clear()

        # =====================================
        # LOG SUCCESS
        # =====================================
        logger.info(

            f'LOGOUT SUCCESS | '
            f'USER: {username} | '
            f'ROLE: {role}'
        )

        flash(

            'Kamu telah keluar dari sistem.',

            'info'
        )

    except Exception as error:

        logger.error(

            f'LOGOUT ERROR | '
            f'{str(error)}'
        )

    return redirect(
        url_for('auth.login')
    )