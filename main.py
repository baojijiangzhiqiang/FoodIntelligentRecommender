import os
import sys

# 确保环境变量已设置
if not os.environ.get("DATABASE_URL"):
    db_user = os.environ.get("PGUSER", "postgres")
    db_password = os.environ.get("PGPASSWORD", "postgres")
    db_host = os.environ.get("PGHOST", "localhost")
    db_port = os.environ.get("PGPORT", "5432")
    db_name = os.environ.get("PGDATABASE", "postgres")
    
    # 构建数据库URL
    os.environ["DATABASE_URL"] = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# 导入应用实例
from app import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
