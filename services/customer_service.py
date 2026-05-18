from sqlalchemy import func, desc
from datetime import datetime, timedelta

from models.entities import (
    db,
    Transaction,
    TransactionItem
)


class CustomerAnalyticsService:

    # =========================================
    # NORMALIZE CUSTOMER NAME
    # =========================================
    @staticmethod
    def normalize_customer_name(name):

        if not name:
            return "Pelanggan Umum"

        name = name.strip()

        if name == "":
            return "Pelanggan Umum"

        return name

    # =========================================
    # TOP SPENDERS
    # =========================================
    @staticmethod
    def top_spenders(limit=5):

        results = db.session.query(

            Transaction.customer_name,

            func.count(Transaction.id).label("total_transactions"),

            func.sum(Transaction.total_amount).label("total_spent")

        ).group_by(

            Transaction.customer_name

        ).order_by(

            desc("total_spent")

        ).limit(limit).all()

        data = []

        for row in results:

            customer_name = CustomerAnalyticsService.normalize_customer_name(
                row.customer_name
            )

            data.append({

                "customer_name": customer_name,

                "total_transactions": row.total_transactions,

                "total_spent": round(row.total_spent or 0, 2)
            })

        return data

    # =========================================
    # MOST ACTIVE CUSTOMERS
    # =========================================
    @staticmethod
    def most_active_customers(limit=5):

        results = db.session.query(

            Transaction.customer_name,

            func.count(Transaction.id).label("transaction_count"),

            func.sum(Transaction.total_amount).label("total_spent")

        ).group_by(

            Transaction.customer_name

        ).order_by(

            desc("transaction_count")

        ).limit(limit).all()

        data = []

        for row in results:

            customer_name = CustomerAnalyticsService.normalize_customer_name(
                row.customer_name
            )

            data.append({

                "customer_name": customer_name,

                "transaction_count": row.transaction_count,

                "total_spent": round(row.total_spent or 0, 2)
            })

        return data

    # =========================================
    # REPEAT CUSTOMERS
    # =========================================
    @staticmethod
    def repeat_customers(min_transactions=2):

        results = db.session.query(

            Transaction.customer_name,

            func.count(Transaction.id).label("transaction_count"),

            func.sum(Transaction.total_amount).label("total_spent"),

            func.max(Transaction.timestamp).label("last_transaction")

        ).group_by(

            Transaction.customer_name

        ).having(

            func.count(Transaction.id) >= min_transactions

        ).order_by(

            desc("transaction_count")

        ).all()

        data = []

        for row in results:

            customer_name = CustomerAnalyticsService.normalize_customer_name(
                row.customer_name
            )

            data.append({

                "customer_name": customer_name,

                "transaction_count": row.transaction_count,

                "total_spent": round(row.total_spent or 0, 2),

                "last_transaction": row.last_transaction
            })

        return data

    # =========================================
    # CUSTOMER CONTRIBUTION
    # =========================================
    @staticmethod
    def customer_contribution(limit=3):

        total_revenue = db.session.query(
            func.sum(Transaction.total_amount)
        ).scalar() or 0

        if total_revenue <= 0:

            return {

                "top_customers": [],
                "contribution_pct": 0,
                "message": "Belum ada transaksi customer"
            }

        top_customers = db.session.query(

            Transaction.customer_name,

            func.sum(Transaction.total_amount).label("total_spent")

        ).group_by(

            Transaction.customer_name

        ).order_by(

            desc("total_spent")

        ).limit(limit).all()

        contribution_total = sum([
            x.total_spent or 0
            for x in top_customers
        ])

        contribution_pct = round(
            (contribution_total / total_revenue) * 100,
            1
        )

        customers = []

        for row in top_customers:

            customers.append({

                "customer_name":
                    CustomerAnalyticsService.normalize_customer_name(
                        row.customer_name
                    ),

                "total_spent":
                    round(row.total_spent or 0, 2)
            })

        return {

            "top_customers": customers,

            "contribution_pct": contribution_pct,

            "message":
                f"{len(customers)} customer menyumbang "
                f"{contribution_pct}% revenue"
        }

    # =========================================
    # CUSTOMER TRANSACTION HISTORY
    # =========================================
    @staticmethod
    def customer_transaction_history(

        customer_name,
        limit=20

    ):

        customer_name = CustomerAnalyticsService.normalize_customer_name(
            customer_name
        )

        transactions = Transaction.query.filter(

            Transaction.customer_name == customer_name

        ).order_by(

            Transaction.timestamp.desc()

        ).limit(limit).all()

        return transactions

    # =========================================
    # CUSTOMER SUMMARY
    # =========================================
    @staticmethod
    def customer_summary(customer_name):

        customer_name = CustomerAnalyticsService.normalize_customer_name(
            customer_name
        )

        transactions = Transaction.query.filter(

            Transaction.customer_name == customer_name

        ).all()

        if not transactions:

            return None

        total_transactions = len(transactions)

        total_spent = sum([
            trx.total_amount
            for trx in transactions
        ])

        last_transaction = max([
            trx.timestamp
            for trx in transactions
        ])

        average_spending = (
            total_spent / total_transactions
            if total_transactions > 0 else 0
        )

        return {

            "customer_name": customer_name,

            "total_transactions": total_transactions,

            "total_spent": round(total_spent, 2),

            "average_spending": round(average_spending, 2),

            "last_transaction": last_transaction
        }

    # =========================================
    # FAVORITE PRODUCTS
    # =========================================
    @staticmethod
    def favorite_products(

        customer_name,
        limit=5

    ):

        customer_name = CustomerAnalyticsService.normalize_customer_name(
            customer_name
        )

        results = db.session.query(

            TransactionItem.product_name,

            func.sum(TransactionItem.qty).label("total_qty")

        ).join(

            Transaction,
            Transaction.id == TransactionItem.transaction_id

        ).filter(

            Transaction.customer_name == customer_name

        ).group_by(

            TransactionItem.product_name

        ).order_by(

            desc("total_qty")

        ).limit(limit).all()

        data = []

        for row in results:

            data.append({

                "product_name": row.product_name,

                "total_qty": row.total_qty
            })

        return data