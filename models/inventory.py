from models.db import get_db


class InventoryModel:
    @staticmethod
    def get_logs(product_id=None, limit=50):
        db = get_db()
        with db.cursor() as cursor:
            query = """
                SELECT il.*, p.name as product_name, p.brand,
                       s.name as supplier_name,
                       u.fullname as created_by_name
                FROM inventory_logs il
                JOIN products p ON il.product_id = p.id
                LEFT JOIN suppliers s ON il.supplier_id = s.id
                JOIN users u ON il.created_by = u.id
            """
            params = []
            if product_id:
                query += " WHERE il.product_id = %s"
                params.append(product_id)
            query += " ORDER BY il.created_at DESC LIMIT %s"
            params.append(limit)
            cursor.execute(query, params)
            return cursor.fetchall()

    @staticmethod
    def import_stock(product_id, supplier_id, quantity, note, created_by):
        if quantity <= 0:
            return False
        db = get_db()
        try:
            with db.cursor() as cursor:
                # Ghi log nhập kho
                cursor.execute("""
                    INSERT INTO inventory_logs (product_id, supplier_id, type, quantity, note, created_by)
                    VALUES (%s, %s, 'import', %s, %s, %s)
                """, (product_id, supplier_id or None, quantity, note, created_by))

                # Cập nhật tồn kho sản phẩm
                cursor.execute("UPDATE products SET stock = stock + %s WHERE id = %s", (quantity, product_id))

                db.commit()
                return True
        except Exception as e:
            db.rollback()
            print(f"Lỗi nhập kho: {e}")
            return False

    @staticmethod
    def export_stock(product_id, quantity, note, created_by):
        if quantity <= 0:
            return False
        db = get_db()
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT stock FROM products WHERE id = %s FOR UPDATE", (product_id,))
                product = cursor.fetchone()
                if not product or product['stock'] < quantity:
                    db.rollback()
                    return False
                    
                cursor.execute("""
                    INSERT INTO inventory_logs (product_id, type, quantity, note, created_by)
                    VALUES (%s, 'export', %s, %s, %s)
                """, (product_id, quantity, note, created_by))

                cursor.execute("UPDATE products SET stock = stock - %s WHERE id = %s", (quantity, product_id))

                db.commit()
                return True
        except Exception as e:
            db.rollback()
            print(f"Lỗi xuất kho: {e}")
            return False

    @staticmethod
    def adjust_stock(product_id, quantity, note, created_by):
        db = get_db()
        try:
            with db.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO inventory_logs (product_id, type, quantity, note, created_by)
                    VALUES (%s, 'adjustment', %s, %s, %s)
                """, (product_id, quantity, note, created_by))

                cursor.execute("UPDATE products SET stock = %s WHERE id = %s", (quantity, product_id))

                db.commit()
                return True
        except Exception as e:
            db.rollback()
            print(f"Lỗi điều chỉnh kho: {e}")
            return False

    @staticmethod
    def get_stock_summary():
        """Tổng hợp tồn kho theo sản phẩm"""
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT p.id, p.name, p.brand, p.stock, p.price, p.is_active,
                       (SELECT SUM(il.quantity) FROM inventory_logs il 
                        WHERE il.product_id = p.id AND il.type = 'import') as total_imported,
                       (SELECT SUM(il.quantity) FROM inventory_logs il 
                        WHERE il.product_id = p.id AND il.type = 'export') as total_exported
                FROM products p
                ORDER BY p.stock ASC
            """)
            return cursor.fetchall()

    @staticmethod
    def get_low_stock(threshold=5):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT id, name, brand, stock FROM products
                WHERE stock <= %s AND is_active = 1
                ORDER BY stock ASC
            """, (threshold,))
            return cursor.fetchall()

    @staticmethod
    def get_total_stock():
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT SUM(stock) as total FROM products WHERE is_active = 1")
            result = cursor.fetchone()
            return result['total'] if result and result['total'] else 0
