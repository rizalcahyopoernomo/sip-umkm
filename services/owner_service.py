from datetime import datetime, timedelta
from sqlalchemy import func, and_
from models.entities import db, Product, Transaction, TransactionItem


class OwnerService:

    # =========================
    # INVENTORY DATA
    # =========================
    @staticmethod
    def get_all_inventory():
        try:
            return Product.query.filter_by(
                is_active=True
            ).order_by(
                Product.name.asc()
            ).all()

        except Exception:
            return []

    # =========================
    # SEARCH INVENTORY
    # =========================
    @staticmethod
    def search_inventory(keyword):
        try:
            if not keyword:
                return Product.query.filter_by(
                    is_active=True
                ).all()

            return Product.query.filter(
                and_(
                    Product.name.ilike(f"%{keyword}%"),
                    Product.is_active == True
                )
            ).order_by(
                Product.name.asc()
            ).all()

        except Exception:
            return []

    # =========================
    # SORT STOCK ASC
    # =========================
    @staticmethod
    def get_inventory_sorted_low_stock():
        try:
            return Product.query.filter_by(
                is_active=True
            ).order_by(
                Product.stock.asc(),
                Product.name.asc()
            ).all()

        except Exception:
            return []

    # =========================
    # SORT STOCK DESC
    # =========================
    @staticmethod
    def get_inventory_sorted_high_stock():
        try:
            return Product.query.filter_by(
                is_active=True
            ).order_by(
                Product.stock.desc(),
                Product.name.asc()
            ).all()

        except Exception:
            return []

    # =========================
    # TOTAL INVENTORY VALUE
    # =========================
    @staticmethod
    def get_inventory_value():
        try:
            total = db.session.query(
                func.sum(
                    func.coalesce(Product.cost, 0) *
                    func.coalesce(Product.stock, 0)
                )
            ).filter(
                Product.is_active == True
            ).scalar()

            return total or 0

        except Exception:
            return 0

    # =========================
    # DASHBOARD DATA
    # =========================
    @staticmethod
    def get_dashboard_data():
        try:
            now = datetime.utcnow()
            today = now.date()

            start_today = datetime.combine(
                today,
                datetime.min.time()
            )

            end_today = datetime.combine(
                today,
                datetime.max.time()
            )

            start_month = datetime(
                today.year,
                today.month,
                1
            )

            if today.month == 12:
                end_month = datetime(
                    today.year + 1,
                    1,
                    1
                )
            else:
                end_month = datetime(
                    today.year,
                    today.month + 1,
                    1
                )

            # =========================
            # TOTAL DATA
            # =========================
            total_products = Product.query.filter_by(
                is_active=True
            ).count()

            total_transactions = Transaction.query.count()

            total_customers = db.session.query(
                func.count(
                    func.distinct(
                        Transaction.customer_name
                    )
                )
            ).scalar() or 0

            # =========================
            # REVENUE
            # =========================
            revenue_all = db.session.query(
                func.sum(Transaction.total_amount)
            ).scalar() or 0

            revenue_today = db.session.query(
                func.sum(Transaction.total_amount)
            ).filter(
                Transaction.timestamp >= start_today,
                Transaction.timestamp <= end_today
            ).scalar() or 0

            revenue_month = db.session.query(
                func.sum(Transaction.total_amount)
            ).filter(
                Transaction.timestamp >= start_month,
                Transaction.timestamp < end_month
            ).scalar() or 0

            # =========================
            # PROFIT TODAY
            # =========================
            profit_today = db.session.query(
                func.sum(
                    (
                        TransactionItem.price_at_time -
                        func.coalesce(Product.cost, 0)
                    ) * TransactionItem.qty
                )
            ).join(
                Product,
                Product.id == TransactionItem.product_id
            ).join(
                Transaction,
                Transaction.id == TransactionItem.transaction_id
            ).filter(
                Transaction.timestamp >= start_today,
                Transaction.timestamp <= end_today
            ).scalar() or 0

            # =========================
            # PROFIT MONTH
            # =========================
            profit_month = db.session.query(
                func.sum(
                    (
                        TransactionItem.price_at_time -
                        func.coalesce(Product.cost, 0)
                    ) * TransactionItem.qty
                )
            ).join(
                Product,
                Product.id == TransactionItem.product_id
            ).join(
                Transaction,
                Transaction.id == TransactionItem.transaction_id
            ).filter(
                Transaction.timestamp >= start_month,
                Transaction.timestamp < end_month
            ).scalar() or 0

            # =========================
            # LOW STOCK
            # =========================
            low_stock_products = Product.query.filter(
                and_(
                    Product.stock <= Product.min_stock,
                    Product.is_active == True
                )
            ).all()

            return {
                "total_products": total_products,
                "total_transactions": total_transactions,
                "total_customers": total_customers,
                "revenue_today": revenue_today,
                "revenue_month": revenue_month,
                "revenue_all": revenue_all,
                "profit_today": float(profit_today),
                "profit_month": float(profit_month),
                "low_stock": low_stock_products
            }

        except Exception:
            return {
                "total_products": 0,
                "total_transactions": 0,
                "total_customers": 0,
                "revenue_today": 0,
                "revenue_month": 0,
                "revenue_all": 0,
                "profit_today": 0,
                "profit_month": 0,
                "low_stock": []
            }

    # =========================
    # CHART 7 HARI
    # =========================
    @staticmethod
    def get_last_7_days_revenue():

        today = datetime.utcnow().date()

        labels = []
        values = []

        for i in range(6, -1, -1):

            day = today - timedelta(days=i)

            start_day = datetime.combine(
                day,
                datetime.min.time()
            )

            end_day = datetime.combine(
                day,
                datetime.max.time()
            )

            total = db.session.query(
                func.sum(Transaction.total_amount)
            ).filter(
                Transaction.timestamp >= start_day,
                Transaction.timestamp <= end_day
            ).scalar() or 0

            labels.append(day.strftime("%d %b"))
            values.append(total)

        return labels, values