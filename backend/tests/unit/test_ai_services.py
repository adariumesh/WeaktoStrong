"""
Unit tests for AI services
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4

from app.core.ai.prompt_validator import PromptValidator, validate_prompt
from app.core.ai.model_router import ModelTierRouter
from app.schemas.ai_schemas import AIRequest, ModelTier, ValidationResult
from app.models.user import User, UserTier


class TestPromptValidator:
    """Test cases for PromptValidator"""

    @pytest.fixture
    def validator(self):
        """Create a PromptValidator instance"""
        return PromptValidator()

    @pytest.mark.unit
    def test_valid_prompt_with_reasoning(self, validator):
        """Test prompt validation with proper reasoning indicators"""
        valid_prompts = [
            "I think the approach should be to use a loop because it's more efficient",
            "My strategy is to break this down since it's a complex problem",
            "The goal is to optimize this function as it needs better performance",
        ]

        for prompt in valid_prompts:
            result = validator.validate(prompt)
            assert result.is_valid == True
            assert result.confidence_score >= 0.7

    @pytest.mark.unit
    def test_invalid_prompt_lazy_patterns(self, validator):
        """Test prompt validation rejects lazy patterns"""
        lazy_prompts = [
            "just fix this code",
            "make it work",
            "write the function for me",
            "generate the solution",
        ]

        for prompt in lazy_prompts:
            result = validator.validate(prompt)
            assert result.is_valid == False
            assert "appears to be asking for a complete solution" in result.feedback

    @pytest.mark.unit
    def test_prompt_too_short(self, validator):
        """Test validation fails for too short prompts"""
        short_prompt = "help"

        result = validator.validate(short_prompt)
        assert result.is_valid == False
        assert "too short" in result.feedback

    @pytest.mark.unit
    def test_prompt_confidence_scoring(self, validator):
        """Test confidence scoring based on reasoning indicators"""
        high_confidence_prompt = (
            "My approach is to use recursion because the problem has a clear base case. "
            "I think this strategy will work since we need to traverse the tree structure."
        )

        low_confidence_prompt = "I want to solve this problem"

        high_result = validator.validate(high_confidence_prompt)
        low_result = validator.validate(low_confidence_prompt)

        assert high_result.confidence_score > low_result.confidence_score

    @pytest.mark.unit
    def test_validate_prompt_function(self):
        """Test the standalone validate_prompt function"""
        good_prompt = "I believe the approach should be to use async/await because it handles concurrency better"
        bad_prompt = "fix this"

        good_result = validate_prompt(good_prompt)
        bad_result = validate_prompt(bad_prompt)

        assert isinstance(good_result, ValidationResult)
        assert good_result.is_valid == True
        assert bad_result.is_valid == False


class TestModelTierRouter:
    """Test cases for ModelTierRouter"""

    @pytest.fixture
    def router(self):
        """Create a ModelTierRouter instance"""
        return ModelTierRouter()

    @pytest.fixture
    def mock_user_free(self):
        """Create a mock free tier user"""
        user = Mock(spec=User)
        user.id = uuid4()
        user.subscription_tier = "free"
        return user

    @pytest.fixture
    def mock_user_pro(self):
        """Create a mock pro tier user"""
        user = Mock(spec=User)
        user.id = uuid4()
        user.subscription_tier = "pro"
        return user

    @pytest.mark.unit
    async def test_get_allowed_tier_free_user_no_challenges(
        self, router, mock_user_free
    ):
        """Test tier calculation for free user with no completed challenges"""
        with patch.object(router, "_count_completed_challenges", return_value=0):
            tier = await router.get_allowed_tier(mock_user_free)
            assert tier == ModelTier.LOCAL

    @pytest.mark.unit
    async def test_get_allowed_tier_free_user_haiku_unlock(
        self, router, mock_user_free
    ):
        """Test tier calculation for free user with enough challenges for Haiku"""
        with patch.object(router, "_count_completed_challenges", return_value=15):
            tier = await router.get_allowed_tier(mock_user_free)
            assert tier == ModelTier.HAIKU

    @pytest.mark.unit
    async def test_get_allowed_tier_pro_user_sonnet_unlock(self, router, mock_user_pro):
        """Test tier calculation for pro user with enough challenges for Sonnet"""
        with patch.object(router, "_count_completed_challenges", return_value=30):
            tier = await router.get_allowed_tier(mock_user_pro)
            assert tier == ModelTier.SONNET

    @pytest.mark.unit
    async def test_get_allowed_tier_pro_user_insufficient_challenges(
        self, router, mock_user_pro
    ):
        """Test tier calculation for pro user without enough challenges for Sonnet"""
        with patch.object(router, "_count_completed_challenges", return_value=5):
            tier = await router.get_allowed_tier(mock_user_pro)
            assert tier == ModelTier.LOCAL

    @pytest.mark.unit
    async def test_tier_progression_requirements(self, router):
        """Test tier requirement configuration"""
        requirements = router.tier_requirements

        assert requirements[ModelTier.LOCAL]["min_challenges_completed"] == 0
        assert requirements[ModelTier.HAIKU]["min_challenges_completed"] == 10
        assert requirements[ModelTier.SONNET]["min_challenges_completed"] == 25
        assert requirements[ModelTier.SONNET].get("requires_pro") == True

    @pytest.mark.unit
    async def test_get_tier_progress_local_to_haiku(self, router, mock_user_free):
        """Test progress calculation from local to haiku tier"""
        with patch.object(router, "_count_completed_challenges", return_value=5):
            progress = await router.get_tier_progress(mock_user_free, ModelTier.LOCAL)

            assert progress["current_tier"] == "local"
            assert progress["next_tier"] == "haiku"
            assert progress["progress"] == 5
            assert progress["required"] == 10
            assert progress["percentage"] == 50.0

    @pytest.mark.unit
    async def test_get_tier_progress_haiku_to_sonnet(self, router, mock_user_free):
        """Test progress calculation from haiku to sonnet tier"""
        with patch.object(router, "_count_completed_challenges", return_value=15):
            progress = await router.get_tier_progress(mock_user_free, ModelTier.HAIKU)

            assert progress["current_tier"] == "haiku"
            assert progress["next_tier"] == "sonnet"
            assert progress["progress"] == 15
            assert progress["required"] == 25
            assert progress["requires_pro"] == True

    @pytest.mark.unit
    async def test_get_tier_progress_max_tier(self, router, mock_user_pro):
        """Test progress calculation for max tier (Sonnet)"""
        with patch.object(router, "_count_completed_challenges", return_value=50):
            progress = await router.get_tier_progress(mock_user_pro, ModelTier.SONNET)

            assert progress["current_tier"] == "sonnet"
            assert progress["next_tier"] == None
            assert progress["percentage"] == 100

    @pytest.mark.unit
    @patch("app.core.ai.model_router.local_llm_service")
    @patch("app.core.ai.model_router.validate_prompt")
    async def test_route_request_validation_success(
        self, mock_validate, mock_llm, router, mock_user_free
    ):
        """Test routing request with successful validation"""
        # Setup mocks
        mock_validate.return_value = Mock(is_valid=True)
        mock_llm.stream_response.return_value = AsyncMock()
        mock_llm.stream_response.return_value.__aiter__.return_value = [
            "response",
            "chunks",
        ]

        request = Mock(spec=AIRequest)
        request.prompt = "I think the approach should be to use a function"
        request.preferred_tier = ModelTier.LOCAL
        request.enforce_validation = True
        request.challenge_context = {}
        request.temperature = 0.7
        request.max_tokens = 1000

        with patch.object(router, "get_allowed_tier", return_value=ModelTier.LOCAL):
            with patch.object(
                router, "_build_system_prompt", return_value="System prompt"
            ):
                chunks = []
                async for chunk in router.route_request(request, mock_user_free):
                    chunks.append(chunk)

                assert len(chunks) > 0
                assert any("Local AI" in chunk for chunk in chunks)

    @pytest.mark.unit
    @patch("app.core.ai.model_router.validate_prompt")
    async def test_route_request_validation_failure(
        self, mock_validate, router, mock_user_free
    ):
        """Test routing request with failed validation"""
        mock_validate.return_value = Mock(
            is_valid=False,
            feedback="Prompt appears to be asking for a complete solution",
        )

        request = Mock(spec=AIRequest)
        request.prompt = "just fix this"
        request.enforce_validation = True
        request.challenge_context = {}

        chunks = []
        async for chunk in router.route_request(request, mock_user_free):
            chunks.append(chunk)

        assert len(chunks) == 1
        assert "❌" in chunks[0]
        assert "complete solution" in chunks[0]

    @pytest.mark.unit
    def test_build_system_prompt_basic(self, router):
        """Test building system prompt with basic request"""
        request = Mock(spec=AIRequest)
        request.challenge_context = None

        prompt = router._build_system_prompt(request)

        assert "Weak-to-Strong platform" in prompt
        assert "helpful guidance" in prompt
        assert "step by step" in prompt

    @pytest.mark.unit
    def test_build_system_prompt_with_context(self, router):
        """Test building system prompt with challenge context"""
        request = Mock(spec=AIRequest)
        request.challenge_context = {
            "title": "Array Sum Challenge",
            "track": "algorithms",
            "difficulty": "beginner",
            "points": 100,
            "requirements": ["Handle empty arrays", "Return integer sum"],
            "user_code": "function sum(arr) {\n  // TODO\n}",
            "language": "javascript",
            "last_test_results": {
                "passed": 2,
                "total": 5,
                "failures": "Empty array test failed",
            },
        }

        prompt = router._build_system_prompt(request)

        assert "Array Sum Challenge" in prompt
        assert "algorithms" in prompt
        assert "beginner" in prompt
        assert "function sum(arr)" in prompt
        assert "2/5 tests passed" in prompt
        assert "Empty array test failed" in prompt
