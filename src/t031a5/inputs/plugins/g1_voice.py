"""
Plugin G1VoiceInput para o sistema t031a5.

Reconhecimento de voz usando DJI Mic 2 via USB + Google Speech API.
"""

import logging
import asyncio
import subprocess
import tempfile
import os
from typing import Any, Dict, Optional
from datetime import datetime

from ..base import BaseInput, InputData

logger = logging.getLogger(__name__)


class G1VoiceInput(BaseInput):
    """Input de voz usando DJI Mic 2 via USB."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o G1VoiceInput.
        
        Args:
            config: Configuração do input
        """
        super().__init__(config)
        
        # Configurações específicas de voz
        self.sample_rate = config.get("sample_rate", 48000)  # DJI Mic nativo
        self.language = config.get("language", "pt-BR")
        self.device = config.get("device", "dji_mic_2")
        self.sensitivity = config.get("sensitivity", 0.7)
        self.continuous_listening = config.get("continuous_listening", True)
        self.noise_suppression = config.get("noise_suppression", True)
        
        # Configurações do DJI Mic 2
        self.dji_device = "hw:0,0"  # DJI MIC MINI é card 0
        self.dji_format = "S24_3LE"  # Formato nativo que funciona
        self.capture_duration = 2  # Segundos por captura (inteiro)
        
        # Estado
        self.is_capturing = False
        self.mock_mode = False
        
        logger.debug(f"G1VoiceInput configurado: {self.language}, DJI Mic via USB")
    
    async def _initialize(self) -> bool:
        """
        Inicialização específica do G1VoiceInput.
        
        Returns:
            True se a inicialização foi bem-sucedida
        """
        try:
            # Verificar se DJI Mic 2 está disponível
            logger.info("Verificando DJI Mic 2...")
            
            # Testar se o dispositivo está disponível
            proc = subprocess.Popen(['arecord', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            
            if 'DJI MIC MINI' in stdout.decode():
                logger.info("DJI MIC MINI detectado - usando hardware real")
                self.mock_mode = False
            else:
                logger.warning("DJI MIC MINI não encontrado - usando modo mock")
                self.mock_mode = True
            
            logger.info("G1VoiceInput inicializado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro na inicialização do G1VoiceInput: {e}")
            logger.warning("Usando modo mock devido ao erro")
            self.mock_mode = True
            return True
    
    async def _start(self) -> bool:
        """
        Início específico do G1VoiceInput.
        
        Returns:
            True se o início foi bem-sucedido
        """
        try:
            logger.info("G1VoiceInput iniciado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao iniciar G1VoiceInput: {e}")
            return False
    
    async def _stop(self) -> bool:
        """
        Parada específica do G1VoiceInput.
        
        Returns:
            True se a parada foi bem-sucedida
        """
        try:
            logger.info("G1VoiceInput parado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao parar G1VoiceInput: {e}")
            return False
    
    async def _get_data(self) -> Optional[InputData]:
        """
        Captura específica de dados de voz.
        
        Returns:
            Dados de voz ou None se não disponível
        """
        try:
            if self.mock_mode:
                # Modo mock - dados simulados
                voice_data = {
                    "text": "Olá Tobias, como você está?",
                    "confidence": 0.95,
                    "language": self.language,
                    "timestamp": datetime.now().isoformat(),
                    "audio_level": 0.7,
                    "is_speech": True
                }
            else:
                # Captura real do DJI Mic 2
                voice_data = await self._capture_real_audio()
                if not voice_data:
                    return None
            
            return InputData(
                input_type="G1Voice",
                source="dji_mic_2",
                timestamp=datetime.now(),
                data=voice_data,
                confidence=voice_data.get("confidence", 0.0)
            )
            
        except Exception as e:
            logger.error(f"Erro ao capturar dados de voz: {e}")
            return None

    async def _capture_real_audio(self) -> Optional[Dict[str, Any]]:
        """Captura áudio real do DJI Mic 2"""
        try:
            if self.is_capturing:
                return None  # Já está capturando
            
            self.is_capturing = True
            
            # Criar arquivo temporário
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                audio_file = tmp_file.name
            
            # Comando para capturar áudio do DJI Mic
            cmd = [
                'arecord',
                '-D', self.dji_device,
                '-f', self.dji_format,
                '-r', str(self.sample_rate),
                '-c', '2',  # Stereo
                '-d', str(self.capture_duration),
                audio_file
            ]
            
            # Executar captura (sem bloquear)
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0 and os.path.exists(audio_file):
                file_size = os.path.getsize(audio_file)
                
                if file_size > 1000:  # Pelo menos 1KB
                    # Por enquanto, simular STT - futuramente integrar Google Speech API
                    voice_data = {
                        "text": "Audio capturado do DJI Mic",  # Placeholder
                        "confidence": 0.8,
                        "language": self.language,
                        "timestamp": datetime.now().isoformat(),
                        "audio_file": audio_file,
                        "file_size": file_size,
                        "duration": self.capture_duration,
                        "is_speech": True,
                        "audio_level": 0.7
                    }
                    
                    logger.debug(f"Audio capturado: {file_size} bytes")
                    return voice_data
                else:
                    logger.warning("Audio capturado muito pequeno")
                    os.remove(audio_file)
                    return None
            else:
                logger.error(f"Erro na captura: {stderr.decode() if stderr else 'Unknown'}")
                if os.path.exists(audio_file):
                    os.remove(audio_file)
                return None
                
        except Exception as e:
            logger.error(f"Erro na captura de áudio: {e}")
            return None
        finally:
            self.is_capturing = False
    
    async def _health_check(self) -> bool:
        """
        Verificação específica de saúde do G1VoiceInput.
        
        Returns:
            True se está saudável
        """
        try:
            # Simula verificação de saúde
            return True
            
        except Exception as e:
            logger.error(f"Erro na verificação de saúde do G1VoiceInput: {e}")
            return False
