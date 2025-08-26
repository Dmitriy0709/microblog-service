# backend/migrations/env.py
from __future__ import annotations

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# this is the Alembic Config object
config = context.config

# setup logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# override sqlalchemy.url with env var DATABASE_URL when present (CI sets it)
database_url = os.getenv("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

# make backend package importable (project root -> backend)
this_dir = os.path.dirname(__file__)  # backend/migrations
backend_dir = os.path.dirname(this_dir)  # backend
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.models import Base  # noqa: E402

target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
