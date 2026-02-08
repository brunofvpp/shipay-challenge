"""
Revision ID: 002
Revises: 001
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None

DEFAULT_ROLES = ("admin", "manager", "viewer")

roles_table = sa.table("roles", sa.column("description", sa.String()))


def upgrade() -> None:
    conn = op.get_bind()
    existing = {row.description for row in conn.execute(sa.select(roles_table.c.description))}
    to_insert = [{"description": role} for role in DEFAULT_ROLES if role not in existing]
    if to_insert:
        op.bulk_insert(roles_table, to_insert)


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.delete(roles_table).where(roles_table.c.description.in_(DEFAULT_ROLES)))
