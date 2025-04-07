from models import User, Recipe, Post, Comment, UserFavorite, RecipeRating
from app import db
from sqlalchemy import func

def get_user_by_id(user_id):
    """根据ID获取用户"""
    return User.query.get(user_id)

def get_user_by_username(username):
    """根据用户名获取用户"""
    return User.query.filter_by(username=username).first()

def get_user_favorite_recipes(user_id):
    """获取用户收藏的菜谱"""
    # 通过关联表获取用户收藏的所有菜谱
    return db.session.query(Recipe).join(
        UserFavorite, UserFavorite.recipe_id == Recipe.id
    ).filter(UserFavorite.user_id == user_id).all()

def get_user_rated_recipes(user_id):
    """获取用户评分过的菜谱及评分"""
    # 查询用户的所有评分记录
    ratings = RecipeRating.query.filter_by(user_id=user_id).all()
    
    # 构建包含菜谱和评分的列表
    rated_recipes = []
    for rating in ratings:
        recipe = Recipe.query.get(rating.recipe_id)
        if recipe:
            rated_recipes.append({
                'recipe': recipe,
                'rating': rating.rating
            })
    
    # 按评分降序排列
    rated_recipes.sort(key=lambda x: x['rating'], reverse=True)
    
    return rated_recipes

def get_user_posts(user_id):
    """获取用户发布的帖子"""
    return Post.query.filter_by(user_id=user_id).all()

def toggle_favorite_recipe(user_id, recipe_id):
    """切换收藏菜谱状态"""
    user = User.query.get(user_id)
    recipe = Recipe.query.get(recipe_id)
    
    if not user or not recipe:
        return False, "用户或菜谱不存在"
    
    # 查找现有收藏
    favorite = UserFavorite.query.filter_by(
        user_id=user_id,
        recipe_id=recipe_id
    ).first()
    
    if favorite:
        # 已收藏，取消收藏
        db.session.delete(favorite)
        db.session.commit()
        return True, "已取消收藏"
    else:
        # 添加收藏
        new_favorite = UserFavorite(
            user_id=user_id,
            recipe_id=recipe_id
        )
        db.session.add(new_favorite)
        db.session.commit()
        return True, "已添加到收藏"

def rate_recipe(user_id, recipe_id, rating_value):
    """为菜谱评分"""
    user = User.query.get(user_id)
    recipe = Recipe.query.get(recipe_id)
    
    if not user or not recipe:
        return False, "用户或菜谱不存在"
    
    if rating_value < 1 or rating_value > 5:
        return False, "评分必须在1-5之间"
    
    # 查找现有评分
    rating = RecipeRating.query.filter_by(
        user_id=user_id,
        recipe_id=recipe_id
    ).first()
    
    if rating:
        # 更新现有评分
        rating.rating = rating_value
    else:
        # 添加新评分
        new_rating = RecipeRating(
            user_id=user_id,
            recipe_id=recipe_id,
            rating=rating_value
        )
        db.session.add(new_rating)
    
    db.session.commit()
    return True, "评分成功"

def update_user_preferences(user_id, preferences):
    """更新用户口味偏好"""
    user = User.query.get(user_id)
    
    if not user:
        return False, "用户不存在"
    
    user.preferences = preferences
    db.session.commit()
    return True, "偏好已更新"

def get_user_stats(user_id):
    """获取用户活动统计"""
    user = User.query.get(user_id)
    if not user:
        return None
    
    # 统计收藏数
    favorites_count = UserFavorite.query.filter_by(user_id=user_id).count()
    
    # 统计评分数
    ratings_count = RecipeRating.query.filter_by(user_id=user_id).count()
    
    # 统计评分分布
    rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    ratings_by_value = db.session.query(
        RecipeRating.rating, func.count(RecipeRating.id)
    ).filter(RecipeRating.user_id == user_id).group_by(RecipeRating.rating).all()
    
    for rating, count in ratings_by_value:
        if rating in rating_distribution:
            rating_distribution[rating] = count
    
    # 统计帖子数
    posts_count = Post.query.filter_by(user_id=user_id).count()
    
    # 统计评论数
    comments_count = Comment.query.filter_by(user_id=user_id).count()
    
    return {
        'favorites_count': favorites_count,
        'ratings_count': ratings_count,
        'rating_distribution': rating_distribution,
        'posts_count': posts_count,
        'comments_count': comments_count
    }
