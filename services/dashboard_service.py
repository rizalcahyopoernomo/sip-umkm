# services/dashboard_service.py

from services.owner_service import OwnerService
from services.dss_service import DSSService
from services.pos_service import POSService


class DashboardService:

    # =========================================
    # DASHBOARD SUMMARY
    # =========================================
    @staticmethod
    def get_dashboard_summary():

        data = OwnerService.get_dashboard_data()

        return {

            "total_produk":
                data.get('total_products', 0),

            "total_transaksi":
                data.get('total_transactions', 0),

            "total_customer":
                data.get('total_customers', 0),

            "revenue_today":
                data.get('revenue_today', 0),

            "revenue_month":
                data.get('revenue_month', 0),

            "revenue_all":
                data.get('revenue_all', 0),

            "profit_today":
                data.get('profit_today', 0),

            "profit_month":
                data.get('profit_month', 0),

            "low_stock":
                data.get('low_stock', [])
        }

    # =========================================
    # SALES OVERVIEW
    # =========================================
    @staticmethod
    def get_sales_overview():

        chart_labels, chart_values = (
            OwnerService.get_last_7_days_revenue()
        )

        return {

            "chart_labels":
                chart_labels,

            "chart_values":
                chart_values
        }

    # =========================================
    # LOW STOCK PRODUCTS
    # =========================================
    @staticmethod
    def get_low_stock_products():

        data = OwnerService.get_dashboard_data()

        return data.get(
            'low_stock',
            []
        )

    # =========================================
    # DASHBOARD DSS
    # =========================================
    @staticmethod
    def get_dashboard_dss():

        dss_depletion = (
            DSSService.stock_depletion_analysis()
        )

        dss_restock = (
            DSSService.restock_recommendation()
        )

        dss_priority = (
            DSSService.product_priority_analysis()
        )

        dss_pareto = (
            DSSService.revenue_contribution_analysis()
        )

        dss_movement = (
            DSSService.product_movement_analysis()
        )

        abc_data = (
            DSSService.abc_classification()
        )

        forecast_insight = (
            DSSService.forecast_insight()
        )

        executive_insight = (
            DSSService.executive_insight()
        )

        # =====================================
        # ABC SUMMARY
        # =====================================
        abc_summary = {

            "A": len([
                x for x in abc_data
                if x.get("class") == "A"
            ]),

            "B": len([
                x for x in abc_data
                if x.get("class") == "B"
            ]),

            "C": len([
                x for x in abc_data
                if x.get("class") == "C"
            ])
        }

        return {

            "dss_depletion":
                dss_depletion,

            "dss_restock":
                dss_restock,

            "dss_priority":
                dss_priority[:5],

            "dss_pareto":
                dss_pareto[:10],

            "dss_movement":
                dss_movement,

            "abc_data":
                abc_data[:10],

            "abc_summary":
                abc_summary,

            "forecast_insight":
                forecast_insight,

            "executive_insight":
                executive_insight
        }

    # =========================================
    # REALTIME DASHBOARD DATA
    # =========================================
    @staticmethod
    def get_realtime_dashboard_data():

        return {

            "kpi": {

                "total_transaksi":
                    POSService.total_transaksi(),

                "total_produk":
                    POSService.total_produk(),

                "total_customer":
                    POSService.total_customer(),

                "total_supplier":
                    POSService.total_supplier(),

                "revenue_today":
                    POSService.revenue_today(),

                "revenue_month":
                    POSService.revenue_month(),

                "profit_today":
                    POSService.profit_today(),

                "profit_month":
                    POSService.profit_month(),
            },

            "chart": {

                "labels":
                    POSService.chart_labels(),

                "values":
                    POSService.chart_values(),
            },

            "dss": {

                "depletion":
                    DSSService.stock_depletion_analysis(),

                "priority":
                    DSSService.product_priority_analysis(),

                "pareto":
                    DSSService.revenue_contribution_analysis(),

                "forecast":
                    DSSService.forecast_insight(),

                "executive":
                    DSSService.executive_insight()
            }
        }