"""
Sistema de LLM do t031a5.

Integração com diferentes provedores de LLM para processamento de linguagem natural.
"""

from .provider import LLMProvider
from .providers.mock_provider import MockLLMProvider

__all__ = [
    "LLMProvider",
    "MockLLMProvider",
]
