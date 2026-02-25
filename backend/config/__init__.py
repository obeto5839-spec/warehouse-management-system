import os
from config.base_config import Settings
from config.development_config import DevelopmentSettings
from config.testing_config import TestingSettings
from config.production_config import ProductionSettings


def get_settings() -> Settings:
    env = os.getenv("ENV", "development").lower()
    config_cls = {
        "development": DevelopmentSettings,
        "testing": TestingSettings,
        "production": ProductionSettings
    }.get(env, DevelopmentSettings)

    return config_cls()


settings = get_settings()