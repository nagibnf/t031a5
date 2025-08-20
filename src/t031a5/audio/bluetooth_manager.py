#!/usr/bin/env python3
"""
Gerenciador de Áudio Bluetooth - Sistema t031a5

Gerencia entrada e saída de áudio via Bluetooth:
- DJI Mic 2 (entrada)
- Anker Soundcore Mobile 300 (saída)
"""

import asyncio
import pyaudio
import numpy as np
import logging
import json
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class BluetoothAudioManager:
    """Gerenciador de áudio Bluetooth para t031a5."""
    
    def __init__(self, config_path: str = "config/g1_bluetooth_audio.json5"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.audio = pyaudio.PyAudio()
        self.input_stream = None
        self.output_stream = None
        self.is_initialized = False
        
    def load_config(self) -> Dict[str, Any]:
        """Carrega configuração de áudio."""
        try:
            import json5
            with open(self.config_path, 'r') as f:
                return json5.load(f)
        except ImportError:
            # Fallback para JSON se json5 não estiver disponível
            with open(self.config_path, 'r') as f:
                return json.load(f)
    
    async def initialize(self) -> bool:
        """Inicializa o AudioManager com dispositivos built-in do Mac."""
        try:
            logger.info("🎤 Inicializando AudioManager (dispositivos built-in)...")
            
            # Lista dispositivos disponíveis
            device_count = self.audio.get_device_count()
            logger.info(f"📱 Dispositivos de áudio encontrados: {device_count}")
            
            # Encontra dispositivos built-in
            input_device_id = None
            output_device_id = None
            
            for i in range(device_count):
                device_info = self.audio.get_device_info_by_index(i)
                name = device_info['name'].lower()
                
                # Procura por dispositivos built-in do Mac
                if 'macbook' in name or 'built-in' in name:
                    if device_info['maxInputChannels'] > 0 and input_device_id is None:
                        input_device_id = i
                        logger.info(f"🎤 Entrada: {device_info['name']} (ID: {i})")
                    if device_info['maxOutputChannels'] > 0 and output_device_id is None:
                        output_device_id = i
                        logger.info(f"🔊 Saída: {device_info['name']} (ID: {i})")
            
            # Configura entrada (microfone built-in)
            if input_device_id is not None:
                try:
                    self.input_stream = self.audio.open(
                        format=pyaudio.paInt16,
                        channels=1,
                        rate=16000,
                        input=True,
                        input_device_index=input_device_id,
                        frames_per_buffer=1024
                    )
                    logger.info("✅ Stream de entrada configurado")
                except Exception as e:
                    logger.error(f"❌ Erro ao configurar entrada: {e}")
                    return False
            else:
                logger.error("❌ Nenhum dispositivo de entrada encontrado")
                return False
            
            # Configura saída (speaker built-in)
            if output_device_id is not None:
                try:
                    self.output_stream = self.audio.open(
                        format=pyaudio.paInt16,
                        channels=2,
                        rate=16000,
                        output=True,
                        output_device_index=output_device_id,
                        frames_per_buffer=1024
                    )
                    logger.info("✅ Stream de saída configurado")
                except Exception as e:
                    logger.error(f"❌ Erro ao configurar saída: {e}")
                    return False
            else:
                logger.error("❌ Nenhum dispositivo de saída encontrado")
                return False
            
            self.is_initialized = True
            logger.info("✅ AudioManager inicializado com sucesso (dispositivos built-in)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar AudioManager: {e}")
            return False
    
    async def capture_audio(self, duration: float = 5.0) -> Optional[bytes]:
        """Captura áudio por um período específico."""
        if not self.is_initialized or self.input_stream is None:
            logger.error("AudioManager não inicializado")
            return None
        
        try:
            # Usa valores fixos para dispositivos built-in
            chunk_size = 1024
            sample_rate = 16000
            
            frames = []
            num_frames = int(sample_rate / chunk_size * duration)
            
            logger.info(f"🎤 Capturando áudio por {duration}s...")
            
            for i in range(num_frames):
                data = self.input_stream.read(chunk_size, exception_on_overflow=False)
                frames.append(data)
                
                # Mostra progresso
                if i % 10 == 0:
                    progress = (i / num_frames) * 100
                    logger.info(f"📊 Progresso: {progress:.1f}%")
            
            audio_data = b''.join(frames)
            logger.info(f"✅ Áudio capturado: {len(audio_data)} bytes")
            return audio_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao capturar áudio: {e}")
            return None
    
    async def play_audio(self, audio_data: bytes) -> bool:
        """Reproduz áudio nos speakers built-in."""
        if not self.is_initialized or self.output_stream is None:
            logger.error("AudioManager não inicializado")
            return False
        
        try:
            logger.info("🔊 Reproduzindo áudio...")
            
            # Se for WAV, remove o header e pega apenas os dados de áudio
            if audio_data.startswith(b'RIFF'):
                # É um arquivo WAV, remove o header (44 bytes)
                audio_samples = audio_data[44:]
            else:
                # Assume que já são dados de áudio puros
                audio_samples = audio_data
            
            # Reproduz o áudio
            self.output_stream.write(audio_samples)
            logger.info("✅ Áudio reproduzido com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao reproduzir áudio: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Limpa recursos de áudio."""
        try:
            logger.info("🧹 Limpando recursos de áudio...")
            
            if self.input_stream:
                try:
                    self.input_stream.stop_stream()
                    self.input_stream.close()
                    logger.info("✅ Stream de entrada fechado")
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao fechar input stream: {e}")
            
            if self.output_stream:
                try:
                    self.output_stream.stop_stream()
                    self.output_stream.close()
                    logger.info("✅ Stream de saída fechado")
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao fechar output stream: {e}")
            
            try:
                self.audio.terminate()
                logger.info("✅ PyAudio terminado")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao terminar PyAudio: {e}")
            
            self.is_initialized = False
            logger.info("✅ AudioManager limpo completamente")
            
        except Exception as e:
            logger.error(f"❌ Erro ao limpar AudioManager: {e}")


# Exemplo de uso
async def main() -> None:
    """Exemplo de uso do AudioManager."""
    manager = BluetoothAudioManager()
    
    if await manager.initialize():
        print("✅ AudioManager inicializado")
        
        # Captura áudio
        audio = await manager.capture_audio(3.0)
        if audio is not None:
            print(f"🎤 Áudio capturado: {len(audio)} bytes")
            
            # Reproduz áudio
            success = await manager.play_audio(audio)
            if success:
                print("🔊 Áudio reproduzido")
        
        await manager.cleanup()
    else:
        print("❌ Falha ao inicializar AudioManager")


if __name__ == "__main__":
    asyncio.run(main())
