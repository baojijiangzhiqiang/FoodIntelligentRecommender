from models import Recipe, User
import random

def get_recommended_recipes(limit=4):
    """获取推荐菜谱列表（首页展示）
    
    当前为简单实现，随机选择评分较高的菜谱
    """
    recipes = Recipe.query().all()
    
    # 按平均评分排序，评分相同则按浏览次数排序
    recipes = sorted(recipes, key=lambda r: (r.get_avg_rating(), r.views), reverse=True)
    
    # 从前10个中随机选4个，保证一定推荐高质量的同时增加多样性
    top_recipes = recipes[:10]
    if len(top_recipes) > limit:
        recommended = random.sample(top_recipes, limit)
    else:
        recommended = top_recipes
    
    return recommended

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

def get_similar_recipes(recipe_id, limit=3):
    """获取相似菜谱推荐
    
    基于同类别和相似评分的简单实现
    """
    target_recipe = Recipe.query().get(recipe_id)
    if not target_recipe:
        return []
    
    # 获取同一分类的其他菜谱
    same_category_recipes = []
    for recipe in Recipe.query().all():
        if recipe.id != recipe_id and recipe.category == target_recipe.category:
            same_category_recipes.append(recipe)
    
    # 按评分相似度排序
    target_rating = target_recipe.get_avg_rating()
    same_category_recipes.sort(key=lambda r: abs(r.get_avg_rating() - target_rating))
    
    return same_category_recipes[:limit]

def get_personalized_recommendations(user_id, limit=4):
    """为用户获取个性化菜谱推荐
    
    基于用户评分和收藏的简单协同过滤实现
    """
    user = User.query().get(user_id)
    if not user:
        return get_recommended_recipes(limit)
    
    # 如果用户有评分记录，基于他们喜欢的菜谱类别推荐
    if user.ratings:
        # 获取用户评分较高的菜谱（4分或以上）
        liked_recipes = []
        for recipe_id, rating in user.ratings.items():
            if rating >= 4:
                recipe = Recipe.query().get(recipe_id)
                if recipe:
                    liked_recipes.append(recipe)
        
        # 如果有高评分菜谱，基于这些菜谱的分类推荐
        if liked_recipes:
            # 获取用户喜欢的分类
            liked_categories = set(recipe.category for recipe in liked_recipes)
            
            # 推荐同类别但用户未评分的菜谱
            recommendations = []
            for recipe in Recipe.query().all():
                if (recipe.id not in user.ratings and 
                    recipe.category in liked_categories and 
                    recipe.id not in user.favorites):
                    recommendations.append(recipe)
            
            # 排序：先按类别匹配度，再按平均评分
            recommendations.sort(
                key=lambda r: (
                    sum(1 for liked in liked_recipes if liked.category == r.category),
                    r.get_avg_rating()
                ),
                reverse=True
            )
            
            if recommendations:
                return recommendations[:limit]
    
    # 如果用户有偏好设置，使用偏好
    if user.preferences:
        preferred_categories = [int(pref) for pref in user.preferences if pref.isdigit()]
        if preferred_categories:
            recommendations = []
            for recipe in Recipe.query().all():
                if (recipe.id not in user.ratings and 
                    recipe.category in preferred_categories and 
                    recipe.id not in user.favorites):
                    recommendations.append(recipe)
            
            recommendations.sort(key=lambda r: r.get_avg_rating(), reverse=True)
            
            if recommendations:
                return recommendations[:limit]
    
    # 如果以上方法都不可用，则回退到一般推荐
    return get_recommended_recipes(limit)
