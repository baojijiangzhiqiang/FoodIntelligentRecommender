import os
import logging
from flask import Flask
from flask_login import LoginManager

# 配置日志
logging.basicConfig(level=logging.DEBUG)

# 创建Flask应用
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# 初始化登录管理
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录以访问此页面'

# 注册蓝图
from routes.auth import auth_bp
from routes.recipes import recipes_bp
from routes.users import users_bp
from routes.community import community_bp
from routes.admin import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(recipes_bp)
app.register_blueprint(users_bp)
app.register_blueprint(community_bp)
app.register_blueprint(admin_bp)

# 导入模型，确保在启动时加载
import models

# 用户加载函数
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# 首页路由
@app.route('/')
def index():
    from flask import render_template
    from services.recommendation_service import get_recommended_recipes
    from services.recipe_service import get_popular_recipes, get_latest_recipes
    
    recommended = get_recommended_recipes()
    popular = get_popular_recipes()
    latest = get_latest_recipes()
    
    return render_template('index.html', 
                        recommended=recommended,
                        popular=popular,
                        latest=latest)

# 初始化数据
with app.app_context():
    from models import init_data
    init_data()
