from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "b7856a5f0b01"
down_revision = "a1b2c3d4e5f7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Берем существующий enum без попытки создать его заново
    language_enum = postgresql.ENUM("en", "ru", "tk", name="language_enum", create_type=False)

    op.create_table(
        "career_i18n",
        sa.Column("career_id", sa.UUID(), nullable=False),
        sa.Column("locale", language_enum, nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["career_id"], ["career.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("career_id", "locale"),
    )
    op.create_index("ix_career_i18n_locale", "career_i18n", ["locale"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_career_i18n_locale", table_name="career_i18n")
    op.drop_table("career_i18n")