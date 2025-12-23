"""
AI API endpoints for chat, streaming responses, and model management
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.ai.challenge_context import challenge_context_service
from ...core.ai.claude_client import claude_service
from ...core.ai.hint_generator import hint_generator
from ...core.ai.local_llm import local_llm_service
from ...core.ai.model_router import model_router
from ...core.ai.prompt_validator import validate_prompt
from ...core.database import get_db
from ...core.deps import get_current_user
from ...schemas.ai_schemas import (
    AIRequest,
    AIResponse,
    AIServiceStatus,
    ModelTier,
    StreamChunk,
    TierProgress,
    ValidationResult,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/status", response_model=AIServiceStatus)
async def get_ai_service_status(
    current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get AI service status and user's current tier info"""

    # Check service availability
    local_available = await local_llm_service.health_check()
    claude_available = await claude_service.health_check()

    # Get user's allowed tier
    current_tier = await model_router.get_allowed_tier(current_user, db_session=db)

    # Get tier progress
    tier_progress_data = await model_router.get_tier_progress(
        current_user, current_tier, db
    )
    tier_progress = TierProgress(**tier_progress_data)

    # Get daily token usage from user's actual usage
    daily_token_usage = await current_user.get_daily_token_usage(db)
    daily_tokens_used = daily_token_usage.get("total", 0)

    # Set daily limits based on user tier
    tier_limits = {
        "free": 10000,
        "pro": 100000,
        "team": 500000,
        "enterprise": -1,  # Unlimited
    }
    daily_token_limit = tier_limits.get(current_user.subscription_tier, 10000)

    return AIServiceStatus(
        local_available=local_available,
        claude_available=claude_available,
        current_tier=current_tier,
        daily_tokens_used=daily_tokens_used,
        daily_token_limit=daily_token_limit,
        tier_progress=tier_progress,
    )


@router.post("/validate-prompt", response_model=ValidationResult)
async def validate_prompt_endpoint(
    request: dict[str, str],
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Validate a prompt against anti-blind-prompting rules"""

    prompt = request.get("prompt", "")
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Prompt is required"
        )

    validation_result = validate_prompt(prompt)
    return validation_result


@router.post("/chat/stream")
async def stream_ai_chat(
    request: AIRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Stream AI chat response using Server-Sent Events"""

    # Check daily token limit before processing request
    daily_usage = await current_user.get_daily_token_usage(db)
    tier_limits = {
        "free": 10000,
        "pro": 100000,
        "team": 500000,
        "enterprise": -1,  # Unlimited
    }
    daily_limit = tier_limits.get(current_user.subscription_tier, 10000)

    if daily_limit != -1 and daily_usage["total"] >= daily_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily token limit of {daily_limit} reached. Upgrade your plan for higher limits.",
        )

    async def generate_stream():
        """Generate streaming response chunks"""

        try:
            # Enhance request with live challenge context if challenge_id provided
            enhanced_request = request
            if hasattr(request, "challenge_id") and request.challenge_id:
                live_context = await challenge_context_service.get_challenge_context(
                    challenge_id=request.challenge_id,
                    user_id=str(current_user.id),
                    db_session=db,
                    include_code=True,
                    include_test_results=True,
                )
                # Merge with existing context
                if hasattr(enhanced_request, "challenge_context"):
                    enhanced_request.challenge_context.update(live_context)
                else:
                    enhanced_request.challenge_context = live_context

            # Send start event
            start_chunk = StreamChunk(
                type="start", model=f"{request.preferred_tier.value}_model"
            )
            yield f"data: {start_chunk.model_dump_json()}\n\n"

            # Stream AI response
            total_tokens = 0
            response_content = ""

            async for chunk in model_router.route_request(
                enhanced_request, current_user, db
            ):
                # Accumulate response for token counting
                response_content += chunk

                # Send chunk to client
                chunk_data = StreamChunk(type="chunk", content=chunk)
                yield f"data: {chunk_data.model_dump_json()}\n\n"

            # Count tokens used (rough estimate for now - will improve with proper tokenizers)
            total_tokens = len(response_content.split()) * 1.3  # Rough estimate

            # Record token usage in database
            model_name = "local"
            if "haiku" in f"{request.preferred_tier.value}_model":
                model_name = "haiku"
            elif "sonnet" in f"{request.preferred_tier.value}_model":
                model_name = "sonnet"

            await current_user.add_token_usage(db, model_name, int(total_tokens))

            # Send end event with metadata
            end_chunk = StreamChunk(type="end", tokens_used=int(total_tokens))
            yield f"data: {end_chunk.model_dump_json()}\n\n"

        except Exception as e:
            logger.error(f"AI streaming failed: {e}")
            error_chunk = StreamChunk(type="error", error=f"AI service error: {e!s}")
            yield f"data: {error_chunk.model_dump_json()}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        },
    )


@router.post("/chat", response_model=AIResponse)
async def generate_ai_response(
    request: AIRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a complete AI response (non-streaming)"""

    # Check daily token limit before processing request
    daily_usage = await current_user.get_daily_token_usage(db)
    tier_limits = {
        "free": 10000,
        "pro": 100000,
        "team": 500000,
        "enterprise": -1,  # Unlimited
    }
    daily_limit = tier_limits.get(current_user.subscription_tier, 10000)

    if daily_limit != -1 and daily_usage["total"] >= daily_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily token limit of {daily_limit} reached. Upgrade your plan for higher limits.",
        )

    try:
        # Enhance request with live challenge context if challenge_id provided
        enhanced_request = request
        if hasattr(request, "challenge_id") and request.challenge_id:
            live_context = await challenge_context_service.get_challenge_context(
                challenge_id=request.challenge_id,
                user_id=str(current_user.id),
                db_session=db,
                include_code=True,
                include_test_results=True,
            )
            # Merge with existing context
            if hasattr(enhanced_request, "challenge_context"):
                enhanced_request.challenge_context.update(live_context)
            else:
                enhanced_request.challenge_context = live_context

        # Validate prompt
        validation_result = validate_prompt(enhanced_request.prompt)
        if not validation_result.is_valid and request.enforce_validation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation_result.feedback,
            )

        # Get user's allowed tier
        allowed_tier = await model_router.get_allowed_tier(current_user, db_session=db)
        effective_tier = min(
            enhanced_request.preferred_tier, allowed_tier, key=lambda x: x.value
        )

        # Generate response based on tier
        if effective_tier == ModelTier.LOCAL:
            response_content = await local_llm_service.generate_response(
                prompt=enhanced_request.prompt,
                system_prompt=model_router._build_system_prompt(enhanced_request),
                temperature=enhanced_request.temperature,
                max_tokens=enhanced_request.max_tokens,
            )
            model_used = local_llm_service.model

        elif effective_tier == ModelTier.HAIKU:
            response_content = await claude_service.generate_response(
                prompt=enhanced_request.prompt,
                system_prompt=model_router._build_system_prompt(enhanced_request),
                model="claude-3-haiku-20240307",
                temperature=enhanced_request.temperature,
                max_tokens=enhanced_request.max_tokens,
            )
            model_used = "claude-3-haiku-20240307"

        elif effective_tier == ModelTier.SONNET:
            response_content = await claude_service.generate_response(
                prompt=enhanced_request.prompt,
                system_prompt=model_router._build_system_prompt(enhanced_request),
                model="claude-3-5-sonnet-20241022",
                temperature=enhanced_request.temperature,
                max_tokens=enhanced_request.max_tokens,
            )
            model_used = "claude-3-5-sonnet-20241022"

        # Count tokens used (rough estimate for now)
        tokens_used = len(response_content.split()) * 1.3

        # Record token usage in database
        model_name = "local"
        if effective_tier == ModelTier.HAIKU:
            model_name = "haiku"
        elif effective_tier == ModelTier.SONNET:
            model_name = "sonnet"

        await current_user.add_token_usage(db, model_name, int(tokens_used))

        return AIResponse(
            content=response_content,
            model_used=model_used,
            tokens_used=int(tokens_used),
            tier=effective_tier,
            validation_passed=validation_result.is_valid,
            validation_feedback=(
                validation_result.feedback if not validation_result.is_valid else None
            ),
        )

    except Exception as e:
        logger.error(f"AI generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {e!s}",
        )


@router.get("/models")
async def list_available_models(
    current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """List AI models available to the current user"""

    allowed_tier = await model_router.get_allowed_tier(current_user, db_session=db)
    models = []

    # Always include local model
    models.append(
        {
            **local_llm_service.get_model_info(),
            "available": True,
            "tier_required": "local",
        }
    )

    # Add Claude Haiku if user has access
    if allowed_tier.value >= ModelTier.HAIKU.value:
        models.append(
            {
                **claude_service.get_model_info("claude-3-haiku-20240307"),
                "available": await claude_service.health_check(),
                "tier_required": "haiku",
            }
        )

    # Add Claude Sonnet if user has access
    if allowed_tier.value >= ModelTier.SONNET.value:
        models.append(
            {
                **claude_service.get_model_info("claude-3-5-sonnet-20241022"),
                "available": await claude_service.health_check(),
                "tier_required": "sonnet",
            }
        )

    return {
        "models": models,
        "current_tier": allowed_tier.value,
        "tier_progress": await model_router.get_tier_progress(
            current_user, allowed_tier, db
        ),
    }


@router.get("/tiers")
async def get_tier_info(
    current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get information about AI model tiers and requirements"""

    current_tier = await model_router.get_allowed_tier(current_user, db_session=db)
    progress = await model_router.get_tier_progress(current_user, current_tier, db)

    tier_info = {
        "tiers": [
            {
                "name": "local",
                "display_name": "Local AI",
                "model": "Llama 3.2 8B",
                "requirements": "Available to all users",
                "features": ["Basic coding help", "Local privacy", "No usage limits"],
            },
            {
                "name": "haiku",
                "display_name": "Claude Haiku",
                "model": "Claude 3 Haiku",
                "requirements": "Complete 10 challenges",
                "features": ["Faster responses", "Better reasoning", "Code analysis"],
            },
            {
                "name": "sonnet",
                "display_name": "Claude Sonnet",
                "model": "Claude 3.5 Sonnet",
                "requirements": "Complete 25 challenges + Pro subscription",
                "features": ["Advanced coding", "Complex reasoning", "Best quality"],
            },
        ],
        "current": progress,
        "unlock_next": {
            "challenges_needed": max(
                0, progress.get("required", 0) - progress.get("progress", 0)
            ),
            "pro_required": progress.get("requires_pro", False),
        },
    }

    return tier_info


@router.get("/usage")
async def get_token_usage_stats(
    current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get detailed token usage statistics for current user"""

    # Get today's usage
    daily_usage = await current_user.get_daily_token_usage(db)

    # Get weekly usage (past 7 days)
    from ...models.token_usage import TokenUsage

    weekly_usage = await TokenUsage.get_weekly_usage(db, str(current_user.id))

    # Get monthly total
    monthly_total = await TokenUsage.get_monthly_total(db, str(current_user.id))

    # Set tier limits
    tier_limits = {
        "free": 10000,
        "pro": 100000,
        "team": 500000,
        "enterprise": -1,  # Unlimited
    }
    daily_limit = tier_limits.get(current_user.subscription_tier, 10000)

    return {
        "daily": {
            "usage": daily_usage,
            "limit": daily_limit,
            "remaining": (
                daily_limit - daily_usage["total"] if daily_limit != -1 else -1
            ),
            "percentage_used": (
                round((daily_usage["total"] / daily_limit) * 100, 1)
                if daily_limit != -1
                else 0
            ),
        },
        "weekly": weekly_usage,
        "monthly_total": monthly_total,
        "tier": current_user.subscription_tier,
        "breakdown_by_model": {
            "local": daily_usage["local"],
            "haiku": daily_usage["haiku"],
            "sonnet": daily_usage["sonnet"],
        },
    }


@router.get("/context/{challenge_id}")
async def get_challenge_ai_context(
    challenge_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get AI context for a specific challenge (for debugging/testing)"""

    context = await challenge_context_service.get_challenge_context(
        challenge_id=challenge_id,
        user_id=str(current_user.id),
        db_session=db,
        include_code=True,
        include_test_results=True,
    )

    # Also get user progress summary
    progress_summary = await challenge_context_service.get_user_progress_summary(
        user_id=str(current_user.id), db_session=db
    )

    return {
        "challenge_context": context,
        "user_progress": progress_summary,
        "ai_tier_available": (
            await model_router.get_allowed_tier(current_user, db_session=db)
        ).value,
    }


@router.post("/hints/{challenge_id}")
async def generate_smart_hints(
    challenge_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    max_hints: int = 3,
):
    """Generate contextual hints for a specific challenge"""

    # Get full challenge context
    context = await challenge_context_service.get_challenge_context(
        challenge_id=challenge_id,
        user_id=str(current_user.id),
        db_session=db,
        include_code=True,
        include_test_results=True,
        include_diff_analysis=True,
        include_learning_path=True,
    )

    # Generate smart hints
    hints = await hint_generator.generate_contextual_hints(
        challenge_id=challenge_id,
        user_id=str(current_user.id),
        db_session=db,
        context=context,
        max_hints=max_hints,
    )

    return {
        "challenge_id": challenge_id,
        "hints": hints,
        "context_summary": {
            "has_code": bool(context.get("user_code")),
            "has_test_results": bool(context.get("last_test_results")),
            "attempts": context.get("attempts", 0),
            "difficulty": context.get("difficulty", "unknown"),
        },
    }
