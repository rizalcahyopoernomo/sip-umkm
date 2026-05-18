# services/ml_service.py

import numpy as np
from sklearn.linear_model import LinearRegression
from services.report_service import ReportService


class MLService:

    # =========================
    # 🔥 BUILD TIME SERIES
    # Zero-filling included: hari tanpa penjualan = 0
    # =========================
    @staticmethod
    def build_time_series(product_data, fill_days=30):
        """
        input:
        [
          {"date": "2024-01-01", "qty": 5},
          {"date": "2024-01-03", "qty": 7}
        ]

        output:
        [5, 0, 7, 0, 0, ...]  ← zero-filled untuk hari tanpa transaksi

        FIX: Zero-Filling — hari tanpa penjualan diisi 0 agar model
        tidak bias ke angka tinggi akibat gap antar transaksi.
        """

        if not product_data:
            return []

        try:
            # Build lookup: date_str -> qty
            date_qty_map = {}

            for d in product_data:
                try:
                    date_key = str(d.get("date", "")).strip()
                    qty      = max(0, float(d.get("qty", 0)))

                    if date_key:
                        date_qty_map[date_key] = qty

                except Exception:
                    continue

            if not date_qty_map:
                return []

            # Jika tidak ada date info, fallback ke list biasa
            # (kompatibel dengan caller lama yang tidak kirim date)
            if len(date_qty_map) == 0:
                return [
                    max(0, float(d.get("qty", 0)))
                    for d in product_data
                ]

            # Zero-fill: urutkan berdasar tanggal, isi 0 untuk gap
            from datetime import datetime, timedelta

            dates_parsed = []
            for date_str, qty in date_qty_map.items():
                try:
                    dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
                    dates_parsed.append((dt, qty))
                except Exception:
                    continue

            if not dates_parsed:
                # Fallback: tidak bisa parse date, kembalikan list qty saja
                return [
                    max(0, float(d.get("qty", 0)))
                    for d in product_data
                ]

            dates_parsed.sort(key=lambda x: x[0])

            min_date = dates_parsed[0][0]
            max_date = dates_parsed[-1][0]

            # Build series dengan zero-fill
            filled_series = []
            current_date  = min_date

            while current_date <= max_date:
                date_str = current_date.strftime("%Y-%m-%d")
                filled_series.append(date_qty_map.get(date_str, 0.0))
                current_date += timedelta(days=1)

            return filled_series

        except Exception:
            # Fallback paling aman: kembalikan list qty mentah
            try:
                return [
                    max(0, float(d.get("qty", 0)))
                    for d in product_data
                ]
            except Exception:
                return []


    # =========================
    # 🔥 MOVING AVERAGE SMOOTHING
    # PRIORITAS 3: Smoothing ringan agar forecast tidak "loncat"
    # =========================
    @staticmethod
    def _apply_smoothing(series, window=3):
        """
        Simple Moving Average untuk data < 7 poin.
        Mengurangi efek outlier tanpa menghilangkan tren.
        """

        if len(series) < window:
            return series

        smoothed = []

        for i in range(len(series)):
            start = max(0, i - window + 1)
            window_vals = series[start:i + 1]
            smoothed.append(sum(window_vals) / len(window_vals))

        return smoothed


    # =========================
    # 🔥 PREDICT NEXT DAY SALES
    # PRIORITAS 2: Prediction cap (max 2x rata-rata historis)
    # PRIORITAS 3: Smoothing untuk data < 7 poin
    # =========================
    @staticmethod
    def predict_next_day(sales_series):
        """
        Linear Regression prediction dengan:
        - Smoothing untuk data pendek (< 7 poin)
        - Slope constraint: prediksi max 2x rata-rata historis
        - Semua safety validation dipertahankan
        """

        # =========================
        # SAFETY VALIDATION
        # =========================

        if not sales_series:
            return 0

        # Remove invalid values (cleaning hanya di sini, tidak duplikat)
        cleaned_series = []

        for value in sales_series:
            try:
                cleaned_series.append(max(0, float(value)))
            except Exception:
                continue

        # Fallback jika semua invalid
        if not cleaned_series:
            return 0

        # =========================
        # HITUNG RATA-RATA HISTORIS
        # Digunakan untuk prediction cap
        # =========================

        historical_avg = sum(cleaned_series) / len(cleaned_series)

        # =========================
        # FALLBACK DATA MINIMAL
        # =========================

        if len(cleaned_series) == 1:
            return round(cleaned_series[0], 2)

        if len(cleaned_series) < 3:
            avg = sum(cleaned_series) / len(cleaned_series)
            return round(max(0, float(avg)), 2)

        # =========================
        # PRIORITAS 3: SMOOTHING
        # Untuk data < 7 poin, gunakan Moving Average
        # agar slope tidak terlalu tajam akibat outlier
        # =========================

        if len(cleaned_series) < 7:
            series_to_use = MLService._apply_smoothing(cleaned_series, window=3)
        else:
            series_to_use = cleaned_series

        # =========================
        # LINEAR REGRESSION
        # =========================

        try:

            X = np.array(
                range(len(series_to_use))
            ).reshape(-1, 1)

            y = np.array(series_to_use)

            model = LinearRegression()
            model.fit(X, y)

            next_day = np.array([[len(series_to_use)]])

            prediction = model.predict(next_day)[0]

            # Prevent minus prediction
            prediction = max(0, float(prediction))

            # Prevent NaN
            if np.isnan(prediction):
                return round(historical_avg, 2)

            # =========================
            # PRIORITAS 2: PREDICTION CAP
            # Batasi prediksi maksimal 2x rata-rata historis
            # agar tidak overpredict saat ada outlier
            # =========================

            cap = historical_avg * 2.0

            if historical_avg > 0 and prediction > cap:
                prediction = cap

            return round(prediction, 2)

        except Exception:

            # Graceful fallback ke rata-rata
            return round(max(0, historical_avg), 2)


    # =========================
    # 🔥 TREND ANALYSIS
    # PRIORITAS 1: Stabilized trend detection
    # Pakai linear regression slope, bukan hanya first vs last
    # =========================
    @staticmethod
    def detect_trend(series):
        """
        FIX: Trend detection menggunakan slope regresi linier,
        bukan hanya perbandingan titik pertama vs terakhir.

        Alasan: first-last tidak menangkap volatilitas di tengah.
        Misal: [1, 10, 1] → first=1, last=1 → STABLE (salah).
        Dengan slope: tren sesungguhnya terdeteksi lebih akurat.

        Threshold slope dikalibrasi terhadap rata-rata agar
        proporsional untuk semua skala data.
        """

        if not series or len(series) < 2:
            return "STABLE"

        try:
            cleaned = [max(0, float(v)) for v in series]

            if len(cleaned) < 2:
                return "STABLE"

            # Hitung slope via linear regression
            X = np.array(range(len(cleaned))).reshape(-1, 1)
            y = np.array(cleaned)

            model = LinearRegression()
            model.fit(X, y)

            slope = float(model.coef_[0])

            # Threshold: 10% dari rata-rata per hari
            # Proporsional → tidak bias ke skala besar/kecil
            avg = sum(cleaned) / len(cleaned)

            if avg == 0:
                return "STABLE"

            threshold = avg * 0.10

            if slope > threshold:
                return "UP"

            elif slope < -threshold:
                return "DOWN"

            return "STABLE"

        except Exception:
            return "STABLE"


    # =========================
    # 🔥 CONFIDENCE LOGIC
    # PRIORITAS 4: Confidence level berdasar jumlah data poin
    # =========================
    @staticmethod
    def get_confidence(history_points):
        """
        Mengembalikan confidence level prediksi
        berdasar jumlah titik data historis.

        LOW    : < 7 hari  → data terlalu sedikit
        MEDIUM : 7–14 hari → cukup untuk tren awal
        HIGH   : > 14 hari → prediksi lebih dapat diandalkan
        """

        if history_points < 7:
            return "LOW"

        elif history_points <= 14:
            return "MEDIUM"

        return "HIGH"


    # =========================
    # 🔥 GET ALL PRODUCT PREDICTIONS
    # Struktur dipertahankan, ditambah confidence field
    # =========================
    @staticmethod
    def get_all_predictions(days=30):
        """
        Output:
        {
          product_id: {
            "predicted_sales": 5.2,
            "trend": "UP / DOWN / STABLE",
            "history_points": 12,
            "confidence": "LOW / MEDIUM / HIGH"
          }
        }
        """

        try:

            daily_data = ReportService.get_daily_sales(days)

            if not daily_data:
                return {}

            results = {}

            for product_id, data in daily_data.items():

                # =========================
                # BUILD SERIES
                # Zero-filling sudah handle di dalam build_time_series
                # =========================

                series = MLService.build_time_series(data)

                # =========================
                # PREDICTION
                # Cleaning dilakukan hanya di predict_next_day
                # tidak duplikat di sini (fix redundant cleaning)
                # =========================

                prediction = MLService.predict_next_day(series)

                # =========================
                # TREND
                # Pakai slope regression, bukan first-last
                # =========================

                trend = MLService.detect_trend(series)

                # =========================
                # CONFIDENCE
                # =========================

                confidence = MLService.get_confidence(len(series))

                # =========================
                # RESULT
                # =========================

                results[product_id] = {

                    "predicted_sales": round(
                        max(0, prediction),
                        2
                    ),

                    "trend": trend,

                    "history_points": len(series),

                    "confidence": confidence
                }

            return results

        except Exception as e:

            print("❌ ML PREDICTION ERROR:", str(e))

            return {}