"""
Conector nativo LEDs do G1.
Permite controlar LEDs RGB nativos do robô.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class EmotionColor(Enum):
    """Cores de emoção predefinidas."""
    NEUTRAL = (128, 128, 128)
    HAPPY = (255, 255, 0)
    SAD = (0, 0, 255)
    EXCITED = (255, 0, 0)
    CALM = (0, 255, 0)
    THINKING = (255, 165, 0)
    SURPRISED = (255, 0, 255)
    FOCUSED = (0, 255, 255)


@dataclass
class LEDRequest:
    """Requisição de controle de LED."""
    r: int
    g: int
    b: int
    emotion: Optional[str] = None
    duration: Optional[float] = None
    fade: bool = False


@dataclass
class LEDResponse:
    """Resposta de controle de LED."""
    success: bool
    error_message: Optional[str] = None


class G1NativeLEDConnector:
    """Conector para LEDs nativos do G1."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", True)
        self.g1_controller = None
        self.logger = logging.getLogger(__name__)
        
        # Configurações específicas
        self.default_brightness = config.get("default_brightness", 0.5)
        self.transition_time = config.get("transition_time", 0.2)
        self.emotion_colors = config.get("emotion_colors", {})
        
        self.logger.info(f"G1NativeLEDConnector inicializado: enabled={self.enabled}")
    
    async def initialize(self, g1_controller) -> bool:
        """Inicializa o conector com o controlador G1."""
        if not self.enabled:
            self.logger.info("G1NativeLEDConnector desabilitado")
            return False
        
        self.g1_controller = g1_controller
        
        # Verifica se o controle de LED nativo está disponível
        if hasattr(self.g1_controller, 'led_control'):
            self.logger.info("✅ LEDs nativos do G1 disponíveis")
            return True
        else:
            self.logger.warning("❌ LEDs nativos do G1 não disponíveis")
            return False
    
    async def set_color(self, request: LEDRequest) -> LEDResponse:
        """Define cor dos LEDs usando controle nativo do G1."""
        if not self.enabled or not self.g1_controller:
            return LEDResponse(
                success=False,
                error_message="G1NativeLEDConnector não inicializado"
            )
        
        try:
            # Aplica brilho padrão se especificado
            r = int(request.r * self.default_brightness)
            g = int(request.g * self.default_brightness)
            b = int(request.b * self.default_brightness)
            
            self.logger.debug(f"LED Nativo: RGB({r}, {g}, {b})")
            
            # Usa controle nativo de LED do G1
            code = self.g1_controller.led_control(r, g, b)
            
            if code == 0:
                self.logger.info(f"✅ LED Nativo definido: RGB({r}, {g}, {b})")
                return LEDResponse(success=True)
            else:
                self.logger.error(f"❌ Erro no LED Nativo: código {code}")
                return LEDResponse(
                    success=False,
                    error_message=f"Erro no LED nativo: código {code}"
                )
                
        except Exception as e:
            self.logger.error(f"❌ Exceção no LED Nativo: {e}")
            return LEDResponse(
                success=False,
                error_message=f"Exceção: {str(e)}"
            )
    
    async def set_emotion(self, emotion: str) -> LEDResponse:
        """Define cor baseada em emoção."""
        # Mapeia emoção para cor
        if emotion.upper() in EmotionColor.__members__:
            color = EmotionColor[emotion.upper()].value
        elif emotion.lower() in self.emotion_colors:
            color = self.emotion_colors[emotion.lower()]
        else:
            color = EmotionColor.NEUTRAL.value
        
        request = LEDRequest(r=color[0], g=color[1], b=color[2], emotion=emotion)
        return await self.set_color(request)
    
    async def is_available(self) -> bool:
        """Verifica se os LEDs nativos estão disponíveis."""
        return (
            self.enabled and 
            self.g1_controller and 
            hasattr(self.g1_controller, 'led_control')
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Retorna capacidades do conector."""
        return {
            "name": "G1NativeLEDs",
            "enabled": self.enabled,
            "available": self.g1_controller is not None,
            "native_leds": hasattr(self.g1_controller, 'led_control') if self.g1_controller else False,
            "features": ["rgb_control", "emotion_colors", "native_hardware", "real_time"]
        }
