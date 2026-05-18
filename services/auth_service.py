from flask_bcrypt import Bcrypt

from models.entities import (
    db,
    User
)

# =========================================
# INIT BCRYPT
# =========================================
bcrypt = Bcrypt()


class AuthService:

    # =====================================
    # CREATE USER
    # =====================================
    @staticmethod
    def create_user(
        username,
        password,
        role
    ):
        """
        Membuat user baru
        dengan password terenkripsi
        """

        try:

            # =============================
            # VALIDASI USERNAME
            # =============================
            existing_user = (
                User.query.filter_by(
                    username=username
                ).first()
            )

            if existing_user:

                raise Exception(
                    "Username sudah digunakan"
                )

            # =============================
            # HASH PASSWORD
            # =============================
            hashed_pw = (

                bcrypt
                .generate_password_hash(
                    password
                )

                .decode('utf-8')
            )

            # =============================
            # CREATE USER
            # =============================
            new_user = User(

                username=username,

                password=hashed_pw,

                role=role
            )

            db.session.add(new_user)

            db.session.commit()

            return new_user

        except Exception:

            db.session.rollback()

            return None

    # =====================================
    # VERIFY USER
    # =====================================
    @staticmethod
    def verify_user(
        username,
        password
    ):
        """
        Validasi login user
        """

        try:

            user = (
                User.query.filter_by(
                    username=username
                ).first()
            )

            if (
                user and
                bcrypt.check_password_hash(
                    user.password,
                    password
                )
            ):

                return user

            return None

        except Exception:

            return None