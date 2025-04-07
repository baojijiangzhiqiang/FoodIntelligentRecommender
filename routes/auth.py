from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from models import User
from app import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录处理"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        # 查询用户
        user = User.query.filter_by(username=username).first()
        
        # 检查用户是否存在及密码是否正确
        if not user or not user.check_password(password):
            flash('用户名或密码错误，请重试！', 'danger')
            return render_template('auth/login.html')
            
        # 登录用户
        login_user(user, remember=remember)
        
        # 获取用户请求的页面（如果有）
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('index')
            
        flash('登录成功！欢迎回来，' + user.username, 'success')
        return redirect(next_page)
        
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册处理"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # 验证表单数据
        if not username or not email or not password:
            flash('所有字段都必须填写', 'danger')
            return render_template('auth/register.html')
            
        if password != password_confirm:
            flash('两次密码输入不一致', 'danger')
            return render_template('auth/register.html')
            
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            flash('该用户名已被注册', 'danger')
            return render_template('auth/register.html')
            
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            flash('该邮箱已被注册', 'danger')
            return render_template('auth/register.html')
            
        # 创建新用户
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        # 将用户添加到数据库
        db.session.add(new_user)
        db.session.commit()
        
        flash('注册成功！请登录', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """用户登出处理"""
    logout_user()
    flash('您已成功登出', 'success')
    return redirect(url_for('index'))
