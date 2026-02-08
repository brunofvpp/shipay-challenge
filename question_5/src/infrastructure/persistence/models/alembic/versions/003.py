"""
Revision ID: 003
Revises: 002
"""

import sqlalchemy as sa
from alembic import op

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None

DEFAULT_CLAIMS = (
    "user:create",
    "user:read",
    "user:update",
    "user:delete",
)

claims_table = sa.table(
    "claims",
    sa.column("description", sa.String()),
)


def upgrade() -> None:
    conn = op.get_bind()
    existing = {row.description for row in conn.execute(sa.select(claims_table.c.description))}
    to_insert = [{"description": claim, "active": True} for claim in DEFAULT_CLAIMS if claim not in existing]
    if to_insert:
        op.bulk_insert(claims_table, to_insert)


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.delete(claims_table).where(claims_table.c.description.in_(DEFAULT_CLAIMS)))
