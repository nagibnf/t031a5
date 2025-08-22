"""
Conectores nativos do G1.
Plugins opcionais para usar capacidades nativas do robô.
"""

# Conectores nativos G1
from .g1_native_tts import G1NativeTTSConnector, TTSRequest, TTSResponse
from .g1_native_leds import G1NativeLEDConnector, LEDRequest, LEDResponse
from .g1_native_audio import G1NativeAudioConnector, AudioRequest, AudioResponse

# Conectores testados para hardware real
from .elevenlabs_tts import ElevenLabsTTSConnector, ElevenLabsTTSRequest, ElevenLabsTTSResponse, ElevenLabsVoice
from .audio_player import AudioPlayerConnector
from .audio_capture import AudioCaptureConnector
from .vision_capture import VisionCaptureConnector
from .g1_network import G1NetworkConnector

__all__ = [
    # Conectores nativos G1
    "G1NativeTTSConnector",
    "TTSRequest", 
    "TTSResponse",
    "G1NativeLEDConnector",
    "LEDRequest",
    "LEDResponse", 
    "G1NativeAudioConnector",
    "AudioRequest",
    "AudioResponse",
    
    # Conectores testados
    "ElevenLabsTTSConnector",
    "ElevenLabsTTSRequest",
    "ElevenLabsTTSResponse",
    "ElevenLabsVoice",
    "AudioPlayerConnector",
    "AudioCaptureConnector", 
    "VisionCaptureConnector",
    "G1NetworkConnector"
]
