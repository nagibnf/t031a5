"""
Plugins de input específicos do G1.
"""

from .g1_voice import G1VoiceInput
from .g1_vision_d435i import G1VisionInput
from .g1_state import G1StateInput

__all__ = [
    "G1VoiceInput",
    "G1VisionInput", 
    "G1StateInput",
]
