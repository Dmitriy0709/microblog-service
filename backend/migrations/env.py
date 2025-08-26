import sys
import os

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Добавляем путь к backend для импорта app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.models import Base  # noqa: E402

config = context.config

# Читаем конфигурацию логгирования из alembic.ini
fileConfig(config.config_file_name)

# Получаем строку подключения к базе из переменной окружения или alembic.ini
database_url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
