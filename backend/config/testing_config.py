from pydantic_settings import SettingsConfigDict
from config.base_config import Settings

class TestingSettings(Settings):
    model_config = SettingsConfigDict(
        env_file='.env.test',
        extra='ignore'
    )