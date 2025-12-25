"""
Subscription models for Stripe integration
"""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class SubscriptionStatus(str, Enum):
    """Subscription status enum matching Stripe subscription statuses"""

    ACTIVE = "active"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    TRIALING = "trialing"


class PriceInterval(str, Enum):
    """Price billing interval"""

    MONTH = "month"
    YEAR = "year"


class Subscription(Base):
    """User subscription tracking"""

    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    # Stripe identifiers
    stripe_customer_id: Mapped[str] = mapped_column(String(255), nullable=False)
    stripe_subscription_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    stripe_price_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Subscription details
    status: Mapped[SubscriptionStatus] = mapped_column(
        String(50), nullable=False, default=SubscriptionStatus.ACTIVE
    )
    tier: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # pro, team, enterprise

    # Billing
    current_period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    current_period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    interval: Mapped[PriceInterval] = mapped_column(
        String(10), nullable=False, default=PriceInterval.MONTH
    )

    # Payment tracking
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # Amount in cents
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="usd")

    # Features
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False)
    canceled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Additional data
    subscription_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user = relationship("User", back_populates="subscription")

    def __repr__(self):
        return f"<Subscription {self.tier} for user {self.user_id}>"

    @property
    def is_active(self) -> bool:
        """Check if subscription is currently active"""
        return self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]

    @property
    def is_past_due(self) -> bool:
        """Check if subscription is past due"""
        return self.status == SubscriptionStatus.PAST_DUE

    @property
    def display_amount(self) -> str:
        """Format amount for display"""
        dollars = self.amount / 100
        return f"${dollars:.2f}"

    @property
    def display_interval(self) -> str:
        """Format billing interval for display"""
        return f"per {self.interval}"


class Payment(Base):
    """Payment history tracking"""

    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    subscription_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=True
    )

    # Stripe identifiers
    stripe_payment_intent_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    stripe_invoice_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Payment details
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # Amount in cents
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="usd")
    status: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # succeeded, failed, pending, etc.

    # Payment method
    payment_method: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )  # card, bank_account, etc.
    last4: Mapped[str | None] = mapped_column(
        String(4), nullable=True
    )  # Last 4 digits of card

    # Timestamps
    processed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Additional data
    subscription_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Relationships
    user = relationship("User", back_populates="payments")
    subscription = relationship("Subscription", backref="payments")

    def __repr__(self):
        return f"<Payment {self.display_amount} for user {self.user_id}>"

    @property
    def display_amount(self) -> str:
        """Format amount for display"""
        dollars = self.amount / 100
        return f"${dollars:.2f}"

    @property
    def is_successful(self) -> bool:
        """Check if payment was successful"""
        return self.status == "succeeded"


class InvoiceEvent(Base):
    """Track Stripe webhook events for auditing"""

    __tablename__ = "invoice_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Stripe event details
    stripe_event_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)

    # Processing
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Event data
    event_data: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Timestamps
    stripe_created: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<InvoiceEvent {self.event_type} - {self.stripe_event_id}>"
