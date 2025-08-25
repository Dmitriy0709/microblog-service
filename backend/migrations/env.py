from logging.config import fileConfig
from alembic import context

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


config = context.config
fileConfig(config.config_file_name)

target_metadata = models.Base.metadata


def run_migrations_offline():
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
