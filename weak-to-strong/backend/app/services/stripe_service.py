"""
Stripe service for handling payments and subscriptions
"""

import logging
from datetime import UTC, datetime
from uuid import UUID

import stripe
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models.subscription import (
    InvoiceEvent,
    Payment,
    Subscription,
    SubscriptionStatus,
)
from app.models.user import User, UserTier
from app.schemas.payments import (
    PRICING_PLANS,
    BillingInfoResponse,
    PaymentResponse,
    StripeCheckoutResponse,
    SubscriptionResponse,
)

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = settings.stripe_secret_key


class StripeService:
    """Service for handling Stripe integration"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_checkout_session(
        self, user_id: UUID, price_id: str, success_url: str, cancel_url: str
    ) -> StripeCheckoutResponse:
        """Create a Stripe checkout session"""

        # Get user
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError("User not found")

        # Get or create Stripe customer
        customer_id = await self._get_or_create_customer(user)

        try:
            # Create checkout session
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "user_id": str(user_id),
                    "tier": self._get_tier_from_price_id(price_id),
                },
            )

            return StripeCheckoutResponse(
                checkout_url=session.url, session_id=session.id
            )

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating checkout session: {e}")
            raise ValueError(f"Payment processing error: {e!s}")

    async def create_customer_portal_session(
        self, user_id: UUID, return_url: str
    ) -> str:
        """Create a customer portal session for subscription management"""

        result = await self.db.execute(
            select(User)
            .options(selectinload(User.subscription))
            .where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user or not user.subscription:
            raise ValueError("User has no subscription")

        try:
            portal_session = stripe.billing_portal.Session.create(
                customer=user.subscription.stripe_customer_id, return_url=return_url
            )

            return portal_session.url

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating portal session: {e}")
            raise ValueError(f"Portal creation error: {e!s}")

    async def handle_webhook_event(self, event_data: dict) -> bool:
        """Handle Stripe webhook events"""

        event_id = event_data.get("id")
        event_type = event_data.get("type")

        # Check if we've already processed this event
        result = await self.db.execute(
            select(InvoiceEvent).where(InvoiceEvent.stripe_event_id == event_id)
        )
        existing_event = result.scalar_one_or_none()

        if existing_event:
            return True  # Already processed

        # Create event record
        invoice_event = InvoiceEvent(
            stripe_event_id=event_id,
            event_type=event_type,
            event_data=event_data,
            stripe_created=datetime.fromtimestamp(event_data.get("created", 0), tz=UTC),
        )
        self.db.add(invoice_event)

        try:
            # Process the event
            success = await self._process_webhook_event(event_data)

            invoice_event.processed = True
            invoice_event.processed_at = datetime.utcnow()

            if not success:
                invoice_event.error_message = "Failed to process event"

            await self.db.commit()
            return success

        except Exception as e:
            logger.error(f"Error processing webhook event {event_type}: {e}")
            invoice_event.error_message = str(e)
            await self.db.commit()
            return False

    async def get_user_billing_info(self, user_id: UUID) -> BillingInfoResponse:
        """Get complete billing information for user"""

        result = await self.db.execute(
            select(User)
            .options(selectinload(User.subscription), selectinload(User.payments))
            .where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError("User not found")

        # Get upcoming invoice from Stripe if subscription exists
        upcoming_invoice = None
        if user.subscription and user.subscription.is_active:
            try:
                upcoming = stripe.Invoice.upcoming(
                    customer=user.subscription.stripe_customer_id
                )
                upcoming_invoice = {
                    "amount_due": upcoming.amount_due,
                    "currency": upcoming.currency,
                    "period_start": datetime.fromtimestamp(upcoming.period_start),
                    "period_end": datetime.fromtimestamp(upcoming.period_end),
                }
            except stripe.error.StripeError:
                pass  # No upcoming invoice

        return BillingInfoResponse(
            subscription=(
                SubscriptionResponse.model_validate(user.subscription)
                if user.subscription
                else None
            ),
            payment_history=[PaymentResponse.model_validate(p) for p in user.payments],
            upcoming_invoice=upcoming_invoice,
        )

    async def cancel_subscription(self, user_id: UUID, immediate: bool = False) -> bool:
        """Cancel user subscription"""

        result = await self.db.execute(
            select(User)
            .options(selectinload(User.subscription))
            .where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user or not user.subscription:
            raise ValueError("User has no active subscription")

        try:
            if immediate:
                # Cancel immediately
                stripe.Subscription.delete(user.subscription.stripe_subscription_id)
                user.subscription.status = SubscriptionStatus.CANCELED
                user.subscription.canceled_at = datetime.utcnow()
                user.tier = UserTier.FREE
            else:
                # Cancel at period end
                stripe.Subscription.modify(
                    user.subscription.stripe_subscription_id, cancel_at_period_end=True
                )
                user.subscription.cancel_at_period_end = True

            await self.db.commit()
            return True

        except stripe.error.StripeError as e:
            logger.error(f"Error canceling subscription: {e}")
            return False

    # Private methods

    async def _get_or_create_customer(self, user: User) -> str:
        """Get existing or create new Stripe customer"""

        # Check if user already has a subscription with customer ID
        if user.subscription and user.subscription.stripe_customer_id:
            return user.subscription.stripe_customer_id

        # Create new customer
        try:
            customer = stripe.Customer.create(
                email=user.email, name=user.name, metadata={"user_id": str(user.id)}
            )
            return customer.id

        except stripe.error.StripeError as e:
            logger.error(f"Error creating Stripe customer: {e}")
            raise ValueError(f"Customer creation error: {e!s}")

    def _get_tier_from_price_id(self, price_id: str) -> str:
        """Get user tier from Stripe price ID"""
        for plan in PRICING_PLANS:
            if price_id in [plan.stripe_monthly_price_id, plan.stripe_yearly_price_id]:
                return plan.tier.value
        return "pro"  # Default fallback

    async def _process_webhook_event(self, event_data: dict) -> bool:
        """Process specific webhook event types"""

        event_type = event_data.get("type")
        data_object = event_data.get("data", {}).get("object", {})

        if event_type == "checkout.session.completed":
            return await self._handle_checkout_completed(data_object)

        elif event_type == "customer.subscription.created":
            return await self._handle_subscription_created(data_object)

        elif event_type == "customer.subscription.updated":
            return await self._handle_subscription_updated(data_object)

        elif event_type == "customer.subscription.deleted":
            return await self._handle_subscription_deleted(data_object)

        elif event_type == "invoice.payment_succeeded":
            return await self._handle_payment_succeeded(data_object)

        elif event_type == "invoice.payment_failed":
            return await self._handle_payment_failed(data_object)

        else:
            logger.info(f"Unhandled webhook event type: {event_type}")
            return True  # Don't fail on unhandled events

    async def _handle_checkout_completed(self, session_data: dict) -> bool:
        """Handle successful checkout session"""

        metadata = session_data.get("metadata", {})
        user_id = metadata.get("user_id")

        if not user_id:
            logger.error("No user_id in checkout session metadata")
            return False

        # The subscription will be created in a separate webhook
        # Just log for now
        logger.info(f"Checkout completed for user {user_id}")
        return True

    async def _handle_subscription_created(self, subscription_data: dict) -> bool:
        """Handle new subscription creation"""

        customer_id = subscription_data.get("customer")

        # Find user by customer ID or metadata
        user_id = await self._get_user_id_from_customer(customer_id, subscription_data)

        if not user_id:
            logger.error(f"Could not find user for customer {customer_id}")
            return False

        # Create subscription record
        tier = self._get_tier_from_price_id(
            subscription_data.get("items", {})
            .get("data", [{}])[0]
            .get("price", {})
            .get("id", "")
        )

        subscription = Subscription(
            user_id=UUID(user_id),
            stripe_customer_id=customer_id,
            stripe_subscription_id=subscription_data.get("id"),
            stripe_price_id=subscription_data.get("items", {})
            .get("data", [{}])[0]
            .get("price", {})
            .get("id"),
            status=SubscriptionStatus(subscription_data.get("status")),
            tier=tier,
            current_period_start=datetime.fromtimestamp(
                subscription_data.get("current_period_start"), tz=UTC
            ),
            current_period_end=datetime.fromtimestamp(
                subscription_data.get("current_period_end"), tz=UTC
            ),
            interval=subscription_data.get("items", {})
            .get("data", [{}])[0]
            .get("price", {})
            .get("recurring", {})
            .get("interval", "month"),
            amount=subscription_data.get("items", {})
            .get("data", [{}])[0]
            .get("price", {})
            .get("unit_amount", 0),
            currency=subscription_data.get("currency", "usd"),
        )

        self.db.add(subscription)

        # Update user tier
        await self.db.execute(
            update(User).where(User.id == UUID(user_id)).values(tier=UserTier(tier))
        )

        await self.db.commit()
        logger.info(f"Created subscription for user {user_id}")
        return True

    async def _handle_subscription_updated(self, subscription_data: dict) -> bool:
        """Handle subscription updates"""

        subscription_id = subscription_data.get("id")

        # Find existing subscription
        result = await self.db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == subscription_id
            )
        )
        subscription = result.scalar_one_or_none()

        if not subscription:
            logger.error(f"Subscription {subscription_id} not found")
            return False

        # Update subscription
        subscription.status = SubscriptionStatus(subscription_data.get("status"))
        subscription.current_period_start = datetime.fromtimestamp(
            subscription_data.get("current_period_start"), tz=UTC
        )
        subscription.current_period_end = datetime.fromtimestamp(
            subscription_data.get("current_period_end"), tz=UTC
        )
        subscription.cancel_at_period_end = subscription_data.get(
            "cancel_at_period_end", False
        )

        if subscription_data.get("canceled_at"):
            subscription.canceled_at = datetime.fromtimestamp(
                subscription_data.get("canceled_at"), tz=UTC
            )

        await self.db.commit()
        logger.info(f"Updated subscription {subscription_id}")
        return True

    async def _handle_subscription_deleted(self, subscription_data: dict) -> bool:
        """Handle subscription cancellation"""

        subscription_id = subscription_data.get("id")

        # Find and update subscription
        result = await self.db.execute(
            select(Subscription)
            .options(selectinload(Subscription.user))
            .where(Subscription.stripe_subscription_id == subscription_id)
        )
        subscription = result.scalar_one_or_none()

        if not subscription:
            logger.error(f"Subscription {subscription_id} not found")
            return False

        subscription.status = SubscriptionStatus.CANCELED
        subscription.canceled_at = datetime.utcnow()

        # Downgrade user to free tier
        subscription.user.tier = UserTier.FREE

        await self.db.commit()
        logger.info(f"Canceled subscription {subscription_id}")
        return True

    async def _handle_payment_succeeded(self, invoice_data: dict) -> bool:
        """Handle successful payment"""

        customer_id = invoice_data.get("customer")
        subscription_id = invoice_data.get("subscription")

        # Find user by customer ID
        result = await self.db.execute(
            select(User)
            .join(Subscription)
            .where(Subscription.stripe_customer_id == customer_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            logger.error(f"User not found for customer {customer_id}")
            return False

        # Find subscription
        result = await self.db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == subscription_id
            )
        )
        subscription = result.scalar_one_or_none()

        # Create payment record
        payment = Payment(
            user_id=user.id,
            subscription_id=subscription.id if subscription else None,
            stripe_payment_intent_id=invoice_data.get("payment_intent", ""),
            stripe_invoice_id=invoice_data.get("id"),
            amount=invoice_data.get("amount_paid", 0),
            currency=invoice_data.get("currency", "usd"),
            status="succeeded",
            processed_at=datetime.fromtimestamp(
                invoice_data.get("status_transitions", {}).get("paid_at", 0),
                tz=UTC,
            ),
        )

        self.db.add(payment)
        await self.db.commit()

        logger.info(f"Recorded payment for user {user.id}")
        return True

    async def _handle_payment_failed(self, invoice_data: dict) -> bool:
        """Handle failed payment"""

        customer_id = invoice_data.get("customer")

        # Find user and update subscription status if needed
        result = await self.db.execute(
            select(Subscription).where(Subscription.stripe_customer_id == customer_id)
        )
        subscription = result.scalar_one_or_none()

        if subscription:
            subscription.status = SubscriptionStatus.PAST_DUE
            await self.db.commit()

        logger.warning(f"Payment failed for customer {customer_id}")
        return True

    async def _get_user_id_from_customer(
        self, customer_id: str, data: dict
    ) -> str | None:
        """Get user ID from Stripe customer or metadata"""

        # First try to find existing subscription with this customer
        result = await self.db.execute(
            select(Subscription).where(Subscription.stripe_customer_id == customer_id)
        )
        subscription = result.scalar_one_or_none()

        if subscription:
            return str(subscription.user_id)

        # Try metadata
        metadata = data.get("metadata", {})
        return metadata.get("user_id")
