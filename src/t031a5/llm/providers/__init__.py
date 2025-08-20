"""
Provedores de LLM para o sistema t031a5.
"""

from .mock_provider import MockLLMProvider

# Provedores reais (opcionais)
try:
    from .openai_provider import OpenAIProvider
    OPENAI_AVAILABLE = True
except ImportError:
    OpenAIProvider = None
    OPENAI_AVAILABLE = False

try:
    from .anthropic_provider import AnthropicProvider
    ANTHROPIC_AVAILABLE = True
except ImportError:
    AnthropicProvider = None
    ANTHROPIC_AVAILABLE = False

__all__ = [
    "MockLLMProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "OPENAI_AVAILABLE",
    "ANTHROPIC_AVAILABLE",
]
