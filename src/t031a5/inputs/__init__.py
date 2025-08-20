"""
Sistema de inputs do t031a5.

Plugins de entrada específicos para o G1:
- G1Voice: Reconhecimento de voz
- G1Vision: Processamento de visão
- G1Sensors: Monitoramento de sensores
- G1GPS: Localização
- G1State: Estado interno do robô
"""

from .base import BaseInput
from .plugins.g1_voice import G1VoiceInput
from .plugins.g1_vision import G1VisionInput
from .plugins.g1_sensors import G1SensorsInput
from .plugins.g1_gps import G1GPSInput
from .plugins.g1_state import G1StateInput

__all__ = [
    "BaseInput",
    "G1VoiceInput",
    "G1VisionInput", 
    "G1SensorsInput",
    "G1GPSInput",
    "G1StateInput",
]
