from models.entities import (
    db,
    Transaction,
    TransactionItem,
    Product
)

from datetime import datetime

import random

from services.inventory_service import InventoryService


class POSService:

    @staticmethod
    def process_transaction(

        cart_data,
        cashier_id,
        customer_name,
        payment_method,
        amount_paid

    ):

        try:

            # =========================
            # VALIDASI CART
            # =========================
            if not cart_data:

                return (

                    False,

                    "Keranjang kosong!",

                    None
                )

            # =========================
            # VALIDASI PAYMENT METHOD
            # =========================
            valid_payment = [

                "Tunai",

                "QRIS",

                "Transfer"
            ]

            if payment_method not in valid_payment:

                return (

                    False,

                    "Metode pembayaran tidak valid!",

                    None
                )

            # =========================
            # CUSTOMER NAME CLEANUP
            # =========================
            customer_name = (

                customer_name.strip()

                if customer_name
                and customer_name.strip()

                else "Pelanggan Umum"
            )

            # =========================
            # INITIAL TOTAL
            # =========================
            total_amount = 0

            validated_items = []

            # =========================
            # GENERATE SAFE INVOICE
            # =========================
            invoice_number = (

                f"INV-"

                f"{datetime.now().strftime('%Y%m%d%H%M%S')}-"

                f"{random.randint(1000, 9999)}"
            )

            # =========================
            # VALIDASI & HITUNG TOTAL
            # =========================
            for item in cart_data:

                product = db.session.get(

                    Product,
                    item.get('product_id')
                )

                # =========================
                # VALIDASI PRODUCT
                # =========================
                if not product:

                    return (

                        False,

                        "Produk tidak ditemukan!",

                        None
                    )

                # =========================
                # VALIDASI QTY
                # =========================
                try:

                    qty = int(

                        item.get('qty', 0)
                    )

                except Exception:

                    return (

                        False,

                        "Qty produk tidak valid!",

                        None
                    )

                if qty <= 0:

                    return (

                        False,

                        "Qty produk harus lebih dari 0!",

                        None
                    )

                # =========================
                # VALIDASI STOCK
                # =========================
                if product.stock < qty:

                    return (

                        False,

                        f"Stok {product.name} tidak cukup!",

                        None
                    )

                # =========================
                # ITEM CALCULATION
                # =========================
                price = round(

                    float(product.price),

                    2
                )

                subtotal = round(

                    price * qty,

                    2
                )

                total_amount += subtotal

                total_amount = round(

                    total_amount,

                    2
                )

                validated_items.append({

                    "product": product,

                    "qty": qty,

                    "price": price,

                    "subtotal": subtotal
                })

            # =========================
            # VALIDASI PEMBAYARAN
            # =========================
            if amount_paid < total_amount:

                return (

                    False,

                    "Uang tidak cukup!",

                    None
                )

            # =========================
            # CREATE TRANSACTION
            # =========================
            new_transaction = Transaction(

                invoice_number=invoice_number,

                cashier_id=cashier_id,

                customer_name=customer_name,

                subtotal=0,

                discount=0,

                total_amount=0,

                payment_method=payment_method,

                amount_paid=round(

                    float(amount_paid),

                    2
                ),

                change_amount=0,

                timestamp=datetime.now()
            )

            db.session.add(new_transaction)

            db.session.flush()

            # =========================
            # SAVE ITEMS & REDUCE STOCK
            # =========================
            for item in validated_items:

                product = item['product']

                qty = item['qty']

                price = item['price']

                subtotal = item['subtotal']

                # =========================
                # SAVE TRANSACTION ITEM
                # =========================
                detail = TransactionItem(

                    transaction_id=new_transaction.id,

                    product_id=product.id,

                    product_name=product.name,

                    price_at_time=price,

                    qty=qty,

                    subtotal=subtotal,

                    created_at=new_transaction.timestamp
                )

                db.session.add(detail)

                # =========================
                # REDUCE INVENTORY
                # =========================
                success = InventoryService.reduce_stock(

                    product_id=product.id,

                    qty=qty
                )

                # =========================
                # STOCK FAILED
                # =========================
                if not success:

                    db.session.rollback()

                    return (

                        False,

                        f"Stok {product.name} tidak cukup!",

                        None
                    )

            # =========================
            # FINAL TRANSACTION
            # =========================
            new_transaction.subtotal = round(

                total_amount,

                2
            )

            new_transaction.total_amount = round(

                total_amount,

                2
            )

            new_transaction.change_amount = round(

                amount_paid - total_amount,

                2
            )

            # =========================
            # SAVE TRANSACTION
            # =========================
            db.session.commit()

            # =========================
            # SUCCESS RESPONSE
            # =========================
            return (

                True,

                "Transaksi berhasil!",

                new_transaction.invoice_number
            )

        except Exception as e:

            db.session.rollback()

            print(
                f"[POS ERROR] {str(e)}"
            )

            return (

                False,

                "Terjadi kesalahan saat transaksi",

                None
            )