from __future__ import annotations

import os
import sys
from logging.config import fileConfig
from sqlalchemy import create_engine
from alembic import context

# -----------------------------
# Пути
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # backend/migrations/
BACKEND_DIR = os.path.dirname(BASE_DIR)                # backend/
sys.path.append(BACKEND_DIR)

# -----------------------------
# Импорты проекта
# -----------------------------
import app.models as models  # noqa
from app.database import engine as app_engine  # твой движок

# -----------------------------
# Alembic конфиг
# -----------------------------
config = context.config

# URL берём из переменной окружения DATABASE_URL или дефолт
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Логирование
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метаданные из моделей
target_metadata = models.Base.metadata


# -----------------------------
# Режимы: offline / online
# -----------------------------
def run_migrations_offline() -> None:
    """Запуск миграций в offline режиме (генерим SQL)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Запуск миграций в online режиме (подключение к БД)."""
    connectable = create_engine(DATABASE_URL)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
