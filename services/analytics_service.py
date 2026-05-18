# services/analytics_service.py

from services.customer_service import (
    CustomerAnalyticsService
)

from services.dss_service import (
    DSSService
)


class AnalyticsService:

    # =========================================
    # TOP SPENDERS
    # =========================================
    @staticmethod
    def top_customers():

        return (
            CustomerAnalyticsService
            .top_spenders()
        )

    # =========================================
    # MOST ACTIVE CUSTOMERS
    # =========================================
    @staticmethod
    def customer_activity():

        return (
            CustomerAnalyticsService
            .most_active_customers()
        )

    # =========================================
    # REPEAT CUSTOMERS
    # =========================================
    @staticmethod
    def repeat_customer():

        return (
            CustomerAnalyticsService
            .repeat_customers()
        )

    # =========================================
    # CUSTOMER REVENUE DISTRIBUTION
    # =========================================
    @staticmethod
    def customer_revenue_distribution():

        return (
            CustomerAnalyticsService
            .customer_contribution()
        )

    # =========================================
    # CUSTOMER SEGMENTATION
    # =========================================
    @staticmethod
    def customer_segmentation():

        top_spenders = (
            CustomerAnalyticsService
            .top_spenders()
        )

        most_active = (
            CustomerAnalyticsService
            .most_active_customers()
        )

        repeat_customers = (
            CustomerAnalyticsService
            .repeat_customers()
        )

        contribution = (
            CustomerAnalyticsService
            .customer_contribution()
        )

        return {

            "top_spenders":
                top_spenders,

            "most_active":
                most_active,

            "repeat_customers":
                repeat_customers,

            "contribution":
                contribution
        }

    # =========================================
    # DSS EXECUTIVE INSIGHT
    # =========================================
    @staticmethod
    def executive_insight():

        return (
            DSSService
            .executive_insight()
        )

    # =========================================
    # PRODUCT PRIORITY
    # =========================================
    @staticmethod
    def product_priority():

        return (
            DSSService
            .product_priority_analysis()
        )

    # =========================================
    # REVENUE CONTRIBUTION
    # =========================================
    @staticmethod
    def revenue_percentage():

        return (
            DSSService
            .revenue_contribution_analysis()
        )

    # =========================================
    # FORECAST INSIGHT
    # =========================================
    @staticmethod
    def forecast_insight():

        return (
            DSSService
            .forecast_insight()
        )

    # =========================================
    # ABC CLASSIFICATION
    # =========================================
    @staticmethod
    def abc_classification():

        return (
            DSSService
            .abc_classification()
        )

    # =========================================
    # ABC SUMMARY
    # =========================================
    @staticmethod
    def abc_summary():

        abc_data = (
            DSSService
            .abc_classification()
        )

        return {

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