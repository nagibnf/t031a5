#!/usr/bin/env python3
"""
Script de teste para o módulo Unitree do sistema t031a5.

Testa G1Interface e G1Controller.
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


async def test_g1_interface():
    """Testa a interface G1."""
    
    print("🤖 Testando G1Interface")
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
        
        # Inicializa
        print("1. Inicializando G1Interface...")
        success = await interface.initialize()
        
        if not success:
            print("❌ Falha na inicialização do G1Interface")
            return False
        
        print("✅ G1Interface inicializado com sucesso")
        
        # Testa leitura de sensores
        print("\n2. Testando leitura de sensores...")
        sensors = await interface.get_sensors()
        print(f"   Bateria: {sensors.battery_level:.1f}%")
        print(f"   Tensão: {sensors.battery_voltage:.1f}V")
        print(f"   Temperatura: {sensors.temperature:.1f}°C")
        
        # Testa leitura de pose
        print("\n3. Testando leitura de pose...")
        pose = await interface.get_pose()
        print(f"   Posição: ({pose.x:.2f}, {pose.y:.2f}, {pose.z:.2f})")
        print(f"   Orientação: ({math.degrees(pose.yaw):.1f}°, {math.degrees(pose.pitch):.1f}°, {math.degrees(pose.roll):.1f}°)")
        
        # Testa movimento
        print("\n4. Testando movimento...")
        success = await interface.move(0.1, 0, 0, 0.2)
        if success:
            print("✅ Movimento executado com sucesso")
        else:
            print("❌ Falha no movimento")
        
        # Testa fala
        print("\n5. Testando fala...")
        success = await interface.speak("Olá! Sou o G1.", 0.6)
        if success:
            print("✅ Fala executada com sucesso")
        else:
            print("❌ Falha na fala")
        
        # Testa emoção
        print("\n6. Testando emoção...")
        success = await interface.set_emotion("happy", 0.7)
        if success:
            print("✅ Emoção definida com sucesso")
        else:
            print("❌ Falha na emoção")
        
        # Verifica status
        print("\n7. Verificando status...")
        status = await interface.get_status()
        print(f"   Estado: {status['state']}")
        print(f"   Conectado: {status['connected']}")
        print(f"   Inicializado: {status['initialized']}")
        
        # Para interface
        await interface.stop()
        print("\n✅ G1Interface testado com sucesso!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do G1Interface: {e}")
        return False


async def test_g1_controller():
    """Testa o controlador G1."""
    
    print("\n🤖 Testando G1Controller")
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
        
        # Inicializa
        print("1. Inicializando G1Controller...")
        success = await controller.initialize()
        
        if not success:
            print("❌ Falha na inicialização do G1Controller")
            return False
        
        print("✅ G1Controller inicializado com sucesso")
        
        # Testa movimento para frente
        print("\n2. Testando movimento para frente...")
        success = await controller.move_forward(0.2, 0.2)
        if success:
            print("✅ Movimento para frente executado")
        else:
            print("❌ Falha no movimento para frente")
        
        # Testa giro para esquerda
        print("\n3. Testando giro para esquerda...")
        success = await controller.turn_left(math.pi / 4, 0.2)  # 45 graus
        if success:
            print("✅ Giro para esquerda executado")
        else:
            print("❌ Falha no giro para esquerda")
        
        # Testa giro para direita
        print("\n4. Testando giro para direita...")
        success = await controller.turn_right(math.pi / 4, 0.2)  # 45 graus
        if success:
            print("✅ Giro para direita executado")
        else:
            print("❌ Falha no giro para direita")
        
        # Testa movimento para trás
        print("\n5. Testando movimento para trás...")
        success = await controller.move_backward(0.2, 0.2)
        if success:
            print("✅ Movimento para trás executado")
        else:
            print("❌ Falha no movimento para trás")
        
        # Testa movimento para posição
        print("\n6. Testando movimento para posição...")
        success = await controller.move_to_position(0.5, 0.3, math.pi / 2, 0.2)
        if success:
            print("✅ Movimento para posição executado")
        else:
            print("❌ Falha no movimento para posição")
        
        # Testa gesto
        print("\n7. Testando gesto...")
        success = await controller.perform_gesture("wave", 2.0)
        if success:
            print("✅ Gesto executado")
        else:
            print("❌ Falha no gesto")
        
        # Testa fala com emoção
        print("\n8. Testando fala com emoção...")
        success = await controller.speak_text("Estou testando meus comandos!", 0.7, "excited")
        if success:
            print("✅ Fala com emoção executada")
        else:
            print("❌ Falha na fala com emoção")
        
        # Verifica status
        print("\n9. Verificando status...")
        status = await controller.get_status()
        print(f"   Controlador inicializado: {status['controller']['initialized']}")
        print(f"   Controlador rodando: {status['controller']['running']}")
        print(f"   Comandos executados: {status['commands_executed']}")
        print(f"   Estado da interface: {status['interface']['state']}")
        
        # Verifica histórico
        print("\n10. Verificando histórico de comandos...")
        history = controller.get_command_history(5)
        print(f"   Últimos {len(history)} comandos:")
        for cmd in history:
            print(f"     - {cmd['command']}: {cmd['parameters']}")
        
        # Para controlador
        await controller.stop()
        print("\n✅ G1Controller testado com sucesso!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do G1Controller: {e}")
        return False


async def test_emergency_stop():
    """Testa a parada de emergência."""
    
    print("\n🚨 Testando Parada de Emergência")
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
        await controller.initialize()
        
        print("1. Controlador inicializado")
        print("2. Executando parada de emergência...")
        
        success = await controller.emergency_stop()
        
        if success:
            print("✅ Parada de emergência executada com sucesso")
        else:
            print("❌ Falha na parada de emergência")
        
        await controller.stop()
        return success
        
    except Exception as e:
        print(f"❌ Erro no teste de emergência: {e}")
        return False


if __name__ == "__main__":
    async def main():
        print("🚀 Iniciando testes do módulo Unitree\n")
        
        results = []
        
        # Teste da interface
        print("Teste 1: G1Interface")
        results.append(await test_g1_interface())
        
        # Teste do controlador
        print("\nTeste 2: G1Controller")
        results.append(await test_g1_controller())
        
        # Teste de emergência
        print("\nTeste 3: Parada de Emergência")
        results.append(await test_emergency_stop())
        
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
            print("O módulo Unitree está funcionando perfeitamente!")
            print("\n💡 Para usar com G1 real:")
            print("   1. Configure o IP correto do robô")
            print("   2. Instale o SDK2 Python: pip install unitree-sdk2py")
            print("   3. Conecte via Ethernet ou WiFi")
        else:
            print("❌ Alguns testes falharam")
        
        return passed == total
    
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
