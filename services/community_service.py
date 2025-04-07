from models import Post, User, Recipe, next_post_id, next_comment_id, Comment
from datetime import datetime

def get_all_posts():
    """获取所有帖子并按时间排序"""
    posts = Post.query().all()
    
    # 按创建时间排序，最新的在前面
    posts.sort(key=lambda x: x.created_at, reverse=True)
    
    return posts

def get_post_with_details(post_id):
    """获取帖子及其详细信息"""
    post = Post.query().get(post_id)
    if not post:
        return None
    
    # 获取帖子作者
    user = User.query().get(post.user_id)
    
    # 获取相关菜谱
    recipe = None
    if post.recipe_id:
        recipe = Recipe.query().get(post.recipe_id)
    
    # 获取评论及对应的用户
    comments_with_user = []
    for comment in post.comments:
        comment_user = User.query().get(comment.user_id)
        comments_with_user.append({
            'comment': comment,
            'user': comment_user
        })
    
    # 按时间排序评论
    comments_with_user.sort(key=lambda x: x['comment'].created_at)
    
    return {
        'post': post,
        'user': user,
        'recipe': recipe,
        'comments': comments_with_user
    }

def create_post(user_id, title, content, recipe_id=None):
    """创建新帖子"""
    # 验证用户是否存在
    user = User.query().get(user_id)
    if not user:
        return False, "用户不存在"
    
    # 验证菜谱是否存在
    if recipe_id:
        recipe = Recipe.query().get(recipe_id)
        if not recipe:
            return False, "菜谱不存在"
    
    # 创建新帖子
    global next_post_id
    new_post = Post(
        id=next_post_id,
        user_id=user_id,
        title=title,
        content=content,
        recipe_id=recipe_id
    )
    
    # 添加到数据库
    from models import posts_db
    posts_db.append(new_post)
    next_post_id += 1
    
    return True, new_post.id

def add_comment(post_id, user_id, content):
    """添加评论"""
    # 验证帖子是否存在
    post = Post.query().get(post_id)
    if not post:
        return False, "帖子不存在"
    
    # 验证用户是否存在
    user = User.query().get(user_id)
    if not user:
        return False, "用户不存在"
    
    # 创建新评论
    global next_comment_id
    new_comment = Comment(
        id=next_comment_id,
        post_id=post_id,
        user_id=user_id,
        content=content
    )
    
    # 添加到帖子的评论列表
    post.comments.append(new_comment)
    next_comment_id += 1
    
    return True, "评论发布成功"

def like_post(post_id):
    """点赞帖子"""
    post = Post.query().get(post_id)
    if not post:
        return False, "帖子不存在"
    
    post.likes += 1
    return True, "点赞成功"

def get_posts_by_recipe(recipe_id):
    """获取与特定菜谱相关的帖子"""
    posts = Post.query().filter_by(recipe_id=recipe_id).all()
    
    # 按时间排序
    posts.sort(key=lambda x: x.created_at, reverse=True)
    
    # 获取用户信息
    posts_with_user = []
    for post in posts:
        user = User.query().get(post.user_id)
        posts_with_user.append({
            'post': post,
            'user': user
        })
    
    return posts_with_user

def get_trending_posts(limit=5):
    """获取热门帖子（根据点赞数和评论数）"""
    posts = Post.query().all()
    
    # 按点赞数和评论数计算热度得分
    for post in posts:
        post.hot_score = post.likes + len(post.comments) * 2
    
    # 按热度得分排序
    posts.sort(key=lambda x: x.hot_score, reverse=True)
    
    # 获取用户信息
    trending_posts = []
    for post in posts[:limit]:
        user = User.query().get(post.user_id)
        trending_posts.append({
            'post': post,
            'user': user
        })
    
    return trending_posts

def get_community_stats():
    """获取社区统计信息"""
    posts = Post.query().all()
    
    # 统计总帖子数
    total_posts = len(posts)
    
    # 统计总评论数
    total_comments = sum(len(post.comments) for post in posts)
    
    # 统计总点赞数
    total_likes = sum(post.likes for post in posts)
    
    # 计算平均每个帖子的评论数
    avg_comments = total_comments / total_posts if total_posts > 0 else 0
    
    # 计算平均每个帖子的点赞数
    avg_likes = total_likes / total_posts if total_posts > 0 else 0
    
    # 最活跃用户（发帖最多）
    user_post_counts = {}
    for post in posts:
        user_id = post.user_id
        if user_id in user_post_counts:
            user_post_counts[user_id] += 1
        else:
            user_post_counts[user_id] = 1
    
    most_active_users = []
    for user_id, count in sorted(user_post_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        user = User.query().get(user_id)
        if user:
            most_active_users.append({
                'user': user,
                'post_count': count
            })
    
    return {
        'total_posts': total_posts,
        'total_comments': total_comments,
        'total_likes': total_likes,
        'avg_comments': avg_comments,
        'avg_likes': avg_likes,
        'most_active_users': most_active_users
    }
