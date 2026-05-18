# utils/helper.py

from datetime import datetime


# =========================================
# FORMAT RUPIAH
# =========================================
def format_rupiah(value):

    try:

        return (

            "Rp {:,.0f}"

            .format(value)

            .replace(",", ".")
        )

    except Exception:

        return "Rp 0"


# =========================================
# FORMAT PERCENTAGE
# =========================================
def format_percentage(value):

    try:

        return f"{value:.1f}%"

    except Exception:

        return "0%"


# =========================================
# FORMAT DATETIME
# =========================================
def format_datetime(value):

    try:

        return value.strftime(
            "%d %B %Y %H:%M"
        )

    except Exception:

        return "-"


# =========================================
# FORMAT DATE
# =========================================
def format_date(value):

    try:

        return value.strftime(
            "%d %B %Y"
        )

    except Exception:

        return "-"


# =========================================
# COMPACT NUMBER
# =========================================
def format_compact_number(value):

    try:

        value = float(value)

        if value >= 1_000_000:

            return f"{value / 1_000_000:.1f}M"

        if value >= 1_000:

            return f"{value / 1_000:.1f}K"

        return str(int(value))

    except Exception:

        return "0"