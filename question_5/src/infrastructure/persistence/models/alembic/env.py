import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

IGNORED_AUTOGEN_CONSTRAINTS = {"user_claims_un"}

BASE_DIR = Path(__file__).resolve().parents[5]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from src.infrastructure.config import get_settings  # noqa: E402
from src.infrastructure.persistence.database import Base  # noqa: E402
from src.infrastructure.persistence.models import claim, role, user, user_claim  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def numeric_revision_id(context, revision, directives):
    script = directives[0]
    versions_dir = Path(context.config.get_main_option("script_location")) / "versions"
    versions_dir.mkdir(parents=True, exist_ok=True)
    existing_numbers = sorted(int(f.name[:3]) for f in versions_dir.glob("*.py") if f.name[:3].isdigit())
    next_number = existing_numbers[-1] + 1 if existing_numbers else 1
    script.rev_id = f"{next_number:03d}"
    script.message = ""


def get_url() -> str:
    return get_settings().sync_database_url


def include_object(obj, name, type_, reflected, compare_to):
    if type_ == "constraint" and name in IGNORED_AUTOGEN_CONSTRAINTS:
        return False
    return True


def run_migrations_offline() -> None:
    url = get_url()

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
        process_revision_directives=numeric_revision_id,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable_config = config.get_section(config.config_ini_section) or {}
    connectable_config["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        connectable_config,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            process_revision_directives=numeric_revision_id,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
