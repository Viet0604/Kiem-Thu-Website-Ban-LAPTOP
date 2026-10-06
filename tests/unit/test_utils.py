from flask import session

from helpers.utils import (
    admin_required,
    format_price,
    login_required,
    order_status_label,
    payment_method_label,
    safe_int,
)


def test_format_price_formats_integer_with_vietnamese_separators():
    assert format_price(1234567) == '1.234.567 ₫'


def test_format_price_accepts_numeric_string():
    assert format_price('25000000') == '25.000.000 ₫'


def test_format_price_returns_zero_for_none():
    assert format_price(None) == '0 ₫'


def test_format_price_returns_zero_for_invalid_value():
    assert format_price('not-a-number') == '0 ₫'


def test_format_price_formats_negative_value():
    assert format_price(-1000) == '-1.000 ₫'


def test_safe_int_returns_integer_for_valid_input():
    assert safe_int('42') == 42


def test_safe_int_returns_default_for_invalid_input():
    assert safe_int('abc', default=7) == 7


def test_safe_int_returns_default_for_none():
    assert safe_int(None) == 0


def test_order_status_label_returns_text_and_css_class():
    assert order_status_label('delivered') == ('Đã giao', 'bg-success')


def test_order_status_label_uses_fallback_for_unknown_status():
    assert order_status_label('unknown') == ('unknown', 'bg-secondary')


def test_payment_method_label_returns_localized_text():
    assert payment_method_label('cod') == 'Thanh toán khi nhận hàng (COD)'


def test_payment_method_label_returns_unknown_value_unchanged():
    assert payment_method_label('cash') == 'cash'


def test_login_required_redirects_anonymous_user(app):
    @login_required
    def protected():
        return 'protected'

    with app.test_request_context('/private'):
        response = protected()

    assert response.status_code == 302
    assert response.location.endswith('/login')


def test_login_required_calls_wrapped_function_for_authenticated_user(app):
    @login_required
    def protected():
        return 'protected'

    with app.test_request_context('/private'):
        session['user_id'] = 2
        assert protected() == 'protected'


def test_admin_required_redirects_anonymous_user(app):
    @admin_required
    def protected():
        return 'admin'

    with app.test_request_context('/admin/private'):
        response = protected()

    assert response.status_code == 302
    assert response.location.endswith('/login')


def test_admin_required_redirects_regular_user(app):
    @admin_required
    def protected():
        return 'admin'

    with app.test_request_context('/admin/private'):
        session['user_id'] = 2
        session['user_role'] = 'user'
        response = protected()

    assert response.status_code == 302
    assert response.location.endswith('/')


def test_admin_required_calls_wrapped_function_for_admin(app):
    @admin_required
    def protected():
        return 'admin'

    with app.test_request_context('/admin/private'):
        session['user_id'] = 1
        session['user_role'] = 'admin'
        assert protected() == 'admin'
