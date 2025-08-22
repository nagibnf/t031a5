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
            # Verificar se DJI Mic 2 está disponível (MÉTODO TESTADO)
            logger.info("Verificando DJI Mic 2...")
        
            # Testar se o dispositivo está disponível
            proc = subprocess.Popen(['arecord', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            
            if 'DJI MIC MINI' in stdout.decode():
                logger.info("🎤 DJI MIC MINI detectado - usando hardware real (método testado)")
                self.mock_mode = False
                
                # Inicializar conector de captura com configurações testadas
                from ...connectors.audio_capture import AudioCaptureConnector
                self.audio_capture = AudioCaptureConnector({
                    "device": "hw:0,0",      # DJI Mic card 0, device 0 (testado)
                    "format": "S24_3LE",    # Formato nativo testado
                    "rate": 48000,          # Taxa nativa testada
                    "channels": 2,          # Estéreo testado
                    "enabled": True
                })
            else:
                logger.warning("DJI MIC MINI não encontrado - usando modo mock")
                self.mock_mode = True
                self.audio_capture = None
                
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
        """Captura áudio real do DJI Mic 2 com Google STT gRPC streaming"""
        try:
            if self.is_capturing:
                return None  # Já está capturando
            
            self.is_capturing = True
            
            # Usar streaming STT via gRPC (MÉTODO REAL-TIME)
            text_result = await self._stream_stt_grpc()
            
            if text_result:
                voice_data = {
                    "text": text_result["transcript"],
                    "confidence": text_result["confidence"],
                    "language": self.language,
                    "timestamp": datetime.now().isoformat(),
                    "is_speech": True,
                    "audio_level": 0.8,
                    "method": "dji_mic_google_stt_grpc_streaming",
                    "is_final": text_result["is_final"]
                }
                
                logger.info(f"🎤 STT gRPC: '{text_result['transcript'][:50]}...' (confidence: {text_result['confidence']:.2f})")
                return voice_data
            else:
                return None
                
        except Exception as e:
            logger.error(f"Erro na captura STT gRPC: {e}")
            return None
        finally:
            self.is_capturing = False
            
    async def _stream_stt_grpc(self) -> Optional[Dict[str, Any]]:
        """Streaming STT via Google Speech API gRPC - TEMPO REAL"""
        try:
            import pyaudio
            import queue
            import threading
            from google.cloud import speech
            
            # Config de áudio para DJI Mic
            RATE = 16000
            CHUNK = int(RATE / 10)  # 100ms chunks
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            
            # Config Google Speech API
            client = speech.SpeechClient()
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=RATE,
                language_code=self.language,
                enable_automatic_punctuation=True,
            )
            streaming_config = speech.StreamingRecognitionConfig(
                config=config,
                interim_results=True,
            )
            
            audio_queue = queue.Queue()
            stream_active = True
            
            def record_audio():
                """Thread de captura DJI Mic"""
                audio = pyaudio.PyAudio()
                stream = audio.open(
                    format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                )
                
                logger.info("🔴 Iniciando captura streaming DJI Mic...")
                while stream_active:
                    try:
                        data = stream.read(CHUNK, exception_on_overflow=False)
                        audio_queue.put(data)
                    except Exception as e:
                        logger.warning(f"Erro captura chunk: {e}")
                        break
                
                stream.stop_stream()
                stream.close()
                audio.terminate()
            
            def audio_generator():
                """Gerador de chunks para gRPC"""
                while stream_active:
                    try:
                        chunk = audio_queue.get(timeout=1.0)
                        yield speech.StreamingRecognizeRequest(audio_content=chunk)
                    except queue.Empty:
                        continue
                    except Exception as e:
                        logger.warning(f"Erro generator: {e}")
                        break
            
            # Iniciar captura em thread
            record_thread = threading.Thread(target=record_audio)
            record_thread.daemon = True
            record_thread.start()
            
            logger.info("🧠 Conectando Google Speech API via gRPC...")
            
            # Stream gRPC
            requests = audio_generator()
            responses = client.streaming_recognize(streaming_config, requests)
            
            logger.info("📝 Streaming STT ativo - fale algo:")
            
            # Processar respostas em tempo real
            for response in responses:
                for result in response.results:
                    transcript = result.alternatives[0].transcript
                    confidence = result.alternatives[0].confidence if result.alternatives[0].confidence else 0.8
                    
                    # Mostrar no console em tempo real
                    if result.is_final:
                        print(f"[FINAL] {transcript}")
                        stream_active = False
                        return {
                            "transcript": transcript,
                            "confidence": confidence,
                            "is_final": True
                        }
                    else:
                        print(f"[TEMP]  {transcript}", end='\r')
            
            return None
            
        except Exception as e:
            logger.error(f"Erro streaming STT gRPC: {e}")
            return None
    
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
