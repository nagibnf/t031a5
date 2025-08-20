"""
Conector nativo TTS do G1.
Permite usar o TTS nativo do robô quando disponível.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TTSRequest:
    """Requisição de TTS."""
    text: str
    speaker_id: int = 0
    emotion: Optional[str] = None
    speed: float = 1.0
    volume: float = 1.0


@dataclass
class TTSResponse:
    """Resposta de TTS."""
    success: bool
    error_message: Optional[str] = None
    duration: Optional[float] = None


class G1NativeTTSConnector:
    """Conector para TTS nativo do G1."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", True)
        self.g1_controller = None
        self.logger = logging.getLogger(__name__)
        
        # Configurações específicas
        self.default_speaker_id = config.get("default_speaker_id", 0)
        self.timeout = config.get("timeout", 10.0)
        self.retry_attempts = config.get("retry_attempts", 3)
        
        self.logger.info(f"G1NativeTTSConnector inicializado: enabled={self.enabled}")
    
    async def initialize(self, g1_controller) -> bool:
        """Inicializa o conector com o controlador G1."""
        if not self.enabled:
            self.logger.info("G1NativeTTSConnector desabilitado")
            return False
        
        self.g1_controller = g1_controller
        
        # Verifica se o TTS nativo está disponível
        if hasattr(self.g1_controller, 'tts_maker'):
            self.logger.info("✅ TTS nativo do G1 disponível")
            return True
        else:
            self.logger.warning("❌ TTS nativo do G1 não disponível")
            return False
    
    async def speak(self, request: TTSRequest) -> TTSResponse:
        """Executa síntese de voz usando TTS nativo do G1."""
        if not self.enabled or not self.g1_controller:
            return TTSResponse(
                success=False,
                error_message="G1NativeTTSConnector não inicializado"
            )
        
        try:
            self.logger.debug(f"TTS Nativo: '{request.text}' (speaker_id={request.speaker_id})")
            
            # Usa TTS nativo do G1
            code = self.g1_controller.tts_maker(
                request.text, 
                request.speaker_id or self.default_speaker_id
            )
            
            if code == 0:
                self.logger.info(f"✅ TTS Nativo executado: '{request.text[:50]}...'")
                return TTSResponse(success=True, duration=len(request.text) * 0.1)
            else:
                self.logger.error(f"❌ Erro no TTS Nativo: código {code}")
                return TTSResponse(
                    success=False,
                    error_message=f"Erro no TTS nativo: código {code}"
                )
                
        except Exception as e:
            self.logger.error(f"❌ Exceção no TTS Nativo: {e}")
            return TTSResponse(
                success=False,
                error_message=f"Exceção: {str(e)}"
            )
    
    async def is_available(self) -> bool:
        """Verifica se o TTS nativo está disponível."""
        return (
            self.enabled and 
            self.g1_controller and 
            hasattr(self.g1_controller, 'tts_maker')
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Retorna capacidades do conector."""
        return {
            "name": "G1NativeTTS",
            "enabled": self.enabled,
            "available": self.g1_controller is not None,
            "native_tts": hasattr(self.g1_controller, 'tts_maker') if self.g1_controller else False,
            "features": ["text_to_speech", "native_hardware", "low_latency"]
        }
