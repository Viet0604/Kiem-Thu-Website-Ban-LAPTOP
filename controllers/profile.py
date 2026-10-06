from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from helpers.utils import safe_int, login_required
from models.user import UserModel

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    user = UserModel.find_by_id(session['user_id'])
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_info':
            fullname = request.form.get('fullname')
            phone = request.form.get('phone')
            address = request.form.get('address')
            
            UserModel.update_info(user['id'], fullname, phone, address)
            session['user_fullname'] = fullname
            flash('Cập nhật thông tin thành công.', 'success')
            return redirect(url_for('profile.index'))
            
        elif action == 'change_password':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if not check_password_hash(user['password'], current_password):
                flash('Mật khẩu hiện tại không đúng.', 'danger')
            elif new_password != confirm_password:
                flash('Mật khẩu xác nhận không khớp.', 'danger')
            else:
                hashed_pw = generate_password_hash(new_password)
                UserModel.update_password(user['id'], hashed_pw)
                flash('Đổi mật khẩu thành công.', 'success')
                
            return redirect(url_for('profile.index'))
            
    return render_template('profile/index.html', page_title='Thông tin cá nhân', user=user)
