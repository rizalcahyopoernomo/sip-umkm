from models.entities import (
    db,
    Product,
    StockMovement,
    TransactionItem
)


class InventoryService:

    # =========================
    # RESTOCK PRODUCT
    # =========================
    @staticmethod
    def restock_product(product_id, qty, note=None):

        try:

            product = db.session.get(
                Product,
                product_id
            )

            # =========================
            # VALIDASI PRODUCT
            # =========================
            if not product or not product.is_active:

                raise Exception(
                    "Produk tidak ditemukan / sudah dihapus"
                )

            # =========================
            # VALIDASI QTY
            # =========================
            if qty <= 0:

                raise Exception(
                    "Qty harus lebih dari 0"
                )

            # =========================
            # UPDATE STOCK
            # =========================
            product.stock += qty

            # =========================
            # STOCK MOVEMENT
            # =========================
            movement = StockMovement(

                product_id=product.id,

                type='IN',

                qty=qty,

                note=note or "Restock"
            )

            db.session.add(movement)

            # =========================
            # SAVE SESSION
            # =========================
            db.session.flush()

            return True

        except Exception:

            return False

    # =========================
    # REDUCE STOCK
    # =========================
    @staticmethod
    def reduce_stock(product_id, qty):

        try:

            product = db.session.get(
                Product,
                product_id
            )

            # =========================
            # VALIDASI PRODUCT
            # =========================
            if not product or not product.is_active:

                raise Exception(
                    "Produk tidak ditemukan"
                )

            # =========================
            # VALIDASI QTY
            # =========================
            if qty <= 0:

                raise Exception(
                    "Qty tidak valid"
                )

            # =========================
            # VALIDASI STOCK
            # =========================
            if product.stock < qty:

                raise Exception(
                    f"Stok tidak cukup (sisa: {product.stock})"
                )

            # =========================
            # REDUCE STOCK
            # =========================
            product.stock -= qty

            # =========================
            # STOCK MOVEMENT
            # =========================
            movement = StockMovement(

                product_id=product.id,

                type='OUT',

                qty=qty,

                note="Penjualan"
            )

            db.session.add(movement)

            # =========================
            # SAVE SESSION
            # =========================
            db.session.flush()

            return True

        except Exception:

            return False

    # =========================
    # ADJUST STOCK
    # =========================
    @staticmethod
    def adjust_stock(product_id, qty, note=None):

        try:

            product = db.session.get(
                Product,
                product_id
            )

            # =========================
            # VALIDASI PRODUCT
            # =========================
            if not product or not product.is_active:

                raise Exception(
                    "Produk tidak ditemukan"
                )

            # =========================
            # VALIDASI QTY
            # =========================
            if qty == 0:

                raise Exception(
                    "Qty tidak boleh 0"
                )

            # =========================
            # HITUNG STOCK BARU
            # =========================
            new_stock = product.stock + qty

            # =========================
            # VALIDASI STOCK
            # =========================
            if new_stock < 0:

                raise Exception(
                    "Stok tidak boleh minus"
                )

            # =========================
            # UPDATE STOCK
            # =========================
            product.stock = new_stock

            # =========================
            # DETERMINE MOVEMENT TYPE
            # =========================
            movement_type = (
                'IN'
                if qty > 0
                else 'OUT'
            )

            # =========================
            # STOCK MOVEMENT
            # =========================
            movement = StockMovement(

                product_id=product.id,

                type=movement_type,

                qty=abs(qty),

                note=note or "Penyesuaian stok"
            )

            db.session.add(movement)

            # =========================
            # SAVE SESSION
            # =========================
            db.session.flush()

            return True

        except Exception:

            return False

    # =========================
    # DELETE PRODUCT
    # =========================
    @staticmethod
    def delete_product(product_id):

        try:

            product = db.session.get(
                Product,
                product_id
            )

            # =========================
            # VALIDASI PRODUCT
            # =========================
            if not product:

                raise Exception(
                    "Produk tidak ditemukan"
                )

            if not product.is_active:

                raise Exception(
                    "Produk sudah dihapus"
                )

            # =========================
            # VALIDASI TRANSACTION
            # =========================
            used = TransactionItem.query.filter_by(
                product_id=product_id
            ).first()

            if used:

                raise Exception(
                    "Produk sudah pernah digunakan dalam transaksi"
                )

            # =========================
            # SOFT DELETE
            # =========================
            product.is_active = False

            # =========================
            # STOCK MOVEMENT
            # =========================
            movement = StockMovement(

                product_id=product.id,

                type='DELETE',

                qty=0,

                note="Produk dihapus"
            )

            db.session.add(movement)

            # =========================
            # SAVE SESSION
            # =========================
            db.session.flush()

            return True

        except Exception:

            return False

    # =========================
    # LOW STOCK
    # =========================
    @staticmethod
    def get_low_stock():

        try:

            return Product.query.filter(

                Product.stock <= Product.min_stock,

                Product.is_active == True

            ).all()

        except Exception:

            return []

    # =========================
    # STOCK HISTORY
    # =========================
    @staticmethod
    def get_stock_history(product_id):

        try:

            return (
                StockMovement.query

                .filter_by(
                    product_id=product_id
                )

                .order_by(
                    StockMovement.created_at.desc()
                )

                .all()
            )

        except Exception:

            return []