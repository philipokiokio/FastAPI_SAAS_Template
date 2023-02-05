"""Organization Table

Revision ID: 80f9e1cc8879
Revises: b59eb2cd4e8c
Create Date: 2023-02-05 17:37:00.078276

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "80f9e1cc8879"
down_revision = "b59eb2cd4e8c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "organization",
        sa.Column("id", sa.Integer),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("revoke_link", sa.Boolean(), server_default=sa.text("false")),
        sa.Column(
            "date_created", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")
        ),
        sa.Column(
            "date_updated", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
    )

    op.create_table(
        "organization_member",
        sa.Column("id", sa.Integer),
        sa.Column("org_id", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column(
            "date_created", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")
        ),
        sa.Column(
            "date_updated", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["org_id"], ["organization.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["member_id"], ["users.id"], ondelete="CASCADE"),
    )
    pass


def downgrade() -> None:
    op.drop_constraint(
        "organization_member_member_id_fkey", table_name="organization_member"
    )
    op.drop_constraint(
        "organization_member_org_id_fkey", table_name="organization_member"
    )
    op.drop_table("organization")
    op.drop_table("organization_member")
    pass
