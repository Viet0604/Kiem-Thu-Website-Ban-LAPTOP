from models.db import get_db


class SupplierModel:
    @staticmethod
    def get_all(active_only=False):
        db = get_db()
        with db.cursor() as cursor:
            query = "SELECT * FROM suppliers"
            if active_only:
                query += " WHERE is_active = 1"
            query += " ORDER BY name ASC"
            cursor.execute(query)
            return cursor.fetchall()

    @staticmethod
    def find_by_id(supplier_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM suppliers WHERE id = %s", (supplier_id,))
            return cursor.fetchone()

    @staticmethod
    def create(data):
        db = get_db()
        with db.cursor() as cursor:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            query = f"INSERT INTO suppliers ({columns}) VALUES ({placeholders})"
            cursor.execute(query, list(data.values()))
            db.commit()
            return cursor.lastrowid

    @staticmethod
    def update(supplier_id, data):
        db = get_db()
        with db.cursor() as cursor:
            set_clause = ', '.join([f"{k}=%s" for k in data.keys()])
            query = f"UPDATE suppliers SET {set_clause} WHERE id=%s"
            values = list(data.values())
            values.append(supplier_id)
            cursor.execute(query, values)
            db.commit()

    @staticmethod
    def delete(supplier_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM suppliers WHERE id = %s", (supplier_id,))
            db.commit()

    @staticmethod
    def toggle_active(supplier_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("UPDATE suppliers SET is_active = NOT is_active WHERE id = %s", (supplier_id,))
            db.commit()

    @staticmethod
    def count_all():
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as total FROM suppliers WHERE is_active = 1")
            result = cursor.fetchone()
            return result['total'] if result else 0
