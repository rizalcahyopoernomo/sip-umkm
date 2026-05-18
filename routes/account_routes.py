from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app
)

from flask_login import (
    login_required,
    current_user
)

from werkzeug.utils import (
    secure_filename
)

from models.entities import (
    db,
    User
)

# =========================================
# LOGGER
# =========================================
from utils.logger import (
    logger
)

import os

from datetime import (
    datetime
)


# =========================================
# BLUEPRINT
# =========================================
account_bp = Blueprint(

    'account',

    __name__,

    url_prefix='/owner/account'
)


# =========================================
# ALLOWED EXTENSIONS
# =========================================
ALLOWED_EXTENSIONS = {

    'png',

    'jpg',

    'jpeg',

    'webp'
}


# =========================================
# VALIDATE FILE
# =========================================
def allowed_file(filename):

    return (

        '.' in filename

        and

        filename.rsplit('.', 1)[1].lower()

        in ALLOWED_EXTENSIONS
    )


# =========================================
# ACCOUNT SETTINGS
# =========================================
@account_bp.route(
    '/',
    methods=['GET', 'POST']
)
@login_required
def settings():

    try:

        # =====================================
        # ONLY OWNER
        # =====================================
        if current_user.role != 'owner':

            logger.warning(

                f'UNAUTHORIZED ACCOUNT ACCESS | '
                f'USER: {current_user.username}'
            )

            flash(

                'Akses ditolak!',

                'danger'
            )

            return redirect(
                url_for('auth.login')
            )

        # =====================================
        # ACCOUNT PAGE ACCESS
        # =====================================
        logger.info(

            f'ACCOUNT SETTINGS ACCESS | '
            f'USER: {current_user.username}'
        )

        # =====================================
        # UPLOAD PROFILE IMAGE
        # =====================================
        if request.method == 'POST':

            file = request.files.get(
                'profile_image'
            )

            # =================================
            # FILE VALIDATION
            # =================================
            if not file or file.filename == '':

                logger.warning(

                    f'UPLOAD FAILED | '
                    f'EMPTY FILE | '
                    f'USER: {current_user.username}'
                )

                flash(

                    'Pilih file gambar terlebih dahulu!',

                    'warning'
                )

                return redirect(
                    url_for('account.settings')
                )

            # =================================
            # EXTENSION VALIDATION
            # =================================
            if not allowed_file(file.filename):

                logger.warning(

                    f'UPLOAD FAILED | '
                    f'INVALID EXTENSION | '
                    f'USER: {current_user.username}'
                )

                flash(

                    'Format gambar tidak didukung!',

                    'danger'
                )

                return redirect(
                    url_for('account.settings')
                )

            try:

                # =============================
                # SECURE FILENAME
                # =============================
                extension = file.filename.rsplit(

                    '.',

                    1

                )[1].lower()

                filename = (

                    f"profile_"

                    f"{current_user.id}_"

                    f"{datetime.now().strftime('%Y%m%d%H%M%S')}"

                    f".{extension}"
                )

                filename = secure_filename(
                    filename
                )

                # =============================
                # UPLOAD PATH
                # =============================
                upload_folder = os.path.join(

                    current_app.root_path,

                    'static',

                    'uploads',

                    'profile'
                )

                os.makedirs(

                    upload_folder,

                    exist_ok=True
                )

                file_path = os.path.join(

                    upload_folder,

                    filename
                )

                # =============================
                # SAVE FILE
                # =============================
                file.save(file_path)

                # =============================
                # DELETE OLD IMAGE
                # =============================
                if (

                    current_user.profile_image

                    and

                    current_user.profile_image != 'default.png'
                ):

                    old_file = os.path.join(

                        upload_folder,

                        current_user.profile_image
                    )

                    if os.path.exists(old_file):

                        os.remove(old_file)

                        logger.info(

                            f'OLD PROFILE IMAGE REMOVED | '
                            f'USER: {current_user.username}'
                        )

                # =============================
                # UPDATE DATABASE
                # =============================
                current_user.profile_image = filename

                db.session.commit()

                logger.info(

                    f'PROFILE UPDATED | '
                    f'USER: {current_user.username}'
                )

                flash(

                    'Foto profile berhasil diperbarui!',

                    'success'
                )

            except Exception as error:

                db.session.rollback()

                logger.error(

                    f'PROFILE UPLOAD ERROR | '
                    f'USER: {current_user.username} | '
                    f'{str(error)}'
                )

                flash(

                    'Terjadi kesalahan saat upload foto!',

                    'danger'
                )

            return redirect(
                url_for('account.settings')
            )

        return render_template(
            'owner/account.html'
        )

    except Exception as error:

        logger.error(

            f'ACCOUNT SETTINGS ERROR | '
            f'{str(error)}'
        )

        flash(

            'Terjadi kesalahan sistem.',

            'danger'
        )

        return redirect(
            url_for('owner.dashboard')
        )