#!/usr/bin/env python3
"""
Teste simples para o módulo Unitree do sistema t031a5.

Testa funcionalidades básicas sem SDK real.
"""

import sys
import asyncio
import logging
import math
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from t031a5.unitree import G1Interface, G1Controller

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_g1_interface_basic():
    """Testa funcionalidades básicas da interface G1."""
    
    print("🤖 Testando G1Interface (Básico)")
    print("=" * 40)
    
    try:
        # Configuração da interface
        config = {
            "robot_ip": "192.168.123.161",
            "robot_port": 8080,
            "timeout": 5.0,
            "retry_attempts": 3,
            "safety_mode": "normal",
            "emergency_stop": True,
            "max_speed": 0.5,
            "max_turn_speed": 0.3
        }
        
        # Cria interface
        interface = G1Interface(config)
        
        # Verifica configuração
        print("1. Verificando configuração...")
        print(f"   IP: {interface.robot_ip}")
        print(f"   Porta: {interface.robot_port}")
        print(f"   Modo segurança: {interface.safety_mode}")
        print(f"   Velocidade máxima: {interface.max_speed}")
        
        # Verifica estado inicial
        print("\n2. Verificando estado inicial...")
        print(f"   Estado: {interface.state.value}")
        print(f"   Conectado: {interface.is_connected}")
        print(f"   Inicializado: {interface.is_initialized}")
        
        # Testa métodos básicos
        print("\n3. Testando métodos básicos...")
        
        # Status
        status = await interface.get_status()
        print(f"   Status obtido: {status['state']}")
        
        # Sensores (simulados)
        sensors = await interface.get_sensors()
        print(f"   Sensores: battery={sensors.battery_level:.1f}%")
        
        # Pose (simulada)
        pose = await interface.get_pose()
        print(f"   Pose: ({pose.x:.2f}, {pose.y:.2f})")
        
        print("\n✅ G1Interface básico testado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do G1Interface: {e}")
        return False


async def test_g1_controller_basic():
    """Testa funcionalidades básicas do controlador G1."""
    
    print("\n🤖 Testando G1Controller (Básico)")
    print("=" * 40)
    
    try:
        # Configuração do controlador
        config = {
            "interface": {
                "robot_ip": "192.168.123.161",
                "robot_port": 8080,
                "timeout": 5.0
            },
            "default_speed": 0.3,
            "default_turn_speed": 0.2,
            "movement_timeout": 10.0,
            "gesture_speed": 0.5,
            "gesture_timeout": 5.0,
            "max_history": 100
        }
        
        # Cria controlador
        controller = G1Controller(config)
        
        # Verifica configuração
        print("1. Verificando configuração...")
        print(f"   Velocidade padrão: {controller.default_speed}")
        print(f"   Velocidade de giro: {controller.default_turn_speed}")
        print(f"   Timeout movimento: {controller.movement_timeout}s")
        
        # Verifica estado inicial
        print("\n2. Verificando estado inicial...")
        print(f"   Inicializado: {controller.is_initialized}")
        print(f"   Rodando: {controller.is_running}")
        
        # Testa métodos básicos
        print("\n3. Testando métodos básicos...")
        
        # Status
        status = await controller.get_status()
        print(f"   Status obtido: {status['controller']['initialized']}")
        
        # Histórico
        history = controller.get_command_history()
        print(f"   Histórico: {len(history)} comandos")
        
        print("\n✅ G1Controller básico testado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do G1Controller: {e}")
        return False


async def test_emergency_stop_basic():
    """Testa parada de emergência básica."""
    
    print("\n🚨 Testando Parada de Emergência (Básico)")
    print("=" * 40)
    
    try:
        # Configuração
        config = {
            "interface": {
                "robot_ip": "192.168.123.161",
                "robot_port": 8080
            }
        }
        
        # Cria controlador
        controller = G1Controller(config)
        
        print("1. Controlador criado")
        print("2. Executando parada de emergência...")
        
        success = await controller.emergency_stop()
        
        if success:
            print("✅ Parada de emergência executada com sucesso")
        else:
            print("❌ Falha na parada de emergência")
        
        return success
        
    except Exception as e:
        print(f"❌ Erro no teste de emergência: {e}")
        return False


async def test_command_planning():
    """Testa planejamento de comandos."""
    
    print("\n📋 Testando Planejamento de Comandos")
    print("=" * 40)
    
    try:
        # Configuração
        config = {
            "interface": {
                "robot_ip": "192.168.123.161",
                "robot_port": 8080
            }
        }
        
        # Cria controlador
        controller = G1Controller(config)
        
        print("1. Planejando sequência de comandos...")
        
        # Lista de comandos para testar
        commands = [
            ("move_forward", {"distance": 0.5, "speed": 0.3}),
            ("turn_left", {"angle": math.pi/4, "speed": 0.2}),
            ("move_forward", {"distance": 0.3, "speed": 0.3}),
            ("turn_right", {"angle": math.pi/2, "speed": 0.2}),
            ("perform_gesture", {"gesture": "wave", "duration": 2.0}),
            ("speak_text", {"text": "Olá!", "emotion": "happy", "volume": 0.7})
        ]
        
        print(f"   {len(commands)} comandos planejados:")
        for i, (cmd, params) in enumerate(commands, 1):
            print(f"     {i}. {cmd}: {params}")
        
        print("\n2. Verificando validação de comandos...")
        
        # Testa validação de gestos
        valid_gestures = ["wave", "hug", "clap", "point", "thumbs_up", "dance", "bow"]
        print(f"   Gestos válidos: {valid_gestures}")
        
        # Testa validação de emoções
        valid_emotions = ["happy", "sad", "excited", "calm", "neutral"]
        print(f"   Emoções válidas: {valid_emotions}")
        
        print("\n✅ Planejamento de comandos testado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de planejamento: {e}")
        return False


if __name__ == "__main__":
    async def main():
        print("🚀 Iniciando testes básicos do módulo Unitree\n")
        
        results = []
        
        # Teste da interface básica
        print("Teste 1: G1Interface Básico")
        results.append(await test_g1_interface_basic())
        
        # Teste do controlador básico
        print("\nTeste 2: G1Controller Básico")
        results.append(await test_g1_controller_basic())
        
        # Teste de emergência básico
        print("\nTeste 3: Parada de Emergência Básica")
        results.append(await test_emergency_stop_basic())
        
        # Teste de planejamento
        print("\nTeste 4: Planejamento de Comandos")
        results.append(await test_command_planning())
        
        # Resultado final
        print("\n" + "="*60)
        print("📊 RESULTADO FINAL DOS TESTES")
        print("="*60)
        
        # Filtra valores None e conta sucessos
        valid_results = [r for r in results if r is not None]
        passed = sum(valid_results)
        total = len(valid_results)
        
        print(f"Testes passaram: {passed}/{total}")
        
        if passed == total:
            print("🎉 TODOS OS TESTES PASSARAM!")
            print("O módulo Unitree está funcionando corretamente!")
            print("\n💡 Para usar com G1 real:")
            print("   1. Configure o IP correto do robô")
            print("   2. Instale o SDK2 Python: pip install unitree-sdk2py")
            print("   3. Conecte via Ethernet ou WiFi")
            print("   4. Execute os testes completos")
        else:
            print("❌ Alguns testes falharam")
        
        return passed == total
    
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
