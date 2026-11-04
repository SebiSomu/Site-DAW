from alembic import op

revision = "a1f3c9d27b10"
down_revision = "7b1d76dc0673"
branch_labels = None
depends_on = None

RENAMED_COLUMNS = (
    ("products", "price_bani", "price_cents"),
    ("order_items", "unit_price_bani", "unit_price_cents"),
    ("payments", "amount_bani", "amount_cents"),
)


def upgrade():
    for table, old_name, new_name in RENAMED_COLUMNS:
        op.execute(f"ALTER TABLE {table} RENAME COLUMN {old_name} TO {new_name}")


def downgrade():
    for table, old_name, new_name in RENAMED_COLUMNS:
        op.execute(f"ALTER TABLE {table} RENAME COLUMN {new_name} TO {old_name}")
