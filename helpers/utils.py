"""
Helper Utilities - Các hàm tiện ích dùng chung
"""
from functools import wraps
from flask import session, flash, redirect, url_for


def format_price(price):
    """Format giá tiền VNĐ"""
    if price is None:
        return "0 ₫"
    try:
        return f"{int(price):,}".replace(",", ".") + " ₫"
    except (ValueError, TypeError):
        return "0 ₫"

def safe_int(value, default=0):
    """An toàn ép kiểu số nguyên"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def order_status_label(status):
    """Trả về (text, css_class) cho trạng thái đơn hàng"""
    labels = {
        'pending': ('Chờ xử lý', 'bg-warning text-dark'),
        'processing': ('Đang xử lý', 'bg-info text-white'),
        'shipping': ('Đang giao', 'bg-primary'),
        'delivered': ('Đã giao', 'bg-success'),
        'cancelled': ('Đã hủy', 'bg-danger'),
    }
    return labels.get(status, (status, 'bg-secondary'))


def payment_method_label(method):
    """Tên phương thức thanh toán tiếng Việt"""
    labels = {
        'cod': 'Thanh toán khi nhận hàng (COD)',
        'bank_transfer': 'Chuyển khoản ngân hàng',
        'momo': 'Ví MoMo',
    }
    return labels.get(method, method)


def login_required(f):
    """Decorator: yêu cầu đăng nhập"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập để tiếp tục.', 'warning')
            return redirect(url_for('auth.login_form'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator: yêu cầu quyền admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập để tiếp tục.', 'warning')
            return redirect(url_for('auth.login_form'))
        if session.get('user_role') != 'admin':
            flash('Bạn không có quyền truy cập trang này.', 'danger')
            return redirect(url_for('products.home'))
        return f(*args, **kwargs)
    return decorated_function
