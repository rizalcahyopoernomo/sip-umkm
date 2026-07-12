from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    url_for,
    redirect,
    flash
)

from flask_login import (
    login_required,
    current_user
)
from werkzeug.utils import secure_filename

from sqlalchemy import func

from datetime import (
    datetime,
    time
)

from models.entities import (
    db,
    Product,
    Category,
    Transaction
)

# =========================
# SERVICES
# =========================
from services.pos_service import POSService
from services.invoice_service import InvoiceService

# =========================
# LOGGER
# =========================
from utils.logger import logger

import os
import uuid


cashier_bp = Blueprint(
    'cashier',
    __name__
)


# =========================================
# ALLOWED IMAGE EXTENSIONS
# =========================================
ALLOWED_EXTENSIONS = {
    'png',
    'jpg',
    'jpeg',
    'webp'
}


# =========================================
# VALIDATE FILE EXTENSION
# =========================================
def allowed_file(filename):

    return (
        '.' in filename
        and
        filename.rsplit('.', 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =========================
# 1. HALAMAN POS
# =========================
@cashier_bp.route('/pos')
@login_required
def pos():

    try:

        products = (

            Product.query

            .filter_by(
                is_active=True
            )

            .all()
        )

        categories = Category.query.all()

        logger.info(

            f'POS ACCESS | '
            f'CASHIER: {current_user.username}'
        )

        

        return render_template(

            'cashier/pos.html',

            products=products,

            categories=categories
        )

    except Exception as error:

        logger.error(

            f'POS PAGE ERROR | '
            f'{str(error)}'
        )

        flash(
            'Gagal membuka halaman POS',
            'danger'
        )

        return redirect(
            url_for('auth.login')
        )


# =========================
# 2. LOGIKA CHECKOUT
# =========================
@cashier_bp.route(
    '/checkout',
    methods=['POST']
)
@login_required
def checkout():

    try:

        data = request.get_json()

        # =========================
        # VALIDASI REQUEST
        # =========================
        if not data:

            logger.warning(

                f'CHECKOUT FAILED | '
                f'INVALID REQUEST | '
                f'CASHIER: {current_user.username}'
            )

            return jsonify({

                "success": False,

                "message": "Request tidak valid"

            }), 400

        # =========================
        # VALIDASI ITEMS
        # =========================
        if 'items' not in data:

            logger.warning(

                f'CHECKOUT FAILED | '
                f'ITEM DATA MISSING | '
                f'CASHIER: {current_user.username}'
            )

            return jsonify({

                "success": False,

                "message": "Data item tidak ditemukan"

            }), 400

        items = data.get('items', [])

        # =========================
        # VALIDASI CART KOSONG
        # =========================
        if not items:

            logger.warning(

                f'CHECKOUT FAILED | '
                f'EMPTY CART | '
                f'CASHIER: {current_user.username}'
            )

            return jsonify({

                "success": False,

                "message": "Keranjang masih kosong"

            }), 400

        try:

            # =========================
            # VALIDASI AMOUNT PAID
            # =========================
            amount_paid = float(
                data.get('amount_paid', 0)
            )

            if amount_paid <= 0:

                logger.warning(

                    f'CHECKOUT FAILED | '
                    f'INVALID PAYMENT | '
                    f'CASHIER: {current_user.username}'
                )

                return jsonify({

                    "success": False,

                    "message": "Nominal pembayaran tidak valid"

                }), 400

        except Exception as error:

            logger.error(

                f'PAYMENT VALIDATION ERROR | '
                f'{str(error)}'
            )

            return jsonify({

                "success": False,

                "message": "Format pembayaran tidak valid"

            }), 400

        # =========================
        # FORMAT CART
        # =========================
        cart_data = []

        for item in items:

            # =========================
            # VALIDASI PRODUCT ID
            # =========================
            product_id = item.get('id')

            if not product_id:

                logger.warning(

                    f'CHECKOUT FAILED | '
                    f'INVALID PRODUCT ID'
                )

                return jsonify({

                    "success": False,

                    "message": "Produk tidak valid"

                }), 400

            # =========================
            # VALIDASI PRODUCT EXIST
            # =========================
            product = db.session.get(
                Product,
                product_id
            )

            if not product:

                logger.warning(

                    f'CHECKOUT FAILED | '
                    f'PRODUCT NOT FOUND'
                )

                return jsonify({

                    "success": False,

                    "message": "Produk tidak ditemukan"

                }), 400

            # =========================
            # VALIDASI QTY
            # =========================
            try:

                qty = int(
                    item.get('qty', 0)
                )

            except Exception as error:

                logger.error(

                    f'QTY VALIDATION ERROR | '
                    f'{str(error)}'
                )

                return jsonify({

                    "success": False,

                    "message": "Qty produk tidak valid"

                }), 400

            if qty <= 0:

                logger.warning(

                    f'CHECKOUT FAILED | '
                    f'INVALID QTY | '
                    f'PRODUCT: {product.name}'
                )

                return jsonify({

                    "success": False,

                    "message": f"Qty produk {product.name} tidak valid"

                }), 400

            # =========================
            # VALIDASI STOCK
            # =========================
            if product.stock < qty:

                logger.warning(

                    f'STOCK NOT ENOUGH | '
                    f'PRODUCT: {product.name} | '
                    f'STOCK: {product.stock}'
                )

                return jsonify({

                    "success": False,

                    "message": f"Stok {product.name} tidak mencukupi"

                }), 400

            # =========================
            # BUILD CART
            # =========================
            cart_data.append({

                "product_id": product_id,

                "qty": qty
            })

        # =========================
        # PROCESS TRANSACTION
        # =========================
        success, message, invoice_number = (

            POSService.process_transaction(

                cart_data=cart_data,

                cashier_id=current_user.id,

                customer_name=data.get(

                    'customer',

                    'Pelanggan Umum'
                ),

                payment_method=data.get(

                    'payment_method',

                    'Tunai'
                ),

                amount_paid=amount_paid
            )
        )

        # =========================
        # FAILED RESPONSE
        # =========================
        if not success:

            logger.warning(

                f'TRANSACTION FAILED | '
                f'CASHIER: {current_user.username}'
            )

            return jsonify({

                "success": False,

                "message": message

            }), 400

        # =========================
        # TRANSACTION SUCCESS
        # =========================
        logger.info(

            f'TRANSACTION SUCCESS | '
            f'CASHIER: {current_user.username} | '
            f'TOTAL: {amount_paid}'
        )

        logger.info(

            f'INVOICE CREATED | '
            f'INVOICE: {invoice_number}'
        )

        logger.info(

            f'PAYMENT SUCCESS | '
            f'METHOD: {data.get("payment_method", "Tunai")}'
        )

        # =========================
        # SUCCESS RESPONSE
        # =========================
        return jsonify({

            "success": True,

            "message": message,

            "invoice_number": invoice_number,

            "redirect_url": url_for(

                'cashier.invoice_detail',

                invoice_number=invoice_number
            )
        })

    except Exception as error:

        db.session.rollback()

        logger.error(

            f'CHECKOUT ERROR | '
            f'{str(error)}'
        )

        return jsonify({

            "success": False,

            "message": "Terjadi kesalahan pada checkout"

        }), 400


# =========================
# 3. HALAMAN HISTORI
# =========================
@cashier_bp.route('/history')
@login_required
def history():

    try:

        recent_transactions = (

            Transaction.query

            .filter_by(
                cashier_id=current_user.id
            )

            .order_by(
                Transaction.timestamp.desc()
            )

            .limit(20)

            .all()
        )

        logger.info(

            f'TRANSACTION HISTORY ACCESS | '
            f'CASHIER: {current_user.username}'
        )

        return render_template(

            'cashier/history.html',

            transactions=recent_transactions
        )

    except Exception as error:

        logger.error(

            f'HISTORY PAGE ERROR | '
            f'{str(error)}'
        )

        flash(
            'Gagal memuat histori transaksi',
            'danger'
        )

        return redirect(
            url_for('cashier.pos')
        )


# =========================
# 4. CASHIER INVOICE DETAIL
# =========================
@cashier_bp.route(
    '/invoice/<invoice_number>'
)
@login_required
def invoice_detail(invoice_number):

    try:

        invoice = InvoiceService.get_invoice(
            invoice_number
        )

        # =========================
        # INVOICE NOT FOUND
        # =========================
        if not invoice:

            logger.warning(

                f'INVOICE NOT FOUND | '
                f'INVOICE: {invoice_number}'
            )

            return redirect(
                url_for('cashier.pos')
            )

        # =========================
        # INVOICE SUMMARY
        # =========================
        summary = InvoiceService.invoice_summary(
            invoice
        )

        logger.info(

            f'INVOICE DETAIL ACCESS | '
            f'INVOICE: {invoice_number}'
        )

        return render_template(

            'cashier/invoice_detail.html',

            invoice=invoice,

            summary=summary
        )

    except Exception as error:

        logger.error(

            f'INVOICE DETAIL ERROR | '
            f'{str(error)}'
        )

        flash(
            'Gagal membuka invoice',
            'danger'
        )

        return redirect(
            url_for('cashier.pos')
        )


# =========================
# 5. CASHIER PROFILE
# =========================
@cashier_bp.route(
    '/profile',
    methods=['GET', 'POST']
)
@login_required
def profile():

    try:

        # =========================
        # VALIDASI ROLE
        # =========================
        if current_user.role != 'cashier':

            logger.warning(

                f'UNAUTHORIZED PROFILE ACCESS | '
                f'USER: {current_user.username}'
            )

            flash(
                'Akses ditolak!',
                'danger'
            )

            return redirect(
                url_for('cashier.pos')
            )

        # =========================
        # HANDLE IMAGE UPLOAD
        # =========================
        if request.method == 'POST':

            file = request.files.get(
                'profile_image'
            )

            # FILE EMPTY
            if not file:

                logger.warning(

                    f'UPLOAD FAILED | '
                    f'FILE EMPTY | '
                    f'USER: {current_user.username}'
                )

                flash(
                    'File tidak ditemukan!',
                    'danger'
                )

                return redirect(
                    url_for('cashier.profile')
                )

            # EMPTY FILENAME
            if file.filename == '':

                logger.warning(

                    f'UPLOAD FAILED | '
                    f'EMPTY FILENAME | '
                    f'USER: {current_user.username}'
                )

                flash(
                    'Pilih gambar terlebih dahulu!',
                    'warning'
                )

                return redirect(
                    url_for('cashier.profile')
                )

            # INVALID EXTENSION
            if not allowed_file(
                file.filename
            ):

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
                    url_for('cashier.profile')
                )

            try:

                extension = (
                    file.filename
                    .rsplit('.', 1)[1]
                    .lower()
                )

                filename = (

                    f"cashier_"

                    f"{current_user.id}_"

                    f"{uuid.uuid4().hex[:10]}."

                    f"{extension}"
                )

                upload_folder = os.path.join(

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

                file.save(file_path)

                # UPDATE USER IMAGE
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

                    f'IMAGE UPLOAD ERROR | '
                    f'USER: {current_user.username} | '
                    f'{str(error)}'
                )

                flash(

                    'Terjadi kesalahan saat upload foto!',

                    'danger'
                )

            return redirect(
                url_for('cashier.profile')
            )

        # =========================
        # DASHBOARD SUMMARY
        # =========================
        today = datetime.now().date()

        start_today = datetime.combine(
            today,
            time.min
        )

        end_today = datetime.combine(
            today,
            time.max
        )

        # Modal barang berdasarkan harga modal
        modal_barang = (

            db.session.query(

                func.sum(

                    Product.cost *
                    Product.stock

                )

            )

            .filter(

                Product.is_active == True

            )

            .scalar()

            or 0
        )

        # Uang masuk hari ini
        uang_masuk_hari_ini = (

            db.session.query(

                func.sum(

                    Transaction.total_amount

                )

            )

            .filter(

                Transaction.timestamp >= start_today,

                Transaction.timestamp <= end_today

            )

            .scalar()

            or 0
        )
        
        # Jumlah transaksi hari ini
        jumlah_transaksi_hari_ini = (

            db.session.query(

                func.count(

                    Transaction.id

                )

            )

            .filter(

                Transaction.timestamp >= start_today,

                Transaction.timestamp <= end_today

            )

            .scalar()

            or 0
        )

        logger.info(

            f'PROFILE ACCESS | '
            f'USER: {current_user.username}'
        )
        
        return render_template(

        'cashier/profile.html',

        modal_barang=modal_barang,

        uang_masuk_hari_ini=uang_masuk_hari_ini,

        jumlah_transaksi_hari_ini=
            jumlah_transaksi_hari_ini
        )

    except Exception as error:

        logger.error(

            f'CASHIER PROFILE ERROR | '
            f'{str(error)}'
        )

        flash(
            'Terjadi kesalahan sistem',
            'danger'
        )

        return redirect(
            url_for('cashier.pos')
        )