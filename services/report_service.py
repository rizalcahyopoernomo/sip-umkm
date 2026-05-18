# services/report_service.py

from datetime import datetime, timedelta
from sqlalchemy import func

from flask import send_file, jsonify

from io import StringIO, BytesIO

import csv
import sys

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from models.entities import (
    db,
    Transaction,
    TransactionItem,
    Product,
)


class ReportService:

    # =====================================================
    # NORMALIZE DATE RANGE
    # =====================================================

    @staticmethod
    def _to_range(start_date, end_date):

        start_dt = datetime.combine(
            start_date,
            datetime.min.time()
        )

        end_dt = datetime.combine(
            end_date,
            datetime.max.time()
        )

        return start_dt, end_dt

    # =====================================================
    # DAILY SALES
    # =====================================================

    @staticmethod
    def get_daily_sales(days=30):

        try:

            start_date = (
                datetime.now() - timedelta(days=days)
            )

            results = (
                db.session.query(
                    TransactionItem.product_id,
                    func.date(Transaction.timestamp).label("date"),
                    func.sum(TransactionItem.qty).label("total_qty"),
                )

                .join(
                    Transaction,
                    Transaction.id == TransactionItem.transaction_id,
                )

                .filter(
                    Transaction.timestamp >= start_date
                )

                .group_by(
                    TransactionItem.product_id,
                    func.date(Transaction.timestamp),
                )

                .order_by(
                    TransactionItem.product_id,
                    func.date(Transaction.timestamp),
                )

                .all()
            )

            data = {}

            for r in results:

                product_id = r.product_id
                date = r.date
                qty = int(r.total_qty or 0)

                if product_id not in data:
                    data[product_id] = []

                data[product_id].append({
                    "date": date,
                    "qty": qty
                })

            return data

        except Exception as e:

            print(
                f"[ReportService] DAILY SALES ERROR: {e}",
                file=sys.stderr
            )

            return {}

    # =====================================================
    # CORE SUMMARY
    # =====================================================

    @staticmethod
    def _calc_summary(start_dt, end_dt):

        total_transactions = (

            db.session.query(
                func.count(Transaction.id)
            )

            .filter(
                Transaction.timestamp >= start_dt,
                Transaction.timestamp <= end_dt,
            )

            .scalar()

            or 0
        )

        total_revenue = (

            db.session.query(
                func.sum(Transaction.total_amount)
            )

            .filter(
                Transaction.timestamp >= start_dt,
                Transaction.timestamp <= end_dt,
            )

            .scalar()

            or 0
        )

        total_profit = (

            db.session.query(

                func.sum(

                    (
                        TransactionItem.price_at_time
                        - Product.cost
                    )

                    * TransactionItem.qty
                )
            )

            .join(
                Product,
                Product.id == TransactionItem.product_id
            )

            .join(
                Transaction,
                Transaction.id == TransactionItem.transaction_id
            )

            .filter(
                Transaction.timestamp >= start_dt,
                Transaction.timestamp <= end_dt,
            )

            .scalar()

            or 0
        )

        avg_transaction = (
            total_revenue / total_transactions
            if total_transactions
            else 0
        )

        return {

            "total_transactions":
                int(total_transactions),

            "total_revenue":
                float(total_revenue),

            "total_profit":
                float(total_profit),

            "avg_transaction":
                float(avg_transaction),
        }

    # =====================================================
    # GROWTH
    # =====================================================

    @staticmethod
    def _calc_growth(current, previous):

        if previous == 0:

            if current > 0:
                return 100.0

            return 0.0

        return (
            (
                current - previous
            )

            / previous
        ) * 100

    # =====================================================
    # REPORT SUMMARY
    # =====================================================

    @staticmethod
    def get_report_summary(start_date, end_date):

        try:

            start_dt, end_dt = (
                ReportService._to_range(
                    start_date,
                    end_date
                )
            )

            current = (
                ReportService._calc_summary(
                    start_dt,
                    end_dt
                )
            )

            delta_days = (
                (
                    end_dt.date()
                    - start_dt.date()
                ).days
            ) + 1

            prev_end = (
                start_dt
                - timedelta(seconds=1)
            )

            prev_start = (
                prev_end
                - timedelta(days=delta_days - 1)
            )

            prev_start_dt = datetime.combine(
                prev_start.date(),
                datetime.min.time()
            )

            prev_end_dt = datetime.combine(
                prev_end.date(),
                datetime.max.time()
            )

            previous = (
                ReportService._calc_summary(
                    prev_start_dt,
                    prev_end_dt
                )
            )

            revenue_growth = (
                ReportService._calc_growth(
                    current["total_revenue"],
                    previous["total_revenue"]
                )
            )

            profit_growth = (
                ReportService._calc_growth(
                    current["total_profit"],
                    previous["total_profit"]
                )
            )

            return {

                **current,

                "revenue_growth":
                    round(revenue_growth, 2),

                "profit_growth":
                    round(profit_growth, 2),
            }

        except Exception as e:

            print(
                f"[ReportService] REPORT SUMMARY ERROR: {e}",
                file=sys.stderr
            )

            return {

                "total_transactions": 0,
                "total_revenue": 0,
                "total_profit": 0,
                "avg_transaction": 0,
                "revenue_growth": 0,
                "profit_growth": 0,
            }

    # =====================================================
    # TOP PRODUCTS
    # =====================================================

    @staticmethod
    def get_top_products(
        start_date,
        end_date,
        limit=5
    ):

        try:

            start_dt, end_dt = (
                ReportService._to_range(
                    start_date,
                    end_date
                )
            )

            results = (

                db.session.query(
                    TransactionItem.product_name,
                    func.sum(TransactionItem.qty),
                )

                .join(
                    Transaction,
                    Transaction.id == TransactionItem.transaction_id,
                )

                .filter(
                    Transaction.timestamp >= start_dt,
                    Transaction.timestamp <= end_dt,
                )

                .group_by(
                    TransactionItem.product_name
                )

                .order_by(
                    func.sum(
                        TransactionItem.qty
                    ).desc()
                )

                .limit(limit)

                .all()
            )

            return [

                {
                    "product_name":
                        str(r[0] or "-"),

                    "total_qty":
                        int(r[1] or 0),
                }

                for r in results
            ]

        except Exception as e:

            print(
                f"[ReportService] TOP PRODUCT ERROR: {e}",
                file=sys.stderr
            )

            return []

    # =====================================================
    # PAYMENT METHODS
    # =====================================================

    @staticmethod
    def get_payment_methods(
        start_date,
        end_date
    ):

        try:

            start_dt, end_dt = (
                ReportService._to_range(
                    start_date,
                    end_date
                )
            )

            results = (

                db.session.query(
                    Transaction.payment_method,
                    func.count(Transaction.id),
                )

                .filter(
                    Transaction.timestamp >= start_dt,
                    Transaction.timestamp <= end_dt,
                )

                .group_by(
                    Transaction.payment_method
                )

                .all()
            )

            return [

                {
                    "method":
                        str(r[0] or "Unknown"),

                    "total":
                        int(r[1] or 0),
                }

                for r in results
            ]

        except Exception as e:

            print(
                f"[ReportService] PAYMENT METHOD ERROR: {e}",
                file=sys.stderr
            )

            return []

    # =====================================================
    # GET TRANSACTIONS
    # =====================================================

    @staticmethod
    def get_transactions(
        start_date,
        end_date
    ):

        try:

            start_dt = datetime.combine(
                start_date,
                datetime.min.time()
            )

            end_dt = datetime.combine(
                end_date,
                datetime.max.time()
            )

            transactions = (

                Transaction.query

                .filter(

                    Transaction.timestamp >= start_dt,

                    Transaction.timestamp <= end_dt

                )

                .order_by(
                    Transaction.timestamp.desc()
                )

                .all()
            )

            return transactions

        except Exception as e:

            print(
                f"[ReportService] GET TRANSACTION ERROR: {e}",
                file=sys.stderr
            )

            return []
    # =====================================================
    # EXPORT PDF
    # =====================================================

    @staticmethod
    def export_pdf(start_date, end_date):

        try:

            transactions = (
                ReportService.get_transactions(
                    start_date,
                    end_date
                )
            )

            buffer = BytesIO()

            doc = SimpleDocTemplate(

                buffer,

                pagesize=letter,

                rightMargin=30,
                leftMargin=30,
                topMargin=30,
                bottomMargin=30,
            )

            elements = []

            styles = (
                getSampleStyleSheet()
            )

            title = Paragraph(
                "Laporan Transaksi SIP-UMKM",
                styles["Title"]
            )

            elements.append(title)

            elements.append(
                Spacer(1, 12)
            )

            range_label = (
                f"Periode: "
                f"{start_date.strftime('%d/%m/%Y')} "
                f"- "
                f"{end_date.strftime('%d/%m/%Y')}"
            )

            elements.append(
                Paragraph(
                    range_label,
                    styles["Normal"]
                )
            )

            elements.append(
                Spacer(1, 20)
            )

            data = [[

                "Invoice",
                "Tanggal",
                "Customer",
                "Total",
                "Pembayaran",
            ]]

            if not transactions:

                data.append([
                    "-",
                    "-",
                    "Tidak ada transaksi",
                    "-",
                    "-"
                ])

            else:

                for trx in transactions:

                    invoice = str(
                        trx.invoice_number or "-"
                    )

                    tanggal = (
                        trx.timestamp.strftime(
                            "%Y-%m-%d %H:%M"
                        )
                    )

                    customer = str(
                        trx.customer_name or "-"
                    )

                    total = (
                        f"Rp "
                        f"{float(trx.total_amount or 0):,.0f}"
                    )

                    pembayaran = str(
                        trx.payment_method or "-"
                    )

                    data.append([

                        invoice,
                        tanggal,
                        customer,
                        total,
                        pembayaran,
                    ])

            table = Table(
                data,
                repeatRows=1,
                hAlign="LEFT"
            )

            table.setStyle(TableStyle([

                (
                    'BACKGROUND',
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#4F46E5")
                ),

                (
                    'TEXTCOLOR',
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),

                (
                    'FONTNAME',
                    (0, 0),
                    (-1, 0),
                    'Helvetica-Bold'
                ),

                (
                    'FONTSIZE',
                    (0, 0),
                    (-1, 0),
                    10
                ),

                (
                    'BOTTOMPADDING',
                    (0, 0),
                    (-1, 0),
                    12
                ),

                (
                    'TOPPADDING',
                    (0, 0),
                    (-1, 0),
                    8
                ),

                (
                    'BACKGROUND',
                    (0, 1),
                    (-1, -1),
                    colors.whitesmoke
                ),

                (
                    'GRID',
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),

                (
                    'FONTNAME',
                    (0, 1),
                    (-1, -1),
                    'Helvetica'
                ),

                (
                    'FONTSIZE',
                    (0, 1),
                    (-1, -1),
                    9
                ),

            ]))

            elements.append(table)

            doc.build(elements)

            buffer.seek(0)

            return send_file(

                buffer,

                mimetype="application/pdf",

                as_attachment=True,

                download_name="laporan_transaksi.pdf",
            )

        except Exception as e:

            print(
                f"[ReportService] EXPORT PDF ERROR: {e}",
                file=sys.stderr
            )

            return jsonify({

                "error":
                    f"Gagal export PDF: {str(e)}"

            }), 500
    # =====================================================
    # EXPORT CSV
    # =====================================================

    @staticmethod
    def export_csv(start_date, end_date):

        try:

            transactions = (
                ReportService.get_transactions(
                    start_date,
                    end_date
                )
            )

            output = StringIO()

            writer = csv.writer(output)

            writer.writerow([

                "Invoice",
                "Tanggal",
                "Customer",
                "Total",
                "Pembayaran"

            ])

            if not transactions:

                writer.writerow([

                    "-",
                    "-",
                    "Tidak ada transaksi",
                    "-",
                    "-"

                ])

            else:

                for trx in transactions:

                    writer.writerow([

                        trx.invoice_number,

                        trx.timestamp.strftime(
                            "%Y-%m-%d %H:%M"
                        )

                        if trx.timestamp
                        else "-",

                        trx.customer_name,

                        trx.total_amount,

                        trx.payment_method

                    ])

            mem = BytesIO()

            mem.write(
                output.getvalue().encode("utf-8")
            )

            mem.seek(0)

            output.close()

            return send_file(

                mem,

                mimetype='text/csv',

                as_attachment=True,

                download_name=(
                    f"report_"
                    f"{start_date}_"
                    f"{end_date}.csv"
                )

            )

        except Exception as e:

            print(
                f"[ReportService] EXPORT CSV ERROR: {e}",
                file=sys.stderr
            )

            return jsonify({

                "success": False,

                "message": str(e)

            }), 500