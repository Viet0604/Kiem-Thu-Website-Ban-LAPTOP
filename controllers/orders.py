from flask import Blueprint, render_template, session, redirect, url_for, flash
from helpers.utils import login_required
from models.order import OrderModel

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/')
@login_required
def index():
    orders = OrderModel.get_by_user(session['user_id'])
    return render_template('orders/index.html', page_title='Lịch sử đơn hàng', orders=orders)

@orders_bp.route('/detail/<int:order_id>')
@login_required
def detail(order_id):
    order = OrderModel.find_by_id(order_id, session['user_id'])
    if not order:
        flash('Đơn hàng không tồn tại.', 'danger')
        return redirect(url_for('orders.index'))
        
    order_details = OrderModel.get_order_details(order_id)
    return render_template('orders/detail.html', page_title=f'Đơn hàng #{order_id}', order=order, order_details=order_details)
