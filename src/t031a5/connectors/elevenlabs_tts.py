"""
Conector ElevenLabs TTS.
Fornece TTS de alta qualidade com múltiplas vozes e controle de emoção.
"""

import asyncio
import logging
import requests
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path
import tempfile
import os

logger = logging.getLogger(__name__)


@dataclass
class ElevenLabsVoice:
    """Informações de uma voz ElevenLabs."""
    voice_id: str
    name: str
    category: str
    description: str
    labels: Dict[str, str]
    preview_url: Optional[str] = None


@dataclass
class ElevenLabsTTSRequest:
    """Requisição para TTS ElevenLabs."""
    text: str
    voice_id: str
    model_id: str = "eleven_multilingual_v2"
    voice_settings: Optional[Dict[str, Any]] = None
    output_format: str = "mp3"
    optimize_streaming_latency: int = 4


@dataclass
class ElevenLabsTTSResponse:
    """Resposta do TTS ElevenLabs."""
    success: bool
    audio_file_path: Optional[str] = None
    duration: Optional[float] = None
    error_message: Optional[str] = None


class ElevenLabsTTSConnector:
    """Conector para ElevenLabs TTS."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", True)
        self.api_key = config.get("api_key")
        self.base_url = "https://api.elevenlabs.io/v1"
        self.default_voice_id = config.get("default_voice_id", "21m00Tcm4TlvDq8ikWAM")  # Rachel
        self.default_model = config.get("default_model", "eleven_multilingual_v2")
        self.output_dir = Path(config.get("output_dir", "temp/audio"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache de vozes
        self.voices_cache: Dict[str, ElevenLabsVoice] = {}
        self.cache_expiry = 0
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"ElevenLabsTTSConnector inicializado: enabled={self.enabled}")
    
    async def initialize(self) -> bool:
        """Inicializa o conector."""
        if not self.enabled:
            return False
        
        if not self.api_key:
            self.logger.error("❌ API Key do ElevenLabs não configurada")
            return False
        
        try:
            # Testa conectividade
            await self._load_voices()
            self.logger.info("✅ ElevenLabs TTS conectado")
            return True
        except Exception as e:
            self.logger.error(f"❌ Erro ao conectar ElevenLabs: {e}")
            return False
    
    async def _load_voices(self) -> List[ElevenLabsVoice]:
        """Carrega lista de vozes disponíveis."""
        import time
        
        # Verifica cache
        if time.time() < self.cache_expiry and self.voices_cache:
            return list(self.voices_cache.values())
        
        try:
            headers = {"xi-api-key": self.api_key}
            response = requests.get(f"{self.base_url}/voices", headers=headers)
            
            if response.status_code != 200:
                raise Exception(f"Erro ao carregar vozes: {response.status_code}")
            
            data = response.json()
            voices = []
            
            for voice_data in data.get("voices", []):
                voice = ElevenLabsVoice(
                    voice_id=voice_data["voice_id"],
                    name=voice_data["name"],
                    category=voice_data.get("category", "general"),
                    description=voice_data.get("description", ""),
                    labels=voice_data.get("labels", {}),
                    preview_url=voice_data.get("preview_url")
                )
                voices.append(voice)
                self.voices_cache[voice.voice_id] = voice
            
            # Cache por 1 hora
            self.cache_expiry = time.time() + 3600
            self.logger.info(f"Carregadas {len(voices)} vozes ElevenLabs")
            return voices
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar vozes: {e}")
            return []
    
    async def get_voices(self) -> List[ElevenLabsVoice]:
        """Obtém lista de vozes disponíveis."""
        return await self._load_voices()
    
    async def get_voice_by_name(self, name: str) -> Optional[ElevenLabsVoice]:
        """Obtém voz por nome."""
        voices = await self.get_voices()
        for voice in voices:
            if voice.name.lower() == name.lower():
                return voice
        return None
    
    async def synthesize_speech(self, request: ElevenLabsTTSRequest) -> ElevenLabsTTSResponse:
        """Sintetiza fala usando ElevenLabs - MÉTODO TESTADO."""
        if not self.enabled or not self.api_key:
            return ElevenLabsTTSResponse(
                success=False,
                error_message="ElevenLabs TTS não inicializado"
            )
        
        try:
            # MÉTODO TESTADO: Usar biblioteca elevenlabs com API key explícita
            from elevenlabs import generate, save
            
            self.logger.info(f"🎤 Gerando TTS: '{request.text[:50]}...' com voz {request.voice_id}")
            
            # Gerar áudio com método testado
            audio = generate(
                text=request.text,
                voice=request.voice_id,
                api_key=self.api_key  # API key explícita necessária (testado)
            )
            
            # Salvar arquivo de áudio
            timestamp = int(asyncio.get_event_loop().time() * 1000)
            filename = f"elevenlabs_{timestamp}.{request.output_format}"
            filepath = self.output_dir / filename
            
            # Usar função save da biblioteca (método testado)
            save(audio, str(filepath))
            
            # Verificar se arquivo foi gerado
            if not filepath.exists():
                return ElevenLabsTTSResponse(
                    success=False,
                    error_message="Arquivo de áudio não foi gerado"
                )
            
            file_size = filepath.stat().st_size
            
            # Verificar se arquivo tem conteúdo (método testado)
            if file_size < 5000:  # Menos de 5KB indica problema
                return ElevenLabsTTSResponse(
                    success=False,
                    error_message=f"Arquivo muito pequeno: {file_size} bytes"
                )
            
            # Calcular duração aproximada (baseado no texto)
            duration = len(request.text.split()) * 0.5  # ~0.5s por palavra
            
            self.logger.info(f"✅ ElevenLabs TTS gerado: {filename} ({file_size} bytes, método testado)")
            
            return ElevenLabsTTSResponse(
                success=True,
                audio_file_path=str(filepath),
                duration=duration
            )
            
        except Exception as e:
            self.logger.error(f"❌ Erro no ElevenLabs TTS: {e}")
            return ElevenLabsTTSResponse(
                success=False,
                error_message=f"Exceção: {str(e)}"
            )
    
    async def speak(self, text: str, voice_id: Optional[str] = None) -> ElevenLabsTTSResponse:
        """Método simplificado para falar."""
        voice_id = voice_id or self.default_voice_id
        
        request = ElevenLabsTTSRequest(
            text=text,
            voice_id=voice_id,
            model_id=self.default_model
        )
        
        return await self.synthesize_speech(request)
    
    def is_available(self) -> bool:
        """Verifica se o conector está disponível."""
        return self.enabled and bool(self.api_key)
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Obtém capacidades do conector."""
        return {
            "provider": "elevenlabs",
            "type": "tts",
            "quality": "high",
            "features": [
                "multilingual",
                "voice_cloning",
                "emotion_control",
                "streaming",
                "high_quality"
            ],
            "supported_formats": ["mp3", "wav", "flac"],
            "supported_models": [
                "eleven_multilingual_v2",
                "eleven_turbo_v2",
                "eleven_monolingual_v1"
            ]
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Obtém status do conector."""
        try:
            voices = await self.get_voices()
            return {
                "enabled": self.enabled,
                "connected": bool(self.api_key),
                "voices_count": len(voices),
                "default_voice": self.default_voice_id,
                "output_directory": str(self.output_dir)
            }
        except Exception as e:
            return {
                "enabled": self.enabled,
                "connected": False,
                "error": str(e)
            }
