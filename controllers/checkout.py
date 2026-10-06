from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from helpers.utils import safe_int, login_required
from models.user import UserModel
from models.order import OrderModel

checkout_bp = Blueprint('checkout', __name__)

@checkout_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    cart = session.get('cart', {})
    if not cart:
        flash('Giỏ hàng trống.', 'warning')
        return redirect(url_for('cart.index'))
        
    user = UserModel.find_by_id(session['user_id'])
    total = sum(int(item['price']) * int(item['quantity']) for item in cart.values())
    
    if request.method == 'POST':
        data = {
            'receiver_name': request.form.get('receiver_name'),
            'receiver_phone': request.form.get('receiver_phone'),
            'receiver_address': request.form.get('receiver_address'),
            'payment_method': request.form.get('payment_method'),
            'note': request.form.get('note'),
            'total_amount': total
        }
        
        order_id = OrderModel.create_order(session['user_id'], data, cart)
        
        if isinstance(order_id, dict) and "error" in order_id:
            flash(order_id["error"], 'danger')
        elif order_id:
            session.pop('cart', None)
            flash('Đặt hàng thành công!', 'success')
            return redirect(url_for('checkout.success', order_id=order_id))
        else:
            flash('Có lỗi xảy ra, vui lòng thử lại.', 'danger')
            
    return render_template('checkout/index.html', page_title='Thanh toán', cart_items=cart.values(), total=total, user=user)

@checkout_bp.route('/success/<int:order_id>')
@login_required
def success(order_id):
    order = OrderModel.find_by_id(order_id, session['user_id'])
    if not order:
        return redirect(url_for('products.home'))
        
    return render_template('checkout/success.html', page_title='Đặt hàng thành công', order=order)
