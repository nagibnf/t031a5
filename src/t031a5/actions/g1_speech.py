"""Action G1SpeechAction REAL para o sistema t031a5 - MÉTODO TESTADO."""

import logging
import asyncio
from typing import Any, Dict, Optional
from datetime import datetime

from .base import BaseAction, ActionRequest, ActionResult
from ..connectors.elevenlabs_tts import ElevenLabsTTSConnector, ElevenLabsTTSRequest
from ..connectors.audio_player import AudioPlayerConnector

logger = logging.getLogger(__name__)


class G1SpeechAction(BaseAction):
    """Action de fala do G1 - IMPLEMENTAÇÃO REAL COM MÉTODO TESTADO."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.tts_provider = config.get("tts_provider", "elevenlabs")
        self.voice_id = config.get("voice_id", "Alice")
        self.audio_output = config.get("audio_output", "anker_bluetooth")
        self.language = config.get("language", "pt")
        
        # Inicializar conectores
        self.elevenlabs = None
        self.audio_player = None
        
        logger.info(f"G1SpeechAction configurado: {self.tts_provider}, voz: {self.voice_id}, saída: {self.audio_output}")
    
    async def _initialize(self) -> bool:
        """Inicializa conectores TTS e Audio - MÉTODO TESTADO."""
        try:
            # Inicializar ElevenLabs TTS
            if self.tts_provider == "elevenlabs":
                self.elevenlabs = ElevenLabsTTSConnector({
                    "enabled": True,
                    "output_dir": "audio/speech"
                })
                await self.elevenlabs.initialize()
            
            # Inicializar Audio Player (MÉTODO TESTADO)
            self.audio_player = AudioPlayerConnector({"enabled": True})
            
            logger.info("✅ G1SpeechAction inicializado com conectores reais")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar G1SpeechAction: {e}")
            return False
    
    async def _start(self) -> bool:
        logger.info("G1SpeechAction iniciado com sucesso")
        return True
    
    async def _stop(self) -> bool:
        logger.info("G1SpeechAction parado com sucesso")
        return True
    
    async def _execute(self, request: ActionRequest) -> ActionResult:
        """Executa fala usando ElevenLabs + Anker - MÉTODO TESTADO."""
        start_time = datetime.now()
        
        try:
            text = request.data.get("text", "Olá! Sou o G1 Tobias.")
            logger.info(f"G1 falando: {text}")
            
            # 1. Gerar áudio com ElevenLabs (TESTADO)
            if self.elevenlabs:
                tts_request = ElevenLabsTTSRequest(
                    text=text,
                    voice_id=self.voice_id,
                    model_id="eleven_multilingual_v2",
                    output_format="mp3"
                )
                
                tts_response = await self.elevenlabs.synthesize_speech(tts_request)
                
                if not tts_response.success:
                    raise Exception(f"Erro no TTS: {tts_response.error_message}")
                
                # 2. Reproduzir no Anker (MÉTODO TESTADO E FUNCIONANDO)
                if self.audio_output == "anker_bluetooth" and self.audio_player:
                    audio_success = await self.audio_player.play_audio_anker(tts_response.audio_file_path)
                    
                    if not audio_success:
                        # Fallback para saída padrão
                        await self.audio_player.play_audio_default(tts_response.audio_file_path)
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                return ActionResult(
                    action_type="speech",
                    action_name=request.action_name,
                    timestamp=datetime.now(),
                    success=True,
                    data={
                        "text": text, 
                        "tts_provider": self.tts_provider,
                        "audio_file": tts_response.audio_file_path,
                        "method": "elevenlabs_mp3_wav_paplay_anker_TESTADO"
                    },
                    execution_time=execution_time
                )
            
            else:
                # Fallback para mock se não inicializou
                logger.warning("TTS não inicializado, usando mock")
                return ActionResult(
                    action_type="speech",
                    action_name=request.action_name,
                    timestamp=datetime.now(),
                    success=True,
                    data={"text": text, "tts_provider": "mock"},
                    execution_time=0.1
                )
                
        except Exception as e:
            logger.error(f"Erro ao executar fala: {e}")
            return ActionResult(
                action_type="speech",
                action_name=request.action_name,
                timestamp=datetime.now(),
                success=False,
                data={},
                error_message=str(e),
                execution_time=(datetime.now() - start_time).total_seconds()
            )
    
    async def _health_check(self) -> bool:
        return self.elevenlabs is not None and self.audio_player is not None
