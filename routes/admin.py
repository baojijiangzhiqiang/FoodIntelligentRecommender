from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import Recipe, User, Category, Post, Comment, UserFavorite, RecipeRating
from app import db
import json

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# 管理员权限检查
def admin_required(func):
    """检查用户是否为管理员的装饰器"""
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('您没有管理员权限', 'danger')
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """管理员仪表盘"""
    # 获取统计数据
    users_count = User.query.count()
    recipes_count = Recipe.query.count()
    posts_count = Post.query.count()
    
    # 获取热门菜谱
    popular_recipes = Recipe.query.order_by(Recipe.views.desc()).limit(5).all()
    
    # 获取最新用户
    latest_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    # 获取最新帖子及其作者
    latest_posts_with_user = []
    latest_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    
    for post in latest_posts:
        latest_posts_with_user.append({
            'post': post,
            'user': post.author
        })
    
    return render_template('admin/dashboard.html',
                          users_count=users_count,
                          recipes_count=recipes_count,
                          posts_count=posts_count,
                          popular_recipes=popular_recipes,
                          latest_users=latest_users,
                          latest_posts=latest_posts_with_user)

@admin_bp.route('/recipes')
@login_required
@admin_required
def manage_recipes():
    """管理菜谱"""
    recipes = Recipe.query.all()
    
    # 为每个菜谱获取分类
    recipes_with_category = []
    for recipe in recipes:
        recipes_with_category.append({
            'recipe': recipe,
            'category': recipe.category
        })
    
    categories = Category.query.all()
    return render_template('admin/recipes.html',
                          recipes=recipes_with_category,
                          categories=categories)

@admin_bp.route('/recipes/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_recipe():
    """添加新菜谱"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        ingredients_text = request.form.get('ingredients')
        steps_text = request.form.get('steps')
        category_id = int(request.form.get('category'))
        image_url = request.form.get('image_url')
        difficulty = request.form.get('difficulty')
        prep_time = int(request.form.get('prep_time'))
        cook_time = int(request.form.get('cook_time'))
        
        # 验证表单
        if not name or not description or not ingredients_text or not steps_text or not category_id:
            flash('所有必填字段都不能为空', 'danger')
            categories = Category.query.all()
            return render_template('admin/recipe_form.html', categories=categories)
        
        # 处理材料和步骤文本
        ingredients_list = [line.strip() for line in ingredients_text.split('\n') if line.strip()]
        steps_list = [line.strip() for line in steps_text.split('\n') if line.strip()]
        
        # 创建新菜谱
        new_recipe = Recipe(
            name=name,
            description=description,
            ingredients=json.dumps(ingredients_list),
            steps=json.dumps(steps_list),
            category_id=category_id,
            image_url=image_url,
            difficulty=difficulty,
            prep_time=prep_time,
            cook_time=cook_time
        )
        
        # 添加到数据库
        db.session.add(new_recipe)
        db.session.commit()
        
        flash('菜谱添加成功', 'success')
        return redirect(url_for('admin.manage_recipes'))
    
    categories = Category.query.all()
    return render_template('admin/recipe_form.html', categories=categories)

@admin_bp.route('/recipes/edit/<int:recipe_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_recipe(recipe_id):
    """编辑菜谱"""
    recipe = Recipe.query.get(recipe_id)
    
    if not recipe:
        flash('菜谱不存在', 'danger')
        return redirect(url_for('admin.manage_recipes'))
    
    if request.method == 'POST':
        recipe.name = request.form.get('name')
        recipe.description = request.form.get('description')
        
        # 处理材料和步骤文本，确保只保留非空行并去除前后空白
        ingredients_text = request.form.get('ingredients')
        steps_text = request.form.get('steps')
        ingredients_list = [line.strip() for line in ingredients_text.split('\n') if line.strip()]
        steps_list = [line.strip() for line in steps_text.split('\n') if line.strip()]
        recipe.ingredients = json.dumps(ingredients_list)
        recipe.steps = json.dumps(steps_list)
        
        recipe.category_id = int(request.form.get('category'))
        recipe.image_url = request.form.get('image_url')
        recipe.difficulty = request.form.get('difficulty')
        recipe.prep_time = int(request.form.get('prep_time'))
        recipe.cook_time = int(request.form.get('cook_time'))
        
        # 保存更改
        db.session.commit()
        
        flash('菜谱更新成功', 'success')
        return redirect(url_for('admin.manage_recipes'))
    
    categories = Category.query.all()
    
    # 获取当前的配料和步骤，从JSON转为多行文本
    try:
        ingredients_list = json.loads(recipe.ingredients)
        steps_list = json.loads(recipe.steps)
        ingredients_text = '\n'.join(ingredients_list)
        steps_text = '\n'.join(steps_list)
    except json.JSONDecodeError:
        ingredients_text = recipe.ingredients
        steps_text = recipe.steps
    
    return render_template('admin/recipe_form.html', 
                          recipe=recipe, 
                          categories=categories,
                          ingredients=ingredients_text,
                          steps=steps_text)

@admin_bp.route('/recipes/delete/<int:recipe_id>', methods=['POST'])
@login_required
@admin_required
def delete_recipe(recipe_id):
    """删除菜谱"""
    recipe = Recipe.query.get(recipe_id)
    
    if not recipe:
        flash('菜谱不存在', 'danger')
        return redirect(url_for('admin.manage_recipes'))
    
    # 从数据库中删除
    db.session.delete(recipe)
    db.session.commit()
    
    flash('菜谱已删除', 'success')
    return redirect(url_for('admin.manage_recipes'))

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """管理用户"""
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/toggle_admin/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    """切换用户的管理员状态"""
    user = User.query.get(user_id)
    
    if not user:
        flash('用户不存在', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    # 不允许撤销自己的管理员权限
    if user.id == current_user.id:
        flash('不能更改自己的管理员状态', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    flash(f'用户 {user.username} 的管理员状态已更改', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """删除用户"""
    user = User.query.get(user_id)
    
    if not user:
        flash('用户不存在', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    # 不允许删除自己
    if user.id == current_user.id:
        flash('不能删除自己的账户', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    # 首先清除用户收藏记录和评分记录（避免外键约束问题）
    UserFavorite.query.filter_by(user_id=user.id).delete()
    RecipeRating.query.filter_by(user_id=user.id).delete()
    
    # 从数据库中删除用户
    db.session.delete(user)
    db.session.commit()
    
    flash(f'用户 {user.username} 已删除', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/categories')
@login_required
@admin_required
def manage_categories():
    """管理分类"""
    categories = Category.query.all()
    
    # 为每个分类获取关联的菜谱数量
    categories_with_count = []
    for category in categories:
        recipe_count = Recipe.query.filter_by(category_id=category.id).count()
        categories_with_count.append({
            'category': category,
            'recipe_count': recipe_count
        })
    
    return render_template('admin/categories.html', categories=categories_with_count)

@admin_bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_category():
    """添加新分类"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('分类名称不能为空', 'danger')
            return redirect(url_for('admin.add_category'))
        
        # 创建新分类
        new_category = Category(
            name=name,
            description=description
        )
        
        # 添加到数据库
        db.session.add(new_category)
        db.session.commit()
        
        flash('分类添加成功', 'success')
        return redirect(url_for('admin.manage_categories'))
    
    return render_template('admin/category_form.html')

@admin_bp.route('/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(category_id):
    """编辑分类"""
    category = Category.query.get(category_id)
    
    if not category:
        flash('分类不存在', 'danger')
        return redirect(url_for('admin.manage_categories'))
    
    if request.method == 'POST':
        category.name = request.form.get('name')
        category.description = request.form.get('description')
        
        # 保存更改
        db.session.commit()
        
        flash('分类更新成功', 'success')
        return redirect(url_for('admin.manage_categories'))
    
    return render_template('admin/category_form.html', category=category)

@admin_bp.route('/categories/delete/<int:category_id>', methods=['POST'])
@login_required
@admin_required
def delete_category(category_id):
    """删除分类"""
    category = Category.query.get(category_id)
    
    if not category:
        flash('分类不存在', 'danger')
        return redirect(url_for('admin.manage_categories'))
    
    # 检查是否有菜谱使用此分类
    recipes_count = Recipe.query.filter_by(category_id=category_id).count()
    if recipes_count > 0:
        flash(f'无法删除该分类，有 {recipes_count} 个菜谱属于此分类', 'danger')
        return redirect(url_for('admin.manage_categories'))
    
    # 从数据库中删除
    db.session.delete(category)
    db.session.commit()
    
    flash('分类已删除', 'success')
    return redirect(url_for('admin.manage_categories'))

@admin_bp.route('/posts')
@login_required
@admin_required
def manage_posts():
    """管理帖子"""
    posts = Post.query.all()
    
    # 为每个帖子获取作者信息和评论数
    posts_with_info = []
    for post in posts:
        posts_with_info.append({
            'post': post,
            'user': post.author,
            'comments_count': post.comments.count()
        })
    
    return render_template('admin/posts.html', posts=posts_with_info)

@admin_bp.route('/posts/delete/<int:post_id>', methods=['POST'])
@login_required
@admin_required
def delete_post(post_id):
    """删除帖子"""
    post = Post.query.get(post_id)
    
    if not post:
        flash('帖子不存在', 'danger')
        return redirect(url_for('admin.manage_posts'))
    
    # 从数据库中删除(会级联删除关联的评论)
    db.session.delete(post)
    db.session.commit()
    
    flash('帖子已删除', 'success')
    return redirect(url_for('admin.manage_posts'))
