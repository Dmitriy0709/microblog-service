from __future__ import annotations
import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Абсолютный путь к backend/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # backend/migrations/
APP_DIR = os.path.join(BASE_DIR, "app")
sys.path.append(os.path.dirname(BASE_DIR))  # добавляем backend/

# теперь импортируем строго наш backend/app
import app.models as models
from app.database import engine

# Метаданные для автогенерации миграций
target_metadata = models.Base.metadata

# Конфигурация Alembic
config = context.config
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL", "sqlite:///./dev.db"))

# Логирование
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
