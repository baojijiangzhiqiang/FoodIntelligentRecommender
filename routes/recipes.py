from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import Recipe, Category

recipes_bp = Blueprint('recipes', __name__, url_prefix='/recipes')

@recipes_bp.route('/')
def index():
    """展示所有菜谱"""
    # 获取搜索参数
    search = request.args.get('search', '')
    category_id = request.args.get('category', type=int)
    difficulty = request.args.get('difficulty', '')
    
    # 获取所有菜谱
    recipes = Recipe.query().all()
    
    # 过滤菜谱
    if search:
        recipes = [r for r in recipes if search.lower() in r.name.lower() or search.lower() in r.description.lower()]
        
    if category_id:
        recipes = [r for r in recipes if r.category == category_id]
        
    if difficulty:
        recipes = [r for r in recipes if r.difficulty == difficulty]
    
    # 获取所有分类
    categories = Category.query().all()
    
    return render_template('recipes/list.html', 
                          recipes=recipes, 
                          categories=categories,
                          search=search,
                          category_id=category_id,
                          difficulty=difficulty)

@recipes_bp.route('/<int:recipe_id>')
def detail(recipe_id):
    """展示菜谱详情"""
    recipe = Recipe.query().get(recipe_id)
    
    if not recipe:
        flash('菜谱不存在', 'danger')
        return redirect(url_for('recipes.index'))
    
    # 增加浏览次数
    recipe.views += 1
    
    # 获取分类信息
    category = Category.query().get(recipe.category)
    
    # 获取相关推荐
    from services.recommendation_service import get_similar_recipes
    similar_recipes = get_similar_recipes(recipe_id)
    
    # 获取社区相关帖子
    from models import Post
    related_posts = Post.query().filter_by(recipe_id=recipe_id).all()
    
    # 获取当前用户是否已收藏
    is_favorite = False
    if current_user.is_authenticated:
        is_favorite = recipe_id in current_user.favorites
        
    # 获取用户评分
    user_rating = 0
    if current_user.is_authenticated and recipe_id in current_user.ratings:
        user_rating = current_user.ratings[recipe_id]
    
    return render_template('recipes/detail.html', 
                          recipe=recipe,
                          category=category,
                          similar_recipes=similar_recipes,
                          related_posts=related_posts,
                          is_favorite=is_favorite,
                          user_rating=user_rating)

@recipes_bp.route('/category/<int:category_id>')
def category(category_id):
    """按分类展示菜谱"""
    category = Category.query().get(category_id)
    
    if not category:
        flash('分类不存在', 'danger')
        return redirect(url_for('recipes.index'))
    
    recipes = Recipe.query().filter_by(category=category_id).all()
    
    return render_template('recipes/category.html', 
                          category=category,
                          recipes=recipes)

@recipes_bp.route('/<int:recipe_id>/favorite', methods=['POST'])
@login_required
def toggle_favorite(recipe_id):
    """收藏/取消收藏菜谱"""
    recipe = Recipe.query().get(recipe_id)
    
    if not recipe:
        flash('菜谱不存在', 'danger')
        return redirect(url_for('recipes.index'))
    
    # 切换收藏状态
    if recipe_id in current_user.favorites:
        current_user.favorites.remove(recipe_id)
        flash('已取消收藏', 'info')
    else:
        current_user.favorites.append(recipe_id)
        flash('已添加到收藏', 'success')
    
    return redirect(url_for('recipes.detail', recipe_id=recipe_id))

@recipes_bp.route('/<int:recipe_id>/rate', methods=['POST'])
@login_required
def rate_recipe(recipe_id):
    """为菜谱评分"""
    recipe = Recipe.query().get(recipe_id)
    
    if not recipe:
        flash('菜谱不存在', 'danger')
        return redirect(url_for('recipes.index'))
    
    rating = int(request.form.get('rating', 0))
    
    if rating < 1 or rating > 5:
        flash('评分必须在1-5之间', 'danger')
        return redirect(url_for('recipes.detail', recipe_id=recipe_id))
    
    # 更新用户评分
    old_rating = current_user.ratings.get(recipe_id)
    current_user.ratings[recipe_id] = rating
    
    # 更新菜谱评分
    if old_rating:
        # 找到并替换旧评分
        if old_rating in recipe.ratings:
            index = recipe.ratings.index(old_rating)
            recipe.ratings[index] = rating
    else:
        # 添加新评分
        recipe.ratings.append(rating)
    
    flash('评分成功', 'success')
    return redirect(url_for('recipes.detail', recipe_id=recipe_id))
