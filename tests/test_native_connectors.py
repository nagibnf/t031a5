"""
Teste para Conectores Nativos do G1.
Testa a funcionalidade dos conectores nativos como plugins opcionais.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.t031a5.connectors.manager import G1NativeConnectorManager
from src.t031a5.connectors.g1_native_tts import TTSRequest
from src.t031a5.connectors.g1_native_leds import LEDRequest
from src.t031a5.connectors.g1_native_audio import AudioRequest

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class MockG1Controller:
    """Controlador G1 mock para testes."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tts_calls = []
        self.led_calls = []
        self.volume_calls = []
    
    def tts_maker(self, text: str, speaker_id: int) -> int:
        """Mock do TTS nativo."""
        self.tts_calls.append({"text": text, "speaker_id": speaker_id})
        self.logger.info(f"Mock TTS: '{text}' (speaker_id={speaker_id})")
        return 0  # Sucesso
    
    def led_control(self, r: int, g: int, b: int) -> int:
        """Mock do controle de LED."""
        self.led_calls.append({"r": r, "g": g, "b": b})
        self.logger.info(f"Mock LED: RGB({r}, {g}, {b})")
        return 0  # Sucesso
    
    def set_volume(self, volume: int) -> int:
        """Mock do controle de volume."""
        self.volume_calls.append({"volume": volume})
        self.logger.info(f"Mock Volume: {volume}")
        return 0  # Sucesso
    
    def get_volume(self):
        """Mock do get volume."""
        return 0, {"volume": 50}  # Sucesso, volume 50


async def test_connector_manager():
    """Testa o gerenciador de conectores."""
    print("\n🧪 TESTE: Gerenciador de Conectores Nativos")
    print("=" * 50)
    
    # Configuração de teste
    config = {
        "native_connectors": {
            "tts": {
                "enabled": True,
                "default_speaker_id": 0,
                "timeout": 10.0,
                "retry_attempts": 3
            },
            "leds": {
                "enabled": True,
                "default_brightness": 0.5,
                "transition_time": 0.2,
                "emotion_colors": {
                    "happy": {"r": 255, "g": 255, "b": 0},
                    "sad": {"r": 0, "g": 0, "b": 255}
                }
            },
            "audio": {
                "enabled": True,
                "default_volume": 50,
                "max_volume": 100,
                "min_volume": 0
            }
        }
    }
    
    # Cria gerenciador
    manager = G1NativeConnectorManager(config)
    
    # Cria controlador mock
    mock_controller = MockG1Controller()
    
    # Inicializa conectores
    success = await manager.initialize(mock_controller)
    
    if success:
        print("✅ Gerenciador inicializado com sucesso")
    else:
        print("❌ Falha na inicialização do gerenciador")
        return False
    
    # Testa status dos conectores
    status = manager.get_all_status()
    print(f"\n📊 Status dos Conectores:")
    for name, connector_status in status.items():
        print(f"  {name}: {'✅' if connector_status.available else '❌'}")
    
    # Testa conectores disponíveis
    available = manager.get_available_connectors()
    print(f"\n🎯 Conectores Disponíveis: {available}")
    
    return True


async def test_tts_connector():
    """Testa o conector TTS."""
    print("\n🗣️ TESTE: Conector TTS Nativo")
    print("=" * 40)
    
    # Configuração
    config = {
        "native_connectors": {
            "tts": {
                "enabled": True,
                "default_speaker_id": 0,
                "timeout": 10.0,
                "retry_attempts": 3
            }
        }
    }
    
    # Cria gerenciador e controlador mock
    manager = G1NativeConnectorManager(config)
    mock_controller = MockG1Controller()
    
    # Inicializa
    await manager.initialize(mock_controller)
    
    # Testa síntese de voz
    test_text = "Olá, sou o G1! Teste de TTS nativo."
    response = await manager.speak(test_text, speaker_id=0)
    
    if response.success:
        print(f"✅ TTS Nativo: '{test_text}'")
        print(f"   Duração estimada: {response.duration:.2f}s")
    else:
        print(f"❌ Erro no TTS: {response.error_message}")
        return False
    
    # Verifica se foi chamado no mock
    if mock_controller.tts_calls:
        call = mock_controller.tts_calls[0]
        print(f"   Mock chamado: '{call['text']}' (speaker_id={call['speaker_id']})")
    
    return True


async def test_led_connector():
    """Testa o conector LEDs."""
    print("\n🎨 TESTE: Conector LEDs Nativo")
    print("=" * 40)
    
    # Configuração
    config = {
        "native_connectors": {
            "leds": {
                "enabled": True,
                "default_brightness": 0.5,
                "transition_time": 0.2,
                "emotion_colors": {
                    "happy": {"r": 255, "g": 255, "b": 0},
                    "sad": {"r": 0, "g": 0, "b": 255}
                }
            }
        }
    }
    
    # Cria gerenciador e controlador mock
    manager = G1NativeConnectorManager(config)
    mock_controller = MockG1Controller()
    
    # Inicializa
    await manager.initialize(mock_controller)
    
    # Testa definição de cor
    response = await manager.set_led_color(255, 0, 0, emotion="excited")
    
    if response.success:
        print("✅ LED Nativo: Cor vermelha definida")
    else:
        print(f"❌ Erro no LED: {response.error_message}")
        return False
    
    # Testa emoção
    response = await manager.set_emotion_led("happy")
    
    if response.success:
        print("✅ LED Nativo: Emoção 'happy' definida")
    else:
        print(f"❌ Erro no LED: {response.error_message}")
        return False
    
    # Verifica se foi chamado no mock
    if mock_controller.led_calls:
        for i, call in enumerate(mock_controller.led_calls):
            print(f"   Mock chamado {i+1}: RGB({call['r']}, {call['g']}, {call['b']})")
    
    return True


async def test_audio_connector():
    """Testa o conector áudio."""
    print("\n🔊 TESTE: Conector Áudio Nativo")
    print("=" * 40)
    
    # Configuração
    config = {
        "native_connectors": {
            "audio": {
                "enabled": True,
                "default_volume": 50,
                "max_volume": 100,
                "min_volume": 0
            }
        }
    }
    
    # Cria gerenciador e controlador mock
    manager = G1NativeConnectorManager(config)
    mock_controller = MockG1Controller()
    
    # Inicializa
    await manager.initialize(mock_controller)
    
    # Testa definição de volume
    response = await manager.set_volume(75)
    
    if response.success:
        print(f"✅ Áudio Nativo: Volume definido para {response.current_volume}")
    else:
        print(f"❌ Erro no áudio: {response.error_message}")
        return False
    
    # Testa obtenção de volume
    response = await manager.get_volume()
    
    if response.success:
        print(f"✅ Áudio Nativo: Volume atual {response.current_volume}")
    else:
        print(f"❌ Erro ao obter volume: {response.error_message}")
        return False
    
    # Verifica se foi chamado no mock
    if mock_controller.volume_calls:
        call = mock_controller.volume_calls[0]
        print(f"   Mock chamado: Volume {call['volume']}")
    
    return True


async def test_connector_capabilities():
    """Testa capacidades dos conectores."""
    print("\n🔧 TESTE: Capacidades dos Conectores")
    print("=" * 40)
    
    # Configuração completa
    config = {
        "native_connectors": {
            "tts": {"enabled": True},
            "leds": {"enabled": True},
            "audio": {"enabled": True}
        }
    }
    
    # Cria gerenciador e controlador mock
    manager = G1NativeConnectorManager(config)
    mock_controller = MockG1Controller()
    
    # Inicializa
    await manager.initialize(mock_controller)
    
    # Obtém capacidades
    capabilities = manager.get_all_capabilities()
    
    print("📋 Capacidades dos Conectores:")
    for name, caps in capabilities.items():
        print(f"  {name}:")
        print(f"    Nome: {caps['name']}")
        print(f"    Habilitado: {caps['enabled']}")
        print(f"    Disponível: {caps['available']}")
        print(f"    Recursos: {', '.join(caps['features'])}")
    
    return True


async def test_connector_availability():
    """Testa disponibilidade dos conectores."""
    print("\n🔍 TESTE: Disponibilidade dos Conectores")
    print("=" * 40)
    
    # Configuração
    config = {
        "native_connectors": {
            "tts": {"enabled": True},
            "leds": {"enabled": True},
            "audio": {"enabled": True}
        }
    }
    
    # Cria gerenciador e controlador mock
    manager = G1NativeConnectorManager(config)
    mock_controller = MockG1Controller()
    
    # Inicializa
    await manager.initialize(mock_controller)
    
    # Testa disponibilidade individual
    connectors = ["tts", "leds", "audio"]
    
    for connector_name in connectors:
        available = await manager.is_connector_available(connector_name)
        status = manager.get_connector_status(connector_name)
        
        print(f"  {connector_name}:")
        print(f"    Disponível: {'✅' if available else '❌'}")
        print(f"    Habilitado: {'✅' if status.enabled else '❌'}")
        print(f"    Inicializado: {'✅' if status.initialized else '❌'}")
        if status.error_message:
            print(f"    Erro: {status.error_message}")
    
    # Testa todos os conectores
    test_results = await manager.test_all_connectors()
    print(f"\n🧪 Resultados dos Testes: {test_results}")
    
    return True


async def main():
    """Função principal de teste."""
    print("🚀 INICIANDO TESTES DOS CONECTORES NATIVOS G1")
    print("=" * 60)
    
    tests = [
        ("Gerenciador de Conectores", test_connector_manager),
        ("Conector TTS", test_tts_connector),
        ("Conector LEDs", test_led_connector),
        ("Conector Áudio", test_audio_connector),
        ("Capacidades", test_connector_capabilities),
        ("Disponibilidade", test_connector_availability)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*60}")
            result = await test_func()
            results[test_name] = result
            print(f"{'='*60}")
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
            results[test_name] = False
    
    # Resumo dos resultados
    print("\n📊 RESUMO DOS TESTES")
    print("=" * 30)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado Final: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        return True
    else:
        print("⚠️ Alguns testes falharam")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
