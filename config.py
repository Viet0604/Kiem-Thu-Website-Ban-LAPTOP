"""
Configuration - Cấu hình Flask & Database
"""
import os

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'laptop-store-secret-key-2024')

    # ===== CẤU HÌNH XAMPP LOCAL =====
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWORD = ''
    DB_NAME = 'laptop_store'

    # ===== CẤU HÌNH INFINITYFREE (uncomment khi deploy) =====
    # DB_HOST = 'sql123.infinityfree.com'
    # DB_USER = 'if0_12345678'
    # DB_PASSWORD = 'your_password_here'
    # DB_NAME = 'if0_12345678_laptop_store'

    # Upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images', 'laptops')
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
