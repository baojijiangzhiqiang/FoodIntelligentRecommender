from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import Post, Comment, User, Recipe
from app import db

community_bp = Blueprint('community', __name__, url_prefix='/community')

@community_bp.route('/')
def index():
    """社区主页，显示所有帖子"""
    # 查询所有帖子，按创建时间排序，最新的在前面
    posts = Post.query.order_by(Post.created_at.desc()).all()
    
    # 为每个帖子准备信息
    posts_with_info = []
    for post in posts:
        posts_with_info.append({
            'post': post,
            'user': post.author,
            'recipe': post.recipe,
            'comments_count': post.comments.count()
        })
    
    return render_template('community/posts.html', posts=posts_with_info)

@community_bp.route('/post/<int:post_id>')
def post_detail(post_id):
    """帖子详情页"""
    post = Post.query.get(post_id)
    
    if not post:
        flash('帖子不存在', 'danger')
        return redirect(url_for('community.index'))
    
    # 获取评论及对应的用户
    comments_with_user = []
    for comment in post.comments.order_by(Comment.created_at).all():
        comments_with_user.append({
            'comment': comment,
            'user': comment.author
        })
    
    return render_template('community/post_detail.html',
                          post=post,
                          user=post.author,
                          recipe=post.recipe,
                          comments=comments_with_user)

@community_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    """创建新帖子"""
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        recipe_id = request.form.get('recipe_id', type=int)
        
        # 验证表单
        if not title or not content:
            flash('标题和内容不能为空', 'danger')
            return redirect(url_for('community.new_post'))
        
        # 验证菜谱是否存在
        if recipe_id:
            recipe = Recipe.query.get(recipe_id)
            if not recipe:
                flash('所选菜谱不存在', 'danger')
                return redirect(url_for('community.new_post'))
        
        # 创建新帖子
        new_post = Post(
            user_id=current_user.id,
            title=title,
            content=content,
            recipe_id=recipe_id
        )
        
        # 添加到数据库
        db.session.add(new_post)
        db.session.commit()
        
        flash('帖子发布成功', 'success')
        return redirect(url_for('community.post_detail', post_id=new_post.id))
    
    # 获取用户收藏的菜谱作为可选项
    favorite_recipes = current_user.favorites
    
    # 获取所有菜谱
    all_recipes = Recipe.query.all()
    
    return render_template('community/new_post.html',
                          favorite_recipes=favorite_recipes,
                          all_recipes=all_recipes)

@community_bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    """添加评论"""
    post = Post.query.get(post_id)
    
    if not post:
        flash('帖子不存在', 'danger')
        return redirect(url_for('community.index'))
    
    content = request.form.get('content')
    
    if not content:
        flash('评论内容不能为空', 'danger')
        return redirect(url_for('community.post_detail', post_id=post_id))
    
    # 创建新评论
    new_comment = Comment(
        post_id=post_id,
        user_id=current_user.id,
        content=content
    )
    
    # 添加到数据库
    db.session.add(new_comment)
    db.session.commit()
    
    flash('评论发布成功', 'success')
    return redirect(url_for('community.post_detail', post_id=post_id))

@community_bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    """点赞帖子"""
    post = Post.query.get(post_id)
    
    if not post:
        flash('帖子不存在', 'danger')
        return redirect(url_for('community.index'))
    
    # 增加点赞数
    post.likes += 1
    db.session.commit()
    
    flash('点赞成功', 'success')
    return redirect(url_for('community.post_detail', post_id=post_id))
