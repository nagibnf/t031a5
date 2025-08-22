# -*- coding: utf-8 -*-
"""
AudioVisualDynamic - Sistema completo áudio-visual dinâmico
Combina: ElevenLabs TTS + Anker + G1 LEDs + análise volume em tempo real
"""

import logging
import asyncio
import threading
import time
import wave
import struct
import numpy as np
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class EmotionConfig:
    """Configuração de emoção para LEDs"""
    name: str
    rgb: Tuple[int, int, int]
    base_intensity: float  # Intensidade base (0.0-1.0)
    keywords: list  # Palavras-chave que ativam esta emoção

# Mapeamento completo de emoções
EMOTION_CONFIGS = {
    "happy": EmotionConfig("happy", (0, 255, 0), 0.8, 
                          ["feliz", "alegre", "ótimo", "excelente", "maravilhoso", "perfeito", "sucesso", "bom"]),
    "excited": EmotionConfig("excited", (255, 128, 0), 0.9,
                            ["animado", "empolgado", "incrível", "fantástico", "wow", "uau", "impressionante"]),
    "calm": EmotionConfig("calm", (0, 255, 255), 0.6,
                         ["calmo", "tranquilo", "relaxado", "pacífico", "sereno", "suave"]),
    "thinking": EmotionConfig("thinking", (128, 0, 128), 0.5,
                             ["pensando", "analisando", "considerando", "avaliando", "hmm", "refletindo"]),
    "concerned": EmotionConfig("concerned", (255, 255, 0), 0.7,
                              ["preocupado", "cuidado", "atenção", "problema", "erro", "alerta"]),
    "sad": EmotionConfig("sad", (0, 0, 255), 0.4,
                        ["triste", "ruim", "falha", "erro", "problema", "não funcionou", "decepcionado"]),
    "neutral": EmotionConfig("neutral", (128, 128, 128), 0.5,
                            ["neutro", "ok", "normal", "padrão", "regular"])
}

class AudioVisualDynamic:
    """Sistema completo áudio-visual dinâmico"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", True)
        
        # Conectores validados
        self.elevenlabs_connector = None
        self.audio_player_connector = None
        self.g1_emotion_connector = None
        
        # Estado do sistema
        self.current_emotion = "neutral"
        self.is_playing = False
        self.audio_analysis_thread = None
        self.stop_analysis = False
        
        # Configurações de análise de áudio
        self.volume_smoothing = 0.8  # Suavização do volume
        self.min_intensity = 0.2     # Intensidade mínima
        self.max_intensity = 1.0     # Intensidade máxima
        self.volume_threshold = 0.01 # Limiar de volume mínimo
        
        logger.info("AudioVisualDynamic inicializado")
    
    async def initialize(self) -> bool:
        """Inicializa todos os conectores"""
        try:
            if not self.enabled:
                logger.info("AudioVisualDynamic desabilitado")
                return True
            
            # Importar conectores validados
            from .elevenlabs_tts import ElevenLabsTTSConnector
            from .audio_player import AudioPlayerConnector
            from .g1_emotion_real import G1EmotionRealConnector
            
            # Inicializar ElevenLabs (VALIDADO Teste 5)
            logger.info("Inicializando ElevenLabs TTS...")
            self.elevenlabs_connector = ElevenLabsTTSConnector({
                "enabled": True,
                "output_dir": "audio/speech"
            })
            await self.elevenlabs_connector.initialize()
            
            # Inicializar Audio Player (VALIDADO Teste 1)
            logger.info("Inicializando Audio Player...")
            self.audio_player_connector = AudioPlayerConnector({"enabled": True})
            
            # Inicializar G1 LEDs (VALIDADO Teste 12)
            logger.info("Inicializando G1 LEDs...")
            self.g1_emotion_connector = G1EmotionRealConnector({
                "enabled": True,
                "network_interface": "eth0",
                "timeout": 10.0
            })
            await self.g1_emotion_connector.initialize()
            
            logger.info("✅ AudioVisualDynamic: Todos conectores inicializados")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar AudioVisualDynamic: {e}")
            return False
    
    def detect_emotion_from_text(self, text: str) -> str:
        """Detecta emoção a partir do texto"""
        text_lower = text.lower()
        
        # Pontuação para cada emoção
        emotion_scores = {}
        
        for emotion_name, config in EMOTION_CONFIGS.items():
            score = 0
            for keyword in config.keywords:
                if keyword in text_lower:
                    score += 1
            emotion_scores[emotion_name] = score
        
        # Análise de pontuação
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
        
        logger.info(f"🎭 Texto: '{text[:50]}...' → Emoção: {best_emotion}")
        return best_emotion
    
    def analyze_audio_volume(self, audio_file: str) -> list:
        """Analisa volume do arquivo de áudio"""
        try:
            with wave.open(audio_file, 'rb') as wav_file:
                frames = wav_file.readframes(-1)
                sound_info = wav_file.getparams()
                
                # Converter para numpy array
                if sound_info.sampwidth == 1:
                    sound_data = np.frombuffer(frames, dtype=np.uint8)
                elif sound_info.sampwidth == 2:
                    sound_data = np.frombuffer(frames, dtype=np.int16)
                elif sound_info.sampwidth == 4:
                    sound_data = np.frombuffer(frames, dtype=np.int32)
                else:
                    logger.warning(f"Formato de áudio não suportado: {sound_info.sampwidth} bytes")
                    return []
                
                # Calcular RMS em janelas
                window_size = int(sound_info.framerate * 0.1)  # 100ms windows
                volumes = []
                
                for i in range(0, len(sound_data), window_size):
                    window = sound_data[i:i + window_size]
                    if len(window) > 0:
                        rms = np.sqrt(np.mean(window.astype(float) ** 2))
                        # Normalizar para 0-1
                        normalized_volume = min(1.0, rms / 5000.0)
                        volumes.append(normalized_volume)
                
                logger.info(f"📊 Áudio analisado: {len(volumes)} janelas, volume médio: {np.mean(volumes):.3f}")
                return volumes
                
        except Exception as e:
            logger.error(f"❌ Erro ao analisar áudio: {e}")
            return []
    
    def start_led_animation(self, emotion_config: EmotionConfig, volumes: list):
        """Inicia animação dos LEDs baseada no volume"""
        def animate_leds():
            try:
                logger.info(f"🎨 Iniciando animação LED para emoção: {emotion_config.name}")
                
                # Timing para sincronizar com áudio
                window_duration = 0.1  # 100ms por janela
                
                for i, volume in enumerate(volumes):
                    if self.stop_analysis:
                        break
                    
                    # Calcular intensidade baseada no volume
                    volume_intensity = max(self.min_intensity, min(self.max_intensity, volume))
                    final_intensity = emotion_config.base_intensity * volume_intensity
                    
                    # Aplicar intensidade às cores RGB
                    r = int(emotion_config.rgb[0] * final_intensity)
                    g = int(emotion_config.rgb[1] * final_intensity)
                    b = int(emotion_config.rgb[2] * final_intensity)
                    
                    # Atualizar LEDs
                    if self.g1_emotion_connector and not self.stop_analysis:
                        try:
                            # Usar asyncio dentro da thread
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            loop.run_until_complete(
                                self.g1_emotion_connector.set_custom_color(r, g, b)
                            )
                            loop.close()
                        except Exception as led_error:
                            logger.warning(f"Erro ao atualizar LED: {led_error}")
                    
                    logger.debug(f"LED frame {i}: volume={volume:.3f}, intensity={final_intensity:.3f}, RGB({r},{g},{b})")
                    time.sleep(window_duration)
                
                # Desligar LEDs ao final
                if self.g1_emotion_connector and not self.stop_analysis:
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(self.g1_emotion_connector.turn_off_leds())
                        loop.close()
                        logger.info("🔴 LEDs desligados após animação")
                    except Exception as e:
                        logger.warning(f"Erro ao desligar LEDs: {e}")
                
            except Exception as e:
                logger.error(f"❌ Erro na animação LED: {e}")
        
        self.stop_analysis = False
        self.audio_analysis_thread = threading.Thread(target=animate_leds)
        self.audio_analysis_thread.start()
    
    async def speak_with_dynamic_leds(self, text: str, emotion: Optional[str] = None) -> bool:
        """
        Fala texto com LEDs dinâmicos baseados no volume
        
        Args:
            text: Texto para falar
            emotion: Emoção específica (ou auto-detecta)
        """
        try:
            # 1. Detectar emoção
            if emotion is None:
                emotion = self.detect_emotion_from_text(text)
            
            emotion_config = EMOTION_CONFIGS.get(emotion, EMOTION_CONFIGS["neutral"])
            self.current_emotion = emotion
            
            logger.info(f"🎤 Falando com LEDs dinâmicos: '{text}' (emoção: {emotion})")
            
            # 2. Gerar TTS
            if not self.elevenlabs_connector:
                logger.error("❌ ElevenLabs não inicializado")
                return False
            
            response = await self.elevenlabs_connector.synthesize_speech(text)
            if not response.success:
                logger.error("❌ Falha na geração TTS")
                return False
            
            audio_file = response.file_path
            logger.info(f"🔊 TTS gerado: {audio_file}")
            
            # 3. Analisar volume do áudio
            volumes = self.analyze_audio_volume(audio_file)
            if not volumes:
                logger.warning("⚠️ Falha na análise de volume, usando intensidade fixa")
                volumes = [0.5] * 50  # Fallback com 5 segundos de intensidade média
            
            # 4. Iniciar animação LED em paralelo
            self.is_playing = True
            self.start_led_animation(emotion_config, volumes)
            
            # 5. Reproduzir áudio no Anker
            if self.audio_player_connector:
                success = await self.audio_player_connector.play_audio_anker(audio_file)
                if success:
                    logger.info("✅ Áudio reproduzido no Anker com LEDs dinâmicos")
                    
                    # Aguardar conclusão da animação
                    if self.audio_analysis_thread:
                        self.audio_analysis_thread.join(timeout=30)
                    
                    return True
                else:
                    logger.error("❌ Falha na reprodução no Anker")
                    self.stop_analysis = True
                    return False
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro em speak_with_dynamic_leds: {e}")
            return False
        finally:
            self.is_playing = False
            self.stop_analysis = True
    
    def get_emotion_info(self) -> Dict[str, Any]:
        """Retorna informações das emoções disponíveis"""
        return {
            name: {
                "rgb": config.rgb,
                "base_intensity": config.base_intensity,
                "keywords": config.keywords
            }
            for name, config in EMOTION_CONFIGS.items()
        }
