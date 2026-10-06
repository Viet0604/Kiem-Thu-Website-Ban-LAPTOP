import os
import time
import random
import csv
from io import StringIO
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, current_app, Response
from helpers.utils import safe_int, admin_required
from models.user import UserModel
from models.product import ProductModel
from models.order import OrderModel
from models.supplier import SupplierModel
from models.inventory import InventoryModel

admin_bp = Blueprint('admin', __name__)

# =============================================
#               DASHBOARD
# =============================================
@admin_bp.route('/')
@admin_required
def dashboard():
    stats = {
        'total_orders': OrderModel.count_all(),
        'pending_orders': OrderModel.count_by_status('pending'),
        'total_revenue': OrderModel.get_total_revenue(),
        'total_products': ProductModel.count_all(),
        'total_users': UserModel.count_all(),
        'total_stock': InventoryModel.get_total_stock(),
    }
    
    revenue_by_month = OrderModel.get_revenue_by_month(12)
    top_products = ProductModel.get_top_selling(5)
    recent_orders = OrderModel.get_all()[:5]
    low_stock = InventoryModel.get_low_stock(5)
    
    return render_template(
        'admin/dashboard.html', 
        page_title='Dashboard', 
        stats=stats, 
        revenue_by_month=revenue_by_month,
        top_products=top_products,
        recent_orders=recent_orders,
        low_stock=low_stock
    )

# =============================================
#               PRODUCTS
# =============================================
@admin_bp.route('/products')
@admin_required
def products():
    products = ProductModel.get_all_admin()
    return render_template('admin/products/index.html', page_title='Quản lý sản phẩm', products=products)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def handle_image_upload(file):
    if file and file.filename != '' and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"laptop_{int(time.time())}_{random.randint(1000, 9999)}.{ext}"
        upload_dir = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        file.save(os.path.join(upload_dir, filename))
        return filename
    return None

@admin_bp.route('/products/create', methods=['GET', 'POST'])
@admin_required
def create_product():
    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'brand': request.form.get('brand'),
            'cpu': request.form.get('cpu'),
            'ram': request.form.get('ram'),
            'storage': request.form.get('storage'),
            'screen_size': request.form.get('screen_size'),
            'gpu': request.form.get('gpu'),
            'price': safe_int(request.form.get('price', 0)),
            'stock': safe_int(request.form.get('stock', 0)),
            'description': request.form.get('description')
        }
        
        file = request.files.get('image')
        image_name = handle_image_upload(file)
        if image_name:
            data['image'] = image_name
            
        ProductModel.create(data)
        flash('Thêm sản phẩm thành công!', 'success')
        return redirect(url_for('admin.products'))
        
    return render_template('admin/products/create.html', page_title='Thêm sản phẩm')

@admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    product = ProductModel.find_by_id(product_id)
    if not product:
        flash('Sản phẩm không tồn tại.', 'danger')
        return redirect(url_for('admin.products'))
        
    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'brand': request.form.get('brand'),
            'cpu': request.form.get('cpu'),
            'ram': request.form.get('ram'),
            'storage': request.form.get('storage'),
            'screen_size': request.form.get('screen_size'),
            'gpu': request.form.get('gpu'),
            'price': safe_int(request.form.get('price', 0)),
            'stock': safe_int(request.form.get('stock', 0)),
            'description': request.form.get('description')
        }
        
        file = request.files.get('image')
        image_name = handle_image_upload(file)
        if image_name:
            data['image'] = image_name
            
        ProductModel.update(product_id, data)
        flash('Cập nhật sản phẩm thành công!', 'success')
        return redirect(url_for('admin.products'))
        
    return render_template('admin/products/edit.html', page_title='Sửa sản phẩm', product=product)

@admin_bp.route('/products/toggle/<int:product_id>', methods=['POST'])
@admin_required
def toggle_product(product_id):
    ProductModel.toggle_active(product_id)
    flash('Cập nhật trạng thái thành công.', 'success')
    return redirect(url_for('admin.products'))

@admin_bp.route('/products/delete/<int:product_id>', methods=['POST'])
@admin_required
def delete_product(product_id):
    ProductModel.delete(product_id)
    flash('Đã xóa sản phẩm.', 'success')
    return redirect(url_for('admin.products'))

# =============================================
#               ORDERS
# =============================================
@admin_bp.route('/orders')
@admin_required
def orders():
    status_filter = request.args.get('status')
    orders = OrderModel.get_all(status_filter)
    return render_template('admin/orders/index.html', page_title='Quản lý đơn hàng', orders=orders)

@admin_bp.route('/orders/detail/<int:order_id>')
@admin_required
def order_detail(order_id):
    order = OrderModel.find_by_id(order_id)
    if not order:
        flash('Đơn hàng không tồn tại.', 'danger')
        return redirect(url_for('admin.orders'))
        
    order_details = OrderModel.get_order_details(order_id)
    return render_template('admin/orders/detail.html', page_title=f'Đơn hàng #{order_id}', order=order, order_details=order_details)

@admin_bp.route('/orders/update-status', methods=['POST'])
@admin_required
def update_order_status():
    order_id = request.form.get('order_id')
    status = request.form.get('status')
    success, msg = OrderModel.update_status(order_id, status)
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'danger')
    return redirect(url_for('admin.order_detail', order_id=order_id))

@admin_bp.route('/orders/export')
@admin_required
def export_orders():
    orders = OrderModel.get_all()
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Mã ĐH', 'Khách hàng', 'SĐT', 'Địa chỉ', 'Tổng tiền', 'Phương thức', 'Trạng thái', 'Ngày đặt'])
    for o in orders:
        # Lấy tên khách hoặc tên người nhận
        customer_name = o.get('user_fullname') or o.get('receiver_name', '')
        cw.writerow([
            f"#{o.get('id', '')}", 
            customer_name, 
            o.get('receiver_phone', ''), 
            o.get('receiver_address', ''), 
            o.get('total_amount', 0), 
            o.get('payment_method', ''), 
            o.get('status', ''), 
            o.get('created_at', '')
        ])
    output = '\ufeff' + si.getvalue() # BOM cho Excel UTF-8
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=orders_export.csv"}
    )

# =============================================
#               USERS
# =============================================
@admin_bp.route('/users')
@admin_required
def users():
    users = UserModel.get_all()
    return render_template('admin/users/index.html', page_title='Quản lý người dùng', users=users)

@admin_bp.route('/users/toggle-lock/<int:user_id>', methods=['POST'])
@admin_required
def toggle_user_lock(user_id):
    if user_id == session.get('user_id'):
        flash('Không thể khóa tài khoản của chính mình.', 'warning')
    else:
        UserModel.toggle_lock(user_id)
        flash('Cập nhật trạng thái tài khoản thành công.', 'success')
    return redirect(url_for('admin.users'))

# =============================================
#               SUPPLIERS
# =============================================
@admin_bp.route('/suppliers')
@admin_required
def suppliers():
    suppliers = SupplierModel.get_all()
    return render_template('admin/suppliers/index.html', page_title='Nhà cung cấp', suppliers=suppliers)

@admin_bp.route('/suppliers/create', methods=['GET', 'POST'])
@admin_required
def create_supplier():
    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'contact_person': request.form.get('contact_person'),
            'phone': request.form.get('phone'),
            'email': request.form.get('email'),
            'address': request.form.get('address'),
        }
        SupplierModel.create(data)
        flash('Thêm nhà cung cấp thành công!', 'success')
        return redirect(url_for('admin.suppliers'))
        
    return render_template('admin/suppliers/create.html', page_title='Thêm nhà cung cấp')

@admin_bp.route('/suppliers/edit/<int:supplier_id>', methods=['GET', 'POST'])
@admin_required
def edit_supplier(supplier_id):
    supplier = SupplierModel.find_by_id(supplier_id)
    if not supplier:
        flash('Nhà cung cấp không tồn tại.', 'danger')
        return redirect(url_for('admin.suppliers'))
        
    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'contact_person': request.form.get('contact_person'),
            'phone': request.form.get('phone'),
            'email': request.form.get('email'),
            'address': request.form.get('address'),
        }
        SupplierModel.update(supplier_id, data)
        flash('Cập nhật nhà cung cấp thành công!', 'success')
        return redirect(url_for('admin.suppliers'))
        
    return render_template('admin/suppliers/edit.html', page_title='Sửa nhà cung cấp', supplier=supplier)

@admin_bp.route('/suppliers/toggle/<int:supplier_id>', methods=['POST'])
@admin_required
def toggle_supplier(supplier_id):
    SupplierModel.toggle_active(supplier_id)
    flash('Cập nhật trạng thái thành công.', 'success')
    return redirect(url_for('admin.suppliers'))

# =============================================
#               INVENTORY
# =============================================
@admin_bp.route('/inventory')
@admin_required
def inventory():
    stock_summary = InventoryModel.get_stock_summary()
    low_stock_products = InventoryModel.get_low_stock(5)
    total_stock = InventoryModel.get_total_stock()
    supplier_count = SupplierModel.count_all()
    
    return render_template(
        'admin/inventory/index.html', 
        page_title='Quản lý kho',
        stock_summary=stock_summary,
        low_stock_products=low_stock_products,
        total_stock=total_stock,
        supplier_count=supplier_count
    )

@admin_bp.route('/inventory/import', methods=['GET', 'POST'])
@admin_required
def import_stock():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        supplier_id = request.form.get('supplier_id') or None
        quantity = safe_int(request.form.get('quantity', 0))
        note = request.form.get('note', '')
        
        if quantity > 0:
            success = InventoryModel.import_stock(
                product_id, supplier_id, quantity, note, session['user_id']
            )
            if success:
                flash(f'Nhập kho thành công: +{quantity} sản phẩm.', 'success')
            else:
                flash('Có lỗi xảy ra khi nhập kho.', 'danger')
        else:
            flash('Số lượng phải lớn hơn 0.', 'warning')
            
        return redirect(url_for('admin.inventory'))
        
    products = ProductModel.get_all_admin()
    suppliers = SupplierModel.get_all(active_only=True)
    return render_template('admin/inventory/import.html', page_title='Nhập kho', products=products, suppliers=suppliers)

@admin_bp.route('/inventory/logs')
@admin_required
def inventory_logs():
    logs = InventoryModel.get_logs(limit=100)
    return render_template('admin/inventory/logs.html', page_title='Lịch sử kho', logs=logs)
