"""
Plugins de input específicos do G1.
"""

from .g1_voice import G1VoiceInput
from .g1_vision import G1VisionInput
from .g1_sensors import G1SensorsInput
from .g1_gps import G1GPSInput
from .g1_state import G1StateInput

__all__ = [
    "G1VoiceInput",
    "G1VisionInput", 
    "G1SensorsInput",
    "G1GPSInput",
    "G1StateInput",
]
