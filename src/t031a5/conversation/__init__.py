"""
Sistema de Conversação Multimodal para G1.

Integra visão, áudio, fala e gestos de forma sincronizada.
"""

from .engine import ConversationEngine, ConversationState, EmotionLevel, ConversationContext, ConversationResponse

__all__ = [
    "ConversationEngine",
    "ConversationState", 
    "EmotionLevel",
    "ConversationContext",
    "ConversationResponse"
]
