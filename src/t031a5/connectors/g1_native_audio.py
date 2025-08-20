"""
Conector nativo controle de áudio do G1.
Permite controlar volume e reprodução de áudio nativo.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AudioRequest:
    """Requisição de controle de áudio."""
    volume: Optional[int] = None
    play_stream: Optional[bytes] = None
    stream_id: Optional[str] = None
    app_name: Optional[str] = None
    stop_play: bool = False


@dataclass
class AudioResponse:
    """Resposta de controle de áudio."""
    success: bool
    error_message: Optional[str] = None
    current_volume: Optional[int] = None


class G1NativeAudioConnector:
    """Conector para controle de áudio nativo do G1."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", True)
        self.g1_controller = None
        self.logger = logging.getLogger(__name__)
        
        # Configurações específicas
        self.default_volume = config.get("default_volume", 50)
        self.max_volume = config.get("max_volume", 100)
        self.min_volume = config.get("min_volume", 0)
        
        self.logger.info(f"G1NativeAudioConnector inicializado: enabled={self.enabled}")
    
    async def initialize(self, g1_controller) -> bool:
        """Inicializa o conector com o controlador G1."""
        if not self.enabled:
            self.logger.info("G1NativeAudioConnector desabilitado")
            return False
        
        self.g1_controller = g1_controller
        
        # Verifica se o controle de áudio nativo está disponível
        if (hasattr(self.g1_controller, 'set_volume') and 
            hasattr(self.g1_controller, 'get_volume')):
            self.logger.info("✅ Controle de áudio nativo do G1 disponível")
            return True
        else:
            self.logger.warning("❌ Controle de áudio nativo do G1 não disponível")
            return False
    
    async def set_volume(self, volume: int) -> AudioResponse:
        """Define volume usando controle nativo do G1."""
        if not self.enabled or not self.g1_controller:
            return AudioResponse(
                success=False,
                error_message="G1NativeAudioConnector não inicializado"
            )
        
        try:
            # Valida volume
            volume = max(self.min_volume, min(self.max_volume, volume))
            
            self.logger.debug(f"Áudio Nativo: Definindo volume {volume}")
            
            # Usa controle nativo de volume do G1
            code = self.g1_controller.set_volume(volume)
            
            if code == 0:
                self.logger.info(f"✅ Volume Nativo definido: {volume}")
                return AudioResponse(success=True, current_volume=volume)
            else:
                self.logger.error(f"❌ Erro no Volume Nativo: código {code}")
                return AudioResponse(
                    success=False,
                    error_message=f"Erro no volume nativo: código {code}"
                )
                
        except Exception as e:
            self.logger.error(f"❌ Exceção no Volume Nativo: {e}")
            return AudioResponse(
                success=False,
                error_message=f"Exceção: {str(e)}"
            )
    
    async def get_volume(self) -> AudioResponse:
        """Obtém volume atual usando controle nativo do G1."""
        if not self.enabled or not self.g1_controller:
            return AudioResponse(
                success=False,
                error_message="G1NativeAudioConnector não inicializado"
            )
        
        try:
            self.logger.debug("Áudio Nativo: Obtendo volume atual")
            
            # Usa controle nativo de volume do G1
            code, data = self.g1_controller.get_volume()
            
            if code == 0 and data:
                volume = data.get("volume", 0)
                self.logger.info(f"✅ Volume Nativo atual: {volume}")
                return AudioResponse(success=True, current_volume=volume)
            else:
                self.logger.error(f"❌ Erro ao obter Volume Nativo: código {code}")
                return AudioResponse(
                    success=False,
                    error_message=f"Erro ao obter volume nativo: código {code}"
                )
                
        except Exception as e:
            self.logger.error(f"❌ Exceção ao obter Volume Nativo: {e}")
            return AudioResponse(
                success=False,
                error_message=f"Exceção: {str(e)}"
            )
    
    async def play_stream(self, pcm_data: bytes, app_name: str = "t031a5", stream_id: str = "default") -> AudioResponse:
        """Reproduz stream de áudio usando controle nativo do G1."""
        if not self.enabled or not self.g1_controller:
            return AudioResponse(
                success=False,
                error_message="G1NativeAudioConnector não inicializado"
            )
        
        try:
            self.logger.debug(f"Áudio Nativo: Reproduzindo stream {stream_id}")
            
            # Usa controle nativo de reprodução do G1
            if hasattr(self.g1_controller, 'play_stream'):
                code = self.g1_controller.play_stream(app_name, stream_id, pcm_data)
                
                if code == 0:
                    self.logger.info(f"✅ Stream Nativo iniciado: {stream_id}")
                    return AudioResponse(success=True)
                else:
                    self.logger.error(f"❌ Erro no Stream Nativo: código {code}")
                    return AudioResponse(
                        success=False,
                        error_message=f"Erro no stream nativo: código {code}"
                    )
            else:
                return AudioResponse(
                    success=False,
                    error_message="Reprodução de stream não disponível"
                )
                
        except Exception as e:
            self.logger.error(f"❌ Exceção no Stream Nativo: {e}")
            return AudioResponse(
                success=False,
                error_message=f"Exceção: {str(e)}"
            )
    
    async def stop_play(self, app_name: str = "t031a5") -> AudioResponse:
        """Para reprodução de áudio usando controle nativo do G1."""
        if not self.enabled or not self.g1_controller:
            return AudioResponse(
                success=False,
                error_message="G1NativeAudioConnector não inicializado"
            )
        
        try:
            self.logger.debug(f"Áudio Nativo: Parando reprodução {app_name}")
            
            # Usa controle nativo de parada do G1
            if hasattr(self.g1_controller, 'play_stop'):
                code = self.g1_controller.play_stop(app_name)
                
                if code == 0:
                    self.logger.info(f"✅ Reprodução Nativa parada: {app_name}")
                    return AudioResponse(success=True)
                else:
                    self.logger.error(f"❌ Erro ao parar reprodução Nativa: código {code}")
                    return AudioResponse(
                        success=False,
                        error_message=f"Erro ao parar reprodução nativa: código {code}"
                    )
            else:
                return AudioResponse(
                    success=False,
                    error_message="Parada de reprodução não disponível"
                )
                
        except Exception as e:
            self.logger.error(f"❌ Exceção ao parar reprodução Nativa: {e}")
            return AudioResponse(
                success=False,
                error_message=f"Exceção: {str(e)}"
            )
    
    async def is_available(self) -> bool:
        """Verifica se o controle de áudio nativo está disponível."""
        return (
            self.enabled and 
            self.g1_controller and 
            hasattr(self.g1_controller, 'set_volume') and
            hasattr(self.g1_controller, 'get_volume')
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Retorna capacidades do conector."""
        return {
            "name": "G1NativeAudio",
            "enabled": self.enabled,
            "available": self.g1_controller is not None,
            "native_volume": hasattr(self.g1_controller, 'set_volume') if self.g1_controller else False,
            "native_playback": hasattr(self.g1_controller, 'play_stream') if self.g1_controller else False,
            "features": ["volume_control", "audio_playback", "native_hardware", "real_time"]
        }
