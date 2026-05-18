# services/dss_service.py

import math

from models.entities import Product
from services.ml_service import MLService


class DSSService:

    # =========================
    # STEP 2: STOCK DEPLETION
    # =========================
    @staticmethod
    def stock_depletion_analysis(days=30):

        ml_data = MLService.get_all_predictions(days)
        products = Product.query.filter_by(is_active=True).all()

        results = []

        for p in products:

            pred = ml_data.get(p.id, {}).get("predicted_sales", 0)

            if pred <= 0:

                days_left = 0
                status = "NO DATA"

            else:

                days_left = p.stock / pred

                if days_left < p.restock_cycle:
                    status = "CRITICAL"

                elif days_left < (p.restock_cycle * 2):
                    status = "WARNING"

                else:
                    status = "SAFE"

            results.append({

                "product_id": p.id,

                "name": p.name,

                "stock": p.stock,

                "predicted_sales": round(pred, 2),

                "days_left": round(days_left, 2),

                "status": status
            })

        return results


    # =========================
    # STEP 3: RESTOCK
    # =========================
    @staticmethod
    def restock_recommendation(days=30, safety_factor=1.2):

        ml_data = MLService.get_all_predictions(days)
        products = Product.query.filter_by(is_active=True).all()

        results = []

        for p in products:

            pred = ml_data.get(
                p.id,
                {}
            ).get(
                "predicted_sales",
                0
            )

            # =========================
            # LOCAL DEPLETION LOGIC
            # =========================

            if pred <= 0:

                depletion_status = "NO DATA"
                days_left = 0

            else:

                days_left = p.stock / pred

                if days_left < p.restock_cycle:
                    depletion_status = "CRITICAL"

                elif days_left < (p.restock_cycle * 2):
                    depletion_status = "WARNING"

                else:
                    depletion_status = "SAFE"

            # =========================
            # NO DEMAND
            # =========================

            if pred <= 0:

                results.append({

                    "product_id": p.id,

                    "name": p.name,

                    "stock": p.stock,

                    "predicted_sales": 0,

                    "target_stock": 0,

                    "restock_qty": 0,

                    "recommended_stock": 0,

                    "reorder_suggestion": 0,

                    "days_left": 0,

                    "status": "NO DATA",

                    "depletion_status": depletion_status
                })

                continue

            # =========================
            # TARGET STOCK
            # =========================

            target_stock = (
                pred *
                p.restock_cycle *
                safety_factor
            )

            target_stock = math.ceil(
                max(0, target_stock)
            )

            # =========================
            # RESTOCK QTY
            # =========================

            restock_qty = max(
                0,
                math.ceil(target_stock - p.stock)
            )

            # =========================
            # WARNING BUFFER
            # =========================

            if depletion_status == "WARNING" and restock_qty == 0:

                restock_qty = math.ceil(pred * 2)

            # =========================
            # REORDER SUGGESTION
            # =========================

            reorder_suggestion = math.ceil(
                pred * p.restock_cycle
            )

            # =========================
            # STATUS
            # =========================

            status = (
                "ORDER"
                if restock_qty > 0
                else "ENOUGH"
            )

            results.append({

                "product_id": p.id,

                "name": p.name,

                "stock": p.stock,

                "predicted_sales": round(pred, 2),

                "target_stock": target_stock,

                "recommended_stock": target_stock,

                "restock_qty": restock_qty,

                "reorder_suggestion": reorder_suggestion,

                "days_left": round(days_left, 2),

                "status": status,

                "depletion_status": depletion_status
            })

        return results


    # =========================
    # STEP 4: MOVEMENT
    # =========================
    @staticmethod
    def product_movement_analysis(days=30):

        ml_data = MLService.get_all_predictions(days)
        products = Product.query.filter_by(is_active=True).all()

        data = []

        for p in products:

            pred = ml_data.get(
                p.id,
                {}
            ).get(
                "predicted_sales",
                0
            )

            data.append({

                "product_id": p.id,

                "name": p.name,

                "predicted_sales": pred
            })

        data.sort(
            key=lambda x: x["predicted_sales"],
            reverse=True
        )

        total = len(data)

        fast_cutoff = int(total * 0.3)
        slow_cutoff = int(total * 0.7)

        results = []

        for i, item in enumerate(data):

            if item["predicted_sales"] <= 0:

                category = "NO DATA"

            elif i < fast_cutoff:

                category = "FAST MOVING"

            elif i >= slow_cutoff:

                category = "SLOW MOVING"

            else:

                category = "MEDIUM"

            results.append({

                "product_id": item["product_id"],

                "name": item["name"],

                "predicted_sales": round(
                    item["predicted_sales"],
                    2
                ),

                "category": category
            })

        return results


    # =========================
    # STEP 5: PRIORITY SCORE
    # =========================
    @staticmethod
    def product_priority_analysis(days=30):

        ml_data = MLService.get_all_predictions(days)
        products = Product.query.filter_by(is_active=True).all()

        results = []

        for p in products:

            pred = ml_data.get(
                p.id,
                {}
            ).get(
                "predicted_sales",
                0
            )

            raw_margin = (
                (p.price - p.cost)
                if p.cost
                else p.price
            )

            margin = max(0, raw_margin)

            safe_stock = max(1, p.stock)

            score = (
                (pred * margin) / safe_stock
                if pred > 0
                else 0
            )

            results.append({

                "product_id": p.id,

                "name": p.name,

                "predicted_sales": round(pred, 2),

                "stock": p.stock,

                "margin": round(margin, 2),

                "priority_score": round(score, 4)
            })

        results.sort(
            key=lambda x: x["priority_score"],
            reverse=True
        )

        return results


    # =========================
    # STEP 6: PARETO
    # =========================
    @staticmethod
    def revenue_contribution_analysis(days=30):

        from services.report_service import ReportService

        daily_data = ReportService.get_daily_sales(days)

        products = Product.query.filter_by(
            is_active=True
        ).all()

        product_map = {
            p.id: p
            for p in products
        }

        revenue_list = []

        for product_id, data in daily_data.items():

            total_qty = sum(
                d["qty"]
                for d in data
            )

            product = product_map.get(product_id)

            if not product:
                continue

            revenue = total_qty * product.price

            revenue_list.append({

                "product_id": product_id,

                "name": product.name,

                "revenue": revenue
            })

        revenue_list.sort(
            key=lambda x: x["revenue"],
            reverse=True
        )

        total_revenue = sum(
            x["revenue"]
            for x in revenue_list
        )

        cumulative = 0

        results = []

        for item in revenue_list:

            contribution = (

                (item["revenue"] / total_revenue * 100)

                if total_revenue

                else 0
            )

            cumulative += contribution

            cumulative = min(cumulative, 100)

            if cumulative <= 80:

                category = "TOP (80%)"

            elif cumulative <= 95:

                category = "MEDIUM"

            else:

                category = "LOW"

            results.append({

                "product_id": item["product_id"],

                "name": item["name"],

                "revenue": round(
                    item["revenue"],
                    2
                ),

                "contribution_pct": round(
                    contribution,
                    2
                ),

                "cumulative_pct": round(
                    cumulative,
                    2
                ),

                "category": category
            })

        return results

    # =========================
    # STEP 6.5: ABC CLASSIFICATION
    # =========================
    @staticmethod
    def abc_classification(days=30):

        pareto_data = DSSService.revenue_contribution_analysis(days)

        results = []

        for item in pareto_data:

            cumulative = item.get(
                "cumulative_pct",
                0
            )

            # =========================
            # CLASSIFICATION
            # =========================

            if cumulative <= 80:

                abc_class = "A"

                class_color = "success"

                class_description = (
                    "High Revenue Contribution"
                )

            elif cumulative <= 95:

                abc_class = "B"

                class_color = "warning"

                class_description = (
                    "Medium Revenue Contribution"
                )

            else:

                abc_class = "C"

                class_color = "secondary"

                class_description = (
                    "Low Revenue Contribution"
                )

            # =========================
            # INVENTORY PRIORITY
            # =========================

            if abc_class == "A":

                inventory_priority = (
                    "HIGH PRIORITY"
                )

            elif abc_class == "B":

                inventory_priority = (
                    "MEDIUM PRIORITY"
                )

            else:

                inventory_priority = (
                    "LOW PRIORITY"
                )

            # =========================
            # RESULT
            # =========================

            results.append({

                "product_id":
                item.get("product_id"),

                "name":
                item.get("name"),

                "revenue":
                round(
                    item.get("revenue", 0),
                    2
                ),

                "contribution_pct":
                round(
                    item.get(
                        "contribution_pct",
                        0
                    ),
                    2
                ),

                "cumulative_pct":
                round(
                    cumulative,
                    2
                ),

                "class":
                abc_class,

                "class_color":
                class_color,

                "class_description":
                class_description,

                "inventory_priority":
                inventory_priority
            })

        return results
    # =========================
    # STEP 7: FORECAST INSIGHT
    # =========================
    @staticmethod
    def forecast_insight(days=7):

        HIGH_DEMAND_THRESHOLD = 10
        LOW_DEMAND_THRESHOLD = 3

        ml_data = MLService.get_all_predictions(days)

        products = Product.query.filter_by(
            is_active=True
        ).all()

        insights = []

        for p in products:

            pred = ml_data.get(
                p.id,
                {}
            ).get(
                "predicted_sales",
                0
            )

            if pred == 0:

                insights.append({

                    "name": p.name,

                    "type": "no_demand",

                    "confidence": 0,

                    "message":
                    f"{p.name} tidak menunjukkan permintaan dalam {days} hari ke depan"
                })

            elif pred > HIGH_DEMAND_THRESHOLD:

                confidence = min(
                    100,
                    int(pred * 5)
                )

                insights.append({

                    "name": p.name,

                    "type": "high_demand",

                    "confidence": confidence,

                    "message":
                    f"Permintaan {p.name} diprediksi tinggi sekitar {round(pred,1)} unit/hari (confidence {confidence}%)"
                })

            elif pred < LOW_DEMAND_THRESHOLD:

                confidence = min(
                    100,
                    int(pred * 20)
                )

                insights.append({

                    "name": p.name,

                    "type": "low_demand",

                    "confidence": confidence,

                    "message":
                    f"Permintaan {p.name} rendah sekitar {round(pred,1)} unit/hari"
                })

            else:

                insights.append({

                    "name": p.name,

                    "type": "normal",

                    "confidence": min(
                        100,
                        int(pred * 8)
                    ),

                    "message":
                    f"Permintaan {p.name} stabil di kisaran {round(pred,1)} unit/hari"
                })

        return insights


    # =========================
    # STEP 8: EXECUTIVE SUMMARY
    # =========================
    @staticmethod
    def executive_summary(days=30):

        forecast = DSSService.forecast_insight(days)

        depletion = DSSService.stock_depletion_analysis(days)

        critical_items = [
            x for x in depletion
            if x["status"] == "CRITICAL"
        ]

        warning_items = [
            x for x in depletion
            if x["status"] == "WARNING"
        ]

        high_demand = [
            x for x in forecast
            if x["type"] == "high_demand"
        ]

        summary = []

        if high_demand:

            summary.append(
                f"{len(high_demand)} produk memiliki permintaan tinggi"
            )

        if critical_items:

            summary.append(
                f"{len(critical_items)} produk berpotensi habis dalam waktu dekat"
            )

        if warning_items:

            summary.append(
                f"{len(warning_items)} produk perlu perhatian stok"
            )

        if not summary:

            summary.append(
                "Kondisi bisnis stabil dan terkendali"
            )

        return summary


    # =========================
    # STEP 9: EXECUTIVE INSIGHT
    # =========================
    @staticmethod
    def executive_insight(days=7):

        insights = []

        depletion = DSSService.stock_depletion_analysis(days)

        priority = DSSService.product_priority_analysis(days)

        abc_data = DSSService.abc_classification(days)

        forecast = DSSService.forecast_insight(days)

        # =========================
        # REVENUE DOMINANCE
        # =========================

        top_products = [

            p for p in abc_data
            if p.get(
                "cumulative_pct",
                0
            ) <= 80
        ]

        if top_products:

            insights.append({

                "type": "revenue",

                "icon": "📊",

                "title": "Revenue Dominance",

                "message":
                f"80% omzet berasal dari {len(top_products)} produk utama"
            })

        # =========================
        # CRITICAL STOCK
        # =========================

        critical = [

            x for x in depletion

            if x.get("status") == "CRITICAL"
        ]

        critical_fast = [

            x for x in critical

            if (
                x.get("days_left")
                or 0
            ) < 2
        ]

        if critical_fast:

            insights.append({

                "type": "critical",

                "icon": "⚠️",

                "title": "Critical Stock",

                "message":
                f"{len(critical_fast)} produk diprediksi habis dalam kurang dari 2 hari"
            })

        # =========================
        # NO DEMAND
        # =========================

        no_demand = [

            x for x in forecast

            if x.get("type") == "no_demand"
        ]

        if no_demand:

            insights.append({

                "type": "forecast",

                "icon": "📉",

                "title": "Low Demand",

                "message":
                f"{len(no_demand)} produk tidak menunjukkan demand dalam {days} hari ke depan"
            })

        # =========================
        # PRIORITY PRODUCT
        # =========================

        if priority:

            top_priority = priority[0]

            insights.append({

                "type": "priority",

                "icon": "🔥",

                "title": "Restock Priority",

                "message":
                f"{top_priority['name']} memiliki priority restock tertinggi"
            })

        # =========================
        # CATEGORY A DOMINANCE
        # =========================
        class_a = [

             p for p in abc_data

             if p.get("class") == "A"
        ]

        if class_a:

            insights.append({

                "type": "abc",

                "icon": "🏆",

                "title": "Top Category",

                "message":
                "Produk kategori A mendominasi kontribusi revenue"
            })

        # =========================
        # HIGH DEMAND TREND
        # =========================

        high_demand = [

            x for x in forecast

            if x.get("type") == "high_demand"
        ]

        if high_demand:

            insights.append({

                "type": "trend",

                "icon": "📈",

                "title": "Demand Trend",

                "message":
                f"{len(high_demand)} produk menunjukkan tren permintaan tinggi"
            })

        return insights[:5]