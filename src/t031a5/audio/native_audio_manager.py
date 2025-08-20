#!/usr/bin/env python3
"""
Gerenciador de Áudio Nativo - Sistema t031a5

Usa o sistema de áudio nativo do Mac para reproduzir MP3 do ElevenLabs
"""

import asyncio
import logging
import os
import tempfile
import subprocess
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class NativeAudioManager:
    """Gerenciador de áudio nativo para t031a5."""
    
    def __init__(self, config_path: str = "config/g1_native_audio.json5"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.is_initialized = False
        
    def load_config(self) -> Dict[str, Any]:
        """Carrega configuração de áudio."""
        try:
            import json5
            with open(self.config_path, 'r') as f:
                return json5.load(f)
        except ImportError:
            import json
            with open(self.config_path, 'r') as f:
                return json.load(f)
    
    async def initialize(self) -> bool:
        """Inicializa o Native Audio Manager."""
        try:
            logger.info("🔊 Inicializando Native Audio Manager...")
            
            # Verifica se o sistema suporta reprodução de áudio
            if await self._check_audio_support():
                logger.info("✅ Sistema de áudio nativo disponível")
                self.is_initialized = True
                return True
            else:
                logger.error("❌ Sistema de áudio nativo não disponível")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Native Audio Manager: {e}")
            return False
    
    async def _check_audio_support(self) -> bool:
        """Verifica se o sistema suporta reprodução de áudio."""
        try:
            # Verifica se o comando 'mpv' está disponível (suporta MP3 nativamente)
            result = subprocess.run(['which', 'mpv'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("✅ mpv disponível (suporta MP3)")
                return True
            
            # Verifica se o comando 'afplay' está disponível (macOS)
            result = subprocess.run(['which', 'afplay'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("✅ afplay disponível (macOS)")
                return True
            
            # Verifica se o comando 'aplay' está disponível (Linux)
            result = subprocess.run(['which', 'aplay'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("✅ aplay disponível (Linux)")
                return True
            
            logger.warning("⚠️ Nenhum player de áudio nativo encontrado")
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar suporte de áudio: {e}")
            return False
    
    async def play_audio(self, audio_data: bytes) -> bool:
        """Reproduz áudio usando o sistema nativo."""
        if not self.is_initialized:
            logger.error("Native Audio Manager não inicializado")
            return False
        
        try:
            logger.info("🔊 Reproduzindo áudio nativo...")
            
            # Salva áudio temporariamente
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Reproduz usando o sistema nativo
                success = await self._play_with_native_player(temp_file_path)
                
                if success:
                    logger.info("✅ Áudio reproduzido com sucesso")
                    return True
                else:
                    logger.error("❌ Falha na reprodução")
                    return False
                    
            finally:
                # Remove arquivo temporário
                os.unlink(temp_file_path)
                
        except Exception as e:
            logger.error(f"❌ Erro ao reproduzir áudio: {e}")
            return False
    
    async def _play_with_native_player(self, file_path: str) -> bool:
        """Reproduz arquivo usando player nativo."""
        try:
            # Prioriza mpv (suporta MP3 nativamente)
            if subprocess.run(['which', 'mpv'], capture_output=True).returncode == 0:
                cmd = ['mpv', '--no-video', '--no-terminal', '--really-quiet', file_path]
                logger.info("🎵 Usando mpv para reprodução")
            elif os.name == 'posix':  # macOS/Linux
                if os.path.exists('/System/Library/CoreServices/SystemVersion.plist'):
                    # macOS - usa afplay (só para WAV)
                    if file_path.endswith('.mp3'):
                        # Converte MP3 para WAV temporariamente
                        wav_path = file_path.replace('.mp3', '.wav')
                        convert_cmd = ['ffmpeg', '-i', file_path, '-acodec', 'pcm_s16le', '-ar', '44100', wav_path, '-y', '-loglevel', 'error']
                        
                        convert_process = await asyncio.create_subprocess_exec(
                            *convert_cmd,
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE
                        )
                        await convert_process.wait()
                        
                        if convert_process.returncode == 0:
                            cmd = ['afplay', wav_path]
                            cleanup_needed = True
                            logger.info("🎵 Convertendo MP3 para WAV e usando afplay")
                        else:
                            logger.error("❌ Falha na conversão MP3 para WAV")
                            return False
                    else:
                        cmd = ['afplay', file_path]
                        cleanup_needed = False
                        logger.info("🎵 Usando afplay para reprodução")
                else:
                    # Linux - usa aplay
                    cmd = ['aplay', file_path]
                    cleanup_needed = False
                    logger.info("🎵 Usando aplay para reprodução")
            else:
                # Windows - usa start
                cmd = ['start', file_path]
                cleanup_needed = False
                logger.info("🎵 Usando start para reprodução")
            
            # Executa o comando
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Aguarda a reprodução (máximo 30 segundos)
            try:
                await asyncio.wait_for(process.wait(), timeout=30.0)
                success = process.returncode == 0
                
                # Log de debug
                if not success:
                    stderr_output = await process.stderr.read()
                    if stderr_output:
                        logger.warning(f"⚠️ Player stderr: {stderr_output.decode()}")
                
                # Limpa arquivo temporário se necessário
                if 'cleanup_needed' in locals() and cleanup_needed and 'wav_path' in locals():
                    try:
                        os.unlink(wav_path)
                    except Exception as e:
                        logger.warning(f"⚠️ Erro ao remover arquivo temporário: {e}")
                
                return success
            except asyncio.TimeoutError:
                # Se demorar muito, mata o processo
                process.terminate()
                await process.wait()
                
                # Limpa arquivo temporário se necessário
                if 'cleanup_needed' in locals() and cleanup_needed and 'wav_path' in locals():
                    try:
                        os.unlink(wav_path)
                    except Exception as e:
                        logger.warning(f"⚠️ Erro ao remover arquivo temporário: {e}")
                
                return True  # Assume que começou a reproduzir
                
        except Exception as e:
            logger.error(f"❌ Erro no player nativo: {e}")
            return False
    
    async def capture_audio(self, duration: float = 5.0) -> Optional[bytes]:
        """Captura áudio usando o sistema nativo."""
        if not self.is_initialized:
            logger.error("Native Audio Manager não inicializado")
            return None
        
        try:
            logger.info(f"🎤 Capturando áudio por {duration}s...")
            
            # Usa sox para captura (se disponível)
            if await self._check_sox_available():
                return await self._capture_with_sox(duration)
            else:
                logger.warning("⚠️ sox não disponível, usando PyAudio como fallback")
                return await self._capture_with_pyaudio(duration)
                
        except Exception as e:
            logger.error(f"❌ Erro ao capturar áudio: {e}")
            return None
    
    async def _check_sox_available(self) -> bool:
        """Verifica se o sox está disponível."""
        try:
            result = subprocess.run(['which', 'sox'], capture_output=True)
            return result.returncode == 0
        except Exception:
            return False
    
    async def _capture_with_sox(self, duration: float) -> Optional[bytes]:
        """Captura áudio usando sox."""
        try:
            # Cria arquivo temporário
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file_path = temp_file.name
            
            try:
                # Comando sox para captura
                cmd = [
                    'sox', '-d', temp_file_path,
                    'trim', '0', str(duration),
                    'rate', '16000', 'channels', '1'
                ]
                
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                await process.wait()
                
                if process.returncode == 0:
                    # Lê o arquivo capturado
                    with open(temp_file_path, 'rb') as f:
                        audio_data = f.read()
                    
                    logger.info(f"✅ Áudio capturado: {len(audio_data)} bytes")
                    return audio_data
                else:
                    logger.error("❌ Falha na captura com sox")
                    return None
                    
            finally:
                # Remove arquivo temporário
                os.unlink(temp_file_path)
                
        except Exception as e:
            logger.error(f"❌ Erro na captura com sox: {e}")
            return None
    
    async def _capture_with_pyaudio(self, duration: float) -> Optional[bytes]:
        """Captura áudio usando PyAudio (fallback)."""
        try:
            import pyaudio
            
            audio = pyaudio.PyAudio()
            
            # Configura stream de entrada
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=1024
            )
            
            frames = []
            num_frames = int(16000 / 1024 * duration)
            
            for _ in range(num_frames):
                data = stream.read(1024, exception_on_overflow=False)
                frames.append(data)
            
            # Fecha stream
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            audio_data = b''.join(frames)
            logger.info(f"✅ Áudio capturado (PyAudio): {len(audio_data)} bytes")
            return audio_data
            
        except Exception as e:
            logger.error(f"❌ Erro na captura com PyAudio: {e}")
            return None
    
    async def cleanup(self) -> None:
        """Limpa recursos do Native Audio Manager."""
        try:
            logger.info("🧹 Limpando Native Audio Manager...")
            self.is_initialized = False
            logger.info("✅ Native Audio Manager limpo")
        except Exception as e:
            logger.error(f"❌ Erro ao limpar Native Audio Manager: {e}")


# Exemplo de uso
async def main() -> None:
    """Exemplo de uso do Native Audio Manager."""
    audio_manager = NativeAudioManager()
    
    if await audio_manager.initialize():
        print("✅ Native Audio Manager inicializado")
        
        # Testa reprodução (se tiver arquivo de teste)
        # audio_data = b'...'  # dados de áudio MP3
        # success = await audio_manager.play_audio(audio_data)
        # print(f"Reprodução: {'✅' if success else '❌'}")
        
        await audio_manager.cleanup()
    else:
        print("❌ Falha ao inicializar Native Audio Manager")


if __name__ == "__main__":
    asyncio.run(main())
