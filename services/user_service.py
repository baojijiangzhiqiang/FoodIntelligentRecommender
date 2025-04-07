from models import User, Recipe, Post

def get_user_by_id(user_id):
    """根据ID获取用户"""
    return User.query().get(user_id)

def get_user_by_username(username):
    """根据用户名获取用户"""
    return User.query().filter_by(username=username).first()

def get_user_favorite_recipes(user_id):
    """获取用户收藏的菜谱"""
    user = User.query().get(user_id)
    if not user:
        return []
    
    favorite_recipes = []
    for recipe_id in user.favorites:
        recipe = Recipe.query().get(recipe_id)
        if recipe:
            favorite_recipes.append(recipe)
    
    return favorite_recipes

def get_user_rated_recipes(user_id):
    """获取用户评分过的菜谱及评分"""
    user = User.query().get(user_id)
    if not user:
        return []
    
    rated_recipes = []
    for recipe_id, rating in user.ratings.items():
        recipe = Recipe.query().get(recipe_id)
        if recipe:
            rated_recipes.append({
                'recipe': recipe,
                'rating': rating
            })
    
    # 按评分降序排列
    rated_recipes.sort(key=lambda x: x['rating'], reverse=True)
    
    return rated_recipes

def get_user_posts(user_id):
    """获取用户发布的帖子"""
    return Post.query().filter_by(user_id=user_id).all()

def toggle_favorite_recipe(user_id, recipe_id):
    """切换收藏菜谱状态"""
    user = User.query().get(user_id)
    recipe = Recipe.query().get(recipe_id)
    
    if not user or not recipe:
        return False, "用户或菜谱不存在"
    
    if recipe_id in user.favorites:
        user.favorites.remove(recipe_id)
        return True, "已取消收藏"
    else:
        user.favorites.append(recipe_id)
        return True, "已添加到收藏"

def rate_recipe(user_id, recipe_id, rating):
    """为菜谱评分"""
    user = User.query().get(user_id)
    recipe = Recipe.query().get(recipe_id)
    
    if not user or not recipe:
        return False, "用户或菜谱不存在"
    
    if rating < 1 or rating > 5:
        return False, "评分必须在1-5之间"
    
    # 记录旧评分
    old_rating = user.ratings.get(recipe_id)
    
    # 更新用户评分
    user.ratings[recipe_id] = rating
    
    # 更新菜谱评分
    if old_rating:
        # 找到并替换旧评分
        if old_rating in recipe.ratings:
            index = recipe.ratings.index(old_rating)
            recipe.ratings[index] = rating
    else:
        # 添加新评分
        recipe.ratings.append(rating)
    
    return True, "评分成功"

def update_user_preferences(user_id, preferences):
    """更新用户口味偏好"""
    user = User.query().get(user_id)
    
    if not user:
        return False, "用户不存在"
    
    user.preferences = preferences
    return True, "偏好已更新"

def get_user_stats(user_id):
    """获取用户活动统计"""
    user = User.query().get(user_id)
    if not user:
        return None
    
    # 统计收藏数
    favorites_count = len(user.favorites)
    
    # 统计评分数
    ratings_count = len(user.ratings)
    
    # 统计评分分布
    rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for rating in user.ratings.values():
        if rating in rating_distribution:
            rating_distribution[rating] += 1
    
    # 统计帖子数
    posts = Post.query().filter_by(user_id=user_id).all()
    posts_count = len(posts)
    
    # 统计评论数
    comments_count = 0
    for post in Post.query().all():
        for comment in post.comments:
            if comment.user_id == user_id:
                comments_count += 1
    
    return {
        'favorites_count': favorites_count,
        'ratings_count': ratings_count,
        'rating_distribution': rating_distribution,
        'posts_count': posts_count,
        'comments_count': comments_count
    }
