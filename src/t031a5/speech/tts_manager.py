#!/usr/bin/env python3
"""
Gerenciador de Text-to-Speech - Sistema t031a5

Usa ElevenLabs para síntese de voz em português
"""

import asyncio
import logging
import os
import requests
import tempfile
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class TTSManager:
    """Gerenciador de Text-to-Speech para t031a5."""
    
    def __init__(self, config_path: str = "config/g1_tts.json5"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        self.is_initialized = False
        
    def load_config(self) -> Dict[str, Any]:
        """Carrega configuração de TTS."""
        try:
            import json5
            with open(self.config_path, 'r') as f:
                return json5.load(f)
        except ImportError:
            import json
            with open(self.config_path, 'r') as f:
                return json.load(f)
    
    async def initialize(self) -> bool:
        """Inicializa o TTS Manager."""
        try:
            logger.info("🔊 Inicializando TTS Manager...")
            
            if not self.api_key:
                logger.error("❌ ElevenLabs API key não configurada")
                return False
            
            # Testa a conexão com ElevenLabs
            if await self._test_elevenlabs_connection():
                logger.info("✅ ElevenLabs conectado")
                self.is_initialized = True
                return True
            else:
                logger.error("❌ Falha na conexão com ElevenLabs")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar TTS Manager: {e}")
            return False
    
    async def _test_elevenlabs_connection(self) -> bool:
        """Testa a conexão com ElevenLabs."""
        try:
            url = "https://api.elevenlabs.io/v1/voices"
            headers = {
                "xi-api-key": self.api_key
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"❌ Erro ao testar ElevenLabs: {e}")
            return False
    
    async def synthesize_speech(self, text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> Optional[bytes]:
        """Sintetiza texto para áudio usando ElevenLabs."""
        if not self.is_initialized:
            logger.error("TTS Manager não inicializado")
            return None
        
        if not text.strip():
            logger.warning("⚠️ Texto vazio para síntese")
            return None
        
        try:
            logger.info(f"🔊 Sintetizando: '{text[:50]}...'")
            
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5,
                    "style": 0.0,
                    "use_speaker_boost": True
                }
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                audio_data = response.content
                logger.info(f"✅ Áudio sintetizado: {len(audio_data)} bytes")
                return audio_data
            elif response.status_code == 401:
                error_data = response.json()
                if "quota_exceeded" in response.text:
                    logger.error("❌ ELEVENLABS: Cota excedida!")
                    logger.error(f"   💳 Créditos restantes: {error_data.get('detail', {}).get('status', 'N/A')}")
                    logger.error(f"   📊 Créditos necessários: {error_data.get('detail', {}).get('message', 'N/A')}")
                    logger.error("   🔗 Adicione créditos em: https://elevenlabs.io/billing")
                else:
                    logger.error("❌ ELEVENLABS: API Key inválida!")
                    logger.error("   🔑 Verifique sua API key no arquivo .env")
                return None
            elif response.status_code == 429:
                logger.error("❌ ELEVENLABS: Muitas requisições!")
                logger.error("   ⏰ Aguarde um momento e tente novamente")
                return None
            else:
                logger.error(f"❌ ELEVENLABS: Erro {response.status_code}")
                logger.error(f"   📝 Detalhes: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro na síntese de voz: {e}")
            return None
    
    async def save_audio_to_file(self, audio_data: bytes, filename: str = "synthesized_speech.wav") -> Optional[str]:
        """Salva áudio sintetizado em arquivo."""
        try:
            output_path = Path("audio/speech") / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, "wb") as f:
                f.write(audio_data)
            
            logger.info(f"✅ Áudio salvo: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar áudio: {e}")
            return None
    
    async def get_available_voices(self) -> Optional[list]:
        """Lista vozes disponíveis no ElevenLabs."""
        try:
            url = "https://api.elevenlabs.io/v1/voices"
            headers = {
                "xi-api-key": self.api_key
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                voices = response.json().get("voices", [])
                logger.info(f"✅ {len(voices)} vozes disponíveis")
                return voices
            else:
                logger.error(f"❌ Erro ao listar vozes: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao listar vozes: {e}")
            return None
    
    async def cleanup(self) -> None:
        """Limpa recursos do TTS Manager."""
        try:
            logger.info("🧹 Limpando TTS Manager...")
            self.is_initialized = False
            logger.info("✅ TTS Manager limpo")
        except Exception as e:
            logger.error(f"❌ Erro ao limpar TTS Manager: {e}")


# Exemplo de uso
async def main() -> None:
    """Exemplo de uso do TTS Manager."""
    tts_manager = TTSManager()
    
    if await tts_manager.initialize():
        print("✅ TTS Manager inicializado")
        
        # Lista vozes disponíveis
        voices = await tts_manager.get_available_voices()
        if voices:
            print(f"Vozes disponíveis: {len(voices)}")
            for voice in voices[:3]:  # Mostra apenas as primeiras 3
                print(f"  - {voice['name']} (ID: {voice['voice_id']})")
        
        # Testa síntese
        text = "Olá! Sou Tobias, o robô G1. Estou pronto para ajudar!"
        audio_data = await tts_manager.synthesize_speech(text)
        
        if audio_data:
            print(f"Áudio sintetizado: {len(audio_data)} bytes")
            await tts_manager.save_audio_to_file(audio_data, "test_speech.wav")
        
        await tts_manager.cleanup()
    else:
        print("❌ Falha ao inicializar TTS Manager")


if __name__ == "__main__":
    asyncio.run(main())
