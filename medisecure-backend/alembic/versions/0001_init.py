from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "patients",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("firstname", sa.String, nullable=False),
        sa.Column("lastname", sa.String, nullable=False),
        sa.Column("birthdate", sa.Date, nullable=True),
    )

def downgrade():
    op.drop_table("patients")
