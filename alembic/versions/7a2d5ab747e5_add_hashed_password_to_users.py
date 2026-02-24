"""add hashed_password to users

Revision ID: 7a2d5ab747e5
Revises: 015f90b1874c
Create Date: 2026-02-24 01:29:00.441656

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "7a2d5ab747e5"
down_revision: Union[str, Sequence[str], None] = "015f90b1874c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    placeholder_bcrypt_hash = (
        "$2b$12$wnAVezdbdvFtblDXMdyrZ.I8Q3lcQ0oYZmwcKkxZRKu54kRF/QwDe"
    )

    op.add_column(
        "users", sa.Column("hashed_password", sa.String(length=255), nullable=True)
    )

    users_table = sa.table(
        "users",
        sa.column("hashed_password", sa.String(length=255)),
    )
    op.execute(
        users_table.update()
        .where(users_table.c.hashed_password.is_(None))
        .values(hashed_password=placeholder_bcrypt_hash)
    )

    op.alter_column(
        "users", "hashed_password", existing_type=sa.String(length=255), nullable=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "hashed_password")
