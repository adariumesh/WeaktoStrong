"""
Payment and subscription endpoints
"""


import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.payments import (
    PRICING_PLANS,
    BillingInfoResponse,
    PortalSessionResponse,
    PricingResponse,
    StripeCheckoutRequest,
    StripeCheckoutResponse,
    SubscriptionCancelRequest,
    SubscriptionResponse,
)
from app.services.stripe_service import StripeService

router = APIRouter()


@router.get("/pricing", response_model=PricingResponse)
async def get_pricing_plans(current_user: User = Depends(get_current_user)):
    """Get available pricing plans"""
    return PricingResponse(plans=PRICING_PLANS, current_tier=current_user.tier)


@router.post("/create-checkout", response_model=StripeCheckoutResponse)
async def create_checkout_session(
    request: StripeCheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create Stripe checkout session"""

    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Stripe is not configured")

    stripe_service = StripeService(db)

    try:
        checkout_response = await stripe_service.create_checkout_session(
            user_id=current_user.id,
            price_id=request.price_id,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
        )

        return checkout_response

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Payment processing failed")


@router.get("/billing", response_model=BillingInfoResponse)
async def get_billing_info(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get user's complete billing information"""

    stripe_service = StripeService(db)

    try:
        billing_info = await stripe_service.get_user_billing_info(current_user.id)
        return billing_info

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=500, detail="Failed to retrieve billing information"
        )


@router.post("/cancel-subscription")
async def cancel_subscription(
    request: SubscriptionCancelRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel user subscription"""

    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Stripe is not configured")

    stripe_service = StripeService(db)

    try:
        success = await stripe_service.cancel_subscription(
            user_id=current_user.id, immediate=request.immediate
        )

        if not success:
            raise HTTPException(status_code=400, detail="Failed to cancel subscription")

        message = (
            "Subscription canceled immediately"
            if request.immediate
            else "Subscription will cancel at period end"
        )
        return {"success": True, "message": message}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Cancellation failed")


@router.post("/customer-portal", response_model=PortalSessionResponse)
async def create_portal_session(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Create Stripe customer portal session"""

    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Stripe is not configured")

    stripe_service = StripeService(db)

    try:
        portal_url = await stripe_service.create_customer_portal_session(
            user_id=current_user.id, return_url=settings.stripe_portal_return_url
        )

        return PortalSessionResponse(portal_url=portal_url)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Portal creation failed")


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Stripe webhook events"""

    if not settings.stripe_webhook_secret:
        raise HTTPException(status_code=503, detail="Webhook not configured")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )

        # Process the event
        stripe_service = StripeService(db)
        success = await stripe_service.handle_webhook_event(event)

        if success:
            return {"received": True}
        else:
            raise HTTPException(status_code=400, detail="Webhook processing failed")

    except ValueError:
        # Invalid signature
        raise HTTPException(status_code=400, detail="Invalid signature")
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception:
        raise HTTPException(status_code=500, detail="Webhook processing error")


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_current_subscription(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get user's current subscription"""

    if not current_user.subscription:
        raise HTTPException(status_code=404, detail="No active subscription")

    return SubscriptionResponse.model_validate(current_user.subscription)


@router.get("/config")
async def get_stripe_config():
    """Get Stripe public configuration"""
    return {
        "publishable_key": settings.stripe_publishable_key,
        "configured": bool(settings.stripe_secret_key),
    }


# Success/Cancel redirect handlers
@router.get("/success")
async def payment_success():
    """Handle successful payment redirect"""
    return RedirectResponse(
        url=f"{settings.api_url.replace('8000', '3000')}/billing?success=true"
    )


@router.get("/cancel")
async def payment_cancel():
    """Handle cancelled payment redirect"""
    return RedirectResponse(
        url=f"{settings.api_url.replace('8000', '3000')}/billing?cancel=true"
    )
