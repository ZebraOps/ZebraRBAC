<div align="center">
  <h1>Zebra-RBAC</h1>
  <span><a href="./README.md">Chinese</a> | English</span>
</div>

---

## 📖 Project Introduction

**Zebra-RBAC** is a versatile permission management microservice designed for multi-application scenarios. It provides comprehensive user, role, permission, and group management capabilities with flexible APIs, well-structured data models, and built-in JWT authentication mechanisms. Seamlessly integrate it into your Python/FastAPI projects.

> Project Repository: [https://github.com/ZebraOps/ZebraRBAC](https://github.com/ZebraOps/ZebraRBAC)

---

## ✨ Core Features

- **User/Role/Permission Grouping** - Support complex permission organization structures across multiple systems and departments
- **RESTful API** - Unified and easy-to-use API standards with automatic documentation
- **High Extensibility** - Designed on FastAPI for easy secondary development and integration
- **Secure Authentication** - Support JWT login authentication and permission validation
- **Database Migration** - Built-in Alembic migration scripts with multi-environment adaptation
- **Auto Documentation** - Swagger/ReDoc automatic generation for quick integration

---

## 🛠️ Tech Stack

- **Backend Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Data Validation**: Pydantic
- **Database Migration**: Alembic
- **Authentication**: JWT
- **Runtime Environment**: Python 3.8+
- **Development Server**: Uvicorn

---

## ⚡ Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/ZebraOps/ZebraRBAC.git
cd ZebraRBAC
```

### 2. Install Dependencies

We recommend creating a virtual environment (optional)

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate.bat # Windows

pip install -r requirements.txt
```

### 3. Environment Configuration

- Copy `.env.example` to `.env` and fill in the necessary information
- Generate a 32-bit random string for JWT secret key:
  ```bash
  cat /dev/urandom | head -c 32 | base64
  ```

### 4. Initialize Database

```bash
alembic upgrade head
python init_db.py
python create_admin.py
python create_initial_data.py
```

### 5. Start the Service

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🔗 API Documentation

After starting the service, access the following URLs to view API documentation:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🌳 Directory Structure

```
ZebraRBAC/
├── app/
│   ├── api/         # API route definitions
│   ├── core/        # Core project configuration
│   ├── crud/        # Database CRUD operations
│   ├── db/          # Database configuration
│   ├── models/      # SQLAlchemy data models
│   ├── schemas/     # Pydantic models
│   └── utils/       # Utility functions
├── migrations/      # Database migration files
├── alembic.ini      # Alembic configuration file
├── requirements.txt # Dependency list
├── .env.example     # Environment variable template
├── init_db.py       # Database initialization script
├── create_admin.py  # Admin creation script
├── create_initial_data.py # Initial data script
└── README.md        # Project documentation
```

---

## 📋 Functional Modules

### User Management
- User creation, update, deletion
- User status management
- User grouping

### Role Management
- Role creation, update, deletion
- Role-permission binding
- Role inheritance

### Permission Management
- Feature point permissions
- Menu permissions
- Component permissions
- Interface permissions
- Custom permission combinations

### Group Management
- Multi-system permission isolation
- Cross-department permission integration
- Flexible permission organization configuration

---

## 📝 Usage Examples

### 1. Create a User

```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "email": "john@example.com", "password": "secure_password"}'
```

### 2. Assign Role

```bash
curl -X POST http://localhost:8000/api/users/1/roles \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"role_id": 1}'
```

### 3. Query Permissions

```bash
curl http://localhost:8000/api/users/1/permissions \
  -H "Authorization: Bearer <your_jwt_token>"
```

For detailed API documentation, visit the `/docs` endpoint.

---

## 📌 Important Notes

- Requires Python 3.8 or higher
- Uses MySQL database by default; modify the connection string for other databases
- In production, update sensitive information in `.env` file (keys, database passwords, etc.)
- Permission validation and gateway interception require project-specific configuration

---

## ☑️ TODO List

- [ ] Optimize permission validation middleware for fine-grained rule support
- [ ] Support OAuth2/SAML and other third-party authentication methods
- [ ] Permission operation audit logging functionality
- [ ] Comprehensive unit test coverage
- [ ] Performance optimization and caching mechanisms
- [ ] CI/CD pipeline integration
- [ ] Provide Chinese documentation

---

## 🤝 Contributing Guide

We welcome contributions in any form! If you have suggestions or find bugs, please submit an Issue.
To contribute code improvements:

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Submit a Pull Request

---


## 💬 Contact & Support

- **Report Issues**: Please use GitHub Issues
- **Join Discussion**: Participate in GitHub Discussions
- **Submit Feedback**: We welcome Pull Requests of any kind

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
