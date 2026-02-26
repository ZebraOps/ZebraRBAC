from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash


def create_admin():
    db = SessionLocal()
    try:
        # 检查管理员是否已存在
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            print("管理员用户已存在!")
            return

        # 创建管理员用户
        admin = User(
            username="admin",
            nickname="系统管理员",
            email="admin@example.com",
            tel="13800000000",
            password=get_password_hash("admin"),
            superuser="0",  # 0表示超级用户
            status="0",  # 0表示正常状态
        )
        db.add(admin)
        db.commit()
        print("管理员用户创建成功!")
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
