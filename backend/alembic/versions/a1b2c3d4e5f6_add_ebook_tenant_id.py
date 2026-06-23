"""Add tenant_id to ebooks for per-tenant plan limits."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "f08c017d5249"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "ebooks",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index(op.f("ix_ebooks_tenant_id"), "ebooks", ["tenant_id"], unique=False)
    op.create_foreign_key(
        "fk_ebooks_tenant_id_tenants",
        "ebooks",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("fk_ebooks_tenant_id_tenants", "ebooks", type_="foreignkey")
    op.drop_index(op.f("ix_ebooks_tenant_id"), table_name="ebooks")
    op.drop_column("ebooks", "tenant_id")
