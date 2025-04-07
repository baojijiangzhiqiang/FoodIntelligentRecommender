from models import Recipe, Category
import random

def get_recipe_by_id(recipe_id):
    """根据ID获取菜谱"""
    return Recipe.query().get(recipe_id)

def get_recipes_by_category(category_id):
    """获取特定分类的菜谱"""
    return Recipe.query().filter_by(category=category_id).all()

def get_popular_recipes(limit=4):
    """获取热门菜谱（按浏览量排序）"""
    recipes = Recipe.query().all()
    
    # 按浏览次数排序
    recipes = sorted(recipes, key=lambda r: r.views, reverse=True)
    
    return recipes[:limit]

def get_latest_recipes(limit=4):
    """获取最新菜谱（按时间排序）"""
    recipes = Recipe.query().all()
    
    # 按创建时间排序
    recipes = sorted(recipes, key=lambda r: r.created_at, reverse=True)
    
    return recipes[:limit]

def get_top_rated_recipes(limit=4):
    """获取评分最高的菜谱"""
    recipes = Recipe.query().all()
    
    # 按平均评分排序，只考虑有至少3个评分的菜谱
    recipes = [r for r in recipes if len(r.ratings) >= 3]
    recipes = sorted(recipes, key=lambda r: r.get_avg_rating(), reverse=True)
    
    return recipes[:limit]

def search_recipes(query, category_id=None, difficulty=None):
    """搜索菜谱"""
    recipes = Recipe.query().all()
    
    # 应用搜索过滤
    if query:
        recipes = [r for r in recipes if query.lower() in r.name.lower() or query.lower() in r.description.lower()]
        
    if category_id:
        recipes = [r for r in recipes if r.category == category_id]
        
    if difficulty:
        recipes = [r for r in recipes if r.difficulty == difficulty]
    
    return recipes

def get_random_recipe():
    """获取随机菜谱（用于探索功能）"""
    recipes = Recipe.query().all()
    if recipes:
        return random.choice(recipes)
    return None

def get_recipe_with_details(recipe_id):
    """获取菜谱及其详细信息（包括分类名称）"""
    recipe = Recipe.query().get(recipe_id)
    if not recipe:
        return None
        
    category = Category.query().get(recipe.category)
    
    return {
        'recipe': recipe,
        'category': category
    }

def get_recipes_by_cooking_time(max_time, limit=4):
    """获取烹饪时间不超过指定时间的菜谱"""
    recipes = Recipe.query().all()
    
    # 过滤总烹饪时间（准备+烹饪）不超过max_time的菜谱
    quick_recipes = [r for r in recipes if (r.prep_time + r.cook_time) <= max_time]
    
    # 按总时间排序
    quick_recipes.sort(key=lambda r: r.prep_time + r.cook_time)
    
    return quick_recipes[:limit]

def get_recipes_stats():
    """获取菜谱统计信息（用于仪表盘）"""
    recipes = Recipe.query().all()
    categories = Category.query().all()
    
    # 按分类统计菜谱数量
    recipes_by_category = {}
    for category in categories:
        count = len([r for r in recipes if r.category == category.id])
        recipes_by_category[category.name] = count
    
    # 按难度统计
    difficulty_counts = {}
    for recipe in recipes:
        if recipe.difficulty in difficulty_counts:
            difficulty_counts[recipe.difficulty] += 1
        else:
            difficulty_counts[recipe.difficulty] = 1
    
    # 计算平均评分
    avg_ratings = {}
    for recipe in recipes:
        if recipe.ratings:
            avg_ratings[recipe.name] = recipe.get_avg_rating()
    
    # 按评分排序的前5个菜谱
    top_rated = sorted(avg_ratings.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        'total_recipes': len(recipes),
        'by_category': recipes_by_category,
        'by_difficulty': difficulty_counts,
        'top_rated': top_rated
    }
