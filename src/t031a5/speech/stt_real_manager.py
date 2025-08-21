#!/usr/bin/env python3
"""
🎤 STT REAL MANAGER - Google Speech API + Whisper Fallback
Sistema de Speech-to-Text com múltiplos providers para máxima confiabilidade
"""

import os
import json
import logging
import tempfile
import wave
import numpy as np
from typing import Optional, Dict, Any
from pathlib import Path
import asyncio

# Carregar variáveis do .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv é opcional

# Google Speech API
try:
    from google.cloud import speech
    GOOGLE_SPEECH_AVAILABLE = True
except ImportError:
    GOOGLE_SPEECH_AVAILABLE = False
    speech = None

# OpenAI Whisper
try:
    import openai
    OPENAI_WHISPER_AVAILABLE = True
except ImportError:
    OPENAI_WHISPER_AVAILABLE = False
    openai = None

# Whisper local (opcional)
try:
    import whisper
    WHISPER_LOCAL_AVAILABLE = True
except ImportError:
    WHISPER_LOCAL_AVAILABLE = False
    whisper = None

logger = logging.getLogger(__name__)

class STTRealManager:
    """
    Gerenciador de Speech-to-Text real com múltiplos providers.
    
    Ordem de prioridade:
    1. Google Speech API (cloud, alta precisão)
    2. OpenAI Whisper API (cloud, fallback)
    3. Whisper Local (offline, último recurso)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa STT Manager.
        
        Args:
            config: Configurações customizadas
        """
        self.config = config or {}
        
        # Configurações padrão
        self.language = self.config.get("language", "pt-BR")
        self.sample_rate = self.config.get("sample_rate", 16000)
        self.encoding = self.config.get("encoding", "LINEAR16")
        
        # Configurações de qualidade
        self.min_confidence = self.config.get("min_confidence", 0.7)
        self.max_retries = self.config.get("max_retries", 2)
        
        # Providers disponíveis
        self.providers_available = {
            "google": GOOGLE_SPEECH_AVAILABLE,
            "openai_whisper": OPENAI_WHISPER_AVAILABLE,
            "whisper_local": WHISPER_LOCAL_AVAILABLE
        }
        
        # Inicializar providers
        self._init_google_speech()
        self._init_openai_whisper()
        self._init_whisper_local()
        
        logger.info("🎤 STT Real Manager inicializado")
        self._log_providers_status()
    
    def _init_google_speech(self):
        """Inicializa Google Speech API."""
        self.google_client = None
        
        if not GOOGLE_SPEECH_AVAILABLE:
            logger.warning("⚠️ Google Speech API não disponível (google-cloud-speech não instalado)")
            return
        
        try:
            # Verificar credenciais
            google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if not google_creds:
                # Tentar criar credenciais do .env
                self._setup_google_credentials()
            
            # Criar cliente
            self.google_client = speech.SpeechClient()
            
            # Configuração de reconhecimento
            self.google_config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=self.sample_rate,
                language_code=self.language,
                enable_automatic_punctuation=True,
                enable_word_confidence=True,
                model="latest_long"  # Modelo otimizado para conversação
            )
            
            logger.info("✅ Google Speech API configurado")
            
        except Exception as e:
            logger.warning(f"⚠️ Falha na configuração Google Speech: {e}")
            self.google_client = None
    
    def _setup_google_credentials(self):
        """Configura credenciais Google do .env."""
        try:
            # Buscar credenciais no .env
            google_creds_path = os.getenv("GOOGLE_SPEECH_CREDENTIALS_JSON")
            if google_creds_path:
                # Verificar se é um caminho para arquivo ou JSON inline
                if google_creds_path.startswith("{"):
                    # É JSON inline - criar arquivo temporário
                    creds_path = Path("/tmp/google_speech_credentials.json")
                    creds_path.write_text(google_creds_path)
                    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(creds_path)
                    logger.info("✅ Credenciais Google configuradas do JSON inline")
                else:
                    # É caminho para arquivo - usar diretamente
                    creds_file = Path(google_creds_path)
                    if not creds_file.is_absolute():
                        # Caminho relativo - resolver a partir do diretório do projeto
                        project_root = Path(__file__).parent.parent.parent.parent
                        creds_file = project_root / creds_file
                    
                    if creds_file.exists():
                        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(creds_file)
                        logger.info(f"✅ Credenciais Google configuradas do arquivo: {creds_file}")
                    else:
                        logger.error(f"❌ Arquivo de credenciais não encontrado: {creds_file}")
            else:
                logger.warning("⚠️ GOOGLE_SPEECH_CREDENTIALS_JSON não encontrado no .env")
        except Exception as e:
            logger.warning(f"⚠️ Erro configurando credenciais Google: {e}")
    
    def _init_openai_whisper(self):
        """Inicializa OpenAI Whisper API."""
        self.openai_client = None
        
        if not OPENAI_WHISPER_AVAILABLE:
            logger.warning("⚠️ OpenAI Whisper não disponível (openai não instalado)")
            return
        
        try:
            # Configurar API key
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("⚠️ OPENAI_API_KEY não encontrada no .env")
                return
            
            # Criar cliente
            self.openai_client = openai.OpenAI(api_key=api_key)
            logger.info("✅ OpenAI Whisper API configurado")
            
        except Exception as e:
            logger.warning(f"⚠️ Falha na configuração OpenAI Whisper: {e}")
            self.openai_client = None
    
    def _init_whisper_local(self):
        """Inicializa Whisper local."""
        self.whisper_model = None
        
        if not WHISPER_LOCAL_AVAILABLE:
            logger.warning("⚠️ Whisper local não disponível (whisper não instalado)")
            return
        
        try:
            # Carregar modelo pequeno para economia de recursos
            model_name = self.config.get("whisper_model", "base")
            self.whisper_model = whisper.load_model(model_name)
            logger.info(f"✅ Whisper local configurado (modelo: {model_name})")
            
        except Exception as e:
            logger.warning(f"⚠️ Falha na configuração Whisper local: {e}")
            self.whisper_model = None
    
    def _log_providers_status(self):
        """Log status dos providers."""
        logger.info("📊 STATUS PROVIDERS STT:")
        for provider, available in self.providers_available.items():
            status = "✅ Disponível" if available else "❌ Indisponível"
            logger.info(f"   {provider}: {status}")
    
    async def transcribe_audio(self, audio_data: np.ndarray) -> Optional[str]:
        """
        Transcreve áudio para texto usando o melhor provider disponível.
        
        Args:
            audio_data: Dados de áudio (mono, 16kHz, float32)
            
        Returns:
            str: Texto transcrito ou None se falha
        """
        if audio_data is None or len(audio_data) == 0:
            logger.error("❌ Dados de áudio inválidos")
            return None
        
        # Tentar providers em ordem de prioridade
        providers = [
            ("google", self._transcribe_google),
            ("openai_whisper", self._transcribe_openai_whisper),
            ("whisper_local", self._transcribe_whisper_local)
        ]
        
        for provider_name, transcribe_func in providers:
            if not self.providers_available[provider_name]:
                continue
            
            try:
                logger.info(f"🎤 Tentando STT via {provider_name}...")
                
                # Tentar transcrição
                resultado = await transcribe_func(audio_data)
                
                if resultado and len(resultado.strip()) > 0:
                    logger.info(f"✅ STT sucesso via {provider_name}: '{resultado}'")
                    return resultado.strip()
                else:
                    logger.warning(f"⚠️ {provider_name} retornou resultado vazio")
                    
            except Exception as e:
                logger.warning(f"⚠️ Falha STT {provider_name}: {e}")
                continue
        
        logger.error("❌ Todos os providers STT falharam")
        return None
    
    async def _transcribe_google(self, audio_data: np.ndarray) -> Optional[str]:
        """Transcrição via Google Speech API."""
        if not self.google_client:
            raise Exception("Google Speech client não inicializado")
        
        # Converter para formato esperado pelo Google
        audio_bytes = self._audio_to_bytes(audio_data)
        
        # Criar objeto de áudio
        audio = speech.RecognitionAudio(content=audio_bytes)
        
        # Executar reconhecimento
        response = self.google_client.recognize(
            config=self.google_config,
            audio=audio
        )
        
        # Processar resultado
        if response.results:
            # Pegar melhor resultado
            result = response.results[0]
            if result.alternatives:
                alternative = result.alternatives[0]
                
                # Verificar confiança
                confidence = getattr(alternative, 'confidence', 1.0)
                if confidence >= self.min_confidence:
                    return alternative.transcript
                else:
                    logger.warning(f"⚠️ Confiança baixa Google Speech: {confidence}")
        
        return None
    
    async def _transcribe_openai_whisper(self, audio_data: np.ndarray) -> Optional[str]:
        """Transcrição via OpenAI Whisper API."""
        if not self.openai_client:
            raise Exception("OpenAI client não inicializado")
        
        # Salvar áudio como arquivo temporário
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            self._save_audio_wav(audio_data, temp_file.name)
            
            try:
                # Fazer upload e transcrição
                with open(temp_file.name, "rb") as audio_file:
                    response = self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language="pt"  # Português
                    )
                
                return response.text
                
            finally:
                # Limpeza
                Path(temp_file.name).unlink()
    
    async def _transcribe_whisper_local(self, audio_data: np.ndarray) -> Optional[str]:
        """Transcrição via Whisper local."""
        if not self.whisper_model:
            raise Exception("Whisper local não inicializado")
        
        # Salvar áudio temporário
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            self._save_audio_wav(audio_data, temp_file.name)
            
            try:
                # Transcrever
                result = self.whisper_model.transcribe(
                    temp_file.name,
                    language="pt"
                )
                
                return result["text"]
                
            finally:
                # Limpeza
                Path(temp_file.name).unlink()
    
    def _audio_to_bytes(self, audio_data: np.ndarray) -> bytes:
        """Converte áudio para bytes (16-bit)."""
        # Converter float32 → int16
        audio_int16 = (audio_data * 32767).astype(np.int16)
        return audio_int16.tobytes()
    
    def _save_audio_wav(self, audio_data: np.ndarray, filename: str):
        """Salva áudio como arquivo WAV."""
        audio_int16 = (audio_data * 32767).astype(np.int16)
        
        with wave.open(filename, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_int16.tobytes())
    
    def get_status(self) -> Dict[str, Any]:
        """Obtém status detalhado do STT Manager."""
        return {
            "providers_available": self.providers_available.copy(),
            "google_ready": self.google_client is not None,
            "openai_ready": self.openai_client is not None,
            "whisper_local_ready": self.whisper_model is not None,
            "language": self.language,
            "sample_rate": self.sample_rate,
            "min_confidence": self.min_confidence
        }

# Exemplo de uso
if __name__ == "__main__":
    import asyncio
    import logging
    
    logging.basicConfig(level=logging.INFO)
    
    async def test_stt():
        """Teste básico do STT."""
        stt_manager = STTRealManager()
        
        # Status
        status = stt_manager.get_status()
        print("📊 STATUS STT:")
        for key, value in status.items():
            print(f"   {key}: {value}")
        
        # Simular áudio (seria do AudioManagerDefinitivo)
        # audio_data = audio_manager.capturar_audio_dji(5.0)
        # texto = await stt_manager.transcribe_audio(audio_data)
        
        print("✅ STT Manager testado")
    
    asyncio.run(test_stt())
