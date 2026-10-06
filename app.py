"""
LaptopStore - Website Bán Laptop
Flask Application Entry Point
"""
from flask import Flask, session, g
from config import Config
from models.db import close_db
from helpers.utils import format_price, order_status_label, payment_method_label

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Đóng DB connection sau mỗi request
    app.teardown_appcontext(close_db)

    # ===== Template Filters =====
    @app.template_filter('format_price')
    def format_price_filter(value):
        return format_price(value)

    @app.template_filter('order_status')
    def order_status_filter(status):
        return order_status_label(status)

    @app.template_filter('payment_label')
    def payment_label_filter(method):
        return payment_method_label(method)

    # ===== Context Processor - Biến dùng chung cho tất cả template =====
    @app.context_processor
    def inject_globals():
        cart = session.get('cart', {})
        cart_count = sum(int(item.get('quantity', 0)) for item in cart.values()) if cart else 0
        return {
            'is_logged_in': 'user_id' in session,
            'is_admin': session.get('user_role') == 'admin',
            'current_user': {
                'id': session.get('user_id'),
                'fullname': session.get('user_fullname', ''),
                'email': session.get('user_email', ''),
                'role': session.get('user_role', ''),
            } if 'user_id' in session else None,
            'cart_count': cart_count,
        }

    # ===== Đăng ký Blueprints =====
    from controllers.auth import auth_bp
    from controllers.products import products_bp
    from controllers.cart import cart_bp
    from controllers.checkout import checkout_bp
    from controllers.orders import orders_bp
    from controllers.profile import profile_bp
    from controllers.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(cart_bp, url_prefix='/cart')
    app.register_blueprint(checkout_bp, url_prefix='/checkout')
    app.register_blueprint(orders_bp, url_prefix='/orders')
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # ===== Error Handlers =====
    @app.errorhandler(404)
    def page_not_found(e):
        from flask import render_template_string
        return render_template_string('''
        {% extends "layouts/base.html" %}
        {% block content %}
        <div class="container py-5 text-center">
            <h1 class="display-1 text-muted">404</h1>
            <p class="lead">Trang bạn tìm không tồn tại.</p>
            <a href="/" class="btn btn-primary">Về trang chủ</a>
        </div>
        {% endblock %}
        '''), 404

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
