from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import Recipe, Category, RecipeRating, UserFavorite
from app import db
from services import recipe_service

recipes_bp = Blueprint('recipes', __name__, url_prefix='/recipes')

@recipes_bp.route('/')
def index():
    """展示所有菜谱"""
    # 获取搜索参数
    search = request.args.get('search', '')
    category_id = request.args.get('category', type=int)
    difficulty = request.args.get('difficulty', '')
    
    # 使用服务层搜索菜谱
    recipes = recipe_service.search_recipes(search, category_id, difficulty)
    
    # 获取所有分类
    categories = Category.query.all()
    
    return render_template('recipes/list.html', 
                          recipes=recipes, 
                          categories=categories,
                          search=search,
                          category_id=category_id,
                          difficulty=difficulty)

@recipes_bp.route('/<int:recipe_id>')
def detail(recipe_id):
    """展示菜谱详情"""
    recipe = Recipe.query.get(recipe_id)
    
    if not recipe:
        flash('菜谱不存在', 'danger')
        return redirect(url_for('recipes.index'))
    
    # 增加浏览次数
    recipe.views += 1
    db.session.commit()
    
    # 获取相关推荐
    from services.recommendation_service import get_similar_recipes
    similar_recipes = get_similar_recipes(recipe_id)
    
    # 获取社区相关帖子
    from models import Post
    related_posts = Post.query.filter_by(recipe_id=recipe_id).all()
    
    # 获取当前用户是否已收藏
    is_favorite = False
    user_rating = 0
    if current_user.is_authenticated:
        # 检查是否已收藏
        favorite = UserFavorite.query.filter_by(
            user_id=current_user.id, 
            recipe_id=recipe_id
        ).first()
        is_favorite = favorite is not None
        
        # 获取用户评分
        rating = RecipeRating.query.filter_by(
            user_id=current_user.id,
            recipe_id=recipe_id
        ).first()
        if rating:
            user_rating = rating.rating
    
    return render_template('recipes/detail.html', 
                          recipe=recipe,
                          category=recipe.category,
                          similar_recipes=similar_recipes,
                          related_posts=related_posts,
                          is_favorite=is_favorite,
                          user_rating=user_rating)

@recipes_bp.route('/category/<int:category_id>')
def category(category_id):
    """按分类展示菜谱"""
    category = Category.query.get(category_id)
    
    if not category:
        flash('分类不存在', 'danger')
        return redirect(url_for('recipes.index'))
    
    recipes = Recipe.query.filter_by(category_id=category_id).all()
    
    return render_template('recipes/category.html', 
                          category=category,
                          recipes=recipes)

@recipes_bp.route('/<int:recipe_id>/favorite', methods=['POST'])
@login_required
def toggle_favorite(recipe_id):
    """收藏/取消收藏菜谱"""
    recipe = Recipe.query.get(recipe_id)
    
    if not recipe:
        flash('菜谱不存在', 'danger')
        return redirect(url_for('recipes.index'))
    
    # 查找现有收藏
    favorite = UserFavorite.query.filter_by(
        user_id=current_user.id,
        recipe_id=recipe_id
    ).first()
    
    if favorite:
        # 已收藏，取消收藏
        db.session.delete(favorite)
        flash('已取消收藏', 'info')
    else:
        # 添加收藏
        new_favorite = UserFavorite(
            user_id=current_user.id,
            recipe_id=recipe_id
        )
        db.session.add(new_favorite)
        flash('已添加到收藏', 'success')
    
    db.session.commit()
    return redirect(url_for('recipes.detail', recipe_id=recipe_id))

@recipes_bp.route('/<int:recipe_id>/rate', methods=['POST'])
@login_required
def rate_recipe(recipe_id):
    """为菜谱评分"""
    recipe = Recipe.query.get(recipe_id)
    
    if not recipe:
        flash('菜谱不存在', 'danger')
        return redirect(url_for('recipes.index'))
    
    rating_value = int(request.form.get('rating', 0))
    
    if rating_value < 1 or rating_value > 5:
        flash('评分必须在1-5之间', 'danger')
        return redirect(url_for('recipes.detail', recipe_id=recipe_id))
    
    # 查找现有评分
    rating = RecipeRating.query.filter_by(
        user_id=current_user.id,
        recipe_id=recipe_id
    ).first()
    
    if rating:
        # 更新现有评分
        rating.rating = rating_value
    else:
        # 添加新评分
        new_rating = RecipeRating(
            user_id=current_user.id,
            recipe_id=recipe_id,
            rating=rating_value
        )
        db.session.add(new_rating)
    
    db.session.commit()
    flash('评分成功', 'success')
    return redirect(url_for('recipes.detail', recipe_id=recipe_id))
