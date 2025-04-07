from models import Recipe, User, RecipeRating, UserFavorite
from sqlalchemy import func, desc
from app import db
import random
import json

def get_recommended_recipes(limit=4):
    """获取推荐菜谱列表（首页展示）
    
    当前为简单实现，随机选择评分较高的菜谱
    """
    # 获取评分较高的菜谱
    top_rated_recipes = db.session.query(
        Recipe, func.avg(RecipeRating.rating).label('avg_rating')
    ).join(RecipeRating).group_by(Recipe).order_by(
        desc('avg_rating'), desc(Recipe.views)
    ).limit(10).all()
    
    # 从前10个中随机选择limit个
    if len(top_rated_recipes) > limit:
        selected_indices = random.sample(range(len(top_rated_recipes)), limit)
        recommended = [top_rated_recipes[i][0] for i in selected_indices]
    else:
        recommended = [r[0] for r in top_rated_recipes]
    
    # 如果没有足够的评分菜谱，添加一些浏览量高的菜谱
    if len(recommended) < limit:
        # 获取已推荐的菜谱ID
        recommended_ids = [r.id for r in recommended]
        
        # 获取浏览量高的其他菜谱
        popular_recipes = Recipe.query.filter(
            ~Recipe.id.in_(recommended_ids)
        ).order_by(Recipe.views.desc()).limit(limit - len(recommended)).all()
        
        recommended.extend(popular_recipes)
    
    return recommended

def get_popular_recipes(limit=4):
    """获取热门菜谱（按浏览量排序）"""
    return Recipe.query.order_by(Recipe.views.desc()).limit(limit).all()

def get_latest_recipes(limit=4):
    """获取最新菜谱（按时间排序）"""
    return Recipe.query.order_by(Recipe.created_at.desc()).limit(limit).all()

def get_similar_recipes(recipe_id, limit=3):
    """获取相似菜谱推荐
    
    基于同类别和相似评分的简单实现
    """
    target_recipe = Recipe.query.get(recipe_id)
    if not target_recipe:
        return []
    
    # 获取同一分类的其他菜谱
    same_category_recipes = Recipe.query.filter(
        Recipe.category_id == target_recipe.category_id,
        Recipe.id != recipe_id
    ).all()
    
    if not same_category_recipes:
        return []
    
    # 获取目标菜谱的平均评分
    target_rating_result = db.session.query(
        func.avg(RecipeRating.rating)
    ).filter(RecipeRating.recipe_id == recipe_id).first()
    target_rating = target_rating_result[0] if target_rating_result[0] else 0
    
    # 获取每个相似菜谱的平均评分
    for recipe in same_category_recipes:
        rating_result = db.session.query(
            func.avg(RecipeRating.rating)
        ).filter(RecipeRating.recipe_id == recipe.id).first()
        recipe.avg_rating = rating_result[0] if rating_result[0] else 0
    
    # 按评分相似度排序
    same_category_recipes.sort(key=lambda r: abs(r.avg_rating - target_rating))
    
    return same_category_recipes[:limit]

def get_personalized_recommendations(user_id, limit=4):
    """为用户获取个性化菜谱推荐
    
    基于用户评分和收藏的简单协同过滤实现
    """
    user = User.query.get(user_id)
    if not user:
        return get_recommended_recipes(limit)
    
    # 获取用户评分较高的菜谱（4分或以上）
    liked_recipes_query = db.session.query(Recipe).join(
        RecipeRating, Recipe.id == RecipeRating.recipe_id
    ).filter(
        RecipeRating.user_id == user_id,
        RecipeRating.rating >= 4
    ).all()
    
    # 如果有高评分菜谱，基于这些菜谱的分类推荐
    if liked_recipes_query:
        # 获取用户喜欢的分类ID
        liked_categories = set(recipe.category_id for recipe in liked_recipes_query)
        
        # 获取用户已评分的菜谱ID
        rated_recipe_ids = db.session.query(RecipeRating.recipe_id).filter(
            RecipeRating.user_id == user_id
        ).all()
        rated_recipe_ids = [r[0] for r in rated_recipe_ids]
        
        # 获取用户已收藏的菜谱ID
        favorited_recipe_ids = db.session.query(UserFavorite.recipe_id).filter(
            UserFavorite.user_id == user_id
        ).all()
        favorited_recipe_ids = [r[0] for r in favorited_recipe_ids]
        
        # 推荐同类别但用户未评分且未收藏的菜谱
        recommendations_query = Recipe.query.filter(
            Recipe.category_id.in_(liked_categories),
            ~Recipe.id.in_(rated_recipe_ids),
            ~Recipe.id.in_(favorited_recipe_ids)
        )
        
        # 计算每个分类出现的次数作为权重
        category_weights = {}
        for recipe in liked_recipes_query:
            category_weights[recipe.category_id] = category_weights.get(recipe.category_id, 0) + 1
        
        # 获取推荐列表
        recommendations = recommendations_query.all()
        
        # 排序：先按类别匹配度（权重），再按平均评分
        for recipe in recommendations:
            # 获取平均评分
            avg_rating_result = db.session.query(
                func.avg(RecipeRating.rating)
            ).filter(RecipeRating.recipe_id == recipe.id).first()
            recipe.avg_rating = avg_rating_result[0] if avg_rating_result[0] else 0
            
            # 设置类别权重
            recipe.category_weight = category_weights.get(recipe.category_id, 0)
        
        recommendations.sort(
            key=lambda r: (r.category_weight, r.avg_rating),
            reverse=True
        )
        
        if recommendations:
            return recommendations[:limit]
    
    # 如果用户有偏好设置，使用偏好
    if user.preferences:
        try:
            # 尝试解析用户偏好
            preferences_list = json.loads(user.preferences)
            preferred_categories = [int(pref) for pref in preferences_list if isinstance(pref, (int, str)) and str(pref).isdigit()]
            
            if preferred_categories:
                # 获取用户已评分的菜谱ID
                rated_recipe_ids = db.session.query(RecipeRating.recipe_id).filter(
                    RecipeRating.user_id == user_id
                ).all()
                rated_recipe_ids = [r[0] for r in rated_recipe_ids]
                
                # 获取用户已收藏的菜谱ID
                favorited_recipe_ids = db.session.query(UserFavorite.recipe_id).filter(
                    UserFavorite.user_id == user_id
                ).all()
                favorited_recipe_ids = [r[0] for r in favorited_recipe_ids]
                
                # 推荐基于偏好类别的菜谱
                recommendations = Recipe.query.filter(
                    Recipe.category_id.in_(preferred_categories),
                    ~Recipe.id.in_(rated_recipe_ids),
                    ~Recipe.id.in_(favorited_recipe_ids)
                ).order_by(Recipe.views.desc()).limit(limit).all()
                
                if recommendations:
                    return recommendations
        except (json.JSONDecodeError, ValueError):
            # 如果偏好解析失败，继续到下一个推荐方法
            pass
    
    # 如果以上方法都不可用，则回退到一般推荐
    return get_recommended_recipes(limit)
