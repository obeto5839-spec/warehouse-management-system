
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from utils.log_manage import init_logger
from router.router import api_router
from config import settings
from security import verify_token
from database.database import engine
from database.models import Base

# 日志初始化
init_logger()

app = FastAPI(title=settings.APP_NAME)

@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境请改为具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由 (添加全局 Token 验证)
# 注意：这会保护所有子路由。如果有些接口（如登录、健康检查）不需要验证，可以分开注册
app.include_router(api_router, dependencies=[Depends(verify_token)])


@app.get("/")
async def root():
    env = settings.ENV
    return {"message": "Hello warehouse-management-system Applications!", "env": env}