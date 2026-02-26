from app.db.init_db import init_db

if __name__ == "__main__":
    print("正在创建数据库表...")
    init_db()
    print("数据库表创建成功!")
