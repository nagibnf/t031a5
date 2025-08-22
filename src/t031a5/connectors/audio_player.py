"""
Conector para reprodução de áudio no sistema t031a5.
MÉTODO TESTADO E FUNCIONANDO: MP3 → WAV → paplay → Anker
"""

import os
import subprocess
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class AudioPlayerConnector:
    """Conector para reprodução de áudio - MÉTODO TESTADO."""
    
    def __init__(self, config: dict):
        self.anker_device = "bluez_sink.F4_2B_7D_2B_D1_B6.a2dp_sink"
        self.enabled = config.get("enabled", True)
        
        logger.info(f"AudioPlayerConnector inicializado: enabled={self.enabled}")
    
    async def play_audio_anker(self, audio_file_path: str) -> bool:
        """
        Reproduz áudio no Anker Soundcore Motion 300.
        MÉTODO TESTADO E FUNCIONANDO: Converte MP3→WAV→paplay→Anker
        """
        if not self.enabled:
            logger.warning("AudioPlayer desabilitado")
            return False
            
        try:
            audio_path = Path(audio_file_path)
            if not audio_path.exists():
                logger.error(f"Arquivo de áudio não encontrado: {audio_file_path}")
                return False
            
            # MÉTODO TESTADO: Converter MP3 para WAV primeiro
            wav_file = str(audio_path).replace('.mp3', '.wav')
            
            # Converter usando ffmpeg (testado e funcionando)
            logger.info(f"🔄 Convertendo {audio_path.name} para WAV...")
            convert_cmd = ["ffmpeg", "-i", str(audio_path), wav_file, "-y"]
            convert_result = subprocess.run(
                convert_cmd, 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if convert_result.returncode != 0:
                logger.error(f"Erro na conversão MP3→WAV: {convert_result.stderr}")
                return False
            
            # MÉTODO TESTADO: Reproduzir WAV no Anker usando paplay
            logger.info(f"🔊 Reproduzindo no Anker: {Path(wav_file).name}")
            play_cmd = [
                "paplay", 
                f"--device={self.anker_device}",
                wav_file
            ]
            
            play_result = subprocess.run(
                play_cmd, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            # Limpar arquivo WAV temporário
            if os.path.exists(wav_file):
                os.remove(wav_file)
            
            if play_result.returncode == 0:
                logger.info(f"✅ Áudio reproduzido com sucesso no Anker (método testado)")
                return True
            else:
                logger.error(f"❌ Erro ao reproduzir no Anker: {play_result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Timeout na reprodução de áudio")
            return False
        except Exception as e:
            logger.error(f"Erro na reprodução de áudio: {e}")
            return False
    
    async def play_audio_default(self, audio_file_path: str) -> bool:
        """Reproduz áudio na saída padrão (fallback)."""
        try:
            cmd = ["paplay", audio_file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info(f"✅ Áudio reproduzido na saída padrão")
                return True
            else:
                logger.error(f"❌ Erro na reprodução padrão: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Erro na reprodução padrão: {e}")
            return False
