"""
Claude AI Client for Anthropic's Claude models (Haiku and Sonnet)
Handles API communication and streaming responses
"""

import logging
from collections.abc import AsyncGenerator

from anthropic import AsyncAnthropic

from ..config import settings

logger = logging.getLogger(__name__)


class ClaudeService:
    """Service for Claude AI models via Anthropic API"""

    def __init__(self):
        self.client = AsyncAnthropic(
            api_key=settings.anthropic_api_key, timeout=settings.ai_default_timeout
        )

    async def health_check(self) -> bool:
        """Check if Claude API is accessible"""
        try:
            # Simple test request to verify API key and connectivity
            response = await self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}],
            )
            return True
        except Exception as e:
            logger.error(f"Claude health check failed: {e}")
            return False

    async def generate_response(
        self,
        prompt: str,
        system_prompt: str | None = None,
        model: str = "claude-3-haiku-20240307",
        max_tokens: int = 4000,
        temperature: float = 0.7,
    ) -> str:
        """Generate a complete response from Claude"""
        try:
            messages = [{"role": "user", "content": prompt}]

            kwargs = {
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages,
            }

            if system_prompt:
                kwargs["system"] = system_prompt

            response = await self.client.messages.create(**kwargs)
            return response.content[0].text

        except Exception as e:
            logger.error(f"Claude generation failed: {e}")
            raise Exception(f"Failed to generate response: {e!s}")

    async def stream_response(
        self,
        prompt: str,
        system_prompt: str | None = None,
        model: str = "claude-3-haiku-20240307",
        max_tokens: int = 4000,
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        """Stream response chunks from Claude"""
        try:
            messages = [{"role": "user", "content": prompt}]

            kwargs = {
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages,
            }

            if system_prompt:
                kwargs["system"] = system_prompt

            async with self.client.messages.stream(**kwargs) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error(f"Claude streaming failed: {e}")
            yield f"Error: {e!s}"

    async def count_tokens(
        self, text: str, model: str = "claude-3-haiku-20240307"
    ) -> int:
        """Count tokens for Claude models"""
        try:
            # Use Anthropic's token counting
            response = await self.client.messages.count_tokens(
                model=model, messages=[{"role": "user", "content": text}]
            )
            return response.input_tokens
        except Exception as e:
            logger.warning(f"Token counting failed, using approximation: {e}")
            # Fallback: rough approximation (1 token ≈ 1.3 words for Claude)
            word_count = len(text.split())
            return int(word_count * 1.3)

    def get_model_info(self, model: str = "claude-3-haiku-20240307") -> dict:
        """Get information about Claude model"""
        model_configs = {
            "claude-3-haiku-20240307": {
                "name": "Claude 3 Haiku",
                "type": "cloud",
                "provider": "anthropic",
                "context_window": 200000,
                "capabilities": ["chat", "streaming", "reasoning", "analysis"],
                "tier": "haiku",
            },
            "claude-3-5-sonnet-20241022": {
                "name": "Claude 3.5 Sonnet",
                "type": "cloud",
                "provider": "anthropic",
                "context_window": 200000,
                "capabilities": [
                    "chat",
                    "streaming",
                    "reasoning",
                    "analysis",
                    "coding",
                ],
                "tier": "sonnet",
            },
        }

        return model_configs.get(
            model,
            {
                "name": "Unknown Claude Model",
                "type": "cloud",
                "provider": "anthropic",
                "context_window": 200000,
                "capabilities": ["chat"],
                "tier": "unknown",
            },
        )


# Global service instance
claude_service = ClaudeService()
