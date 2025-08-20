"""
Gerenciador de Conectores Nativos do G1.
Gerencia e coordena todos os conectores nativos disponíveis.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .g1_native_tts import G1NativeTTSConnector, TTSRequest, TTSResponse
from .g1_native_leds import G1NativeLEDConnector, LEDRequest, LEDResponse
from .g1_native_audio import G1NativeAudioConnector, AudioRequest, AudioResponse

logger = logging.getLogger(__name__)


@dataclass
class ConnectorStatus:
    """Status de um conector."""
    name: str
    enabled: bool
    available: bool
    initialized: bool
    error_message: Optional[str] = None


class G1NativeConnectorManager:
    """Gerenciador de conectores nativos do G1."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Conectores disponíveis
        self.connectors: Dict[str, Any] = {}
        self.g1_controller = None
        
        # Status dos conectores
        self.connector_status: Dict[str, ConnectorStatus] = {}
        
        self.logger.info("G1NativeConnectorManager inicializado")
    
    async def initialize(self, g1_controller) -> bool:
        """Inicializa todos os conectores com o controlador G1."""
        self.g1_controller = g1_controller
        
        # Configurações dos conectores
        connectors_config = self.config.get("native_connectors", {})
        
        # Inicializa TTS Connector
        if connectors_config.get("tts", {}).get("enabled", True):
            tts_config = connectors_config.get("tts", {})
            self.connectors["tts"] = G1NativeTTSConnector(tts_config)
            await self._initialize_connector("tts", self.connectors["tts"])
        
        # Inicializa LED Connector
        if connectors_config.get("leds", {}).get("enabled", True):
            leds_config = connectors_config.get("leds", {})
            self.connectors["leds"] = G1NativeLEDConnector(leds_config)
            await self._initialize_connector("leds", self.connectors["leds"])
        
        # Inicializa Audio Connector
        if connectors_config.get("audio", {}).get("enabled", True):
            audio_config = connectors_config.get("audio", {})
            self.connectors["audio"] = G1NativeAudioConnector(audio_config)
            await self._initialize_connector("audio", self.connectors["audio"])
        
        # Log do status final
        self._log_connector_status()
        
        return True
    
    async def _initialize_connector(self, name: str, connector: Any) -> None:
        """Inicializa um conector específico."""
        try:
            initialized = await connector.initialize(self.g1_controller)
            available = await connector.is_available()
            
            self.connector_status[name] = ConnectorStatus(
                name=name,
                enabled=connector.enabled,
                available=available,
                initialized=initialized
            )
            
            if initialized and available:
                self.logger.info(f"✅ Conector {name} inicializado com sucesso")
            else:
                self.logger.warning(f"⚠️ Conector {name} não disponível")
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar conector {name}: {e}")
            self.connector_status[name] = ConnectorStatus(
                name=name,
                enabled=connector.enabled,
                available=False,
                initialized=False,
                error_message=str(e)
            )
    
    def _log_connector_status(self) -> None:
        """Loga o status de todos os conectores."""
        self.logger.info("📊 Status dos Conectores Nativos:")
        
        for name, status in self.connector_status.items():
            if status.initialized and status.available:
                self.logger.info(f"  ✅ {name}: Disponível e inicializado")
            elif status.enabled:
                self.logger.warning(f"  ⚠️ {name}: Habilitado mas não disponível")
            else:
                self.logger.info(f"  ❌ {name}: Desabilitado")
    
    # Métodos de conveniência para TTS
    async def speak(self, text: str, speaker_id: int = 0, emotion: Optional[str] = None) -> TTSResponse:
        """Executa síntese de voz usando TTS nativo."""
        if "tts" not in self.connectors:
            return TTSResponse(
                success=False,
                error_message="Conector TTS não disponível"
            )
        
        request = TTSRequest(text=text, speaker_id=speaker_id, emotion=emotion)
        return await self.connectors["tts"].speak(request)
    
    # Métodos de conveniência para LEDs
    async def set_led_color(self, r: int, g: int, b: int, emotion: Optional[str] = None) -> LEDResponse:
        """Define cor dos LEDs."""
        if "leds" not in self.connectors:
            return LEDResponse(
                success=False,
                error_message="Conector LEDs não disponível"
            )
        
        request = LEDRequest(r=r, g=g, b=b, emotion=emotion)
        return await self.connectors["leds"].set_color(request)
    
    async def set_emotion_led(self, emotion: str) -> LEDResponse:
        """Define cor dos LEDs baseada em emoção."""
        if "leds" not in self.connectors:
            return LEDResponse(
                success=False,
                error_message="Conector LEDs não disponível"
            )
        
        return await self.connectors["leds"].set_emotion(emotion)
    
    # Métodos de conveniência para Áudio
    async def set_volume(self, volume: int) -> AudioResponse:
        """Define volume do áudio."""
        if "audio" not in self.connectors:
            return AudioResponse(
                success=False,
                error_message="Conector Áudio não disponível"
            )
        
        return await self.connectors["audio"].set_volume(volume)
    
    async def get_volume(self) -> AudioResponse:
        """Obtém volume atual do áudio."""
        if "audio" not in self.connectors:
            return AudioResponse(
                success=False,
                error_message="Conector Áudio não disponível"
            )
        
        return await self.connectors["audio"].get_volume()
    
    # Métodos de status e informações
    def get_connector_status(self, name: str) -> Optional[ConnectorStatus]:
        """Obtém status de um conector específico."""
        return self.connector_status.get(name)
    
    def get_all_status(self) -> Dict[str, ConnectorStatus]:
        """Obtém status de todos os conectores."""
        return self.connector_status.copy()
    
    def get_available_connectors(self) -> List[str]:
        """Obtém lista de conectores disponíveis."""
        return [
            name for name, status in self.connector_status.items()
            if status.available and status.initialized
        ]
    
    def get_connector_capabilities(self, name: str) -> Optional[Dict[str, Any]]:
        """Obtém capacidades de um conector específico."""
        if name in self.connectors:
            return self.connectors[name].get_capabilities()
        return None
    
    def get_all_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """Obtém capacidades de todos os conectores."""
        return {
            name: connector.get_capabilities()
            for name, connector in self.connectors.items()
        }
    
    async def is_connector_available(self, name: str) -> bool:
        """Verifica se um conector específico está disponível."""
        if name in self.connectors:
            return await self.connectors[name].is_available()
        return False
    
    async def test_all_connectors(self) -> Dict[str, bool]:
        """Testa todos os conectores disponíveis."""
        results = {}
        
        for name, connector in self.connectors.items():
            try:
                available = await connector.is_available()
                results[name] = available
                self.logger.info(f"🧪 Teste {name}: {'✅' if available else '❌'}")
            except Exception as e:
                results[name] = False
                self.logger.error(f"🧪 Teste {name}: ❌ Erro - {e}")
        
        return results
