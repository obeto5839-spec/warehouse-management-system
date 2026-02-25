from pydantic_settings import SettingsConfigDict
from config.base_config import Settings
class DevelopmentSettings(Settings):
    model_config = SettingsConfigDict(
        env_file='.env.dev',
        extra='ignore'
    )
    DEBUG: bool = True
    DATABASE_URL: str = "mysql+pymysql://root:root@localhost:3307/warehouse_system"
