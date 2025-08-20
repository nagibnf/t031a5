#!/usr/bin/env python3
"""
Configuração de Áudio Bluetooth - Sistema t031a5

Configura e testa:
- DJI Mic 2 (entrada Bluetooth)
- Anker Soundcore Mobile 300 (saída Bluetooth)
- Fallback para G1 built-in
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional


class BluetoothAudioConfig:
    """Configurador de áudio Bluetooth para t031a5."""
    
    def __init__(self):
        self.config_path = Path("config/g1_bluetooth_audio.json5")
        self.devices = {
            "input": {
                "primary": {
                    "name": "DJI Mic 2",
                    "type": "bluetooth",
                    "device_id": None,
                    "sample_rate": 48000,
                    "channels": 2,
                    "bit_depth": 32
                },
                "fallback": {
                    "name": "G1 Built-in Mic",
                    "type": "builtin",
                    "device_id": None,
                    "sample_rate": 16000,
                    "channels": 1,
                    "bit_depth": 16
                }
            },
            "output": {
                "primary": {
                    "name": "Anker Soundcore Mobile 300",
                    "type": "bluetooth",
                    "device_id": None,
                    "sample_rate": 48000,
                    "channels": 2,
                    "bit_depth": 32
                },
                "fallback": {
                    "name": "G1 Built-in Speakers",
                    "type": "builtin",
                    "device_id": None,
                    "sample_rate": 16000,
                    "channels": 2,
                    "bit_depth": 16
                }
            }
        }
    
    def create_bluetooth_config(self) -> Dict[str, Any]:
        """Cria configuração de áudio Bluetooth."""
        config = {
            "name": "G1 Bluetooth Audio Configuration",
            "description": "Configuração de áudio Bluetooth para Tobias (G1)",
            "version": "1.0",
            "audio": {
                "input": {
                    "primary": {
                        "device": "dji_mic_2",
                        "type": "bluetooth",
                        "sample_rate": 48000,
                        "channels": 2,
                        "bit_depth": 32,
                        "format": "float32",
                        "chunk_size": 1024,
                        "latency": 50,
                        "noise_reduction": True,
                        "echo_cancellation": True,
                        "auto_gain_control": True
                    },
                    "fallback": {
                        "device": "g1_builtin_mic",
                        "type": "builtin",
                        "sample_rate": 16000,
                        "channels": 1,
                        "bit_depth": 16,
                        "format": "int16",
                        "chunk_size": 1024,
                        "noise_reduction": True,
                        "echo_cancellation": False,
                        "auto_gain_control": True
                    }
                },
                "output": {
                    "primary": {
                        "device": "anker_soundcore_300",
                        "type": "bluetooth",
                        "sample_rate": 48000,
                        "channels": 2,
                        "bit_depth": 32,
                        "format": "float32",
                        "volume": 0.8,
                        "latency": 100,
                        "equalizer": {
                            "enabled": True,
                            "preset": "voice"
                        }
                    },
                    "fallback": {
                        "device": "g1_builtin_speakers",
                        "type": "builtin",
                        "sample_rate": 16000,
                        "channels": 2,
                        "bit_depth": 16,
                        "format": "int16",
                        "volume": 1.0,
                        "equalizer": {
                            "enabled": False
                        }
                    }
                },
                "processing": {
                    "noise_reduction": {
                        "enabled": True,
                        "algorithm": "spectral_subtraction",
                        "strength": 0.7
                    },
                    "echo_cancellation": {
                        "enabled": True,
                        "algorithm": "nlms",
                        "filter_length": 512
                    },
                    "gain_control": {
                        "enabled": True,
                        "target_level": -20,
                        "attack_time": 0.1,
                        "release_time": 0.5
                    },
                    "voice_activity_detection": {
                        "enabled": True,
                        "threshold": 0.01,
                        "min_duration": 0.1
                    }
                },
                "bluetooth": {
                    "auto_connect": True,
                    "reconnect_attempts": 3,
                    "timeout": 10.0,
                    "battery_monitoring": True,
                    "low_battery_threshold": 20
                }
            }
        }
        
        return config
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Salva configuração em arquivo JSON5."""
        try:
            # Converte para JSON5 (com comentários)
            json5_content = f"""// Configuração de Áudio Bluetooth - Sistema t031a5
// Para Tobias (G1) - Jetson Orin NX 16GB
// DJI Mic 2 + Anker Soundcore Mobile 300

{json.dumps(config, indent=2, ensure_ascii=False)}
"""
            
            self.config_path.write_text(json5_content, encoding='utf-8')
            print(f"✅ Configuração salva: {self.config_path}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar configuração: {e}")
            return False
    
    def create_audio_manager(self) -> str:
        """Cria gerenciador de áudio Bluetooth."""
        audio_manager_code = '''#!/usr/bin/env python3
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
        """Inicializa gerenciador de áudio."""
        try:
            logger.info("Inicializando BluetoothAudioManager...")
            
            # Configura entrada
            input_config = self.config["audio"]["input"]["primary"]
            self.input_stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=input_config["channels"],
                rate=input_config["sample_rate"],
                input=True,
                frames_per_buffer=input_config["chunk_size"]
            )
            
            # Configura saída
            output_config = self.config["audio"]["output"]["primary"]
            self.output_stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=output_config["channels"],
                rate=output_config["sample_rate"],
                output=True,
                frames_per_buffer=output_config["chunk_size"]
            )
            
            self.is_initialized = True
            logger.info("BluetoothAudioManager inicializado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao inicializar BluetoothAudioManager: {e}")
            return False
    
    async def capture_audio(self, duration: float = 1.0) -> Optional[np.ndarray]:
        """Captura áudio do DJI Mic 2."""
        if not self.is_initialized or not self.input_stream:
            logger.warning("BluetoothAudioManager não inicializado")
            return None
        
        try:
            frames = []
            chunk_size = self.config["audio"]["input"]["primary"]["chunk_size"]
            sample_rate = self.config["audio"]["input"]["primary"]["sample_rate"]
            
            chunks = int(sample_rate / chunk_size * duration)
            
            for _ in range(chunks):
                data = self.input_stream.read(chunk_size, exception_on_overflow=False)
                frames.append(data)
            
            audio_data = np.frombuffer(b''.join(frames), dtype=np.float32)
            return audio_data
            
        except Exception as e:
            logger.error(f"Erro ao capturar áudio: {e}")
            return None
    
    async def play_audio(self, audio_data: np.ndarray) -> bool:
        """Reproduz áudio na Anker Soundcore 300."""
        if not self.is_initialized or not self.output_stream:
            logger.warning("BluetoothAudioManager não inicializado")
            return False
        
        try:
            self.output_stream.write(audio_data.tobytes())
            return True
            
        except Exception as e:
            logger.error(f"Erro ao reproduzir áudio: {e}")
            return False
    
    async def cleanup(self):
        """Limpa recursos de áudio."""
        try:
            if self.input_stream:
                self.input_stream.stop_stream()
                self.input_stream.close()
            
            if self.output_stream:
                self.output_stream.stop_stream()
                self.output_stream.close()
            
            self.audio.terminate()
            self.is_initialized = False
            logger.info("BluetoothAudioManager limpo")
            
        except Exception as e:
            logger.error(f"Erro ao limpar BluetoothAudioManager: {e}")


# Exemplo de uso
async def main():
    """Exemplo de uso do BluetoothAudioManager."""
    manager = BluetoothAudioManager()
    
    if await manager.initialize():
        print("✅ Áudio Bluetooth inicializado")
        
        # Captura áudio
        audio = await manager.capture_audio(3.0)
        if audio is not None:
            print(f"🎤 Áudio capturado: {len(audio)} amostras")
            
            # Reproduz áudio
            success = await manager.play_audio(audio)
            if success:
                print("🔊 Áudio reproduzido")
        
        await manager.cleanup()
    else:
        print("❌ Falha ao inicializar áudio Bluetooth")


if __name__ == "__main__":
    asyncio.run(main())
'''
        
        manager_path = Path("src/t031a5/audio/bluetooth_manager.py")
        manager_path.parent.mkdir(parents=True, exist_ok=True)
        manager_path.write_text(audio_manager_code, encoding='utf-8')
        
        return str(manager_path)
    
    def create_test_script(self) -> str:
        """Cria script de teste para áudio Bluetooth."""
        test_script = '''#!/usr/bin/env python3
"""
Teste de Áudio Bluetooth - Sistema t031a5

Testa DJI Mic 2 + Anker Soundcore Mobile 300
"""

import asyncio
import sys
from pathlib import Path

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from t031a5.audio.bluetooth_manager import BluetoothAudioManager


async def test_bluetooth_audio():
    """Testa sistema de áudio Bluetooth."""
    print("🎵 TESTE DE ÁUDIO BLUETOOTH - SISTEMA t031a5")
    print("=" * 50)
    
    manager = BluetoothAudioManager()
    
    print("🔧 Inicializando...")
    if await manager.initialize():
        print("✅ Sistema inicializado")
        
        print("\\n🎤 Teste de captura (3 segundos)...")
        print("Fale algo no DJI Mic 2...")
        
        audio = await manager.capture_audio(3.0)
        if audio is not None:
            volume = np.sqrt(np.mean(audio**2))
            print(f"✅ Áudio capturado: {len(audio)} amostras")
            print(f"📊 Volume médio: {volume:.4f}")
            
            if volume > 0.001:
                print("🎵 Áudio detectado!")
                
                print("\\n🔊 Reproduzindo áudio...")
                success = await manager.play_audio(audio)
                if success:
                    print("✅ Áudio reproduzido na Anker Soundcore 300")
                else:
                    print("❌ Falha ao reproduzir áudio")
            else:
                print("🔇 Sem áudio detectado")
        else:
            print("❌ Falha ao capturar áudio")
        
        await manager.cleanup()
    else:
        print("❌ Falha ao inicializar sistema")
    
    print("\\n🎉 Teste concluído!")


if __name__ == "__main__":
    asyncio.run(test_bluetooth_audio())
'''
        
        test_path = Path("scripts/test/test_bluetooth_audio.py")
        test_path.parent.mkdir(parents=True, exist_ok=True)
        test_path.write_text(test_script, encoding='utf-8')
        
        return str(test_path)
    
    def setup_complete(self) -> bool:
        """Configuração completa do sistema de áudio Bluetooth."""
        print("🎵 CONFIGURAÇÃO DE ÁUDIO BLUETOOTH - SISTEMA t031a5")
        print("=" * 60)
        
        # Cria configuração
        config = self.create_bluetooth_config()
        if not self.save_config(config):
            return False
        
        # Cria gerenciador
        manager_path = self.create_audio_manager()
        print(f"✅ Gerenciador criado: {manager_path}")
        
        # Cria script de teste
        test_path = self.create_test_script()
        print(f"✅ Script de teste criado: {test_path}")
        
        print("\\n📋 RESUMO DA CONFIGURAÇÃO")
        print("=" * 30)
        print("🎤 Entrada: DJI Mic 2 (Bluetooth)")
        print("🔊 Saída: Anker Soundcore Mobile 300 (Bluetooth)")
        print("🔄 Fallback: G1 built-in")
        print("⚡ Processamento: Noise reduction + Echo cancellation")
        print("🔋 Monitoramento: Bateria + Conexão")
        
        print("\\n💡 PRÓXIMOS PASSOS")
        print("=" * 20)
        print("1. Conecte o DJI Mic 2 ao G1")
        print("2. Conecte o Anker Soundcore 300 ao G1")
        print("3. Execute: python scripts/test/test_bluetooth_audio.py")
        print("4. Teste a captura e reprodução de áudio")
        
        return True


def main():
    """Função principal."""
    try:
        configurator = BluetoothAudioConfig()
        success = configurator.setup_complete()
        
        if success:
            print("\\n🎉 Configuração de áudio Bluetooth concluída!")
            print("🚀 Sistema t031a5 pronto para áudio Bluetooth")
        else:
            print("\\n❌ Falha na configuração")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
