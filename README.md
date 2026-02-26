<div align="center">
  <h1>Zebra-RBAC</h1>
  <span>中文 | <a href="./README.en.md">English</a></span>
</div>

---

## 📖 项目简介

**Zebra-RBAC** 是一个适用于多应用场景的权限管理微服务，支持通用的用户、角色、权限、分组管理。具备灵活的接口、自带完善的数据模型，以及内置的 JWT 鉴权机制，可无缝集成到 Python/FastAPI 项目中。

> 项目主页：[https://github.com/ZebraOps/ZebraRBAC](https://github.com/ZebraOps/ZebraRBAC)

---

## ✨ 核心特性

- **用户/角色/权限分组** - 支持多系统、跨部门复杂权限组织结构
- **RESTful API** - 统一易用 API 规范，自动化文档
- **高扩展性** - 基于 FastAPI 设计，便于二次开发和集成
- **安全认证** - 支持 JWT 登录认证和权限校验
- **数据库迁移** - 内置 Alembic 迁移脚本及多环境适配
- **自动文档** - Swagger/ReDoc 自动生成，快速集成

---

## 🛠️ 技术栈

- **后端框架**：FastAPI
- **ORM**：SQLAlchemy
- **数据校验**：Pydantic
- **数据库迁移**：Alembic
- **认证方式**：JWT
- **运行环境**：Python 3.8+
- **开发服务器**：Uvicorn

---

## ⚡ 快速开始

### 1. 获取代码

```bash
git clone https://github.com/ZebraOps/ZebraRBAC.git
cd ZebraRBAC
```

### 2. 安装依赖

建议创建虚拟环境（可选）

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate.bat # Windows

pip install -r requirements.txt
```

### 3. 环境变量配置

- 复制 `.env.example` 为 `.env`，并根据实际需求填写信息
- 生成 32 位随机字符串用作 JWT 密钥：
  ```bash
  cat /dev/urandom | head -c 32 | base64
  ```

### 4. 初始化数据库

```bash
alembic upgrade head
python init_db.py
python create_admin.py
python create_initial_data.py
```

### 5. 启动服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🔗 API 文档

启动服务后，访问以下 URL 查看 API 文档：

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🌳 目录结构

```
ZebraRBAC/
├── app/
│   ├── api/         # API 路由定义
│   ├── core/        # 项目核心配置
│   ├── crud/        # 数据库 CRUD 操作
│   ├── db/          # 数据库配置
│   ├── models/      # SQLAlchemy 数据模型
│   ├── schemas/     # Pydantic 模型
│   └── utils/       # 工具函数
├── migrations/      # 数据库迁移文件
├── alembic.ini      # Alembic 配置文件
├── requirements.txt # 依赖清单
├── .env.example     # 环境变量模板
├── init_db.py       # 数据库初始化脚本
├── create_admin.py  # 管理员创建脚本
├── create_initial_data.py # 初始数据脚本
└── README.md        # 项目文档
```

---

## 📋 功能模块

### 用户管理
- 用户创建、更新、删除
- 用户状态管理
- 用户分组

### 角色管理
- 角色创建、更新、删除
- 角色绑定权限
- 角色继承

### 权限管理
- 功能点权限
- 菜单权限
- 组件权限
- 接口权限
- 自定义权限组合

### 分组管理
- 支持多系统权限隔离
- 跨部门权限整合
- 权限组织灵活配置

---

## 📝 使用示例

### 1. 创建用户

```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "email": "john@example.com", "password": "secure_password"}'
```

### 2. 分配角色

```bash
curl -X POST http://localhost:8000/api/users/1/roles \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"role_id": 1}'
```

### 3. 查询权限

```bash
curl http://localhost:8000/api/users/1/permissions \
  -H "Authorization: Bearer <your_jwt_token>"
```

详细的 API 文档请访问 `/docs` 端点。

---

## 📌 注意事项

- 需要 Python 3.8 及以上版本
- 默认使用 MySQL 数据库，其他数据库需要修改连接字符串
- 生产环境请修改 `.env` 文件中的敏感信息（密钥、数据库密码等）
- 权限校验与网关拦截需根据实际项目进行配置

---

## ☑️ 待办事项

- [ ] 权限校验中间件优化，支持更细粒度的规则配置
- [ ] 支持 OAuth2/SAML 等第三方认证方式
- [ ] 权限操作审计日志功能
- [ ] 完善单元测试覆盖率
- [ ] 性能优化与缓存机制
- [ ] 集成 CI/CD 流程
- [ ] 提供英文文档

---

## 🤝 贡献指南

欢迎任何形式的贡献！如果你有建议或发现 bug，请提交 Issue。  
如果你想提交代码改进，请：

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

---

## 📄 License

本项目采用 MIT 许可证，详见 [LICENSE](./LICENSE) 文件。

---

## 💬 联系方式

- **提交问题**：请使用 GitHub Issues
- **讨论建议**：欢迎在 GitHub Discussions 中参与交流
- **贡献反馈**：感谢任何形式的 Pull Request

---

## 🎯 项目目标

Zebra-RBAC 致力于提供一个易于集成、功能完整且高度可扩展的权限管理解决方案，帮助开发者快速构建安全、灵活的权限系统。

---

**Made with ❤️ by ZebraOps**
