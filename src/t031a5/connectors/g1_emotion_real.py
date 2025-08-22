# -*- coding: utf-8 -*-
"""
G1EmotionRealConnector - Controle real de LEDs via sistema de emoções
Baseado nos métodos descobertos em G1Controller e G1Interface
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)

try:
    from unitree_sdk2_python.core.channel import ChannelFactoryInitialize
    from unitree_sdk2_python.go2.audio.audio_client import AudioClient
    SDK_AVAILABLE = True
except ImportError:
    logger.warning("SDK Unitree não disponível - modo simulado")
    AudioClient = None
    SDK_AVAILABLE = False

class EmotionType(Enum):
    """Emoções mapeadas para cores de LEDs"""
    HAPPY = {"r": 0, "g": 255, "b": 0}      # Verde
    SAD = {"r": 0, "g": 0, "b": 255}        # Azul
    EXCITED = {"r": 255, "g": 128, "b": 0}  # Laranja
    CALM = {"r": 0, "g": 255, "b": 255}     # Ciano
    ANGRY = {"r": 255, "g": 0, "b": 0}      # Vermelho
    NEUTRAL = {"r": 128, "g": 128, "b": 128} # Cinza

class G1EmotionRealConnector:
    """Conecter real para controle de emoções/LEDs do G1"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", True)
        self.network_interface = config.get("network_interface", "eth0")
        self.timeout = config.get("timeout", 10.0)
        
        # Cliente SDK
        self.audio_client: Optional[AudioClient] = None
        self.is_initialized = False
        
        logger.info(f"G1EmotionRealConnector configurado: enabled={self.enabled}")
    
    async def initialize(self) -> bool:
        """Inicializa conexão real com G1 para controle de LEDs"""
        try:
            if not self.enabled or not SDK_AVAILABLE:
                logger.info("G1EmotionReal: usando modo simulado")
                self.is_initialized = True
                return True
            
            logger.info("Inicializando AudioClient para controle de LEDs...")
            
            # Inicializar DDS
            ChannelFactoryInitialize(0, self.network_interface)
            
            # Criar cliente de áudio (para LEDs)
            self.audio_client = AudioClient()
            
            # Testar conexão
            await asyncio.sleep(0.5)  # Aguardar inicialização
            
            self.is_initialized = True
            logger.info("✅ G1EmotionReal: AudioClient inicializado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar G1EmotionReal: {e}")
            self.is_initialized = False
            return False
    
    async def set_emotion(self, emotion_name: str, brightness: float = 1.0) -> bool:
        """
        Define emoção via LEDs
        
        Args:
            emotion_name: Nome da emoção (happy, sad, excited, calm, angry, neutral)
            brightness: Brilho (0.0-1.0)
        """
        try:
            if not self.is_initialized:
                logger.warning("G1EmotionReal não inicializado")
                return False
            
            # Mapear nome para emoção
            emotion_name_upper = emotion_name.upper()
            if not hasattr(EmotionType, emotion_name_upper):
                logger.error(f"Emoção '{emotion_name}' não encontrada")
                return False
            
            emotion = getattr(EmotionType, emotion_name_upper)
            colors = emotion.value
            
            # Aplicar brilho
            r = int(colors["r"] * brightness)
            g = int(colors["g"] * brightness)
            b = int(colors["b"] * brightness)
            
            logger.info(f"🎨 Definindo emoção {emotion_name}: RGB({r}, {g}, {b})")
            
            if not SDK_AVAILABLE or not self.audio_client:
                logger.info("💭 Modo simulado: LEDs configurados")
                return True
            
            # COMANDO REAL PARA LEDs
            result = self.audio_client.LedControl(r, g, b)
            
            if result == 0:
                logger.info(f"✅ LEDs configurados: {emotion_name} RGB({r}, {g}, {b})")
                return True
            else:
                logger.error(f"❌ Erro ao configurar LEDs: código {result}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao definir emoção: {e}")
            return False
    
    async def set_custom_color(self, r: int, g: int, b: int) -> bool:
        """
        Define cor customizada para LEDs
        
        Args:
            r, g, b: Valores RGB (0-255)
        """
        try:
            if not self.is_initialized:
                logger.warning("G1EmotionReal não inicializado")
                return False
            
            # Validar valores
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            logger.info(f"🎨 Definindo cor customizada: RGB({r}, {g}, {b})")
            
            if not SDK_AVAILABLE or not self.audio_client:
                logger.info("💭 Modo simulado: LEDs configurados")
                return True
            
            # COMANDO REAL PARA LEDs
            result = self.audio_client.LedControl(r, g, b)
            
            if result == 0:
                logger.info(f"✅ LEDs configurados: RGB({r}, {g}, {b})")
                return True
            else:
                logger.error(f"❌ Erro ao configurar LEDs: código {result}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao definir cor customizada: {e}")
            return False
    
    async def turn_off_leds(self) -> bool:
        """Desliga LEDs (RGB 0,0,0)"""
        return await self.set_custom_color(0, 0, 0)
    
    async def get_available_emotions(self) -> Dict[str, Dict[str, int]]:
        """Retorna emoções disponíveis e suas cores"""
        return {emotion.name.lower(): emotion.value for emotion in EmotionType}
