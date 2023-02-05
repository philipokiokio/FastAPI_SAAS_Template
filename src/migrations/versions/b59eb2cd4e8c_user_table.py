"""User Table

Revision ID: b59eb2cd4e8c
Revises: 
Create Date: 2023-02-05 13:56:20.314855

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b59eb2cd4e8c"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer),
        sa.Column("first_name", sa.String(), nullable=False),
        sa.Column("last_name", sa.String(), nullable=False),
        sa.Column("email", sa.String, unique=True, nullable=False),
        sa.Column("password", sa.String, nullable=False),
        sa.Column("is_verified", sa.Boolean, nullable=False),
        sa.Column("is_premium", sa.Boolean, nullable=False),
        sa.Column(
            "date_created", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")
        ),
        sa.Column(
            "date_updated", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user_refresh_token",
        sa.Column("id", sa.Integer),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("token", sa.String, nullable=False),
        sa.Column(
            "date_created", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")
        ),
        sa.Column(
            "date_updated", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    pass


def downgrade() -> None:
    op.drop_constraint("user_refresh_token_user_id_fkey", "user_refresh_token")
    op.drop_table("user_refresh_token")
    op.drop_table("users")
    pass
