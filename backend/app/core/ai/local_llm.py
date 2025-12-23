"""
Local LLM Integration using Ollama
Handles Llama 3.2 8B model for local AI inference
"""

import logging
from collections.abc import AsyncGenerator
from typing import Any

import ollama

from ..config import settings

logger = logging.getLogger(__name__)


class LocalLLMService:
    """Service for local LLM inference using Ollama"""

    def __init__(self):
        self.client = ollama.AsyncClient(
            host=settings.OLLAMA_BASE_URL, timeout=settings.AI_DEFAULT_TIMEOUT
        )
        self.model = settings.OLLAMA_MODEL

    async def health_check(self) -> bool:
        """Check if Ollama service is healthy and model is available"""
        try:
            models = await self.client.list()
            available_models = [model["name"] for model in models["models"]]
            return self.model in available_models
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False

    async def ensure_model_available(self) -> bool:
        """Pull the model if it's not available locally"""
        try:
            models = await self.client.list()
            available_models = [model["name"] for model in models["models"]]

            if self.model not in available_models:
                logger.info(f"Pulling model {self.model}...")
                await self.client.pull(self.model)
                logger.info(f"Model {self.model} pulled successfully")

            return True
        except Exception as e:
            logger.error(f"Failed to ensure model availability: {e}")
            return False

    async def generate_response(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 4000,
        temperature: float = 0.7,
    ) -> str:
        """Generate a complete response from the local LLM"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = await self.client.chat(
                model=self.model,
                messages=messages,
                options={"temperature": temperature, "num_predict": max_tokens},
            )

            return response["message"]["content"]

        except Exception as e:
            logger.error(f"Local LLM generation failed: {e}")
            raise Exception(f"Failed to generate response: {e!s}")

    async def stream_response(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 4000,
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        """Stream response chunks from the local LLM"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            stream = await self.client.chat(
                model=self.model,
                messages=messages,
                stream=True,
                options={"temperature": temperature, "num_predict": max_tokens},
            )

            async for chunk in stream:
                if chunk["message"]["content"]:
                    yield chunk["message"]["content"]

        except Exception as e:
            logger.error(f"Local LLM streaming failed: {e}")
            yield f"Error: {e!s}"

    async def count_tokens(self, text: str) -> int:
        """Estimate token count for the local model"""
        # Rough approximation: 1 token ≈ 1.3 words for Llama models
        word_count = len(text.split())
        return int(word_count * 1.3)

    def get_model_info(self) -> dict[str, Any]:
        """Get information about the current local model"""
        return {
            "name": self.model,
            "type": "local",
            "provider": "ollama",
            "context_window": 32768,  # Llama 3.2 context window
            "capabilities": ["chat", "streaming", "reasoning"],
            "tier": "local",
        }


# Global service instance
local_llm_service = LocalLLMService()
