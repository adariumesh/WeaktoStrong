"""
Pydantic schemas for payment and subscription endpoints
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.subscription import PriceInterval, SubscriptionStatus
from app.models.user import UserTier


class StripeCheckoutRequest(BaseModel):
    """Request to create Stripe checkout session"""

    price_id: str = Field(..., description="Stripe price ID")
    success_url: str = Field(..., description="URL to redirect after success")
    cancel_url: str = Field(..., description="URL to redirect on cancel")


class StripeCheckoutResponse(BaseModel):
    """Response from checkout session creation"""

    checkout_url: str = Field(..., description="Stripe checkout URL")
    session_id: str = Field(..., description="Stripe session ID")


class SubscriptionResponse(BaseModel):
    """User subscription response"""

    id: UUID
    status: SubscriptionStatus
    tier: str
    current_period_start: datetime
    current_period_end: datetime
    interval: PriceInterval
    amount: int
    currency: str
    cancel_at_period_end: bool
    canceled_at: datetime | None = None

    # Computed fields
    display_amount: str
    display_interval: str
    is_active: bool
    is_past_due: bool

    class Config:
        from_attributes = True


class PaymentResponse(BaseModel):
    """Payment history response"""

    id: UUID
    amount: int
    currency: str
    status: str
    payment_method: str | None = None
    last4: str | None = None
    processed_at: datetime

    # Computed fields
    display_amount: str
    is_successful: bool

    class Config:
        from_attributes = True


class BillingInfoResponse(BaseModel):
    """Complete billing information"""

    subscription: SubscriptionResponse | None = None
    payment_history: list[PaymentResponse] = []
    upcoming_invoice: dict | None = None


class PricingPlan(BaseModel):
    """Pricing plan details"""

    tier: UserTier
    name: str
    price_monthly: int  # in cents
    price_yearly: int  # in cents
    stripe_monthly_price_id: str
    stripe_yearly_price_id: str
    features: list[str]
    popular: bool = False

    @property
    def monthly_display_price(self) -> str:
        return f"${self.price_monthly / 100:.0f}"

    @property
    def yearly_display_price(self) -> str:
        return f"${self.price_yearly / 100:.0f}"

    @property
    def yearly_savings(self) -> int:
        """Calculate yearly savings percentage"""
        monthly_yearly = self.price_monthly * 12
        return int(((monthly_yearly - self.price_yearly) / monthly_yearly) * 100)


class PricingResponse(BaseModel):
    """Available pricing plans"""

    plans: list[PricingPlan]
    current_tier: UserTier


class StripeWebhookEvent(BaseModel):
    """Stripe webhook event data"""

    id: str
    type: str
    data: dict
    created: int


class SubscriptionCancelRequest(BaseModel):
    """Request to cancel subscription"""

    immediate: bool = Field(
        default=False, description="Cancel immediately or at period end"
    )


class PortalSessionResponse(BaseModel):
    """Customer portal session response"""

    portal_url: str = Field(..., description="Stripe customer portal URL")


class UsageResponse(BaseModel):
    """Usage metrics for billing"""

    current_period_start: datetime
    current_period_end: datetime
    tokens_used: int
    tokens_limit: int
    challenges_completed: int
    ai_conversations: int


class TierFeatures(BaseModel):
    """Features for each tier"""

    tier: UserTier
    features: dict[str, any]


TIER_FEATURES = {
    UserTier.FREE: TierFeatures(
        tier=UserTier.FREE,
        features={
            "challenges_per_track": 5,
            "ai_models": ["local"],
            "total_tokens_per_day": 1000,
            "certificates": False,
            "support": "community",
            "analytics": False,
        },
    ),
    UserTier.PRO: TierFeatures(
        tier=UserTier.PRO,
        features={
            "challenges_per_track": "unlimited",
            "ai_models": ["local", "claude-haiku", "claude-sonnet"],
            "total_tokens_per_day": 50000,
            "certificates": True,
            "support": "email",
            "analytics": True,
            "priority_queue": True,
        },
    ),
    UserTier.TEAM: TierFeatures(
        tier=UserTier.TEAM,
        features={
            "challenges_per_track": "unlimited",
            "ai_models": ["local", "claude-haiku", "claude-sonnet"],
            "total_tokens_per_day": 200000,
            "certificates": True,
            "support": "priority",
            "analytics": True,
            "priority_queue": True,
            "team_dashboard": True,
            "shared_progress": True,
            "bulk_invites": True,
        },
    ),
    UserTier.ENTERPRISE: TierFeatures(
        tier=UserTier.ENTERPRISE,
        features={
            "challenges_per_track": "unlimited",
            "ai_models": ["local", "claude-haiku", "claude-sonnet", "custom"],
            "total_tokens_per_day": "unlimited",
            "certificates": True,
            "support": "dedicated",
            "analytics": True,
            "priority_queue": True,
            "team_dashboard": True,
            "shared_progress": True,
            "bulk_invites": True,
            "sso": True,
            "audit_logs": True,
            "on_premise": True,
            "white_label": True,
        },
    ),
}


PRICING_PLANS = [
    PricingPlan(
        tier=UserTier.FREE,
        name="Free",
        price_monthly=0,
        price_yearly=0,
        stripe_monthly_price_id="",
        stripe_yearly_price_id="",
        features=[
            "5 challenges per track",
            "Local AI model only",
            "1,000 tokens per day",
            "Community support",
        ],
    ),
    PricingPlan(
        tier=UserTier.PRO,
        name="Pro",
        price_monthly=2900,  # $29
        price_yearly=29000,  # $290 (save ~17%)
        stripe_monthly_price_id="price_pro_monthly_29",
        stripe_yearly_price_id="price_pro_yearly_290",
        features=[
            "Unlimited challenges",
            "Claude Haiku & Sonnet access",
            "50,000 tokens per day",
            "Verifiable certificates",
            "Email support",
            "Progress analytics",
        ],
        popular=True,
    ),
    PricingPlan(
        tier=UserTier.TEAM,
        name="Team",
        price_monthly=4900,  # $49 per user
        price_yearly=49000,  # $490 per user (save ~17%)
        stripe_monthly_price_id="price_team_monthly_49",
        stripe_yearly_price_id="price_team_yearly_490",
        features=[
            "Everything in Pro",
            "200,000 tokens per day",
            "Team dashboard",
            "Shared progress tracking",
            "Bulk user invites",
            "Priority support",
        ],
    ),
    PricingPlan(
        tier=UserTier.ENTERPRISE,
        name="Enterprise",
        price_monthly=0,  # Custom pricing
        price_yearly=0,
        stripe_monthly_price_id="",
        stripe_yearly_price_id="",
        features=[
            "Everything in Team",
            "Unlimited tokens",
            "Custom AI models",
            "SSO integration",
            "Audit logs",
            "On-premise deployment",
            "White-label options",
            "Dedicated support",
        ],
    ),
]
