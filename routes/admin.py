from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import Recipe, User, Category, Post, next_recipe_id, next_category_id

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
    users_count = len(User.query().all())
    recipes_count = len(Recipe.query().all())
    posts_count = len(Post.query().all())
    
    # 获取热门菜谱
    recipes = Recipe.query().all()
    popular_recipes = sorted(recipes, key=lambda x: x.views, reverse=True)[:5]
    
    # 获取最新用户
    users = User.query().all()
    latest_users = sorted(users, key=lambda x: x.created_at, reverse=True)[:5]
    
    # 获取最新帖子
    posts = Post.query().all()
    latest_posts = sorted(posts, key=lambda x: x.created_at, reverse=True)[:5]
    
    # 为最新帖子获取作者信息
    latest_posts_with_user = []
    for post in latest_posts:
        user = User.query().get(post.user_id)
        latest_posts_with_user.append({
            'post': post,
            'user': user
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
    recipes = Recipe.query().all()
    categories = Category.query().all()
    
    # 为每个菜谱获取分类名
    recipes_with_category = []
    for recipe in recipes:
        category = next((c for c in categories if c.id == recipe.category), None)
        recipes_with_category.append({
            'recipe': recipe,
            'category': category
        })
    
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
        ingredients = request.form.get('ingredients').split('\n')
        steps = request.form.get('steps').split('\n')
        category_id = int(request.form.get('category'))
        image_url = request.form.get('image_url')
        difficulty = request.form.get('difficulty')
        prep_time = int(request.form.get('prep_time'))
        cook_time = int(request.form.get('cook_time'))
        
        # 验证表单
        if not name or not description or not ingredients or not steps or not category_id:
            flash('所有必填字段都不能为空', 'danger')
            categories = Category.query().all()
            return render_template('admin/recipe_form.html', categories=categories)
        
        # 创建新菜谱
        global next_recipe_id
        new_recipe = Recipe(
            id=next_recipe_id,
            name=name,
            description=description,
            ingredients=ingredients,
            steps=steps,
            category=category_id,
            image_url=image_url,
            difficulty=difficulty,
            prep_time=prep_time,
            cook_time=cook_time
        )
        
        # 添加到数据库
        from models import recipes_db
        recipes_db.append(new_recipe)
        next_recipe_id += 1
        
        flash('菜谱添加成功', 'success')
        return redirect(url_for('admin.manage_recipes'))
    
    categories = Category.query().all()
    return render_template('admin/recipe_form.html', categories=categories)

@admin_bp.route('/recipes/edit/<int:recipe_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_recipe(recipe_id):
    """编辑菜谱"""
    recipe = Recipe.query().get(recipe_id)
    
    if not recipe:
        flash('菜谱不存在', 'danger')
        return redirect(url_for('admin.manage_recipes'))
    
    if request.method == 'POST':
        recipe.name = request.form.get('name')
        recipe.description = request.form.get('description')
        recipe.ingredients = request.form.get('ingredients').split('\n')
        recipe.steps = request.form.get('steps').split('\n')
        recipe.category = int(request.form.get('category'))
        recipe.image_url = request.form.get('image_url')
        recipe.difficulty = request.form.get('difficulty')
        recipe.prep_time = int(request.form.get('prep_time'))
        recipe.cook_time = int(request.form.get('cook_time'))
        
        flash('菜谱更新成功', 'success')
        return redirect(url_for('admin.manage_recipes'))
    
    categories = Category.query().all()
    return render_template('admin/recipe_form.html', 
                          recipe=recipe, 
                          categories=categories,
                          ingredients='\n'.join(recipe.ingredients),
                          steps='\n'.join(recipe.steps))

@admin_bp.route('/recipes/delete/<int:recipe_id>', methods=['POST'])
@login_required
@admin_required
def delete_recipe(recipe_id):
    """删除菜谱"""
    recipe = Recipe.query().get(recipe_id)
    
    if not recipe:
        flash('菜谱不存在', 'danger')
        return redirect(url_for('admin.manage_recipes'))
    
    # 从数据库中删除
    from models import recipes_db
    recipes_db.remove(recipe)
    
    flash('菜谱已删除', 'success')
    return redirect(url_for('admin.manage_recipes'))

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """管理用户"""
    users = User.query().all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/toggle_admin/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    """切换用户的管理员状态"""
    user = User.query().get(user_id)
    
    if not user:
        flash('用户不存在', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    # 不允许撤销自己的管理员权限
    if user.id == current_user.id:
        flash('不能更改自己的管理员状态', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    user.is_admin = not user.is_admin
    
    flash(f'用户 {user.username} 的管理员状态已更改', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """删除用户"""
    user = User.query().get(user_id)
    
    if not user:
        flash('用户不存在', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    # 不允许删除自己
    if user.id == current_user.id:
        flash('不能删除自己的账户', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    # 从数据库中删除
    from models import users_db
    users_db.remove(user)
    
    flash(f'用户 {user.username} 已删除', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/categories')
@login_required
@admin_required
def manage_categories():
    """管理分类"""
    categories = Category.query().all()
    
    # 为每个分类获取关联的菜谱数量
    categories_with_count = []
    for category in categories:
        recipes = Recipe.query().filter_by(category=category.id).all()
        categories_with_count.append({
            'category': category,
            'recipe_count': len(recipes)
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
        global next_category_id
        new_category = Category(
            id=next_category_id,
            name=name,
            description=description
        )
        
        # 添加到数据库
        from models import categories_db
        categories_db.append(new_category)
        next_category_id += 1
        
        flash('分类添加成功', 'success')
        return redirect(url_for('admin.manage_categories'))
    
    return render_template('admin/category_form.html')

@admin_bp.route('/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(category_id):
    """编辑分类"""
    category = Category.query().get(category_id)
    
    if not category:
        flash('分类不存在', 'danger')
        return redirect(url_for('admin.manage_categories'))
    
    if request.method == 'POST':
        category.name = request.form.get('name')
        category.description = request.form.get('description')
        
        flash('分类更新成功', 'success')
        return redirect(url_for('admin.manage_categories'))
    
    return render_template('admin/category_form.html', category=category)

@admin_bp.route('/categories/delete/<int:category_id>', methods=['POST'])
@login_required
@admin_required
def delete_category(category_id):
    """删除分类"""
    category = Category.query().get(category_id)
    
    if not category:
        flash('分类不存在', 'danger')
        return redirect(url_for('admin.manage_categories'))
    
    # 检查是否有菜谱使用此分类
    recipes = Recipe.query().filter_by(category=category_id).all()
    if recipes:
        flash(f'无法删除该分类，有 {len(recipes)} 个菜谱属于此分类', 'danger')
        return redirect(url_for('admin.manage_categories'))
    
    # 从数据库中删除
    from models import categories_db
    categories_db.remove(category)
    
    flash('分类已删除', 'success')
    return redirect(url_for('admin.manage_categories'))

@admin_bp.route('/posts')
@login_required
@admin_required
def manage_posts():
    """管理帖子"""
    posts = Post.query().all()
    
    # 为每个帖子获取用户和评论数
    posts_with_info = []
    for post in posts:
        user = User.query().get(post.user_id)
        posts_with_info.append({
            'post': post,
            'user': user,
            'comments_count': len(post.comments)
        })
    
    return render_template('admin/posts.html', posts=posts_with_info)

@admin_bp.route('/posts/delete/<int:post_id>', methods=['POST'])
@login_required
@admin_required
def delete_post(post_id):
    """删除帖子"""
    post = Post.query().get(post_id)
    
    if not post:
        flash('帖子不存在', 'danger')
        return redirect(url_for('admin.manage_posts'))
    
    # 从数据库中删除
    from models import posts_db
    posts_db.remove(post)
    
    flash('帖子已删除', 'success')
    return redirect(url_for('admin.manage_posts'))
