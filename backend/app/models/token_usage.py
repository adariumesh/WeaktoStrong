"""
SQLAlchemy model for token usage tracking
"""

from datetime import date

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class TokenUsage(Base):
    """Daily token usage tracking per user and model"""

    __tablename__ = "token_usage"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    date = Column(Date, nullable=False, default=date.today)
    model = Column(String(20), nullable=False)  # 'local', 'haiku', 'sonnet'
    tokens_used = Column(Integer, default=0, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="token_usage")

    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "date", "model", name="unique_user_date_model"),
    )

    def __repr__(self):
        return f"<TokenUsage(user_id={self.user_id}, date={self.date}, model='{self.model}', tokens={self.tokens_used})>"

    @classmethod
    async def get_daily_usage(
        cls, db_session, user_id: str, target_date: date = None
    ) -> dict:
        """Get token usage for a specific user and date"""
        if target_date is None:
            target_date = date.today()

        from sqlalchemy import func, select

        query = (
            select(cls.model, func.sum(cls.tokens_used).label("total_tokens"))
            .where(cls.user_id == user_id, cls.date == target_date)
            .group_by(cls.model)
        )

        result = await db_session.execute(query)
        usage_dict = {row.model: row.total_tokens for row in result}

        return {
            "local": usage_dict.get("local", 0),
            "haiku": usage_dict.get("haiku", 0),
            "sonnet": usage_dict.get("sonnet", 0),
            "total": sum(usage_dict.values()),
            "date": target_date.isoformat(),
        }

    @classmethod
    async def add_usage(
        cls, db_session, user_id: str, model: str, tokens: int, target_date: date = None
    ):
        """Add token usage for a user and model"""
        if target_date is None:
            target_date = date.today()

        from sqlalchemy.dialects.postgresql import insert

        # Use PostgreSQL's ON CONFLICT to handle upserts
        stmt = insert(cls).values(
            user_id=user_id, date=target_date, model=model, tokens_used=tokens
        )

        # If record exists, add to existing tokens_used
        stmt = stmt.on_conflict_do_update(
            index_elements=["user_id", "date", "model"],
            set_=dict(tokens_used=cls.tokens_used + stmt.excluded.tokens_used),
        )

        await db_session.execute(stmt)
        await db_session.commit()

    @classmethod
    async def get_weekly_usage(cls, db_session, user_id: str) -> dict:
        """Get token usage for the past 7 days"""
        from datetime import date, timedelta

        from sqlalchemy import and_, func, select

        end_date = date.today()
        start_date = end_date - timedelta(days=6)

        query = (
            select(cls.date, cls.model, func.sum(cls.tokens_used).label("total_tokens"))
            .where(
                and_(
                    cls.user_id == user_id, cls.date >= start_date, cls.date <= end_date
                )
            )
            .group_by(cls.date, cls.model)
            .order_by(cls.date)
        )

        result = await db_session.execute(query)

        # Organize by date
        usage_by_date = {}
        for row in result:
            date_str = row.date.isoformat()
            if date_str not in usage_by_date:
                usage_by_date[date_str] = {"local": 0, "haiku": 0, "sonnet": 0}
            usage_by_date[date_str][row.model] = row.total_tokens

        return usage_by_date

    @classmethod
    async def get_monthly_total(cls, db_session, user_id: str) -> int:
        """Get total token usage for the current month"""
        from datetime import date

        from sqlalchemy import and_, extract, func, select

        today = date.today()

        query = select(func.sum(cls.tokens_used)).where(
            and_(
                cls.user_id == user_id,
                extract("year", cls.date) == today.year,
                extract("month", cls.date) == today.month,
            )
        )

        result = await db_session.execute(query)
        total = result.scalar() or 0
        return total
