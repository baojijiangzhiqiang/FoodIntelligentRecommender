from datetime import datetime
import random
import json
from flask_login import UserMixin
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

# 用户收藏关联表
class UserFavorite(db.Model):
    __tablename__ = 'user_favorites'
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

# 菜谱评分关联表
class RecipeRating(db.Model):
    __tablename__ = 'recipe_ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))
    rating = db.Column(db.Integer, nullable=False)  # 1-5星评分
    created_at = db.Column(db.DateTime, default=datetime.now)

# 用户模型
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    preferences = db.Column(db.Text, default='[]')  # 存储为JSON字符串
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # 关系
    favorites = db.relationship('Recipe', secondary='user_favorites', 
                               backref=db.backref('favorited_by', lazy='dynamic'))
    ratings = db.relationship('RecipeRating', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    posts = db.relationship('Post', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def get_preferences(self):
        if not self.preferences:
            return []
        return json.loads(self.preferences)
        
    def set_preferences(self, preferences_list):
        self.preferences = json.dumps(preferences_list)
        
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'preferences': self.get_preferences(),
            'created_at': self.created_at
        }

# 菜谱模型
class Recipe(db.Model):
    __tablename__ = 'recipe'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    ingredients = db.Column(db.Text, nullable=False)  # 存储为JSON
    steps = db.Column(db.Text, nullable=False)  # 存储为JSON
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    image_url = db.Column(db.Text)
    difficulty = db.Column(db.String(20))
    prep_time = db.Column(db.Integer)  # 单位：分钟
    cook_time = db.Column(db.Integer)  # 单位：分钟
    views = db.Column(db.Integer, default=0)
    tags = db.Column(db.Text, default='[]')  # 存储为JSON
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # 关系
    category = db.relationship('Category', backref='recipes')
    ratings = db.relationship('RecipeRating', backref='recipe', lazy='dynamic')
    posts = db.relationship('Post', backref='recipe', lazy='dynamic')
    
    def get_ingredients(self):
        return json.loads(self.ingredients)
        
    def set_ingredients(self, ingredients_list):
        self.ingredients = json.dumps(ingredients_list)
        
    def get_steps(self):
        return json.loads(self.steps)
        
    def set_steps(self, steps_list):
        self.steps = json.dumps(steps_list)
        
    def get_tags(self):
        if not self.tags:
            return []
        return json.loads(self.tags)
        
    def set_tags(self, tags_list):
        self.tags = json.dumps(tags_list)
    
    def get_avg_rating(self):
        ratings = [r.rating for r in self.ratings.all()]
        return sum(ratings) / len(ratings) if ratings else 0
        
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'ingredients': self.get_ingredients(),
            'steps': self.get_steps(),
            'category': self.category_id,
            'category_name': self.category.name if self.category else None,
            'image_url': self.image_url,
            'difficulty': self.difficulty,
            'prep_time': self.prep_time,
            'cook_time': self.cook_time,
            'avg_rating': self.get_avg_rating(),
            'ratings_count': self.ratings.count(),
            'views': self.views,
            'created_at': self.created_at,
            'tags': self.get_tags()
        }

# 社区帖子模型
class Post(db.Model):
    __tablename__ = 'post'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # 关系
    comments = db.relationship('Comment', backref='post', lazy='dynamic', 
                             cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.author.username,
            'title': self.title,
            'content': self.content,
            'recipe_id': self.recipe_id,
            'recipe_name': self.recipe.name if self.recipe else None,
            'created_at': self.created_at,
            'comments': [comment.to_dict() for comment in self.comments],
            'likes': self.likes
        }

# 评论模型
class Comment(db.Model):
    __tablename__ = 'comment'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'username': self.author.username,
            'content': self.content,
            'created_at': self.created_at
        }

# 分类模型
class Category(db.Model):
    __tablename__ = 'category'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(200))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

# 初始化示例数据
def init_data():
    # 如果已有数据，不再初始化
    if Category.query.count() > 0:
        return
    
    # 添加分类
    categories = [
        {"name": "川菜", "description": "四川传统菜系，特点是麻辣鲜香"},
        {"name": "粤菜", "description": "广东传统菜系，特点是清淡爽口"},
        {"name": "鲁菜", "description": "山东传统菜系，特点是咸鲜醇厚"},
        {"name": "苏菜", "description": "江苏传统菜系，特点是甜咸适中"},
        {"name": "浙菜", "description": "浙江传统菜系，特点是鲜甜清爽"},
        {"name": "湘菜", "description": "湖南传统菜系，特点是香辣酸"},
        {"name": "徽菜", "description": "安徽传统菜系，特点是重油重色"},
        {"name": "闽菜", "description": "福建传统菜系，特点是鲜甜、香辣"},
        {"name": "早餐", "description": "一日之计在于晨"},
        {"name": "午餐", "description": "一天的能量补充"},
        {"name": "晚餐", "description": "轻松愉快的晚餐时光"},
        {"name": "甜点", "description": "生活需要一点甜"},
        {"name": "饮品", "description": "各种美味饮料"},
        {"name": "小吃", "description": "解馋又美味的小食"}
    ]
    
    for cat in categories:
        category = Category(name=cat["name"], description=cat["description"])
        db.session.add(category)
    db.session.commit()
    
    # 添加管理员账户
    admin = User(username="admin", email="admin@example.com", is_admin=True)
    admin.set_password("admin123")
    db.session.add(admin)
    
    # 添加普通用户
    user1 = User(username="张三", email="zhangsan@example.com")
    user1.set_password("password")
    db.session.add(user1)
    
    user2 = User(username="李四", email="lisi@example.com")
    user2.set_password("password")
    db.session.add(user2)
    db.session.commit()
    
    # 添加菜谱
    recipes = [
        {
            "name": "麻婆豆腐",
            "description": "麻婆豆腐是四川传统名菜，由豆腐、牛肉末、辣椒和花椒等烹制而成，麻辣鲜香。",
            "ingredients": ["豆腐 300g", "牛肉末 100g", "郫县豆瓣酱 2勺", "花椒粉 适量", "葱姜蒜 适量", "生抽 适量", "盐 适量"],
            "steps": ["豆腐切丁，用开水焯烫；", "锅中油热后，爆香葱姜蒜；", "加入牛肉末炒至变色；", "加入豆瓣酱炒出香味；", "加入适量水和豆腐，炖煮5分钟；", "调味后撒上花椒粉即可。"],
            "category_id": 1,  # 川菜
            "image_url": "https://images.unsplash.com/photo-1582196016295-f8c8bd4b3a99",
            "difficulty": "中等",
            "prep_time": 15,
            "cook_time": 20
        },
        {
            "name": "宫保鸡丁",
            "description": "宫保鸡丁是一道经典川菜，鸡肉与花生米的搭配非常经典。",
            "ingredients": ["鸡胸肉 300g", "花生米 50g", "干辣椒 10个", "葱姜蒜 适量", "生抽 适量", "醋 适量", "白糖 适量"],
            "steps": ["鸡胸肉切丁，用生抽、料酒腌制；", "花生米炸脆备用；", "锅中油热后，炒香干辣椒和花椒；", "加入鸡丁炒至变色；", "加入调味料翻炒；", "最后加入花生米即可。"],
            "category_id": 1,  # 川菜
            "image_url": "https://images.unsplash.com/photo-1619631428091-f2206ca68e7a",
            "difficulty": "简单",
            "prep_time": 20,
            "cook_time": 15
        },
        {
            "name": "清蒸鲈鱼",
            "description": "清蒸鲈鱼是一道经典粤菜，保留了鱼的鲜美。",
            "ingredients": ["鲈鱼 1条", "姜 适量", "葱 适量", "蒸鱼豉油 适量"],
            "steps": ["鲈鱼洗净，在两面划几刀；", "放入姜丝和葱段；", "大火蒸8-10分钟；", "淋上蒸鱼豉油即可。"],
            "category_id": 2,  # 粤菜
            "image_url": "https://images.unsplash.com/photo-1616645258469-ec681c17f3ee",
            "difficulty": "简单",
            "prep_time": 10,
            "cook_time": 10
        },
        {
            "name": "糖醋排骨",
            "description": "糖醋排骨是一道色香味俱全的传统名菜，酸甜可口。",
            "ingredients": ["排骨 500g", "白糖 3勺", "醋 2勺", "生抽 1勺", "料酒 1勺", "姜片 适量"],
            "steps": ["排骨洗净切段，焯水去血水；", "锅中放油，倒入排骨煎至两面金黄；", "加入糖醋汁，小火煮至汁液浓稠；", "出锅前撒上香菜点缀。"],
            "category_id": 3,  # 鲁菜
            "image_url": "https://images.unsplash.com/photo-1625471204433-874c88e428e1",
            "difficulty": "中等",
            "prep_time": 15,
            "cook_time": 30
        },
        {
            "name": "西湖醋鱼",
            "description": "西湖醋鱼是浙江杭州的传统名菜，鱼肉鲜嫩，带有甜酸味。",
            "ingredients": ["草鱼 1条", "醋 3勺", "白糖 2勺", "生抽 1勺", "葱姜 适量"],
            "steps": ["草鱼宰杀洗净，在两面划几刀；", "热锅冷油，煎至两面金黄；", "加入调味料，焖煮10分钟；", "出锅前撒上葱花。"],
            "category_id": 5,  # 浙菜
            "image_url": "https://images.unsplash.com/photo-1580476262798-bddd9f4b7369",
            "difficulty": "中等",
            "prep_time": 20,
            "cook_time": 25
        }
    ]
    
    for recipe_data in recipes:
        recipe = Recipe(
            name=recipe_data["name"],
            description=recipe_data["description"],
            ingredients=json.dumps(recipe_data["ingredients"]),
            steps=json.dumps(recipe_data["steps"]),
            category_id=recipe_data["category_id"],
            image_url=recipe_data["image_url"],
            difficulty=recipe_data["difficulty"],
            prep_time=recipe_data["prep_time"],
            cook_time=recipe_data["cook_time"],
            views=random.randint(20, 100)
        )
        db.session.add(recipe)
    db.session.commit()
    
    # 添加评分
    recipes = Recipe.query.all()
    users = User.query.all()
    
    for recipe in recipes:
        for _ in range(random.randint(5, 15)):
            user = random.choice(users)
            rating = RecipeRating(
                user_id=user.id,
                recipe_id=recipe.id,
                rating=random.randint(3, 5)
            )
            db.session.add(rating)
    db.session.commit()
    
    # 添加社区帖子
    posts_data = [
        {
            "user_id": 2,  # 张三
            "title": "分享我的麻婆豆腐做法",
            "content": "今天尝试了一下麻婆豆腐的做法，加了一点自己的创新，味道非常棒！大家可以试试在最后加一点鸡精提鲜。",
            "recipe_id": 1
        },
        {
            "user_id": 3,  # 李四
            "title": "宫保鸡丁太辣怎么办？",
            "content": "请问有什么方法可以减轻宫保鸡丁的辣味但又不影响整体风味？我家人不太能吃辣。",
            "recipe_id": 2
        },
        {
            "user_id": 2,  # 张三
            "title": "自制糖醋排骨的小技巧",
            "content": "分享一个让糖醋排骨色泽更亮丽的小技巧：在焖煮前加一点番茄酱，不仅色泽好看，味道也更丰富。",
            "recipe_id": 4
        }
    ]
    
    for post_data in posts_data:
        post = Post(
            user_id=post_data["user_id"],
            title=post_data["title"],
            content=post_data["content"],
            recipe_id=post_data["recipe_id"]
        )
        db.session.add(post)
    db.session.commit()
    
    # 添加评论
    posts = Post.query.all()
    for post in posts:
        comments_data = [
            {"user_id": 1, "content": "非常棒的分享，谢谢！"},
            {"user_id": 3 if post.user_id == 2 else 2, "content": "我也试过，效果确实不错。"}
        ]
        
        for comment_data in comments_data:
            comment = Comment(
                post_id=post.id,
                user_id=comment_data["user_id"],
                content=comment_data["content"]
            )
            db.session.add(comment)
    db.session.commit()
