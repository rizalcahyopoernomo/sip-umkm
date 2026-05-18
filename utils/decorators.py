from functools import wraps
from flask import redirect, url_for, flash, abort
from flask_login import current_user


# =========================
# LOGIN REQUIRED (CUSTOM)
# =========================
def login_required_custom(func):
    """
    Memastikan user sudah login.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):

        if not current_user.is_authenticated:
            flash("Silakan login terlebih dahulu.", "warning")
            return redirect(url_for('auth.login'))

        return func(*args, **kwargs)

    return wrapper


# =========================
# OWNER REQUIRED
# =========================
def owner_required(func):
    """
    Hanya user dengan role OWNER yang boleh akses.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):

        # 🔒 Belum login
        if not current_user.is_authenticated:
            flash("Silakan login terlebih dahulu.", "warning")
            return redirect(url_for('auth.login'))

        # 🔒 Bukan owner
        if current_user.role != 'owner':
            flash("Akses ditolak! Hanya untuk Owner.", "danger")

            # 🔥 OPSI AMAN (RECOMMENDED)
            return abort(403)

            # 🔁 OPSI ALTERNATIF:
            # return redirect(url_for('cashier.pos'))

        return func(*args, **kwargs)

    return wrapper