
"""Initial marketplace MVP schema.

Revision ID: 0001_initial
Revises:
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    user_role = sa.Enum(
        "customer",
        "seller",
        "admin",
        "support",
        name="userrole",
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("full_name", sa.String(120), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("email"),
    )

    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(180), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("sku", sa.String(80), nullable=False),
        sa.Column("price_paise", sa.Integer(), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False),
        sa.Column("image_url", sa.String(500), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "price_paise >= 0",
            name="ck_products_price_nonnegative",
        ),
        sa.CheckConstraint(
            "stock >= 0",
            name="ck_products_stock_nonnegative",
        ),
        sa.UniqueConstraint("sku"),
    )

    op.create_index("ix_products_name", "products", ["name"])
    op.create_index("ix_products_category", "products", ["category"])
    op.create_index("ix_products_sku", "products", ["sku"])

    op.create_table(
        "cart_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            sa.Integer(),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "quantity > 0",
            name="ck_cart_quantity_positive",
        ),
        sa.UniqueConstraint(
            "user_id",
            "product_id",
            name="uq_cart_user_product",
        ),
    )

    op.create_index("ix_cart_items_user_id", "cart_items", ["user_id"])

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "customer_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("payment_method", sa.String(24), nullable=False),
        sa.Column("payment_status", sa.String(24), nullable=False),
        sa.Column("total_paise", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "total_paise >= 0",
            name="ck_orders_total_nonnegative",
        ),
    )

    op.create_index("ix_orders_customer_id", "orders", ["customer_id"])

    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey(
            "orders.id",
            ondelete="CASCADE",
        ), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey(
            "products.id",
            ondelete="SET NULL",
        )),
        sa.Column("product_name", sa.String(180), nullable=False),
        sa.Column("sku", sa.String(80), nullable=False),
        sa.Column("unit_price_paise", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "unit_price_paise >= 0",
            name="ck_order_items_price_nonnegative",
        ),
        sa.CheckConstraint(
            "quantity > 0",
            name="ck_order_items_quantity_positive",
        ),
    )

    op.create_index(
        "ix_order_items_order_id",
        "order_items",
        ["order_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_order_items_order_id", table_name="order_items")
    op.drop_table("order_items")

    op.drop_index("ix_orders_customer_id", table_name="orders")
    op.drop_table("orders")

    op.drop_index("ix_cart_items_user_id", table_name="cart_items")
    op.drop_table("cart_items")

    op.drop_index("ix_products_sku", table_name="products")
    op.drop_index("ix_products_category", table_name="products")
    op.drop_index("ix_products_name", table_name="products")
    op.drop_table("products")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    # The userrole enum is dropped when its owning table is dropped.
