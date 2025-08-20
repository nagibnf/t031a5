"""
Conectores nativos do G1.
Plugins opcionais para usar capacidades nativas do robô.
"""

from .g1_native_tts import G1NativeTTSConnector, TTSRequest, TTSResponse
from .g1_native_leds import G1NativeLEDConnector, LEDRequest, LEDResponse
from .g1_native_audio import G1NativeAudioConnector, AudioRequest, AudioResponse
from .elevenlabs_tts import ElevenLabsTTSConnector, ElevenLabsTTSRequest, ElevenLabsTTSResponse, ElevenLabsVoice

__all__ = [
    "G1NativeTTSConnector",
    "TTSRequest", 
    "TTSResponse",
    "G1NativeLEDConnector",
    "LEDRequest",
    "LEDResponse", 
    "G1NativeAudioConnector",
    "AudioRequest",
    "AudioResponse",
    "ElevenLabsTTSConnector",
    "ElevenLabsTTSRequest",
    "ElevenLabsTTSResponse",
    "ElevenLabsVoice"
]
