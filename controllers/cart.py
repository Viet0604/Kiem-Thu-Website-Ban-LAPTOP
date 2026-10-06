from helpers.utils import safe_int
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.product import ProductModel

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/')
def index():
    cart = session.get('cart', {})
    total = sum(int(item['price']) * int(item['quantity']) for item in cart.values())
    return render_template('cart/index.html', page_title='Giỏ hàng', cart_items=cart.values(), total=total)

@cart_bp.route('/add', methods=['POST'])
def add():
    product_id = request.form.get('product_id')
    quantity = safe_int(request.form.get('quantity', 1))
    
    if quantity <= 0:
        flash('Số lượng phải lớn hơn 0.', 'warning')
        return redirect(request.referrer or url_for('products.home'))
        
    product = ProductModel.find_by_id(product_id)
    if not product or not product['is_active']:
        flash('Sản phẩm không tồn tại.', 'danger')
        return redirect(request.referrer or url_for('products.home'))
        
    if product['stock'] < quantity:
        flash('Số lượng tồn kho không đủ.', 'warning')
        return redirect(request.referrer or url_for('products.home'))
        
    cart = session.get('cart', {})
    pid = str(product_id)
    
    if pid in cart:
        if cart[pid]['quantity'] + quantity > product['stock']:
            flash('Số lượng vượt quá tồn kho.', 'warning')
        else:
            cart[pid]['quantity'] += quantity
            flash('Đã cập nhật giỏ hàng.', 'success')
    else:
        cart[pid] = {
            'id': product['id'],
            'name': product['name'],
            'price': int(product['price']),
            'image': product['image'],
            'quantity': quantity
        }
        flash('Đã thêm vào giỏ hàng.', 'success')
        
    session['cart'] = cart
    session.modified = True
    return redirect(request.referrer or url_for('cart.index'))

@cart_bp.route('/update', methods=['POST'])
def update():
    product_id = str(request.form.get('product_id'))
    quantity = safe_int(request.form.get('quantity', 1))
    
    cart = session.get('cart', {})
    if product_id in cart:
        product = ProductModel.find_by_id(product_id)
        if not product:
            del cart[product_id]
            flash('Sản phẩm không còn tồn tại.', 'danger')
        elif quantity > 0 and quantity <= product['stock']:
            cart[product_id]['quantity'] = quantity
        elif quantity == 0:
            del cart[product_id]
        else:
            flash('Số lượng không hợp lệ.', 'warning')
            
    session['cart'] = cart
    session.modified = True
    return redirect(url_for('cart.index'))

@cart_bp.route('/remove/<product_id>')
def remove(product_id):
    cart = session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        session['cart'] = cart
        session.modified = True
        flash('Đã xóa sản phẩm khỏi giỏ hàng.', 'success')
    return redirect(url_for('cart.index'))
