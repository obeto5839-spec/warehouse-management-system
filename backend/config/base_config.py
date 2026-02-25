from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    ENV: str = "development"
    APP_NAME: str = "warehouse-management-system app"
    
    # API 安全认证
    API_TOKEN: str = "warehouse-secret-token"
    API_TOKEN_NAME: str = "x-token"

    # 日志管理配置
    LOG_LEVEL: int = 20
    LOG_DIR: str = os.path.join(os.getcwd(), "logs")

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding="utf-8",
        extra='ignore'
    )

settings = Settings()
