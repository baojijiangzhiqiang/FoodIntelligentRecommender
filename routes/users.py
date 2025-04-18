from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import Recipe, User, Post, Category, RecipeRating, UserFavorite
from app import db
import json
from werkzeug.security import check_password_hash, generate_password_hash
from services import user_service

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/profile')
@login_required
def profile():
    """用户个人资料页面"""
    # 获取用户收藏的菜谱
    favorite_recipes = user_service.get_user_favorite_recipes(current_user.id)
    
    # 获取用户评分的菜谱
    rated_recipes = user_service.get_user_rated_recipes(current_user.id)
    
    # 获取用户的社区帖子
    user_posts = Post.query.filter_by(user_id=current_user.id).all()
    
    # 获取个性化推荐
    from services.recommendation_service import get_personalized_recommendations
    recommended_recipes = get_personalized_recommendations(current_user.id)
    
    return render_template('user/profile.html',
                          user=current_user,
                          favorite_recipes=favorite_recipes,
                          rated_recipes=rated_recipes,
                          user_posts=user_posts,
                          recommended_recipes=recommended_recipes)

@users_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """编辑用户个人资料"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        preferences = request.form.getlist('preferences')
        
        # 验证用户名、邮箱
        if not username or not email:
            flash('用户名和邮箱不能为空', 'danger')
            return redirect(url_for('users.edit_profile'))
        
        # 检查用户名是否已被其他用户使用
        user_with_same_name = User.query.filter_by(username=username).first()
        if user_with_same_name and user_with_same_name.id != current_user.id:
            flash('该用户名已被使用', 'danger')
            return redirect(url_for('users.edit_profile'))
        
        # 检查邮箱是否已被其他用户使用
        user_with_same_email = User.query.filter_by(email=email).first()
        if user_with_same_email and user_with_same_email.id != current_user.id:
            flash('该邮箱已被使用', 'danger')
            return redirect(url_for('users.edit_profile'))
        
        # 更新用户信息
        current_user.username = username
        current_user.email = email
        
        # 将偏好转换为JSON字符串
        current_user.preferences = json.dumps(preferences)
        
        # 保存更改
        db.session.commit()
        
        flash('个人资料已更新', 'success')
        return redirect(url_for('users.profile'))
    
    # 获取所有菜谱分类作为口味偏好选项
    categories = Category.query.all()
    
    # 解析当前用户偏好
    user_preferences = []
    if current_user.preferences:
        try:
            user_preferences = json.loads(current_user.preferences)
        except json.JSONDecodeError:
            user_preferences = []
    
    return render_template('user/profile_edit.html', 
                          user=current_user,
                          categories=categories,
                          user_preferences=user_preferences)

@users_bp.route('/favorites')
@login_required
def favorites():
    """用户收藏的菜谱"""
    # 获取用户收藏的菜谱
    favorite_recipes = user_service.get_user_favorite_recipes(current_user.id)
    
    return render_template('user/favorites.html',
                          favorite_recipes=favorite_recipes)

@users_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """修改密码"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # 验证当前密码
        if not check_password_hash(current_user.password_hash, current_password):
            flash('当前密码不正确', 'danger')
            return redirect(url_for('users.change_password'))
        
        # 验证新密码
        if not new_password or len(new_password) < 6:
            flash('新密码长度不能小于6个字符', 'danger')
            return redirect(url_for('users.change_password'))
        
        # 验证确认密码
        if new_password != confirm_password:
            flash('两次密码输入不一致', 'danger')
            return redirect(url_for('users.change_password'))
        
        # 更新密码
        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        flash('密码已更新', 'success')
        return redirect(url_for('users.profile'))
    
    return render_template('user/change_password.html')
