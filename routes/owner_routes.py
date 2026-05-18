# routes/owner_routes.py

from flask import (
    Blueprint,
    render_template,
    request,
    send_file,
    redirect,
    url_for,
    jsonify,
    flash
)

from flask_login import (
    login_required,
    current_user
)

from datetime import (
    datetime,
    date,
    timedelta
)

import os

from werkzeug.utils import (
    secure_filename
)

from sqlalchemy import (
    extract,
    func
)

from models.entities import (
    db,
    Product,
    Transaction
)

from utils.decorators import (
    owner_required
)

# =========================================
# LOGGER
# =========================================
from utils.logger import (
    logger
)

from services.owner_service import (
    OwnerService
)

from services.report_service import (
    ReportService
)

from services.inventory_service import (
    InventoryService
)

from services.invoice_service import (
    InvoiceService
)

from services.dashboard_service import (
    DashboardService
)

from services.analytics_service import (
    AnalyticsService
)



# =========================================
# BLUEPRINT
# =========================================
owner_bp = Blueprint(
    'owner',
    __name__
)

UPLOAD_FOLDER = 'static/products'
ALLOWED_EXTENSIONS = {
    'png',
    'jpg',
    'jpeg',
    'webp'
}


def allowed_file(filename):

    return (

        '.' in filename

        and

        filename.rsplit('.', 1)[1]
        .lower()

        in ALLOWED_EXTENSIONS
    )


# =========================================
# HELPER
# =========================================
def parse_date_range(
    start_date_str,
    end_date_str
):

    if not start_date_str or not end_date_str:

        return (
            date.today(),
            date.today()
        )

    try:

        return (

            datetime.strptime(
                start_date_str,
                "%Y-%m-%d"
            ).date(),

            datetime.strptime(
                end_date_str,
                "%Y-%m-%d"
            ).date()
        )

    except ValueError:

        logger.warning(
            'INVALID DATE RANGE FORMAT'
        )

        return (
            date.today(),
            date.today()
        )


# =========================================
# CONVERT WIB
# =========================================
def convert_to_wib(data_list):

    for d in data_list:

        if hasattr(d, 'created_at') and d.created_at:

            d.created_at = (
                d.created_at
                + timedelta(hours=7)
            )

        if hasattr(d, 'timestamp') and d.timestamp:

            d.timestamp = (
                d.timestamp
                + timedelta(hours=7)
            )

    return data_list


# =========================================
# DASHBOARD
# =========================================
@owner_bp.route('/dashboard')
@login_required
@owner_required
def dashboard():

    try:

        summary = (
            DashboardService
            .get_dashboard_summary()
        )

        sales = (
            DashboardService
            .get_sales_overview()
        )

        dss = (
            DashboardService
            .get_dashboard_dss()
        )

        # =====================================
        # PEAK HOUR ANALYTICS
        # =====================================
        peak_hour_result = (

            db.session.query(

                extract(
                    'hour',
                    Transaction.timestamp
                ).label('hour'),

                func.count(
                    Transaction.id
                ).label('total')

            )

            .group_by('hour')

            .order_by(

                func.count(
                    Transaction.id
                ).desc()

            )

            .first()
        )

        # =====================================
        # FORMAT PEAK HOUR
        # =====================================
        if peak_hour_result:

            peak_hour = (

                f"{int(peak_hour_result.hour):02d}.00 WIB"
            )

        else:

            peak_hour = "Belum Ada Data"

        logger.info(

            f'DASHBOARD ACCESS | '
            f'OWNER: {current_user.username}'
        )

        return render_template(

            'owner/dashboard.html',

            # =====================================
            # KPI
            # =====================================
            total_produk=
                summary['total_produk'],

            total_transaksi=
                summary['total_transaksi'],

            total_customer=
                summary['total_customer'],

            revenue_today=
                summary['revenue_today'],

            revenue_month=
                summary['revenue_month'],

            revenue_all=
                summary['revenue_all'],

            profit_today=
                summary['profit_today'],

            profit_month=
                summary['profit_month'],

            peak_hour=
                peak_hour,

            # =====================================
            # CHART
            # =====================================
            chart_labels=
                sales['chart_labels'],

            chart_values=
                sales['chart_values'],

            # =====================================
            # STOCK ALERT
            # =====================================
            low_stock=
                summary['low_stock'],

            # =====================================
            # DSS
            # =====================================
            dss_depletion=
                dss['dss_depletion'],

            dss_restock=
                dss['dss_restock'],

            dss_priority=
                dss['dss_priority'],

            dss_pareto=
                dss['dss_pareto'],

            dss_movement=
                dss['dss_movement'],

            abc_data=
                dss['abc_data'],

            abc_summary=
                dss['abc_summary'],

            forecast_insight=
                dss['forecast_insight'],

            executive_insight=
                dss['executive_insight']
        )

    except Exception as error:

        logger.error(

            f'DASHBOARD ERROR | '
            f'{str(error)}'
        )

        flash(
            'Gagal memuat dashboard',
            'danger'
        )

        return redirect(
            url_for('auth.login')
        )


# =========================================
# REALTIME DASHBOARD API
# =========================================
@owner_bp.route('/dashboard/data')
@login_required
@owner_required
def dashboard_data():

    try:

        data = (
            DashboardService
            .get_realtime_dashboard_data()
        )

        logger.info(
            'REALTIME DASHBOARD API ACCESS'
        )

        return jsonify(data)

    except Exception as error:

        logger.error(

            f'REALTIME DASHBOARD ERROR | '
            f'{str(error)}'
        )

        return jsonify({

            "success": False,

            "message":
                "Gagal memuat dashboard realtime"

        }), 500


# =========================================
# INVENTORY
# =========================================
@owner_bp.route('/inventory')
@login_required
@owner_required
def inventory():

    try:

        keyword = request.args.get('q')

        low_stock = request.args.get(
            'low_stock'
        )

        from models.entities import Category

        categories = Category.query.all()

        if keyword:

            products = (
                OwnerService
                .search_inventory(keyword)
            )

        elif low_stock:

            products = (
                OwnerService
                .get_low_stock_products()
            )

        else:

            products = (
                OwnerService
                .get_all_inventory()
            )

        total_value = (
            OwnerService
            .get_inventory_value()
        )

        dss_restock = (
            DashboardService
            .get_dashboard_dss()
            ['dss_restock']
        )

        dss_map = {

            item["product_id"]: item

            for item in dss_restock
        }

        logger.info(

            f'INVENTORY ACCESS | '
            f'OWNER: {current_user.username}'
        )

        return render_template(

            'owner/inventory.html',

            products=products,

            categories=categories,

            total_value=total_value,

            dss_map=dss_map
        )

    except Exception as error:

        logger.error(

            f'INVENTORY PAGE ERROR | '
            f'{str(error)}'
        )

        flash(
            'Gagal memuat inventory',
            'danger'
        )

        return redirect(
            url_for('owner.dashboard')
        )


# =========================================
# ADD PRODUCT
# =========================================
@owner_bp.route(
    '/inventory/add',
    methods=['POST']
)
@login_required
@owner_required
def add_product():

    try:

        name = request.form.get('name')

        price = float(
            request.form.get('price')
        )

        cost = float(
            request.form.get('cost')
        )

        stock = int(
            request.form.get('stock')
        )

        category_id = int(
            request.form.get('category_id')
        )

        min_stock = int(

            request.form.get(
                'min_stock',
                5
            )
        )

        file = request.files.get(
            'image'
        )

        filename = 'default.jpg'

        if file and file.filename != '':

            if not allowed_file(file.filename):

                flash(
                'Format gambar tidak didukung',
                'danger'
                )

                return redirect(
                url_for('owner.inventory')
                )

            filename = secure_filename(
                file.filename
            )

            filepath = os.path.join(

                UPLOAD_FOLDER,

                filename
            )

            os.makedirs(

             UPLOAD_FOLDER,

             exist_ok=True
            )

            file.save(filepath)

        new_product = Product(

            name=name,

            price=price,

            cost=cost,

            stock=stock,

            category_id=category_id,

            image=filename,

            min_stock=min_stock
        )

        db.session.add(new_product)

        db.session.commit()

        logger.info(

            f'PRODUCT CREATED | '
            f'PRODUCT: {name} | '
            f'STOCK: {stock}'
        )

        flash(
            'Produk berhasil ditambahkan',
            'success'
        )

        return redirect(
            url_for('owner.inventory')
        )

    except Exception as error:

        db.session.rollback()

        logger.error(

            f'ADD PRODUCT ERROR | '
            f'{str(error)}'
        )

        flash(
            'Gagal menambahkan produk',
            'danger'
        )

        return redirect(
            url_for('owner.inventory')
        )


# =========================================
# RESTOCK PRODUCT
# =========================================
@owner_bp.route(
    '/inventory/restock',
    methods=['POST']
)
@login_required
@owner_required
def restock():

    try:

        product_id = request.form.get(
            'product_id'
        )

        qty = request.form.get('qty')

        note = request.form.get('note')

        success = (
            InventoryService
            .restock_product(

                product_id=int(product_id),

                qty=int(qty),

                note=note
            )
        )

        if not success:

            logger.warning(
                'RESTOCK FAILED'
            )

            flash(
                'Restock gagal',
                'danger'
            )

            return redirect(
                url_for('owner.inventory')
            )

        product = db.session.get(
            Product,
            int(product_id)
        )

        db.session.commit()

        logger.info(

            f'STOCK RESTOCK | '
            f'PRODUCT: {product.name} | '
            f'QTY: {qty}'
        )

        flash(
            'Restock berhasil',
            'success'
        )

        return redirect(
            url_for('owner.inventory')
        )

    except Exception as error:

        db.session.rollback()

        logger.error(

            f'RESTOCK ERROR | '
            f'{str(error)}'
        )

        flash(
            'Terjadi kesalahan restock',
            'danger'
        )

        return redirect(
            url_for('owner.inventory')
        )


# =========================================
# ADJUST STOCK
# =========================================
@owner_bp.route(
    '/inventory/adjust',
    methods=['POST']
)
@login_required
@owner_required
def adjust_stock():

    try:

        product_id = request.form.get(
            'product_id'
        )

        qty = request.form.get('qty')

        note = request.form.get('note')

        min_stock = request.form.get(
            'min_stock',
            5
        )

        success = (
            InventoryService
            .adjust_stock(

                product_id=int(product_id),

                qty=int(qty),

                note=note
            )
        )

        if not success:

            logger.warning(
                'STOCK ADJUST FAILED'
            )

            flash(
                'Adjust stok gagal',
                'danger'
            )

            return redirect(
                url_for('owner.inventory')
            )

        product = db.session.get(
            Product,
            int(product_id)
        )

        if product:

            product.min_stock = int(
                min_stock
            )

        db.session.commit()

        logger.info(

            f'STOCK UPDATED | '
            f'PRODUCT: {product.name} | '
            f'STOCK: {product.stock}'
        )

        flash(
            'Stok berhasil diperbarui',
            'success'
        )

        return redirect(
            url_for('owner.inventory')
        )

    except Exception as error:

        db.session.rollback()

        logger.error(

            f'STOCK UPDATE ERROR | '
            f'{str(error)}'
        )

        flash(
            'Terjadi kesalahan update stok',
            'danger'
        )

        return redirect(
            url_for('owner.inventory')
        )


# =========================================
# STOCK HISTORY
# =========================================
@owner_bp.route(
    '/inventory/history/<int:product_id>'
)
@login_required
@owner_required
def stock_history(product_id):

    try:

        history = (
            InventoryService
            .get_stock_history(product_id)
        )

        history = convert_to_wib(history)

        logger.info(

            f'STOCK HISTORY ACCESS | '
            f'PRODUCT ID: {product_id}'
        )

        return render_template(

            'owner/stock_history.html',

            history=history
        )

    except Exception as error:

        logger.error(

            f'STOCK HISTORY ERROR | '
            f'{str(error)}'
        )

        flash(
            'Gagal memuat histori stok',
            'danger'
        )

        return redirect(
            url_for('owner.inventory')
        )


# =========================================
# DELETE PRODUCT
# =========================================
@owner_bp.route(
    '/inventory/delete/<int:product_id>',
    methods=['POST']
)
@login_required
@owner_required
def delete_product(product_id):

    try:

        product = db.session.get(
            Product,
            product_id
        )

        product_name = (
            product.name
            if product
            else 'Unknown'
        )

        success = (
            InventoryService
            .delete_product(product_id)
        )

        if not success:

            logger.warning(
                'DELETE PRODUCT FAILED'
            )

            flash(
                'Gagal menghapus produk',
                'danger'
            )

            return redirect(
                url_for('owner.inventory')
            )

        db.session.commit()

        logger.warning(

            f'PRODUCT DELETED | '
            f'PRODUCT: {product_name}'
        )

        flash(
            'Produk berhasil dihapus',
            'success'
        )

        return redirect(
            url_for('owner.inventory')
        )

    except Exception as error:

        db.session.rollback()

        logger.error(

            f'DELETE PRODUCT ERROR | '
            f'{str(error)}'
        )

        flash(
            'Terjadi kesalahan menghapus produk',
            'danger'
        )

        return redirect(
            url_for('owner.inventory')
        )


# =========================================
# CUSTOMER ANALYTICS
# =========================================
@owner_bp.route('/customer')
@login_required
@owner_required
def customer():

    try:

        analytics = (
            AnalyticsService
            .customer_segmentation()
        )

        logger.info(
            'CUSTOMER ANALYTICS ACCESS'
        )

        return render_template(

            'owner/customer.html',

            top_spenders=
                analytics['top_spenders'],

            most_active=
                analytics['most_active'],

            repeat_customers=
                analytics['repeat_customers'],

            contribution=
                analytics['contribution']
        )

    except Exception as error:

        logger.error(

            f'CUSTOMER ANALYTICS ERROR | '
            f'{str(error)}'
        )

        flash(
            'Gagal memuat customer analytics',
            'danger'
        )

        return redirect(
            url_for('owner.dashboard')
        )


# =========================================
# REPORTS
# =========================================
@owner_bp.route(
    '/reports',
    methods=['GET']
)
@login_required
@owner_required
def reports():

    try:

        start_date, end_date = (
            parse_date_range(

                request.args.get(
                    'start_date'
                ),

                request.args.get(
                    'end_date'
                )
            )
        )

        summary = (
            ReportService
            .get_report_summary(

                start_date,

                end_date
            )
        )

        top_products = (
            ReportService
            .get_top_products(

                start_date,

                end_date
            )
        )

        payment_methods = (
            ReportService
            .get_payment_methods(

                start_date,

                end_date
            )
        )

        transactions = (
            ReportService
            .get_transactions(

                start_date,

                end_date
            )
        )

        transactions = convert_to_wib(
            transactions
        )

        logger.info(
            'REPORT PAGE ACCESS'
        )

        return render_template(

            'owner/reports.html',

            start_date=start_date,

            end_date=end_date,

            total_transaksi=
                summary['total_transactions'],

            total_revenue=
                summary['total_revenue'],

            total_profit=
                summary['total_profit'],

            avg_transaction=
                summary['avg_transaction'],

            revenue_growth=
                summary.get(
                    'revenue_growth',
                    0
                ),

            profit_growth=
                summary.get(
                    'profit_growth',
                    0
                ),

            top_products=
                top_products,

            payment_methods=
                payment_methods,

            transactions=
                transactions
        )

    except Exception as error:

        logger.error(

            f'REPORT ERROR | '
            f'{str(error)}'
        )

        flash(
            'Gagal memuat laporan',
            'danger'
        )

        return redirect(
            url_for('owner.dashboard')
        )


# =========================================
# EXPORT CSV
# =========================================
@owner_bp.route(
    '/reports/export/csv'
)
@login_required
@owner_required
def export_csv():

    try:

        start_date, end_date = (
            parse_date_range(

                request.args.get(
                    'start_date'
                ),

                request.args.get(
                    'end_date'
                )
            )
        )

        logger.info(
            'EXPORT CSV REPORT'
        )

        return (
            ReportService
            .export_csv(

                start_date,

                end_date
            )
        )

    except Exception as error:

        logger.error(

            f'EXPORT CSV ERROR | '
            f'{str(error)}'
        )

        flash(
            'Gagal export CSV',
            'danger'
        )

        return redirect(
            url_for('owner.reports')
        )


# =========================================
# EXPORT PDF
# =========================================
@owner_bp.route(
    '/reports/export/pdf'
)
@login_required
@owner_required
def export_pdf():

    try:

        start_date, end_date = (
            parse_date_range(

                request.args.get(
                    'start_date'
                ),

                request.args.get(
                    'end_date'
                )
            )
        )

        logger.info(
            'EXPORT PDF REPORT'
        )

        # IMPORTANT:
        # langsung return dari service
        # jangan dibungkus send_file lagi

        return (
            ReportService
            .export_pdf(

                start_date,

                end_date
            )
        )

    except Exception as error:

        logger.error(

            f'EXPORT PDF ERROR | '
            f'{str(error)}'
        )

        flash(
            'Gagal export PDF',
            'danger'
        )

        return redirect(
            url_for('owner.reports')
        )

# =========================================
# INVOICE DETAIL
# =========================================
@owner_bp.route(
    '/invoice/<invoice_number>'
)
@login_required
@owner_required
def invoice_detail(invoice_number):

    try:

        invoice = (
            InvoiceService
            .get_invoice(invoice_number)
        )

        if not invoice:

            logger.warning(

                f'INVOICE NOT FOUND | '
                f'INVOICE: {invoice_number}'
            )

            return redirect(
                url_for('owner.reports')
            )

        summary = (
            InvoiceService
            .invoice_summary(invoice)
        )

        logger.info(

            f'INVOICE DETAIL ACCESS | '
            f'INVOICE: {invoice_number}'
        )

        return render_template(

            'owner/invoice_detail.html',

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
            url_for('owner.reports')
        )

# =========================================
# ACCOUNT SETTINGS
# =========================================
@owner_bp.route('/account-settings')
@login_required
@owner_required
def account_settings():

    return render_template(
        'owner/account.html'
    )

# =========================================
# INVOICE HISTORY
# =========================================
@owner_bp.route('/invoices')
@login_required
@owner_required
def invoice_history():

    try:

        keyword = request.args.get('q')

        invoices = (
            InvoiceService
            .search_invoices(
                keyword=keyword
            )
        )

        logger.info(
            'INVOICE HISTORY ACCESS'
        )

        return render_template(

            'owner/invoice_history.html',

            invoices=invoices,

            keyword=keyword
        )

    except Exception as error:

        logger.error(

            f'INVOICE HISTORY ERROR | '
            f'{str(error)}'
        )

        flash(
            'Gagal memuat histori invoice',
            'danger'
        )

        return redirect(
            url_for('owner.dashboard')
        )
