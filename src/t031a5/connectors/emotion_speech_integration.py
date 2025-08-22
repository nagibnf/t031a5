# -*- coding: utf-8 -*-
"""
EmotionSpeechIntegration - Integração completa emoções + fala + LEDs dinâmicos
Combina: ElevenLabs TTS + Anker + G1 LEDs + análise de áudio em tempo real
"""

import logging
import asyncio
import threading
import time
import re
import numpy as np
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    import wave
    import pyaudio
    AUDIO_ANALYSIS_AVAILABLE = True
except ImportError:
    logger.warning("PyAudio não disponível - intensidade será simulada")
    AUDIO_ANALYSIS_AVAILABLE = False

@dataclass
class EmotionMapping:
    """Mapeamento de emoção para cores LED"""
    name: str
    rgb: Tuple[int, int, int]
    intensity_base: float  # Intensidade base (0.0-1.0)
    keywords: list  # Palavras-chave que ativam esta emoção

# Mapeamento de emoções para LEDs
EMOTION_MAPPINGS = {
    "happy": EmotionMapping("happy", (0, 255, 0), 0.8, 
                           ["feliz", "alegre", "ótimo", "excelente", "maravilhoso", "perfeito", "sucesso"]),
    "excited": EmotionMapping("excited", (255, 128, 0), 0.9,
                             ["animado", "empolgado", "incrível", "fantástico", "wow", "uau"]),
    "calm": EmotionMapping("calm", (0, 255, 255), 0.6,
                          ["calmo", "tranquilo", "relaxado", "pacífico", "sereno"]),
    "thinking": EmotionMapping("thinking", (128, 0, 128), 0.5,
                              ["pensando", "analisando", "considerando", "avaliando", "hmm"]),
    "concerned": EmotionMapping("concerned", (255, 255, 0), 0.7,
                               ["preocupado", "cuidado", "atenção", "problema", "erro"]),
    "sad": EmotionMapping("sad", (0, 0, 255), 0.4,
                         ["triste", "ruim", "falha", "erro", "problema", "não funcionou"]),
    "neutral": EmotionMapping("neutral", (128, 128, 128), 0.5,
                             ["neutro", "ok", "normal", "padrão"])
}

class EmotionSpeechIntegration:
    """Integração completa de emoções, fala e LEDs dinâmicos"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", True)
        
        # Conectores (já validados)
        self.elevenlabs_connector = None
        self.audio_player_connector = None
        self.g1_emotion_connector = None
        
        # Estado atual
        self.current_emotion = "neutral"
        self.current_intensity = 0.5
        self.is_speaking = False
        self.audio_analysis_thread = None
        self.stop_analysis = False
        
        logger.info("EmotionSpeechIntegration inicializado")
    
    async def initialize(self) -> bool:
        """Inicializa todos os conectores necessários"""
        try:
            if not self.enabled:
                logger.info("EmotionSpeechIntegration desabilitado")
                return True
            
            # Importar conectores validados
            from .elevenlabs_tts import ElevenLabsTTSConnector
            from .audio_player import AudioPlayerConnector
            from .g1_emotion_real import G1EmotionRealConnector
            
            # Inicializar ElevenLabs (TESTADO)
            self.elevenlabs_connector = ElevenLabsTTSConnector({
                "enabled": True,
                "output_dir": "audio/speech"
            })
            await self.elevenlabs_connector.initialize()
            
            # Inicializar Audio Player (TESTADO)
            self.audio_player_connector = AudioPlayerConnector({"enabled": True})
            
            # Inicializar G1 LEDs (TESTADO)
            self.g1_emotion_connector = G1EmotionRealConnector({
                "enabled": True,
                "network_interface": "eth0",
                "timeout": 10.0
            })
            await self.g1_emotion_connector.initialize()
            
            logger.info("✅ EmotionSpeechIntegration: Todos conectores inicializados")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar EmotionSpeechIntegration: {e}")
            return False
    
    def analyze_text_emotion(self, text: str) -> str:
        """Analisa texto e determina emoção apropriada"""
        text_lower = text.lower()
        
        # Pontuação para diferentes emoções
        emotion_scores = {}
        
        for emotion_name, mapping in EMOTION_MAPPINGS.items():
            score = 0
            for keyword in mapping.keywords:
                if keyword in text_lower:
                    score += 1
            emotion_scores[emotion_name] = score
        
        # Análise de pontuação e caracteres especiais
        if "!" in text:
            emotion_scores["excited"] += 2
        if "?" in text:
            emotion_scores["thinking"] += 1
        if "..." in text:
            emotion_scores["thinking"] += 1
        
        # Retorna emoção com maior pontuação
        best_emotion = max(emotion_scores, key=emotion_scores.get)
        
        # Se nenhuma emoção específica, usar neutral
        if emotion_scores[best_emotion] == 0:
            best_emotion = "neutral"
        
        logger.info(f"🎭 Texto analisado: '{text[:50]}...' → Emoção: {best_emotion}")
        return best_emotion
    
    async def speak_with_emotion(self, text: str, emotion: Optional[str] = None) -> bool:
        """
        Fala texto com emoção LED correspondente
        
        Args:
            text: Texto para falar
            emotion: Emoção específica (ou auto-detecta do texto)
        """
        try:
            # 1. Determinar emoção
            if emotion is None:
                emotion = self.analyze_text_emotion(text)
            
            self.current_emotion = emotion
            emotion_mapping = EMOTION_MAPPINGS.get(emotion, EMOTION_MAPPINGS["neutral"])
            
            logger.info(f"🎤 Falando com emoção {emotion}: '{text}'")
            
            # 2. Configurar LEDs com emoção base
            if self.g1_emotion_connector:
                rgb = emotion_mapping.rgb
                intensity = emotion_mapping.intensity_base
                
                # Aplicar intensidade base
                r = int(rgb[0] * intensity)
                g = int(rgb[1] * intensity)
                b = int(rgb[2] * intensity)
                
                await self.g1_emotion_connector.set_custom_color(r, g, b)
                logger.info(f"🎨 LEDs configurados: {emotion} RGB({r}, {g}, {b})")
            
            # 3. Gerar TTS via ElevenLabs
            if self.elevenlabs_connector:
                response = await self.elevenlabs_connector.synthesize_speech(text)
                if response.success:
                    audio_file = response.file_path
                    logger.info(f"🔊 TTS gerado: {audio_file}")
                    
                    # 4. Iniciar análise de áudio em tempo real
                    self.is_speaking = True
                    if AUDIO_ANALYSIS_AVAILABLE:
                        self.start_audio_analysis(audio_file, emotion_mapping)
                    
                    # 5. Reproduzir no Anker
                    if self.audio_player_connector:
                        success = await self.audio_player_connector.play_audio_anker(audio_file)
                        if success:
                            logger.info("✅ Áudio reproduzido no Anker com sucesso")
                        else:
                            logger.warning("⚠️ Falha na reprodução no Anker")
                    
                    # 6. Aguardar fim da reprodução
                    await self.wait_for_speech_completion()
                    
                    # 7. Desligar LEDs após fala
                    if self.g1_emotion_connector:
                        await self.g1_emotion_connector.turn_off_leds()
                    
                    return True
                else:
                    logger.error("❌ Falha na geração TTS")
                    return False
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro em speak_with_emotion: {e}")
            return False
        finally:
            self.is_speaking = False
            self.stop_analysis = True
    
    def start_audio_analysis(self, audio_file: str, emotion_mapping: EmotionMapping):
        """Inicia análise de áudio em tempo real para controle de intensidade"""
        if not AUDIO_ANALYSIS_AVAILABLE:
            return
        
        def analyze_audio():
            try:
                # Simular análise de áudio (versão simplificada)
                # Em implementação real, analisaria amplitude do áudio
                duration = 3.0  # Duração estimada
                steps = 30
                step_time = duration / steps
                
                for i in range(steps):
                    if self.stop_analysis:
                        break
                    
                    # Simular variação de intensidade baseada no áudio
                    # Valores sinusoidais para simular variação natural da fala
                    intensity_variation = 0.3 * np.sin(i * 0.5) + 0.7
                    
                    # Aplicar variação aos LEDs
                    rgb = emotion_mapping.rgb
                    intensity = emotion_mapping.intensity_base * intensity_variation
                    
                    r = int(rgb[0] * intensity)
                    g = int(rgb[1] * intensity)
                    b = int(rgb[2] * intensity)
                    
                    # Atualizar LEDs (execução assíncrona)
                    if self.g1_emotion_connector:
                        asyncio.run_coroutine_threadsafe(
                            self.g1_emotion_connector.set_custom_color(r, g, b),
                            asyncio.get_event_loop()
                        )
                    
                    time.sleep(step_time)
                    
            except Exception as e:
                logger.error(f"Erro na análise de áudio: {e}")
        
        self.stop_analysis = False
        self.audio_analysis_thread = threading.Thread(target=analyze_audio)
        self.audio_analysis_thread.start()
    
    async def wait_for_speech_completion(self):
        """Aguarda conclusão da fala"""
        # Tempo estimado baseado no comprimento do texto
        # Em implementação real, monitoria o processo de reprodução
        await asyncio.sleep(5.0)
    
    def get_available_emotions(self) -> Dict[str, Any]:
        """Retorna emoções disponíveis e suas configurações"""
        return {
            name: {
                "rgb": mapping.rgb,
                "intensity": mapping.intensity_base,
                "keywords": mapping.keywords
            }
            for name, mapping in EMOTION_MAPPINGS.items()
        }
