from flask_login import UserMixin
from datetime import datetime
import random

# 由于我们使用内存存储而非数据库，定义简单的数据结构和存储机制

# 用户模型
class User(UserMixin):
    def __init__(self, id, username, email, password, is_admin=False):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.is_admin = is_admin
        self.favorites = []  # 收藏的菜谱ID列表
        self.ratings = {}    # 评分字典 {菜谱ID: 评分}
        self.preferences = []  # 用户口味偏好
        self.created_at = datetime.now()

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'favorites': self.favorites,
            'ratings': self.ratings,
            'preferences': self.preferences,
            'created_at': self.created_at
        }
        
    @staticmethod
    def query(user_id=None):
        class UserQuery:
            @staticmethod
            def get(user_id):
                for user in users_db:
                    if user.id == user_id:
                        return user
                return None
                
            @staticmethod
            def filter_by(username=None, email=None):
                class UserFilter:
                    def __init__(self, filtered_users):
                        self.filtered_users = filtered_users
                        
                    def first(self):
                        return self.filtered_users[0] if self.filtered_users else None
                
                filtered = []
                for user in users_db:
                    if username and user.username == username:
                        filtered.append(user)
                    elif email and user.email == email:
                        filtered.append(user)
                
                return UserFilter(filtered)
                
            @staticmethod
            def all():
                return users_db
        
        return UserQuery

# 菜谱模型
class Recipe:
    def __init__(self, id, name, description, ingredients, steps, category, image_url, difficulty, prep_time, cook_time):
        self.id = id
        self.name = name
        self.description = description
        self.ingredients = ingredients
        self.steps = steps
        self.category = category
        self.image_url = image_url
        self.difficulty = difficulty
        self.prep_time = prep_time
        self.cook_time = cook_time
        self.ratings = []  # 评分列表
        self.views = 0     # 浏览次数
        self.created_at = datetime.now()
        self.tags = []     # 标签列表

    def get_avg_rating(self):
        return sum(self.ratings) / len(self.ratings) if self.ratings else 0
        
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'ingredients': self.ingredients,
            'steps': self.steps,
            'category': self.category,
            'image_url': self.image_url,
            'difficulty': self.difficulty,
            'prep_time': self.prep_time,
            'cook_time': self.cook_time,
            'avg_rating': self.get_avg_rating(),
            'ratings_count': len(self.ratings),
            'views': self.views,
            'created_at': self.created_at,
            'tags': self.tags
        }
        
    @staticmethod
    def query():
        class RecipeQuery:
            @staticmethod
            def get(recipe_id):
                for recipe in recipes_db:
                    if recipe.id == recipe_id:
                        return recipe
                return None
                
            @staticmethod
            def filter_by(category=None):
                class RecipeFilter:
                    def __init__(self, filtered_recipes):
                        self.filtered_recipes = filtered_recipes
                        
                    def all(self):
                        return self.filtered_recipes
                
                filtered = []
                for recipe in recipes_db:
                    if category and recipe.category == category:
                        filtered.append(recipe)
                
                return RecipeFilter(filtered)
                
            @staticmethod
            def all():
                return recipes_db
        
        return RecipeQuery

# 社区帖子模型
class Post:
    def __init__(self, id, user_id, title, content, recipe_id=None):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.content = content
        self.recipe_id = recipe_id
        self.created_at = datetime.now()
        self.comments = []  # 评论列表
        self.likes = 0      # 点赞数

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'recipe_id': self.recipe_id,
            'created_at': self.created_at,
            'comments': [comment.to_dict() for comment in self.comments],
            'likes': self.likes
        }
        
    @staticmethod
    def query():
        class PostQuery:
            @staticmethod
            def get(post_id):
                for post in posts_db:
                    if post.id == post_id:
                        return post
                return None
                
            @staticmethod
            def filter_by(user_id=None, recipe_id=None):
                class PostFilter:
                    def __init__(self, filtered_posts):
                        self.filtered_posts = filtered_posts
                        
                    def all(self):
                        return self.filtered_posts
                
                filtered = []
                for post in posts_db:
                    if user_id and post.user_id == user_id:
                        filtered.append(post)
                    elif recipe_id and post.recipe_id == recipe_id:
                        filtered.append(post)
                
                return PostFilter(filtered)
                
            @staticmethod
            def all():
                return posts_db
        
        return PostQuery

# 评论模型
class Comment:
    def __init__(self, id, post_id, user_id, content):
        self.id = id
        self.post_id = post_id
        self.user_id = user_id
        self.content = content
        self.created_at = datetime.now()

    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'content': self.content,
            'created_at': self.created_at
        }

# 分类模型
class Category:
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description
        
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }
        
    @staticmethod
    def query():
        class CategoryQuery:
            @staticmethod
            def get(category_id):
                for category in categories_db:
                    if category.id == category_id:
                        return category
                return None
                
            @staticmethod
            def all():
                return categories_db
        
        return CategoryQuery

# 内存数据存储
users_db = []
recipes_db = []
posts_db = []
categories_db = []
next_user_id = 1
next_recipe_id = 1
next_post_id = 1
next_comment_id = 1
next_category_id = 1

# 初始化示例数据
def init_data():
    global next_user_id, next_recipe_id, next_post_id, next_category_id, next_comment_id
    
    # 如果已有数据，不再初始化
    if users_db or recipes_db or posts_db or categories_db:
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
        category = Category(next_category_id, cat["name"], cat["description"])
        categories_db.append(category)
        next_category_id += 1
    
    # 添加管理员账户
    from werkzeug.security import generate_password_hash
    admin = User(next_user_id, "admin", "admin@example.com", generate_password_hash("admin123"), True)
    users_db.append(admin)
    next_user_id += 1
    
    # 添加普通用户
    user1 = User(next_user_id, "张三", "zhangsan@example.com", generate_password_hash("password"), False)
    users_db.append(user1)
    next_user_id += 1
    
    user2 = User(next_user_id, "李四", "lisi@example.com", generate_password_hash("password"), False)
    users_db.append(user2)
    next_user_id += 1
    
    # 添加菜谱
    recipes = [
        {
            "name": "麻婆豆腐",
            "description": "麻婆豆腐是四川传统名菜，由豆腐、牛肉末、辣椒和花椒等烹制而成，麻辣鲜香。",
            "ingredients": ["豆腐 300g", "牛肉末 100g", "郫县豆瓣酱 2勺", "花椒粉 适量", "葱姜蒜 适量", "生抽 适量", "盐 适量"],
            "steps": ["豆腐切丁，用开水焯烫；", "锅中油热后，爆香葱姜蒜；", "加入牛肉末炒至变色；", "加入豆瓣酱炒出香味；", "加入适量水和豆腐，炖煮5分钟；", "调味后撒上花椒粉即可。"],
            "category": 1,  # 川菜
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
            "category": 1,  # 川菜
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
            "category": 2,  # 粤菜
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
            "category": 3,  # 鲁菜
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
            "category": 5,  # 浙菜
            "image_url": "https://images.unsplash.com/photo-1580476262798-bddd9f4b7369",
            "difficulty": "中等",
            "prep_time": 20,
            "cook_time": 25
        }
    ]
    
    for recipe_data in recipes:
        recipe = Recipe(
            next_recipe_id,
            recipe_data["name"],
            recipe_data["description"],
            recipe_data["ingredients"],
            recipe_data["steps"],
            recipe_data["category"],
            recipe_data["image_url"],
            recipe_data["difficulty"],
            recipe_data["prep_time"],
            recipe_data["cook_time"]
        )
        # 添加一些随机评分
        for _ in range(random.randint(5, 15)):
            recipe.ratings.append(random.randint(3, 5))
        recipe.views = random.randint(20, 100)
        recipes_db.append(recipe)
        next_recipe_id += 1
    
    # 添加社区帖子
    posts = [
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
    
    for post_data in posts:
        post = Post(
            next_post_id,
            post_data["user_id"],
            post_data["title"],
            post_data["content"],
            post_data["recipe_id"]
        )
        posts_db.append(post)
        next_post_id += 1
        
        # 添加评论
        comments = [
            {"user_id": 1, "content": "非常棒的分享，谢谢！"},
            {"user_id": 3 if post_data["user_id"] == 2 else 2, "content": "我也试过，效果确实不错。"}
        ]
        
        for comment_data in comments:
            comment = Comment(
                next_comment_id,
                post.id,
                comment_data["user_id"],
                comment_data["content"]
            )
            post.comments.append(comment)
            next_comment_id += 1
