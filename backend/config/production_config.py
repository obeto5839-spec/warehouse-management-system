from pydantic_settings import SettingsConfigDict
from config.base_config import Settings

class ProductionSettings(Settings):
    model_config = SettingsConfigDict(
        env_file='.env.prod',
        extra='ignore'
    )
    DEBUG: bool = False
