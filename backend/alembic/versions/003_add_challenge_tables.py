"""Add challenge, submission, and progress tracking tables

Revision ID: 003
Revises: 002
Create Date: 2024-12-21 14:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create challenges table
    op.create_table(
        "challenges",
        sa.Column(
            "id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("slug", sa.VARCHAR(length=100), nullable=False),
        sa.Column("title", sa.VARCHAR(length=200), nullable=False),
        sa.Column("description", sa.TEXT(), nullable=False),
        sa.Column("track", sa.VARCHAR(length=20), nullable=False),
        sa.Column("difficulty", sa.VARCHAR(length=20), nullable=False),
        sa.Column("order_index", sa.INTEGER(), nullable=False),
        sa.Column("requirements", sa.JSON(), nullable=True),
        sa.Column("constraints", sa.JSON(), nullable=True),
        sa.Column("test_config", sa.JSON(), nullable=True),
        sa.Column("points", sa.INTEGER(), nullable=False, server_default="100"),
        sa.Column("estimated_time", sa.INTEGER(), nullable=True),
        sa.Column("starter_code", sa.TEXT(), nullable=True),
        sa.Column("solution_code", sa.TEXT(), nullable=True),
        sa.Column("hints", sa.JSON(), nullable=True),
        sa.Column("resources", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.BOOLEAN(), nullable=False, server_default="true"),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="unique_challenge_slug"),
        sa.CheckConstraint(
            "track IN ('web', 'data', 'cloud')", name="valid_challenge_track"
        ),
        sa.CheckConstraint(
            "difficulty IN ('beginner', 'intermediate', 'advanced')",
            name="valid_challenge_difficulty",
        ),
    )

    # Create submissions table
    op.create_table(
        "submissions",
        sa.Column(
            "id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("challenge_id", sa.UUID(), nullable=False),
        sa.Column("code", sa.TEXT(), nullable=False),
        sa.Column(
            "status", sa.VARCHAR(length=20), nullable=False, server_default="'pending'"
        ),
        sa.Column("passed", sa.BOOLEAN(), nullable=False, server_default="false"),
        sa.Column("score", sa.INTEGER(), nullable=False, server_default="0"),
        sa.Column("points_earned", sa.INTEGER(), nullable=False, server_default="0"),
        sa.Column("completion_time", sa.INTEGER(), nullable=True),
        sa.Column(
            "submitted_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("completed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("test_results", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.TEXT(), nullable=True),
        sa.Column("feedback", sa.TEXT(), nullable=True),
        sa.Column("ai_requests", sa.INTEGER(), nullable=False, server_default="0"),
        sa.Column("hints_used", sa.INTEGER(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["challenge_id"], ["challenges.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "status IN ('pending', 'running', 'completed', 'failed', 'timeout')",
            name="valid_submission_status",
        ),
    )

    # Create test_results table
    op.create_table(
        "test_results",
        sa.Column(
            "id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("test_name", sa.VARCHAR(length=200), nullable=False),
        sa.Column("test_type", sa.VARCHAR(length=50), nullable=False),
        sa.Column("description", sa.TEXT(), nullable=True),
        sa.Column("passed", sa.BOOLEAN(), nullable=False),
        sa.Column("score", sa.INTEGER(), nullable=False, server_default="0"),
        sa.Column("execution_time", sa.INTEGER(), nullable=True),
        sa.Column("output", sa.TEXT(), nullable=True),
        sa.Column("error_message", sa.TEXT(), nullable=True),
        sa.Column("expected_output", sa.TEXT(), nullable=True),
        sa.Column("actual_output", sa.TEXT(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.ForeignKeyConstraint(
            ["submission_id"], ["submissions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create user_progress table
    op.create_table(
        "user_progress",
        sa.Column(
            "id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("total_points", sa.INTEGER(), nullable=False, server_default="0"),
        sa.Column(
            "challenges_completed", sa.INTEGER(), nullable=False, server_default="0"
        ),
        sa.Column(
            "challenges_attempted", sa.INTEGER(), nullable=False, server_default="0"
        ),
        sa.Column(
            "web_track_completed", sa.INTEGER(), nullable=False, server_default="0"
        ),
        sa.Column(
            "data_track_completed", sa.INTEGER(), nullable=False, server_default="0"
        ),
        sa.Column(
            "cloud_track_completed", sa.INTEGER(), nullable=False, server_default="0"
        ),
        sa.Column(
            "ai_requests_total", sa.INTEGER(), nullable=False, server_default="0"
        ),
        sa.Column(
            "ai_tier_unlocked",
            sa.VARCHAR(length=20),
            nullable=False,
            server_default="'local'",
        ),
        sa.Column("current_streak", sa.INTEGER(), nullable=False, server_default="0"),
        sa.Column("longest_streak", sa.INTEGER(), nullable=False, server_default="0"),
        sa.Column("last_activity", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("achievements", sa.JSON(), nullable=True),
        sa.Column("badges", sa.JSON(), nullable=True),
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
        sa.UniqueConstraint("user_id", name="unique_user_progress"),
    )

    # Create indexes for better query performance
    op.create_index("ix_challenges_track", "challenges", ["track"])
    op.create_index("ix_challenges_difficulty", "challenges", ["difficulty"])
    op.create_index("ix_challenges_order_index", "challenges", ["order_index"])
    op.create_index("ix_challenges_is_active", "challenges", ["is_active"])

    op.create_index("ix_submissions_user_id", "submissions", ["user_id"])
    op.create_index("ix_submissions_challenge_id", "submissions", ["challenge_id"])
    op.create_index("ix_submissions_status", "submissions", ["status"])
    op.create_index("ix_submissions_passed", "submissions", ["passed"])
    op.create_index("ix_submissions_submitted_at", "submissions", ["submitted_at"])

    op.create_index("ix_test_results_submission_id", "test_results", ["submission_id"])
    op.create_index("ix_test_results_test_type", "test_results", ["test_type"])
    op.create_index("ix_test_results_passed", "test_results", ["passed"])

    op.create_index("ix_user_progress_user_id", "user_progress", ["user_id"])
    op.create_index(
        "ix_user_progress_challenges_completed",
        "user_progress",
        ["challenges_completed"],
    )
    op.create_index("ix_user_progress_total_points", "user_progress", ["total_points"])


def downgrade() -> None:
    # Drop indexes
    op.drop_index("ix_user_progress_total_points")
    op.drop_index("ix_user_progress_challenges_completed")
    op.drop_index("ix_user_progress_user_id")

    op.drop_index("ix_test_results_passed")
    op.drop_index("ix_test_results_test_type")
    op.drop_index("ix_test_results_submission_id")

    op.drop_index("ix_submissions_submitted_at")
    op.drop_index("ix_submissions_passed")
    op.drop_index("ix_submissions_status")
    op.drop_index("ix_submissions_challenge_id")
    op.drop_index("ix_submissions_user_id")

    op.drop_index("ix_challenges_is_active")
    op.drop_index("ix_challenges_order_index")
    op.drop_index("ix_challenges_difficulty")
    op.drop_index("ix_challenges_track")

    # Drop tables
    op.drop_table("user_progress")
    op.drop_table("test_results")
    op.drop_table("submissions")
    op.drop_table("challenges")
