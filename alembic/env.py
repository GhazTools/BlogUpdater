"""
file_name = env.py
Created On: 2024/07/09
Lasted Updated: 2024/07/09
Description: _FILL OUT HERE_
Edit Log:
2024/07/09
    - Created file
"""

# STANDARD LIBRARY IMPORTS
from logging.config import fileConfig

# THIRD PARTY LIBRARY IMPORTS
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# LOCAL LIBRARY IMPORTS
from src.database.database import BASE
from src.database.models.blog_post import BlogPost
from src.database.models.image import Image

# Have to import all models so BASE picks up on it
from src.utils.environment import Environment, EnvironmentVariableKeys


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.


def get_db_url() -> str:
    """
    A function to retrieve database url in a form that alembic can read
    """

    url: str = Environment.get_environment_variable(
        EnvironmentVariableKeys.DATABASE_URL
    )
    modified_url: str = url.replace("%", "%%")

    return modified_url


config = context.config
config.set_main_option(
    "sqlalchemy.url",
    get_db_url(),
)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = BASE.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
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
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
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
