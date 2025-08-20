"""
Sistema de fusão de inputs do t031a5.

Responsável por combinar e priorizar múltiplos inputs do G1.
"""

from .base import BaseFuser
from .priority import PriorityFuser
from .multimodal import MultimodalFuser

__all__ = [
    "BaseFuser",
    "PriorityFuser", 
    "MultimodalFuser",
]
