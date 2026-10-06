from models.db import get_db

class ProductModel:
    @staticmethod
    def get_all(filters=None):
        db = get_db()
        query = "SELECT * FROM products WHERE is_active = 1"
        params = []
        
        if filters:
            if filters.get('keyword'):
                query += " AND name LIKE %s"
                params.append(f"%{filters['keyword']}%")
            if filters.get('brand'):
                query += " AND brand = %s"
                params.append(filters['brand'])
            if filters.get('cpu'):
                query += " AND cpu LIKE %s"
                params.append(f"%{filters['cpu']}%")
            if filters.get('ram'):
                query += " AND ram LIKE %s"
                params.append(f"%{filters['ram']}%")
            if filters.get('price_min'):
                try:
                    price_min = int(filters['price_min'])
                    if price_min >= 0:
                        query += " AND price >= %s"
                        params.append(price_min)
                except ValueError:
                    pass
            if filters.get('price_max'):
                try:
                    price_max = int(filters['price_max'])
                    if price_max >= 0:
                        query += " AND price <= %s"
                        params.append(price_max)
                except ValueError:
                    pass
                
            sort = filters.get('sort', 'newest')
            if sort == 'price_asc':
                query += " ORDER BY price ASC"
            elif sort == 'price_desc':
                query += " ORDER BY price DESC"
            elif sort == 'name_asc':
                query += " ORDER BY name ASC"
            else:
                query += " ORDER BY created_at DESC"
        else:
            query += " ORDER BY created_at DESC"
            
        with db.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    @staticmethod
    def get_all_admin():
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM products ORDER BY id DESC")
            return cursor.fetchall()

    @staticmethod
    def get_latest(limit=8):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM products WHERE is_active = 1 AND stock > 0 ORDER BY created_at DESC LIMIT %s", (limit,))
            return cursor.fetchall()

    @staticmethod
    def find_by_id(product_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
            return cursor.fetchone()
            
    @staticmethod
    def get_related(brand, exclude_id, limit=4):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM products WHERE brand = %s AND id != %s AND is_active = 1 LIMIT %s", 
                (brand, exclude_id, limit)
            )
            return cursor.fetchall()

    @staticmethod
    def get_all_brands():
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT DISTINCT brand FROM products WHERE is_active = 1")
            return [row['brand'] for row in cursor.fetchall()]

    @staticmethod
    def create(data):
        db = get_db()
        with db.cursor() as cursor:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            query = f"INSERT INTO products ({columns}) VALUES ({placeholders})"
            cursor.execute(query, list(data.values()))
            db.commit()
            return cursor.lastrowid

    @staticmethod
    def update(product_id, data):
        db = get_db()
        with db.cursor() as cursor:
            set_clause = ', '.join([f"{k}=%s" for k in data.keys()])
            query = f"UPDATE products SET {set_clause} WHERE id=%s"
            values = list(data.values())
            values.append(product_id)
            cursor.execute(query, values)
            db.commit()

    @staticmethod
    def delete(product_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
            db.commit()

    @staticmethod
    def toggle_active(product_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("UPDATE products SET is_active = NOT is_active WHERE id = %s", (product_id,))
            db.commit()

    @staticmethod
    def count_all():
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as total FROM products")
            result = cursor.fetchone()
            return result['total'] if result else 0

    @staticmethod
    def get_top_selling(limit=5):
        db = get_db()
        with db.cursor() as cursor:
            query = """
                SELECT p.id, p.name, SUM(od.quantity) as total_sold
                FROM products p
                JOIN order_details od ON p.id = od.product_id
                JOIN orders o ON od.order_id = o.id
                WHERE o.status != 'cancelled'
                GROUP BY p.id, p.name
                ORDER BY total_sold DESC
                LIMIT %s
            """
            cursor.execute(query, (limit,))
            return cursor.fetchall()
