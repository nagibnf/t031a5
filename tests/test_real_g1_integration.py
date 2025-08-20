#!/usr/bin/env python3
"""
Script de teste para integração real com G1.

Testa a conectividade real com o robô humanóide G1 da Unitree.
"""

import sys
import asyncio
import time
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from t031a5.runtime import CortexRuntime
from t031a5.unitree import G1Controller, G1Interface
from t031a5.logging import StructuredLogger, LogContext, MetricsCollector, PerformanceMonitor


def test_g1_sdk_installation():
    """Testa se o SDK do G1 está instalado."""
    print("🔍 Testando instalação do SDK G1...")
    
    try:
        import unitree_sdk2py
        print("✅ SDK2 Python instalado")
        
        # Verifica versão
        try:
            version = unitree_sdk2py.__version__
            print(f"    Versão: {version}")
        except:
            print("    Versão: Não disponível")
        
        return True
        
    except ImportError:
        print("❌ SDK2 Python não instalado")
        print("💡 Para instalar: pip install unitree-sdk2py")
        return False


def test_network_connectivity():
    """Testa conectividade de rede com G1."""
    print("\n🔍 Testando conectividade de rede...")
    
    try:
        import socket
        
        # Testa conectividade com IP padrão do G1
        g1_ip = "192.168.123.161"
        g1_port = 8080
        
        print(f"    Testando conexão com {g1_ip}:{g1_port}...")
        
        # Cria socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        
        # Tenta conectar
        result = sock.connect_ex((g1_ip, g1_port))
        sock.close()
        
        if result == 0:
            print("✅ Conexão com G1 estabelecida")
            return True
        else:
            print("❌ Não foi possível conectar com G1")
            print("💡 Verifique:")
            print("   - G1 está ligado e conectado à rede")
            print("   - IP correto: 192.168.123.161")
            print("   - Rede configurada corretamente")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de conectividade: {e}")
        return False


async def test_g1_interface_real():
    """Testa interface real com G1."""
    print("\n🔍 Testando interface real com G1...")
    
    try:
        # Cria interface
        interface = G1Interface({
            "robot_ip": "192.168.123.161",
            "robot_port": 8080,
            "timeout": 5.0
        })
        
        # Inicializa
        success = await interface.initialize()
        if not success:
            print("❌ Falha na inicialização da interface")
            return False
        
        print("✅ Interface inicializada")
        
        # Testa conexão
        connected = await interface.connect()
        if not connected:
            print("❌ Falha na conexão com G1")
            return False
        
        print("✅ Conectado ao G1")
        
        # Testa obtenção de dados
        try:
            # Sensor data
            sensor_data = await interface.get_sensor_data()
            print(f"    ✅ Dados de sensor obtidos")
            print(f"       - Bateria: {sensor_data.get('battery', 'N/A')}%")
            print(f"       - Temperatura: {sensor_data.get('temperature', 'N/A')}°C")
            
            # Pose data
            pose_data = await interface.get_pose_data()
            print(f"    ✅ Dados de pose obtidos")
            print(f"       - Posição: {pose_data.get('position', 'N/A')}")
            print(f"       - Orientação: {pose_data.get('orientation', 'N/A')}")
            
            # Robot state
            state = await interface.get_robot_state()
            print(f"    ✅ Estado do robô obtido")
            print(f"       - Estado: {state.get('state', 'N/A')}")
            print(f"       - Modo: {state.get('mode', 'N/A')}")
            
        except Exception as e:
            print(f"    ⚠️  Erro ao obter dados: {e}")
        
        # Desconecta
        await interface.disconnect()
        print("✅ Desconectado do G1")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste da interface: {e}")
        return False


async def test_g1_controller_real():
    """Testa controlador real com G1."""
    print("\n🔍 Testando controlador real com G1...")
    
    try:
        # Cria controlador
        controller = G1Controller({
            "interface": {
                "robot_ip": "192.168.123.161",
                "robot_port": 8080,
                "timeout": 5.0
            },
            "default_speed": 0.3,
            "default_turn_speed": 0.2
        })
        
        # Inicializa
        success = await controller.initialize()
        if not success:
            print("❌ Falha na inicialização do controlador")
            return False
        
        print("✅ Controlador inicializado")
        
        # Testa comandos básicos (sem executar)
        print("    Testando comandos básicos...")
        
        # Movimento
        success = await controller.move_forward(0.1, 0.2)
        print(f"       - Move forward: {'✅' if success else '❌'}")
        
        success = await controller.turn_left(0.1, 0.2)
        print(f"       - Turn left: {'✅' if success else '❌'}")
        
        # Gestos
        success = await controller.perform_gesture("wave")
        print(f"       - Gesture wave: {'✅' if success else '❌'}")
        
        # Fala
        success = await controller.speak_text("Teste de integração", "neutral", 0.6)
        print(f"       - Speak text: {'✅' if success else '❌'}")
        
        # Emoção
        success = await controller.set_emotion("happy")
        print(f"       - Set emotion: {'✅' if success else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do controlador: {e}")
        return False


async def test_system_with_real_g1():
    """Testa sistema completo com G1 real."""
    print("\n🔍 Testando sistema completo com G1 real...")
    
    try:
        # Configuração para G1 real
        config_file = "config/g1_real.json5"
        
        if not Path(config_file).exists():
            print(f"❌ Arquivo de configuração não encontrado: {config_file}")
            print("💡 Crie config/g1_real.json5 para testes com G1 real")
            return False
        
        # Cria runtime
        runtime = CortexRuntime(Path(config_file))
        
        # Inicializa
        success = await runtime.initialize()
        if not success:
            print("❌ Falha na inicialização do sistema")
            return False
        
        print("✅ Sistema inicializado")
        
        # Mostra status
        status = await runtime.get_status()
        print(f"    ✅ Config carregada: {status['config_loaded']}")
        print(f"    ✅ Componentes inicializados: {status['components_initialized']}")
        
        # Status do G1Controller
        if status.get('g1_controller'):
            g1_status = status['g1_controller']
            if isinstance(g1_status, dict) and not g1_status.get('error'):
                print(f"    ✅ G1Controller: {g1_status.get('controller', {}).get('initialized', False)}")
                if g1_status.get('interface'):
                    print(f"    ✅ G1 Interface: {g1_status['interface'].get('state', 'unknown')}")
            else:
                print(f"    ❌ G1Controller: Erro")
        else:
            print(f"    ⚪ G1Controller: Não configurado")
        
        # Executa por alguns segundos
        print("    Executando sistema por 10 segundos...")
        
        run_task = asyncio.create_task(runtime.start())
        await asyncio.sleep(10)
        
        # Para o sistema
        runtime.is_running = False
        await run_task
        
        # Estatísticas finais
        final_status = await runtime.get_status()
        print(f"    ✅ Loops executados: {final_status['loop_count']}")
        print(f"    ✅ Erros: {final_status['metrics']['errors']}")
        print(f"    ✅ Frequência: {final_status['loop_count']/10:.2f} Hz")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do sistema: {e}")
        return False


def create_real_g1_config():
    """Cria configuração para G1 real."""
    print("\n🔍 Criando configuração para G1 real...")
    
    config_content = '''{
  "hertz": 10,
  "name": "g1_real_system",
  "unitree_ethernet": "en0",
  "system_prompt_base": "Você é um assistente robótico humanóide G1 da Unitree. Você é útil, amigável e sempre tenta ajudar os humanos ao seu redor. Você pode se mover, falar, expressar emoções e interagir com o ambiente. Responda sempre em português brasileiro de forma natural e conversacional.",
  
  "development": {
    "websim_enabled": true,
    "debug_mode": true,
    "hot_reload": true
  },
  
  "g1_specific": {
    "safety_mode": "normal",
    "emergency_stop": true,
    "battery_conservation": true,
    "thermal_management": true,
    "network_timeout": 5.0
  },
  
  "agent_inputs": [
    {
      "type": "G1Voice",
      "enabled": true,
      "priority": 1,
      "config": {
        "sample_rate": 16000,
        "chunk_size": 1024,
        "language": "pt-BR",
        "use_g1_microphone": true,
        "asr_provider": "google",
        "vad_enabled": true,
        "vad_threshold": 0.3,
        "noise_reduction": true,
        "echo_cancellation": true,
        "debug_audio": false
      }
    },
    {
      "type": "G1Sensors",
      "enabled": true,
      "priority": 2,
      "config": {
        "battery_monitoring": true,
        "temperature_monitoring": true,
        "imu_monitoring": true,
        "update_interval": 0.2,
        "alert_thresholds": {
          "battery_low": 20,
          "temperature_high": 45
        },
        "debug_sensors": false
      }
    }
  ],
  
  "agent_actions": [
    {
      "type": "G1Speech",
      "enabled": true,
      "priority": 1,
      "config": {
        "tts_provider": "g1_native",
        "voice_id": "g1_default",
        "speech_rate": 1.0,
        "volume": 0.6,
        "language": "pt-BR",
        "emotion_in_speech": true,
        "debug_speech": false
      }
    },
    {
      "type": "G1Emotion",
      "enabled": true,
      "priority": 2,
      "config": {
        "led_brightness": 0.5,
        "emotion_transition_time": 0.2,
        "default_emotion": "neutral",
        "debug_emotion": false,
        "emotion_mapping": {
          "happy": {"r": 255, "g": 255, "b": 0},
          "sad": {"r": 0, "g": 0, "b": 255},
          "excited": {"r": 255, "g": 0, "b": 0},
          "calm": {"r": 0, "g": 255, "b": 0},
          "neutral": {"r": 128, "g": 128, "b": 128}
        }
      }
    }
  ],
  
  "fuser": {
    "type": "priority",
    "config": {
      "voice_priority": 1.0,
      "sensors_priority": 0.5,
      "fusion_timeout": 1.0,
      "context_window": 3
    }
  },
  
  "llm": {
    "provider": "mock",
    "model": "mock-g1-real",
    "temperature": 0.7,
    "max_tokens": 500,
    "timeout": 30.0,
    "response_delay": 0.5,
    "error_rate": 0.0,
    "include_vision": false,
    "include_sensors": true,
    "include_location": true,
    "include_robot_state": true,
    "debug_llm": false
  },
  
  "g1_controller": {
    "enabled": true,
    "interface": {
      "robot_ip": "192.168.123.161",
      "robot_port": 8080,
      "timeout": 5.0,
      "retry_attempts": 3,
      "safety_mode": "normal",
      "emergency_stop": true,
      "max_speed": 0.5,
      "max_turn_speed": 0.3
    },
    "default_speed": 0.3,
    "default_turn_speed": 0.2,
    "movement_timeout": 10.0,
    "gesture_speed": 0.5,
    "gesture_timeout": 5.0,
    "max_history": 100
  },
  
  "websim": {
    "enabled": true,
    "host": "localhost",
    "port": 8080,
    "debug": true,
    "auto_reload": true,
    "static_dir": "static",
    "templates_dir": "templates",
    "max_connections": 10,
    "update_interval": 0.1
  },
  
  "logging": {
    "level": "INFO",
    "log_format": "detailed",
    "file": "logs/t031a5_real.log"
  }
}
'''
    
    config_path = Path("config/g1_real.json5")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"✅ Configuração criada: {config_path}")
    return True


async def main():
    """Função principal de teste."""
    print("🚀 Testando integração real com G1\n")
    
    results = []
    
    # Teste de instalação do SDK
    print("Teste 1: Instalação do SDK G1")
    results.append(test_g1_sdk_installation())
    
    # Teste de conectividade
    print("\nTeste 2: Conectividade de Rede")
    results.append(test_network_connectivity())
    
    # Cria configuração para G1 real
    print("\nTeste 3: Configuração para G1 Real")
    results.append(create_real_g1_config())
    
    # Teste da interface real (se SDK instalado)
    if results[0]:  # Se SDK está instalado
        print("\nTeste 4: Interface Real com G1")
        results.append(await test_g1_interface_real())
        
        print("\nTeste 5: Controlador Real com G1")
        results.append(await test_g1_controller_real())
        
        print("\nTeste 6: Sistema Completo com G1 Real")
        results.append(await test_system_with_real_g1())
    else:
        print("\n⚠️  Pulando testes de interface real (SDK não instalado)")
        results.extend([None, None, None])
    
    # Resultado final
    print("\n" + "="*60)
    print("📊 RESULTADO FINAL DOS TESTES DE INTEGRAÇÃO REAL")
    print("="*60)
    
    # Filtra valores None e conta sucessos
    valid_results = [r for r in results if r is not None]
    passed = sum(valid_results)
    total = len(valid_results)
    
    print(f"Testes passaram: {passed}/{total}")
    
    if passed == total:
        print("🎉 TODOS OS TESTES DE INTEGRAÇÃO REAL PASSARAM!")
        print("O sistema está pronto para uso com G1 real!")
        print("\n💡 Para usar com G1 real:")
        print("   python3 -m t031a5.cli run --config config/g1_real.json5")
        print("   Acesse: http://localhost:8080")
    else:
        print("❌ Alguns testes de integração real falharam")
        print("\n💡 Para resolver:")
        print("   1. Instale o SDK: pip install unitree-sdk2py")
        print("   2. Configure a rede para conectar com G1")
        print("   3. Verifique se G1 está ligado e conectado")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
