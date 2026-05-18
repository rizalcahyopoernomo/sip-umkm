from models.entities import Transaction
from sqlalchemy import or_


class InvoiceService:

    # =========================================
    # FORMAT CURRENCY
    # =========================================
    @staticmethod
    def format_currency(value):

        try:

            value = float(value or 0)

            return f"Rp {value:,.0f}".replace(",", ".")

        except Exception:

            return "Rp 0"

    # =========================================
    # GET INVOICE BY NUMBER
    # =========================================
    @staticmethod
    def get_invoice(invoice_number):

        if not invoice_number:

            return None

        invoice = Transaction.query.filter_by(

            invoice_number=invoice_number

        ).first()

        return invoice

    # =========================================
    # GET RECENT INVOICES
    # =========================================
    @staticmethod
    def recent_invoices(limit=20):

        try:

            limit = int(limit)

        except Exception:

            limit = 20

        if limit <= 0:

            limit = 20

        invoices = Transaction.query.order_by(

            Transaction.timestamp.desc()

        ).limit(limit).all()

        return invoices

    # =========================================
    # INVOICE SUMMARY
    # =========================================
    @staticmethod
    def invoice_summary(invoice):

        if not invoice:

            return {

                "invoice_number": "-",

                "customer_name": "-",

                "cashier_name": "-",

                "payment_method": "-",

                "subtotal": 0,

                "discount": 0,

                "total_amount": 0,

                "amount_paid": 0,

                "change_amount": 0,

                "total_items": 0,

                "timestamp": None
            }

        items = invoice.items or []

        total_items = sum(

            item.qty or 0

            for item in items
        )

        return {

            "invoice_number": (
                invoice.invoice_number or "-"
            ),

            "customer_name": (
                invoice.customer_name or "-"
            ),

            "cashier_name": (

                invoice.cashier.username

                if invoice.cashier

                else "-"
            ),

            "payment_method": (
                invoice.payment_method or "-"
            ),

            "subtotal": (
                invoice.subtotal or 0
            ),

            "discount": (
                invoice.discount or 0
            ),

            "total_amount": (
                invoice.total_amount or 0
            ),

            "amount_paid": (
                invoice.amount_paid or 0
            ),

            "change_amount": (
                invoice.change_amount or 0
            ),

            "total_items": total_items,

            "timestamp": invoice.timestamp
        }

    # =========================================
    # SEARCH INVOICES
    # =========================================
    @staticmethod
    def search_invoices(

        keyword=None,
        limit=50

    ):

        try:

            limit = int(limit)

        except Exception:

            limit = 50

        if limit <= 0:

            limit = 50

        query = Transaction.query

        if keyword:

            keyword = f"%{keyword.strip()}%"

            query = query.filter(

                or_(

                    Transaction.invoice_number.ilike(keyword),

                    Transaction.customer_name.ilike(keyword),

                    Transaction.payment_method.ilike(keyword)
                )
            )

        invoices = query.order_by(

            Transaction.timestamp.desc()

        ).limit(limit).all()

        return invoices