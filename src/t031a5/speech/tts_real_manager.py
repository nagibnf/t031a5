#!/usr/bin/env python3
"""
🔊 TTS REAL MANAGER - ElevenLabs + Fallback Synthesizers
Sistema de Text-to-Speech com voz natural em português brasileiro
"""

import os
import logging
import tempfile
import asyncio
import aiohttp
import json
import numpy as np
from typing import Optional, Dict, Any, List
from pathlib import Path
import wave

# Carregar variáveis do .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv é opcional

# ElevenLabs
try:
    import elevenlabs
    from elevenlabs import Voice, VoiceSettings
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    elevenlabs = None

# Pyttsx3 (fallback local)
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    pyttsx3 = None

# gTTS (Google TTS fallback)
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    gTTS = None

logger = logging.getLogger(__name__)

class TTSRealManager:
    """
    Gerenciador de Text-to-Speech real com múltiplos providers.
    
    Ordem de prioridade:
    1. ElevenLabs (qualidade profissional, português brasileiro)
    2. Google TTS (boa qualidade, gratuito)
    3. Pyttsx3 Local (offline, qualidade básica)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa TTS Manager.
        
        Args:
            config: Configurações customizadas
        """
        self.config = config or {}
        
        # Configurações ElevenLabs
        self.elevenlabs_voice_id = self.config.get("elevenlabs_voice_id", "pNInz6obpgDQGcFmaJgB")  # Adam voice
        self.elevenlabs_model = self.config.get("elevenlabs_model", "eleven_multilingual_v2")
        
        # Configurações de voz
        self.voice_stability = self.config.get("voice_stability", 0.75)
        self.voice_similarity = self.config.get("voice_similarity", 0.75)
        self.voice_style = self.config.get("voice_style", 0.50)
        
        # Configurações de áudio
        self.sample_rate = self.config.get("sample_rate", 16000)
        self.language = self.config.get("language", "pt")
        
        # Configurações de qualidade
        self.max_text_length = self.config.get("max_text_length", 500)
        self.chunk_size = self.config.get("chunk_size", 200)
        
        # Providers disponíveis
        self.providers_available = {
            "elevenlabs": ELEVENLABS_AVAILABLE,
            "gtts": GTTS_AVAILABLE,
            "pyttsx3": PYTTSX3_AVAILABLE
        }
        
        # Inicializar providers
        self._init_elevenlabs()
        self._init_gtts()
        self._init_pyttsx3()
        
        logger.info("🔊 TTS Real Manager inicializado")
        self._log_providers_status()
    
    def _init_elevenlabs(self):
        """Inicializa ElevenLabs API."""
        self.elevenlabs_client = None
        
        if not ELEVENLABS_AVAILABLE:
            logger.warning("⚠️ ElevenLabs não disponível (elevenlabs não instalado)")
            return
        
        try:
            # Configurar API key
            api_key = os.getenv("ELEVENLABS_API_KEY")
            if not api_key:
                logger.warning("⚠️ ELEVENLABS_API_KEY não encontrada no .env")
                return
            
            # Configurar cliente
            elevenlabs.set_api_key(api_key)
            
            # Configurar voz
            self.elevenlabs_voice = Voice(
                voice_id=self.elevenlabs_voice_id,
                settings=VoiceSettings(
                    stability=self.voice_stability,
                    similarity_boost=self.voice_similarity,
                    style=self.voice_style,
                    use_speaker_boost=True
                )
            )
            
            self.elevenlabs_client = True  # Marcador de configuração
            logger.info("✅ ElevenLabs configurado")
            
        except Exception as e:
            logger.warning(f"⚠️ Falha na configuração ElevenLabs: {e}")
            self.elevenlabs_client = None
    
    def _init_gtts(self):
        """Inicializa Google TTS."""
        if GTTS_AVAILABLE:
            logger.info("✅ Google TTS disponível")
        else:
            logger.warning("⚠️ Google TTS não disponível (gtts não instalado)")
    
    def _init_pyttsx3(self):
        """Inicializa Pyttsx3 local."""
        self.pyttsx3_engine = None
        
        if not PYTTSX3_AVAILABLE:
            logger.warning("⚠️ Pyttsx3 não disponível (pyttsx3 não instalado)")
            return
        
        try:
            # Criar engine
            self.pyttsx3_engine = pyttsx3.init()
            
            # Configurar propriedades
            voices = self.pyttsx3_engine.getProperty('voices')
            
            # Tentar encontrar voz em português
            for voice in voices:
                if 'pt' in voice.id.lower() or 'portuguese' in voice.name.lower():
                    self.pyttsx3_engine.setProperty('voice', voice.id)
                    break
            
            # Configurar taxa e volume
            self.pyttsx3_engine.setProperty('rate', 180)  # Palavras por minuto
            self.pyttsx3_engine.setProperty('volume', 0.9)
            
            logger.info("✅ Pyttsx3 configurado")
            
        except Exception as e:
            logger.warning(f"⚠️ Falha na configuração Pyttsx3: {e}")
            self.pyttsx3_engine = None
    
    def _log_providers_status(self):
        """Log status dos providers."""
        logger.info("📊 STATUS PROVIDERS TTS:")
        for provider, available in self.providers_available.items():
            status = "✅ Disponível" if available else "❌ Indisponível"
            logger.info(f"   {provider}: {status}")
    
    async def synthesize_speech(self, text: str) -> Optional[np.ndarray]:
        """
        Sintetiza fala a partir de texto.
        
        Args:
            text: Texto para sintetizar
            
        Returns:
            np.ndarray: Áudio sintetizado (mono, 16kHz) ou None se falha
        """
        if not text or len(text.strip()) == 0:
            logger.warning("⚠️ Texto vazio para TTS")
            return None
        
        # Limitar comprimento do texto
        text = text.strip()
        if len(text) > self.max_text_length:
            text = text[:self.max_text_length].rsplit(' ', 1)[0] + "..."
            logger.warning(f"⚠️ Texto truncado para {self.max_text_length} caracteres")
        
        # Tentar providers em ordem de prioridade
        providers = [
            ("elevenlabs", self._synthesize_elevenlabs),
            ("gtts", self._synthesize_gtts),
            ("pyttsx3", self._synthesize_pyttsx3)
        ]
        
        for provider_name, synthesize_func in providers:
            if not self.providers_available[provider_name]:
                continue
            
            try:
                logger.info(f"🔊 Tentando TTS via {provider_name}...")
                
                audio_data = await synthesize_func(text)
                
                if audio_data is not None and len(audio_data) > 0:
                    logger.info(f"✅ TTS sucesso via {provider_name}")
                    return audio_data
                else:
                    logger.warning(f"⚠️ {provider_name} retornou áudio vazio")
                    
            except Exception as e:
                logger.warning(f"⚠️ Falha TTS {provider_name}: {e}")
                continue
        
        logger.error("❌ Todos os providers TTS falharam")
        return None
    
    async def _synthesize_elevenlabs(self, text: str) -> Optional[np.ndarray]:
        """Sintetiza via ElevenLabs."""
        if not self.elevenlabs_client:
            raise Exception("ElevenLabs não inicializado")
        
        # Gerar áudio
        audio_generator = elevenlabs.generate(
            text=text,
            voice=self.elevenlabs_voice,
            model=self.elevenlabs_model,
            stream=False
        )
        
        # Converter generator para bytes
        audio_bytes = b"".join(audio_generator)
        
        if audio_bytes:
            # Converter para numpy array
            # ElevenLabs retorna áudio em formato específico - vamos salvar e carregar
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_file.flush()
                
                try:
                    # Converter MP3 para WAV usando ffmpeg ou similar
                    audio_data = await self._convert_audio_to_numpy(temp_file.name)
                    return audio_data
                    
                finally:
                    # Limpeza
                    Path(temp_file.name).unlink()
        
        return None
    
    async def _synthesize_gtts(self, text: str) -> Optional[np.ndarray]:
        """Sintetiza via Google TTS."""
        if not GTTS_AVAILABLE:
            raise Exception("gTTS não disponível")
        
        # Criar TTS
        tts = gTTS(text=text, lang=self.language, slow=False)
        
        # Salvar em arquivo temporário
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            tts.save(temp_file.name)
            
            try:
                # Converter para numpy
                audio_data = await self._convert_audio_to_numpy(temp_file.name)
                return audio_data
                
            finally:
                # Limpeza
                Path(temp_file.name).unlink()
    
    async def _synthesize_pyttsx3(self, text: str) -> Optional[np.ndarray]:
        """Sintetiza via Pyttsx3 local."""
        if not self.pyttsx3_engine:
            raise Exception("Pyttsx3 não inicializado")
        
        # Salvar em arquivo temporário
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            try:
                # Configurar output para arquivo
                self.pyttsx3_engine.save_to_file(text, temp_file.name)
                self.pyttsx3_engine.runAndWait()
                
                # Aguardar criação do arquivo
                await asyncio.sleep(1)
                
                if Path(temp_file.name).exists():
                    # Carregar áudio
                    audio_data = await self._load_wav_file(temp_file.name)
                    return audio_data
                
            except Exception as e:
                logger.error(f"❌ Erro Pyttsx3: {e}")
                
            finally:
                # Limpeza
                if Path(temp_file.name).exists():
                    Path(temp_file.name).unlink()
        
        return None
    
    async def _convert_audio_to_numpy(self, audio_file: str) -> Optional[np.ndarray]:
        """
        Converte arquivo de áudio para numpy array usando ffmpeg.
        
        Args:
            audio_file: Caminho do arquivo de áudio
            
        Returns:
            np.ndarray: Áudio convertido ou None se erro
        """
        try:
            import subprocess
            
            # Arquivo WAV temporário
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                # Converter usando ffmpeg
                cmd = [
                    "ffmpeg", "-y", "-i", audio_file,
                    "-ar", str(self.sample_rate),  # Sample rate
                    "-ac", "1",                    # Mono
                    "-f", "wav",                   # Formato WAV
                    temp_wav.name
                ]
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    # Carregar WAV
                    audio_data = await self._load_wav_file(temp_wav.name)
                    Path(temp_wav.name).unlink()
                    return audio_data
                else:
                    logger.error(f"❌ Erro ffmpeg: {result.stderr}")
                    Path(temp_wav.name).unlink()
                    return None
                    
        except Exception as e:
            logger.warning(f"⚠️ Erro conversão ffmpeg: {e}")
            # Fallback: tentar carregar diretamente
            return await self._load_wav_file(audio_file)
    
    async def _load_wav_file(self, wav_file: str) -> Optional[np.ndarray]:
        """Carrega arquivo WAV como numpy array."""
        try:
            with wave.open(wav_file, 'rb') as wav:
                # Verificar formato
                frames = wav.getnframes()
                sample_rate = wav.getframerate()
                channels = wav.getnchannels()
                sample_width = wav.getsampwidth()
                
                # Ler dados
                audio_bytes = wav.readframes(frames)
                
                # Converter para numpy
                if sample_width == 1:
                    audio_data = np.frombuffer(audio_bytes, dtype=np.uint8)
                    audio_data = audio_data.astype(np.float32) / 127.5 - 1.0
                elif sample_width == 2:
                    audio_data = np.frombuffer(audio_bytes, dtype=np.int16)
                    audio_data = audio_data.astype(np.float32) / 32767.0
                else:
                    logger.error(f"❌ Formato não suportado: {sample_width} bytes")
                    return None
                
                # Converter para mono se necessário
                if channels > 1:
                    audio_data = audio_data.reshape(-1, channels)
                    audio_data = np.mean(audio_data, axis=1)
                
                # Resample se necessário
                if sample_rate != self.sample_rate:
                    # Resample simples (pode ser melhorado com scipy)
                    factor = self.sample_rate / sample_rate
                    new_length = int(len(audio_data) * factor)
                    audio_data = np.interp(
                        np.linspace(0, len(audio_data), new_length),
                        np.arange(len(audio_data)),
                        audio_data
                    )
                
                return audio_data
                
        except Exception as e:
            logger.error(f"❌ Erro carregando WAV: {e}")
            return None
    
    def _split_text_for_synthesis(self, text: str) -> List[str]:
        """Divide texto longo em chunks para síntese."""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        sentences = text.split('. ')
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) <= self.chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def synthesize_long_text(self, text: str) -> Optional[np.ndarray]:
        """Sintetiza texto longo dividindo em chunks."""
        chunks = self._split_text_for_synthesis(text)
        
        if len(chunks) == 1:
            return await self.synthesize_speech(text)
        
        # Sintetizar cada chunk
        audio_chunks = []
        for i, chunk in enumerate(chunks):
            logger.info(f"🔊 Sintetizando chunk {i+1}/{len(chunks)}")
            
            chunk_audio = await self.synthesize_speech(chunk)
            if chunk_audio is not None:
                audio_chunks.append(chunk_audio)
                
                # Pausa entre chunks
                silence = np.zeros(int(0.3 * self.sample_rate))  # 300ms de silêncio
                audio_chunks.append(silence)
        
        if audio_chunks:
            # Concatenar todos os chunks
            return np.concatenate(audio_chunks)
        
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Obtém status detalhado do TTS Manager."""
        return {
            "providers_available": self.providers_available.copy(),
            "elevenlabs_ready": self.elevenlabs_client is not None,
            "elevenlabs_voice_id": self.elevenlabs_voice_id,
            "sample_rate": self.sample_rate,
            "language": self.language,
            "voice_settings": {
                "stability": self.voice_stability,
                "similarity": self.voice_similarity,
                "style": self.voice_style
            }
        }

# Exemplo de uso
if __name__ == "__main__":
    import asyncio
    import logging
    
    logging.basicConfig(level=logging.INFO)
    
    async def test_tts():
        """Teste básico do TTS."""
        tts_manager = TTSRealManager()
        
        # Status
        status = tts_manager.get_status()
        print("📊 STATUS TTS:")
        for key, value in status.items():
            print(f"   {key}: {value}")
        
        # Teste de síntese
        audio_data = await tts_manager.synthesize_speech("Olá, eu sou o Tobias!")
        if audio_data is not None:
            print(f"🔊 Áudio sintetizado: {len(audio_data)} samples")
        
        print("✅ TTS Manager testado")
    
    asyncio.run(test_tts())
