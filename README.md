# Zebra-RBAC

---

## 📖 简介
[`Zebra-RBAC`](https://github.com/numachen/zebra-ui) 是一个基于 FastAPI 实现的RBAC权限管理服务。该项目提供了完整的用户、角色、权限的统一分组管理解决方案，支持多系统的权限管理需求。系统采用SQLAlchemy进行数据建模，使用Pydantic进行数据验证，实现了RESTful API接口，提供JWT认证和权限控制功能。项目包含用户管理、角色管理、分组管理和权限管理（功能点、菜单、组件、接口权限等）模块，并自动生成API文档。

## ✨ 功能特性
- 数据模型：使用SQLAlchemy定义所有必要的模型
- Pydantic模型：用于请求和响应的数据验证
- CRUD操作：封装所有数据库操作
- API端点：实现RESTful API接口
- 认证授权：JWT认证和权限控制
- 用户管理：创建、更新、删除用户
- 角色管理：创建、更新、删除角色
- 分组管理：支持多系统RBAC统一管理
- 权限管理：包括功能点、菜单、组件、接口权限
- 自动API文档：基于FastAPI的自动API文档生成

## 🛠️ 技术栈
- 后端框架：FastAPI
- ORM框架：SQLAlchemy
- 数据验证：Pydantic
- 数据库迁移：Alembic
- 认证方式：JWT
- 编程语言：Python
- 服务器：Uvicorn

## 🚀 安装

1. 克隆代码库
```bash
  git clone [repository-url]
  cd zebra-rbac
```

2. 创建虚拟环境并安装依赖
```bash
  python -m venv venv
  source venv/bin/activate  # Linux/Mac
  # or
  venv\Scripts\activate.bat  # Windows
  pip install -r requirements.txt
```

3. 配置环境变量
复制 `.env.example` 到 `.env` 并填写必要的配置信息：
生成32位的随机字符串作为JWT密钥： ` cat /dev/urandom | head -c 32 | base64`
```bash
  cp .env.example .env
  # 然后编辑 .env 文件
```

4. 初始化数据库
```bash
  alembic upgrade head
```

5. 运行服务
```bash
  # 初始化数据库
  python init_db.py
  python create_admin.py
  python create_initial_data.py
  uvicorn app.main:app --reload --host 192.168.102.43 --port 8000
```

## 🔗 API文档

启动服务后，访问以下URL查看API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🌳 目录结构
```yaml
zebra-rbac/
├── app/
│ ├── api/ # API路由
│ ├── core/ # 核心配置
│ ├── crud/ # CRUD操作
│ ├── db/ # 数据库配置
│ ├── models/ # SQLAlchemy模型
│ ├── schemas/ # Pydantic模型
│ └── utils/ # 工具函数
├── migrations # 数据库迁移
├── alembic.ini # 数据库迁移
├── requirements.txt # 项目依赖
└── .env # 环境变量
```

## ✅ 待办
- function没有对用户进行校验，判断用户是否有调用接口的权限，这块需要在网关层面进行拦截判断；