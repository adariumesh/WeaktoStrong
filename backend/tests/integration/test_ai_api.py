"""
Integration tests for AI API endpoints
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from unittest.mock import patch, Mock, AsyncMock

from app.models.user import User, UserTier
from app.core.auth import get_password_hash


class TestAIAPI:
    """Integration tests for AI endpoints"""

    @pytest_asyncio.fixture
    async def authenticated_user(self, test_db_session) -> tuple[User, str]:
        """Create an authenticated user and return user and token"""
        user = User(
            email="aiuser@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="AI User",
            tier=UserTier.FREE,
            subscription_tier="free",
        )
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Create mock token for testing
        from app.core.auth import create_session_tokens

        tokens = create_session_tokens(str(user.id))
        return user, tokens["access_token"]

    @pytest.mark.integration
    async def test_ai_status_endpoint(self, client: AsyncClient, authenticated_user):
        """Test AI service status endpoint"""
        user, token = authenticated_user

        with patch(
            "app.core.ai.local_llm.local_llm_service.health_check", return_value=True
        ):
            with patch(
                "app.core.ai.claude_client.claude_service.health_check",
                return_value=True,
            ):
                response = await client.get(
                    "/api/v1/ai/status", headers={"Authorization": f"Bearer {token}"}
                )

        assert response.status_code == 200
        data = response.json()
        assert "local_available" in data
        assert "claude_available" in data
        assert "current_tier" in data
        assert "daily_tokens_used" in data
        assert "daily_token_limit" in data

    @pytest.mark.integration
    async def test_ai_status_unauthorized(self, client: AsyncClient):
        """Test AI status endpoint without authentication"""
        response = await client.get("/api/v1/ai/status")
        assert response.status_code == 401

    @pytest.mark.integration
    async def test_validate_prompt_endpoint(
        self, client: AsyncClient, authenticated_user
    ):
        """Test prompt validation endpoint"""
        user, token = authenticated_user

        # Test valid prompt
        valid_prompt = {
            "prompt": "I think the approach should be to use a loop because it's more efficient"
        }

        response = await client.post(
            "/api/v1/ai/validate-prompt",
            json=valid_prompt,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "is_valid" in data
        assert "feedback" in data
        assert data["is_valid"] == True

    @pytest.mark.integration
    async def test_validate_prompt_invalid(
        self, client: AsyncClient, authenticated_user
    ):
        """Test prompt validation with invalid prompt"""
        user, token = authenticated_user

        # Test invalid prompt
        invalid_prompt = {"prompt": "just fix this code"}

        response = await client.post(
            "/api/v1/ai/validate-prompt",
            json=invalid_prompt,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] == False
        assert "complete solution" in data["feedback"]

    @pytest.mark.integration
    async def test_validate_prompt_missing_prompt(
        self, client: AsyncClient, authenticated_user
    ):
        """Test prompt validation with missing prompt"""
        user, token = authenticated_user

        response = await client.post(
            "/api/v1/ai/validate-prompt",
            json={},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 400

    @pytest.mark.integration
    @patch("app.core.ai.model_router.model_router.route_request")
    async def test_ai_chat_endpoint(
        self, mock_route_request, client: AsyncClient, authenticated_user
    ):
        """Test AI chat endpoint"""
        user, token = authenticated_user

        # Mock the AI response
        async def mock_response():
            yield "This is a test response"

        mock_route_request.return_value = mock_response()

        chat_request = {
            "prompt": "I think the approach should be to use recursion because it simplifies the problem",
            "preferred_tier": "local",
            "temperature": 0.7,
            "max_tokens": 1000,
            "enforce_validation": False,
        }

        response = await client.post(
            "/api/v1/ai/chat",
            json=chat_request,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert "model_used" in data
        assert "tokens_used" in data
        assert "tier" in data

    @pytest.mark.integration
    async def test_ai_chat_validation_failure(
        self, client: AsyncClient, authenticated_user
    ):
        """Test AI chat with validation failure"""
        user, token = authenticated_user

        chat_request = {
            "prompt": "just fix this",
            "preferred_tier": "local",
            "enforce_validation": True,
        }

        response = await client.post(
            "/api/v1/ai/chat",
            json=chat_request,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 400
        assert "complete solution" in response.json()["detail"]

    @pytest.mark.integration
    async def test_ai_models_endpoint(self, client: AsyncClient, authenticated_user):
        """Test available AI models endpoint"""
        user, token = authenticated_user

        with patch(
            "app.core.ai.local_llm.local_llm_service.get_model_info",
            return_value={"name": "Local LLM"},
        ):
            with patch(
                "app.core.ai.claude_client.claude_service.health_check",
                return_value=True,
            ):
                response = await client.get(
                    "/api/v1/ai/models", headers={"Authorization": f"Bearer {token}"}
                )

        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert "current_tier" in data
        assert "tier_progress" in data
        assert len(data["models"]) >= 1  # At least local model

    @pytest.mark.integration
    async def test_ai_tiers_endpoint(self, client: AsyncClient, authenticated_user):
        """Test AI tiers information endpoint"""
        user, token = authenticated_user

        response = await client.get(
            "/api/v1/ai/tiers", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "tiers" in data
        assert "current" in data
        assert "unlock_next" in data

        # Verify tier structure
        tiers = data["tiers"]
        tier_names = [tier["name"] for tier in tiers]
        assert "local" in tier_names
        assert "haiku" in tier_names
        assert "sonnet" in tier_names

    @pytest.mark.integration
    async def test_ai_usage_endpoint(self, client: AsyncClient, authenticated_user):
        """Test AI token usage endpoint"""
        user, token = authenticated_user

        response = await client.get(
            "/api/v1/ai/usage", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "daily" in data
        assert "weekly" in data
        assert "monthly_total" in data
        assert "tier" in data
        assert "breakdown_by_model" in data

        # Verify daily usage structure
        daily = data["daily"]
        assert "usage" in daily
        assert "limit" in daily
        assert "remaining" in daily
        assert "percentage_used" in daily

    @pytest.mark.integration
    @patch(
        "app.core.ai.challenge_context.challenge_context_service.get_challenge_context"
    )
    async def test_ai_context_endpoint(
        self, mock_get_context, client: AsyncClient, authenticated_user
    ):
        """Test AI challenge context endpoint"""
        user, token = authenticated_user

        # Mock the context response
        mock_context = {
            "title": "Test Challenge",
            "difficulty": "beginner",
            "user_code": "function test() {}",
            "attempts": 3,
        }
        mock_get_context.return_value = mock_context

        response = await client.get(
            "/api/v1/ai/context/test-challenge-1",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "challenge_context" in data
        assert "user_progress" in data
        assert "ai_tier_available" in data

    @pytest.mark.integration
    @patch("app.core.ai.hint_generator.hint_generator.generate_contextual_hints")
    @patch(
        "app.core.ai.challenge_context.challenge_context_service.get_challenge_context"
    )
    async def test_ai_hints_endpoint(
        self,
        mock_get_context,
        mock_generate_hints,
        client: AsyncClient,
        authenticated_user,
    ):
        """Test AI smart hints endpoint"""
        user, token = authenticated_user

        # Mock the context and hints
        mock_get_context.return_value = {
            "title": "Test Challenge",
            "user_code": "function test() {}",
            "last_test_results": {"passed": 2, "total": 5},
        }

        mock_generate_hints.return_value = [
            {
                "type": "debugging",
                "priority": "high",
                "title": "Check edge cases",
                "message": "Your function doesn't handle empty inputs",
                "category": "debugging",
            }
        ]

        response = await client.post(
            "/api/v1/ai/hints/test-challenge-1",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "challenge_id" in data
        assert "hints" in data
        assert "context_summary" in data
        assert len(data["hints"]) >= 1
        assert data["hints"][0]["priority"] == "high"

    @pytest.mark.integration
    async def test_ai_chat_stream_endpoint(
        self, client: AsyncClient, authenticated_user
    ):
        """Test AI chat streaming endpoint"""
        user, token = authenticated_user

        chat_request = {
            "prompt": "I think the approach should be to use a for loop because it's straightforward",
            "preferred_tier": "local",
            "temperature": 0.7,
            "max_tokens": 100,
            "enforce_validation": False,
        }

        with patch("app.core.ai.model_router.model_router.route_request") as mock_route:
            # Mock streaming response
            async def mock_stream():
                yield "Chunk 1"
                yield "Chunk 2"

            mock_route.return_value = mock_stream()

            response = await client.post(
                "/api/v1/ai/chat/stream",
                json=chat_request,
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    @pytest.mark.integration
    async def test_ai_endpoints_require_auth(self, client: AsyncClient):
        """Test that all AI endpoints require authentication"""
        endpoints = [
            ("GET", "/api/v1/ai/status"),
            ("POST", "/api/v1/ai/validate-prompt"),
            ("POST", "/api/v1/ai/chat"),
            ("POST", "/api/v1/ai/chat/stream"),
            ("GET", "/api/v1/ai/models"),
            ("GET", "/api/v1/ai/tiers"),
            ("GET", "/api/v1/ai/usage"),
            ("GET", "/api/v1/ai/context/test-challenge"),
            ("POST", "/api/v1/ai/hints/test-challenge"),
        ]

        for method, endpoint in endpoints:
            if method == "GET":
                response = await client.get(endpoint)
            else:
                response = await client.post(endpoint, json={})

            assert (
                response.status_code == 401
            ), f"Endpoint {method} {endpoint} should require auth"
