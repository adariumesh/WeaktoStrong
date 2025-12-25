"""Add AI conversation and token tracking tables

Revision ID: 002
Revises: 001
Create Date: 2024-12-21 13:45:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create conversations table
    op.create_table(
        "conversations",
        sa.Column(
            "id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("challenge_id", sa.UUID(), nullable=True),
        sa.Column("title", sa.VARCHAR(length=200), nullable=False),
        sa.Column("model_tier", sa.VARCHAR(length=20), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "model_tier IN ('local', 'haiku', 'sonnet')", name="valid_model_tier"
        ),
    )

    # Create conversation_messages table
    op.create_table(
        "conversation_messages",
        sa.Column(
            "id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("conversation_id", sa.UUID(), nullable=False),
        sa.Column("role", sa.VARCHAR(length=20), nullable=False),
        sa.Column("content", sa.TEXT(), nullable=False),
        sa.Column("tokens_used", sa.INTEGER(), nullable=False, server_default="0"),
        sa.Column("model_used", sa.VARCHAR(length=50), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"], ["conversations.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "role IN ('user', 'assistant', 'system')", name="valid_message_role"
        ),
    )

    # Create token_usage table
    op.create_table(
        "token_usage",
        sa.Column(
            "id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("date", sa.DATE(), nullable=False),
        sa.Column("model", sa.VARCHAR(length=20), nullable=False),
        sa.Column("tokens_used", sa.INTEGER(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "date", "model", name="unique_user_date_model"),
    )

    # Create indexes for better query performance
    op.create_index("ix_conversations_user_id", "conversations", ["user_id"])
    op.create_index("ix_conversations_challenge_id", "conversations", ["challenge_id"])
    op.create_index("ix_conversations_created_at", "conversations", ["created_at"])

    op.create_index(
        "ix_conversation_messages_conversation_id",
        "conversation_messages",
        ["conversation_id"],
    )
    op.create_index(
        "ix_conversation_messages_created_at", "conversation_messages", ["created_at"]
    )

    op.create_index("ix_token_usage_user_id", "token_usage", ["user_id"])
    op.create_index("ix_token_usage_date", "token_usage", ["date"])
    op.create_index("ix_token_usage_model", "token_usage", ["model"])


def downgrade() -> None:
    # Drop indexes
    op.drop_index("ix_token_usage_model")
    op.drop_index("ix_token_usage_date")
    op.drop_index("ix_token_usage_user_id")

    op.drop_index("ix_conversation_messages_created_at")
    op.drop_index("ix_conversation_messages_conversation_id")

    op.drop_index("ix_conversations_created_at")
    op.drop_index("ix_conversations_challenge_id")
    op.drop_index("ix_conversations_user_id")

    # Drop tables
    op.drop_table("token_usage")
    op.drop_table("conversation_messages")
    op.drop_table("conversations")
