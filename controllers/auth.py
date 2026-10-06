from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import UserModel

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login_form():
    if 'user_id' in session:
        return redirect(url_for('products.home'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Vui lòng nhập email và mật khẩu.', 'danger')
            return redirect(url_for('auth.login_form'))
        
        user = UserModel.find_by_email(email)
        
        if user and check_password_hash(user['password'], password):
            if user['is_locked']:
                flash('Tài khoản của bạn đã bị khóa. Vui lòng liên hệ quản trị viên.', 'danger')
                return redirect(url_for('auth.login_form'))
                
            session['user_id'] = user['id']
            session['user_fullname'] = user['fullname']
            session['user_email'] = user['email']
            session['user_role'] = user['role']
            
            flash('Đăng nhập thành công!', 'success')
            
            if user['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('products.home'))
            
        flash('Email hoặc mật khẩu không chính xác.', 'danger')
        
    return render_template('auth/login.html', page_title='Đăng nhập')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('products.home'))
        
    if request.method == 'POST':
        fullname = request.form.get('fullname', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        import re
        if not fullname or not email or not password:
            flash('Vui lòng điền đầy đủ các trường bắt buộc.', 'danger')
            return redirect(url_for('auth.register'))
            
        if len(password) < 6:
            flash('Mật khẩu phải có ít nhất 6 ký tự.', 'danger')
            return redirect(url_for('auth.register'))
            
        if password != password_confirm:
            flash('Mật khẩu xác nhận không khớp.', 'danger')
            return redirect(url_for('auth.register'))
            
        # Kiểm tra định dạng email
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            flash('Email sai định dạng.', 'danger')
            return redirect(url_for('auth.register'))
            
        # Kiểm tra định dạng số điện thoại (tùy chọn nhưng nếu có phải hợp lệ, ví dụ 10 số)
        if phone:
            phone_regex = r'^(0|\+84)[35789][0-9]{8}$'
            if not re.match(phone_regex, phone):
                flash('Số điện thoại sai định dạng.', 'danger')
                return redirect(url_for('auth.register'))
            
        if UserModel.find_by_email(email):
            flash('Email này đã được sử dụng.', 'danger')
            return redirect(url_for('auth.register'))
            
        hashed_password = generate_password_hash(password)
        UserModel.create(fullname, email, phone, hashed_password)
        
        flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('auth.login_form'))
        
    return render_template('auth/register.html', page_title='Đăng ký')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Bạn đã đăng xuất.', 'info')
    return redirect(url_for('auth.login_form'))
