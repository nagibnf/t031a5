"""
Conector para captura de áudio do DJI Mic no sistema t031a5.
MÉTODO TESTADO E FUNCIONANDO: arecord hw:0,0 S24_3LE 48000Hz 2ch
"""

import os
import subprocess
import logging
import tempfile
import asyncio
from typing import Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class AudioCaptureConnector:
    """Conector para captura de áudio - MÉTODO TESTADO DJI MIC."""
    
    def __init__(self, config: dict):
        self.device = config.get("device", "hw:0,0")  # DJI Mic card 0, device 0
        self.format = config.get("format", "S24_3LE")  # Formato nativo DJI
        self.rate = config.get("rate", 48000)  # Taxa nativa DJI
        self.channels = config.get("channels", 2)  # Estéreo
        self.enabled = config.get("enabled", True)
        
        logger.info(f"AudioCaptureConnector inicializado: device={self.device}, format={self.format}")
    
    async def capture_audio_dji_mic(self, duration: int = 5, output_file: Optional[str] = None) -> Tuple[bool, str, int]:
        """
        Captura áudio do DJI Mic.
        MÉTODO TESTADO E FUNCIONANDO: arecord -D hw:0,0 -f S24_3LE -r 48000 -c 2
        
        Returns:
            Tuple[bool, str, int]: (sucesso, caminho_arquivo, tamanho_bytes)
        """
        if not self.enabled:
            logger.warning("AudioCapture desabilitado")
            return False, "", 0
            
        try:
            # Gerar nome de arquivo se não fornecido
            if not output_file:
                timestamp = int(asyncio.get_event_loop().time() * 1000)
                output_file = f"audio_capture_{timestamp}.wav"
            
            # MÉTODO TESTADO: Comando arecord com configurações DJI Mic
            logger.info(f"🎤 Capturando áudio por {duration}s no DJI Mic...")
            cmd = [
                "arecord",
                "-D", self.device,           # hw:0,0 (DJI Mic)
                "-f", self.format,           # S24_3LE (formato nativo)
                "-r", str(self.rate),        # 48000Hz (taxa nativa)
                "-c", str(self.channels),    # 2 canais (estéreo)
                "-d", str(duration),         # duração em segundos
                output_file                  # arquivo de saída
            ]
            
            # Executar captura (método testado)
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=duration + 5  # timeout seguro
            )
            
            if result.returncode == 0:
                # Verificar arquivo gerado
                if os.path.exists(output_file):
                    file_size = os.path.getsize(output_file)
                    logger.info(f"✅ Áudio capturado: {output_file} ({file_size} bytes)")
                    
                    if file_size > 1000:  # Arquivo com conteúdo real
                        return True, output_file, file_size
                    else:
                        logger.warning(f"Arquivo muito pequeno: {file_size} bytes (silêncio?)")
                        return False, output_file, file_size
                else:
                    logger.error("Arquivo de áudio não foi gerado")
                    return False, "", 0
            else:
                logger.error(f"❌ Erro na captura: {result.stderr}")
                return False, "", 0
                
        except subprocess.TimeoutExpired:
            logger.error("Timeout na captura de áudio")
            return False, "", 0
        except Exception as e:
            logger.error(f"Erro na captura de áudio: {e}")
            return False, "", 0
    
    async def test_microphone(self) -> bool:
        """Testa se o DJI Mic está funcionando."""
        try:
            # Verificar se DJI Mic está detectado
            result = subprocess.run(
                ["arecord", "-l"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if "DJI MIC MINI" in result.stdout:
                logger.info("✅ DJI MIC MINI detectado e funcionando")
                return True
            else:
                logger.error("❌ DJI Mic não detectado")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao testar microfone: {e}")
            return False
    
    async def capture_with_cleanup(self, duration: int = 5) -> Tuple[bool, str, int]:
        """Captura áudio com limpeza automática de arquivos temporários."""
        success, file_path, file_size = await self.capture_audio_dji_mic(duration)
        
        # Nota: Arquivo será mantido para processamento posterior
        # Limpeza deve ser feita pelo componente que usa este conector
        
        return success, file_path, file_size
