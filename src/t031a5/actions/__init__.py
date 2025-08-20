"""
Sistema de actions do t031a5.

Plugins de ação específicos para o G1:
- G1Speech: Síntese de voz
- G1Emotion: Expressões emocionais
- G1Movement: Locomoção
- G1Arms: Ações dos braços
- G1Audio: Reprodução de áudio
"""

from .base import BaseAction
from .g1_speech import G1SpeechAction
from .g1_emotion import G1EmotionAction
from .g1_movement import G1MovementAction
from .g1_arms import G1ArmsAction
from .g1_audio import G1AudioAction

__all__ = [
    "BaseAction",
    "G1SpeechAction",
    "G1EmotionAction", 
    "G1MovementAction",
    "G1ArmsAction",
    "G1AudioAction",
]
