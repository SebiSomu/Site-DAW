import logging
from logging.config import fileConfig

from alembic import context
from flask import current_app

config = context.config
fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")

target_db = current_app.extensions["migrate"].db


def get_engine():
    return target_db.engine


def get_engine_url() -> str:
    return get_engine().url.render_as_string(hide_password=False).replace("%", "%%")


config.set_main_option("sqlalchemy.url", get_engine_url())


def get_metadata():
    return target_db.metadata


def skip_empty_autogenerate(context, revision, directives) -> None:
    if getattr(config.cmd_opts, "autogenerate", False) and directives[0].upgrade_ops.is_empty():
        directives[:] = []
        logger.info("No changes in schema detected.")


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=get_metadata(),
        literal_binds=True,
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configure_args = current_app.extensions["migrate"].configure_args
    configure_args.setdefault("process_revision_directives", skip_empty_autogenerate)
    with get_engine().connect() as connection:
        context.configure(connection=connection, target_metadata=get_metadata(), **configure_args)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
