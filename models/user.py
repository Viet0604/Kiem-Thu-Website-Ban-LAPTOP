from models.db import get_db

class UserModel:
    @staticmethod
    def find_by_email(email):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s LIMIT 1", (email,))
            return cursor.fetchone()

    @staticmethod
    def find_by_id(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s LIMIT 1", (user_id,))
            return cursor.fetchone()

    @staticmethod
    def create(fullname, email, phone, password, role='user'):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (fullname, email, phone, password, role) VALUES (%s, %s, %s, %s, %s)",
                (fullname, email, phone, password, role)
            )
            db.commit()
            return cursor.lastrowid

    @staticmethod
    def update_info(user_id, fullname, phone, address):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET fullname=%s, phone=%s, address=%s WHERE id=%s",
                (fullname, phone, address, user_id)
            )
            db.commit()

    @staticmethod
    def update_password(user_id, password_hash):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("UPDATE users SET password=%s WHERE id=%s", (password_hash, user_id))
            db.commit()

    @staticmethod
    def get_all():
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
            return cursor.fetchall()

    @staticmethod
    def toggle_lock(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("UPDATE users SET is_locked = NOT is_locked WHERE id = %s", (user_id,))
            db.commit()

    @staticmethod
    def count_all():
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as total FROM users WHERE role = 'user'")
            result = cursor.fetchone()
            return result['total'] if result else 0
