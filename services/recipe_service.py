from models import Recipe, Category, RecipeRating
from sqlalchemy import func, desc
from app import db
import random

def get_recipe_by_id(recipe_id):
    """根据ID获取菜谱"""
    return Recipe.query.get(recipe_id)

def get_recipes_by_category(category_id):
    """获取特定分类的菜谱"""
    return Recipe.query.filter_by(category_id=category_id).all()

def get_popular_recipes(limit=4):
    """获取热门菜谱（按浏览量排序）"""
    return Recipe.query.order_by(Recipe.views.desc()).limit(limit).all()

def get_latest_recipes(limit=4):
    """获取最新菜谱（按时间排序）"""
    return Recipe.query.order_by(Recipe.created_at.desc()).limit(limit).all()

def get_top_rated_recipes(limit=4):
    """获取评分最高的菜谱"""
    # 获取至少有3个评分的菜谱
    from sqlalchemy import func
    recipes_with_ratings = db.session.query(
        Recipe, func.avg(RecipeRating.rating).label('avg_rating'), func.count(RecipeRating.id).label('ratings_count')
    ).join(RecipeRating).group_by(Recipe).having(func.count(RecipeRating.id) >= 3).order_by(desc('avg_rating')).limit(limit).all()
    
    return [r[0] for r in recipes_with_ratings]

def search_recipes(query, category_id=None, difficulty=None):
    """搜索菜谱"""
    # 基础查询
    recipes_query = Recipe.query
    
    # 应用搜索过滤
    if query:
        recipes_query = recipes_query.filter(
            (Recipe.name.ilike(f'%{query}%')) | (Recipe.description.ilike(f'%{query}%'))
        )
        
    if category_id:
        recipes_query = recipes_query.filter_by(category_id=category_id)
        
    if difficulty:
        recipes_query = recipes_query.filter_by(difficulty=difficulty)
    
    return recipes_query.all()

def get_random_recipe():
    """获取随机菜谱（用于探索功能）"""
    from sqlalchemy.sql.expression import func
    return Recipe.query.order_by(func.random()).first()

def get_recipe_with_details(recipe_id):
    """获取菜谱及其详细信息（包括分类名称）"""
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        return None
    
    return {
        'recipe': recipe,
        'category': recipe.category
    }

def get_recipes_by_cooking_time(max_time, limit=4):
    """获取烹饪时间不超过指定时间的菜谱"""
    # 计算总烹饪时间（准备+烹饪）不超过max_time的菜谱
    return Recipe.query.filter(Recipe.prep_time + Recipe.cook_time <= max_time).order_by(Recipe.prep_time + Recipe.cook_time).limit(limit).all()

def get_recipes_stats():
    """获取菜谱统计信息（用于仪表盘）"""
    from sqlalchemy import func
    
    # 获取菜谱总数
    total_recipes = Recipe.query.count()
    
    # 按分类统计菜谱数量
    category_counts = db.session.query(
        Category.name, func.count(Recipe.id)
    ).join(Recipe, Recipe.category_id == Category.id).group_by(Category.name).all()
    
    recipes_by_category = {cat[0]: cat[1] for cat in category_counts}
    
    # 按难度统计
    difficulty_counts_data = db.session.query(
        Recipe.difficulty, func.count(Recipe.id)
    ).group_by(Recipe.difficulty).all()
    
    difficulty_counts = {diff[0]: diff[1] for diff in difficulty_counts_data}
    
    # 计算平均评分
    avg_ratings_data = db.session.query(
        Recipe.name, func.avg(RecipeRating.rating)
    ).join(RecipeRating, Recipe.id == RecipeRating.recipe_id).group_by(Recipe.name).order_by(func.avg(RecipeRating.rating).desc()).limit(5).all()
    
    top_rated = [(name, float(avg)) for name, avg in avg_ratings_data]
    
    return {
        'total_recipes': total_recipes,
        'by_category': recipes_by_category,
        'by_difficulty': difficulty_counts,
        'top_rated': top_rated
    }
