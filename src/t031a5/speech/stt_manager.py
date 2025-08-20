#!/usr/bin/env python3
"""
Gerenciador de Speech-to-Text - Sistema t031a5

Usa Google Speech API como primário e OpenAI Whisper como fallback
"""

import asyncio
import logging
import os
import tempfile
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class STTManager:
    """Gerenciador de Speech-to-Text para t031a5."""
    
    def __init__(self, config_path: str = "config/g1_stt.json5"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.is_initialized = False
        
    def load_config(self) -> Dict[str, Any]:
        """Carrega configuração de STT."""
        try:
            import json5
            with open(self.config_path, 'r') as f:
                return json5.load(f)
        except ImportError:
            import json
            with open(self.config_path, 'r') as f:
                return json.load(f)
    
    async def initialize(self) -> bool:
        """Inicializa o STT Manager."""
        try:
            logger.info("🎤 Inicializando STT Manager...")
            
            # Verifica APIs disponíveis
            google_available = self._check_google_credentials()
            openai_available = self._check_openai_key()
            
            if google_available:
                logger.info("✅ Google Speech API disponível")
            else:
                logger.warning("⚠️ Google Speech API não configurada")
            
            if openai_available:
                logger.info("✅ OpenAI Whisper disponível")
            else:
                logger.warning("⚠️ OpenAI Whisper não configurado")
            
            if not google_available and not openai_available:
                logger.error("❌ Nenhuma API de STT disponível")
                return False
            
            self.is_initialized = True
            logger.info("✅ STT Manager inicializado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar STT Manager: {e}")
            return False
    
    def _check_google_credentials(self) -> bool:
        """Verifica se as credenciais do Google estão configuradas."""
        # Verifica se já temos GOOGLE_APPLICATION_CREDENTIALS
        google_creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if google_creds_path and Path(google_creds_path).exists():
            return True
        
        # Verifica a variável do .env: GOOGLE_ASR_CREDENTIALS_FILE
        google_asr_file = os.getenv('GOOGLE_ASR_CREDENTIALS_FILE')
        if google_asr_file and Path(google_asr_file).exists():
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(Path(google_asr_file).absolute())
            logger.info(f"✅ Google ASR credentials configuradas: {google_asr_file}")
            return True
        
        return False
    
    def _check_openai_key(self) -> bool:
        """Verifica se a API key do OpenAI está configurada."""
        return bool(os.getenv('OPENAI_API_KEY'))
    
    async def transcribe_audio(self, audio_data: bytes, language: str = "pt-BR") -> Optional[str]:
        """Transcreve áudio para texto usando Google Speech API ou OpenAI Whisper."""
        if not self.is_initialized:
            logger.error("STT Manager não inicializado")
            return None
        
        try:
            # Verifica qual API usar baseado na disponibilidade
            google_available = self._check_google_credentials()
            openai_available = self._check_openai_key()
            
            # Prioriza Google se disponível
            if google_available:
                result = await self._transcribe_google(audio_data, language)
                if result:
                    return result
                # Se Google falhar, tenta OpenAI
                elif openai_available:
                    logger.info("🔄 Google STT falhou, usando OpenAI Whisper...")
                    result = await self._transcribe_openai(audio_data, language)
                    if result:
                        return result
            # Se Google não disponível, usa OpenAI diretamente
            elif openai_available:
                result = await self._transcribe_openai(audio_data, language)
                if result:
                    return result
            
            logger.error("❌ Falha na transcrição - nenhuma API disponível")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro na transcrição: {e}")
            return None
    
    async def _transcribe_google(self, audio_data: bytes, language: str) -> Optional[str]:
        """Transcreve usando Google Speech API."""
        try:
            from google.cloud import speech
            
            client = speech.SpeechClient()
            
            # Configura o áudio
            audio = speech.RecognitionAudio(content=audio_data)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=language,
                enable_automatic_punctuation=True,
                model="latest_long"
            )
            
            # Faz a transcrição
            response = client.recognize(config=config, audio=audio)
            
            if response.results:
                transcript = " ".join([result.alternatives[0].transcript for result in response.results])
                logger.info(f"✅ Google STT: '{transcript}'")
                return transcript
            else:
                logger.debug("🔍 Google STT: Nenhum resultado (silêncio ou áudio muito baixo)")
                return None
                
        except Exception as e:
            error_msg = str(e)
            if "quota_exceeded" in error_msg or "billing" in error_msg:
                logger.error("❌ GOOGLE SPEECH: Cota excedida!")
                logger.error("   💳 Adicione créditos em: https://console.cloud.google.com/billing")
                logger.error("   📊 Verifique seu uso em: https://console.cloud.google.com/apis/credentials")
            elif "invalid_credentials" in error_msg or "authentication" in error_msg:
                logger.error("❌ GOOGLE SPEECH: Credenciais inválidas!")
                logger.error("   🔑 Verifique GOOGLE_ASR_CREDENTIALS_FILE no arquivo .env")
                logger.error("   📁 Arquivo deve existir e ser válido")
            elif "project" in error_msg and "not found" in error_msg:
                logger.error("❌ GOOGLE SPEECH: Projeto não encontrado!")
                logger.error("   🏗️ Verifique se o projeto está ativo no Google Cloud")
            else:
                logger.debug(f"🔍 Google STT não disponível: {error_msg}")
            return None
    
    async def _transcribe_openai(self, audio_data: bytes, language: str) -> Optional[str]:
        """Transcreve usando OpenAI Whisper."""
        try:
            import openai
            
            # Salva áudio temporariamente
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Faz a transcrição usando a nova API
                client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                
                with open(temp_file_path, "rb") as audio_file:
                    response = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language=language.split("-")[0] if "-" in language else language
                    )
                
                transcript = response.text
                logger.info(f"✅ OpenAI Whisper: '{transcript}'")
                return transcript
                
            finally:
                # Remove arquivo temporário
                os.unlink(temp_file_path)
                
        except Exception as e:
            logger.error(f"❌ Erro no OpenAI Whisper: {e}")
            return None
    
    async def cleanup(self) -> None:
        """Limpa recursos do STT Manager."""
        try:
            logger.info("🧹 Limpando STT Manager...")
            self.is_initialized = False
            logger.info("✅ STT Manager limpo")
        except Exception as e:
            logger.error(f"❌ Erro ao limpar STT Manager: {e}")


# Exemplo de uso
async def main() -> None:
    """Exemplo de uso do STT Manager."""
    stt_manager = STTManager()
    
    if await stt_manager.initialize():
        print("✅ STT Manager inicializado")
        
        # Aqui você testaria com áudio real
        # audio_data = await capture_audio()
        # text = await stt_manager.transcribe_audio(audio_data)
        # print(f"Transcrição: {text}")
        
        await stt_manager.cleanup()
    else:
        print("❌ Falha ao inicializar STT Manager")


if __name__ == "__main__":
    asyncio.run(main())
