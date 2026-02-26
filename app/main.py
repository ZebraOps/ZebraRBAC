import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings

from app.middleware.request_timer import request_timer_middleware
from app.core.init_handler import init_system
from app.schemas import organization, position, user_organization

# 重建所有涉及循环引用的模型
organization.OrganizationTree.model_rebuild()
user_organization.UserOrganization.model_rebuild()

# 创建日志记录器
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for application startup and shutdown
    """
    # Startup
    init_system()
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filename="logs/app.log",
        filemode="a"
    )

    # 添加控制台日志处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    logging.getLogger().addHandler(console_handler)

    logger.info("Application started")
    yield
    # Shutdown
    logger.info("Application shutting down")
    # Add cleanup code here if needed


app = FastAPI(
    title="Zebra RBAC",
    description="RBAC管理系统API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加请求计时中间件
app.middleware("http")(request_timer_middleware)

# 添加路由
app.include_router(api_router, prefix="/api")


@app.get("/health")
async def root():
    return {"message": "Zebra RBAC is running."}
