"""Add subscription and payment models

Revision ID: add_subscription_payment_models
Revises: last_revision
Create Date: 2024-12-22 08:47:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers
revision = "add_subscription_payment_models"
down_revision = "c5a2f1e8d3b4"  # Update with actual last revision
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create subscription status enum
    subscription_status_enum = sa.Enum(
        "active",
        "past_due",
        "unpaid",
        "canceled",
        "incomplete",
        "incomplete_expired",
        "trialing",
        name="subscriptionstatus",
        create_type=True,
    )
    subscription_status_enum.create(op.get_bind())

    # Create price interval enum
    price_interval_enum = sa.Enum(
        "month", "year", name="priceinterval", create_type=True
    )
    price_interval_enum.create(op.get_bind())

    # Create subscriptions table
    op.create_table(
        "subscriptions",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            nullable=False,
            default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("stripe_customer_id", sa.String(length=255), nullable=False),
        sa.Column("stripe_subscription_id", sa.String(length=255), nullable=False),
        sa.Column("stripe_price_id", sa.String(length=255), nullable=False),
        sa.Column("status", subscription_status_enum, nullable=False, default="active"),
        sa.Column("tier", sa.String(length=50), nullable=False),
        sa.Column("current_period_start", sa.DateTime(), nullable=False),
        sa.Column("current_period_end", sa.DateTime(), nullable=False),
        sa.Column("interval", price_interval_enum, nullable=False, default="month"),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False, default="usd"),
        sa.Column("cancel_at_period_end", sa.Boolean(), nullable=True, default=False),
        sa.Column("canceled_at", sa.DateTime(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True, default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True, default=sa.text("now()")),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stripe_subscription_id"),
    )
    op.create_index(
        op.f("ix_subscriptions_user_id"), "subscriptions", ["user_id"], unique=False
    )
    op.create_index(
        op.f("ix_subscriptions_stripe_customer_id"),
        "subscriptions",
        ["stripe_customer_id"],
        unique=False,
    )

    # Create payments table
    op.create_table(
        "payments",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            nullable=False,
            default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("subscription_id", UUID(as_uuid=True), nullable=True),
        sa.Column("stripe_payment_intent_id", sa.String(length=255), nullable=False),
        sa.Column("stripe_invoice_id", sa.String(length=255), nullable=True),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False, default="usd"),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("payment_method", sa.String(length=100), nullable=True),
        sa.Column("last4", sa.String(length=4), nullable=True),
        sa.Column("processed_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True, default=sa.text("now()")),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(
            ["subscription_id"],
            ["subscriptions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stripe_payment_intent_id"),
    )
    op.create_index(op.f("ix_payments_user_id"), "payments", ["user_id"], unique=False)
    op.create_index(
        op.f("ix_payments_subscription_id"),
        "payments",
        ["subscription_id"],
        unique=False,
    )

    # Create invoice_events table
    op.create_table(
        "invoice_events",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            nullable=False,
            default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("stripe_event_id", sa.String(length=255), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("processed", sa.Boolean(), nullable=True, default=False),
        sa.Column("error_message", sa.String(length=1000), nullable=True),
        sa.Column("event_data", sa.JSON(), nullable=False),
        sa.Column("stripe_created", sa.DateTime(), nullable=False),
        sa.Column("processed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True, default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stripe_event_id"),
    )
    op.create_index(
        op.f("ix_invoice_events_event_type"),
        "invoice_events",
        ["event_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_invoice_events_processed"),
        "invoice_events",
        ["processed"],
        unique=False,
    )


def downgrade() -> None:
    # Drop tables
    op.drop_table("invoice_events")
    op.drop_table("payments")
    op.drop_table("subscriptions")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS subscriptionstatus")
    op.execute("DROP TYPE IF EXISTS priceinterval")
