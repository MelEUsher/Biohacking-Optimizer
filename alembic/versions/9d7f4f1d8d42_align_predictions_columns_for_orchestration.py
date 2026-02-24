"""align predictions columns for orchestration

Revision ID: 9d7f4f1d8d42
Revises: 7a2d5ab747e5
Create Date: 2026-02-24 19:45:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "9d7f4f1d8d42"
down_revision: Union[str, Sequence[str], None] = "7a2d5ab747e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("predictions", "daily_entry_id", new_column_name="entry_id")
    op.alter_column("predictions", "prediction_score", new_column_name="prediction")
    op.alter_column("predictions", "recommendations", new_column_name="recommendation")


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column("predictions", "recommendation", new_column_name="recommendations")
    op.alter_column("predictions", "prediction", new_column_name="prediction_score")
    op.alter_column("predictions", "entry_id", new_column_name="daily_entry_id")
