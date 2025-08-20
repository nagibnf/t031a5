#!/usr/bin/env python3
"""
Teste para plugins avançados do G1.

Valida:
- G1Vision (visão computacional)
- G1GPS (navegação e localização)
- G1State (estado do robô)
- G1Movement (locomoção)
- G1Arms (controle de braços)
- G1Audio (sistema de áudio)
"""

import sys
import os
import asyncio
import logging
from datetime import datetime
from pathlib import Path

# Adiciona src ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from t031a5.inputs.plugins.g1_vision import G1VisionInput
from t031a5.inputs.plugins.g1_gps import G1GPSInput
from t031a5.inputs.plugins.g1_state import G1StateInput
from t031a5.actions.g1_movement import G1MovementAction
from t031a5.actions.g1_arms import G1ArmsAction
from t031a5.actions.g1_audio import G1AudioAction


async def test_g1_vision():
    """Testa G1Vision."""
    print("\n🔍 Testando G1Vision...")
    
    try:
        # Configuração
        config = {
            "enabled": True,
            "camera_index": 0,
            "resolution": (640, 480),
            "fps": 30,
            "detection_confidence": 0.7,
            "enable_face_detection": True,
            "enable_object_detection": True,
            "enable_motion_detection": True,
            "enable_ocr": True,
            "mock_mode": True
        }
        
        # Inicializa plugin
        vision = G1VisionInput(config)
        success = await vision.initialize()
        
        if not success:
            print("❌ Falha na inicialização do G1Vision")
            return False
        
        print("✅ G1Vision inicializado")
        
        # Testa coleta de dados
        data = await vision.get_data()
        if data:
            print(f"✅ Dados coletados: {len(str(data.data))} caracteres")
            print(f"   Objetos detectados: {data.data.get('objects', [])}")
            print(f"   Faces detectadas: {data.data.get('faces', [])}")
            print(f"   Movimento detectado: {data.data.get('motion_detected', False)}")
        else:
            print("❌ Falha na coleta de dados")
            return False
        
        # Testa status
        status = await vision.get_status()
        print(f"✅ Status: {status.get('status', 'unknown')}")
        
        # Para plugin
        await vision.stop()
        print("✅ G1Vision parado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste G1Vision: {e}")
        return False


async def test_g1_gps():
    """Testa G1GPS."""
    print("\n📍 Testando G1GPS...")
    
    try:
        # Configuração
        config = {
            "enabled": True,
            "port": "/dev/ttyUSB0",
            "baudrate": 9600,
            "update_interval": 1.0,
            "enable_navigation": True,
            "enable_waypoints": True,
            "enable_route_tracking": True,
            "mock_mode": True,
            "mock_location": {
                "latitude": -23.5505,
                "longitude": -46.6333,
                "altitude": 760.0
            }
        }
        
        # Inicializa plugin
        gps = G1GPSInput(config)
        success = await gps.initialize()
        
        if not success:
            print("❌ Falha na inicialização do G1GPS")
            return False
        
        print("✅ G1GPS inicializado")
        
        # Testa coleta de dados
        data = await gps.get_data()
        if data:
            print(f"✅ Dados coletados: {len(str(data.data))} caracteres")
            location = data.data.get('location', {})
            print(f"   Latitude: {location.get('latitude', 'N/A')}")
            print(f"   Longitude: {location.get('longitude', 'N/A')}")
            print(f"   Altitude: {location.get('altitude', 'N/A')}m")
            print(f"   Velocidade: {data.data.get('speed', 'N/A')} km/h")
        else:
            print("❌ Falha na coleta de dados")
            return False
        
        # Testa navegação
        waypoints = await gps._load_waypoints()
        print(f"✅ Waypoints carregados: {len(waypoints)}")
        
        # Testa status
        status = await gps.get_status()
        print(f"✅ Status: {status.get('status', 'unknown')}")
        
        # Para plugin
        await gps.stop()
        print("✅ G1GPS parado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste G1GPS: {e}")
        return False


async def test_g1_state():
    """Testa G1State."""
    print("\n🤖 Testando G1State...")
    
    try:
        # Configuração
        config = {
            "enabled": True,
            "update_interval": 0.1,
            "enable_joint_monitoring": True,
            "enable_motor_monitoring": True,
            "enable_battery_monitoring": True,
            "enable_thermal_monitoring": True,
            "enable_safety_monitoring": True,
            "mock_mode": True
        }
        
        # Inicializa plugin
        state = G1StateInput(config)
        success = await state.initialize()
        
        if not success:
            print("❌ Falha na inicialização do G1State")
            return False
        
        print("✅ G1State inicializado")
        
        # Testa coleta de dados
        data = await state.get_data()
        if data:
            print(f"✅ Dados coletados: {len(str(data.data))} caracteres")
            robot_state = data.data.get('robot_state', {})
            print(f"   Modo: {robot_state.get('mode', 'N/A')}")
            print(f"   Bateria: {robot_state.get('battery_percentage', 'N/A')}%")
            print(f"   Temperatura: {robot_state.get('temperature', 'N/A')}°C")
            print(f"   Status de segurança: {robot_state.get('safety_status', 'N/A')}")
        else:
            print("❌ Falha na coleta de dados")
            return False
        
        # Testa status
        status = await state.get_status()
        print(f"✅ Status: {status.get('status', 'unknown')}")
        
        # Para plugin
        await state.stop()
        print("✅ G1State parado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste G1State: {e}")
        return False


async def test_g1_movement():
    """Testa G1Movement."""
    print("\n🚶 Testando G1Movement...")
    
    try:
        # Configuração
        config = {
            "enabled": True,
            "max_speed": 2.0,
            "max_turn_speed": 1.0,
            "safety_distance": 0.5,
            "enable_obstacle_detection": True,
            "enable_posture_control": True,
            "enable_navigation": True,
            "mock_mode": True
        }
        
        # Inicializa plugin
        movement = G1MovementAction(config)
        success = await movement.initialize()
        
        if not success:
            print("❌ Falha na inicialização do G1Movement")
            return False
        
        print("✅ G1Movement inicializado")
        
        # Testa comando de movimento
        from t031a5.actions.base import ActionRequest
        
        request = ActionRequest(
            action_type="movement",
            action_name="walk",
            timestamp=datetime.now(),
            data={
                "action": "walk",
                "direction": "forward",
                "distance": 1.0,
                "speed": 0.5
            }
        )
        
        result = await movement.execute(request)
        if result.success:
            print("✅ Comando de movimento executado")
            print(f"   Ação: {result.data.get('action', 'N/A')}")
            print(f"   Status: {result.data.get('status', 'N/A')}")
        else:
            print("❌ Falha na execução do comando")
            return False
        
        # Testa status
        status = await movement.get_status()
        print(f"✅ Status: {status.get('status', 'unknown')}")
        
        # Para plugin
        await movement.stop()
        print("✅ G1Movement parado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste G1Movement: {e}")
        return False


async def test_g1_arms():
    """Testa G1Arms."""
    print("\n🤲 Testando G1Arms...")
    
    try:
        # Configuração
        config = {
            "enabled": True,
            "max_force": 50.0,
            "max_speed": 1.0,
            "enable_force_control": True,
            "enable_collision_detection": True,
            "enable_gestures": True,
            "mock_mode": True
        }
        
        # Inicializa plugin
        arms = G1ArmsAction(config)
        success = await arms.initialize()
        
        if not success:
            print("❌ Falha na inicialização do G1Arms")
            return False
        
        print("✅ G1Arms inicializado")
        
        # Testa comando de braço
        from t031a5.actions.base import ActionRequest
        
        request = ActionRequest(
            action_type="arms",
            action_name="move",
            timestamp=datetime.now(),
            data={
                "action": "move",
                "arm": "right",
                "position": {"x": 0.3, "y": 0.2, "z": 0.1},
                "speed": 0.5
            }
        )
        
        result = await arms.execute(request)
        if result.success:
            print("✅ Comando de braço executado")
            print(f"   Ação: {result.data.get('action', 'N/A')}")
            print(f"   Braço: {result.data.get('arm', 'N/A')}")
            print(f"   Status: {result.data.get('status', 'N/A')}")
        else:
            print("❌ Falha na execução do comando")
            return False
        
        # Testa status
        status = await arms.get_status()
        print(f"✅ Status: {status.get('status', 'unknown')}")
        
        # Para plugin
        await arms.stop()
        print("✅ G1Arms parado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste G1Arms: {e}")
        return False


async def test_g1_audio():
    """Testa G1Audio."""
    print("\n🔊 Testando G1Audio...")
    
    try:
        # Configuração
        config = {
            "enabled": True,
            "sample_rate": 44100,
            "channels": 2,
            "default_volume": 0.7,
            "enable_effects": True,
            "enable_equalizer": True,
            "mock_mode": True
        }
        
        # Inicializa plugin
        audio = G1AudioAction(config)
        success = await audio.initialize()
        
        if not success:
            print("❌ Falha na inicialização do G1Audio")
            return False
        
        print("✅ G1Audio inicializado")
        
        # Testa comando de áudio
        from t031a5.actions.base import ActionRequest
        
        request = ActionRequest(
            action_type="audio",
            action_name="play",
            timestamp=datetime.now(),
            data={
                "action": "play",
                "sound": "success",
                "volume": 0.8
            }
        )
        
        result = await audio.execute(request)
        if result.success:
            print("✅ Comando de áudio executado")
            print(f"   Ação: {result.data.get('action', 'N/A')}")
            print(f"   Volume: {result.data.get('volume', 'N/A')}")
            print(f"   Status: {result.data.get('status', 'N/A')}")
        else:
            print("❌ Falha na execução do comando")
            return False
        
        # Testa status
        status = await audio.get_status()
        print(f"✅ Status: {status.get('audio_status', 'unknown')}")
        print(f"   Volume: {status.get('volume', 'N/A')}")
        print(f"   Faixas reproduzidas: {status.get('tracks_played', 'N/A')}")
        
        # Para plugin
        await audio.stop()
        print("✅ G1Audio parado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste G1Audio: {e}")
        return False


async def test_integration():
    """Testa integração entre plugins."""
    print("\n🔗 Testando Integração entre Plugins...")
    
    try:
        # Configurações
        vision_config = {"enabled": True, "mock_mode": True}
        gps_config = {"enabled": True, "mock_mode": True}
        state_config = {"enabled": True, "mock_mode": True}
        movement_config = {"enabled": True, "mock_mode": True}
        arms_config = {"enabled": True, "mock_mode": True}
        audio_config = {"enabled": True, "mock_mode": True}
        
        # Inicializa todos os plugins
        plugins = {
            "vision": G1VisionInput(vision_config),
            "gps": G1GPSInput(gps_config),
            "state": G1StateInput(state_config),
            "movement": G1MovementAction(movement_config),
            "arms": G1ArmsAction(arms_config),
            "audio": G1AudioAction(audio_config)
        }
        
        # Inicializa todos
        for name, plugin in plugins.items():
            success = await plugin.initialize()
            if not success:
                print(f"❌ Falha na inicialização do {name}")
                return False
            print(f"✅ {name} inicializado")
        
        # Simula fluxo de dados
        print("\n📊 Simulando fluxo de dados...")
        
        # Coleta dados dos inputs
        vision_data = await plugins["vision"].get_data()
        gps_data = await plugins["gps"].get_data()
        state_data = await plugins["state"].get_data()
        
        print(f"   Visão: {len(str(vision_data.data)) if vision_data else 0} chars")
        print(f"   GPS: {len(str(gps_data.data)) if gps_data else 0} chars")
        print(f"   Estado: {len(str(state_data.data)) if state_data else 0} chars")
        
        # Executa ações
        from t031a5.actions.base import ActionRequest
        
        # Movimento
        movement_request = ActionRequest(
            action_type="movement",
            action_name="walk",
            timestamp=datetime.now(),
            data={"action": "walk", "direction": "forward", "distance": 0.5}
        )
        movement_result = await plugins["movement"].execute(movement_request)
        
        # Braços
        arms_request = ActionRequest(
            action_type="arms",
            action_name="gesture",
            timestamp=datetime.now(),
            data={"action": "gesture", "gesture": "wave"}
        )
        arms_result = await plugins["arms"].execute(arms_request)
        
        # Áudio
        audio_request = ActionRequest(
            action_type="audio",
            action_name="play",
            timestamp=datetime.now(),
            data={"action": "play", "sound": "notification"}
        )
        audio_result = await plugins["audio"].execute(audio_request)
        
        print(f"   Movimento: {'✅' if movement_result.success else '❌'}")
        print(f"   Braços: {'✅' if arms_result.success else '❌'}")
        print(f"   Áudio: {'✅' if audio_result.success else '❌'}")
        
        # Para todos os plugins
        for name, plugin in plugins.items():
            await plugin.stop()
            print(f"✅ {name} parado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de integração: {e}")
        return False


async def main():
    """Função principal."""
    print("🚀 Testando Plugins Avançados do G1")
    print("=" * 50)
    
    # Configura logging
    logging.basicConfig(level=logging.INFO)
    
    # Lista de testes
    tests = [
        ("G1Vision", test_g1_vision),
        ("G1GPS", test_g1_gps),
        ("G1State", test_g1_state),
        ("G1Movement", test_g1_movement),
        ("G1Arms", test_g1_arms),
        ("G1Audio", test_g1_audio),
        ("Integração", test_integration)
    ]
    
    # Executa testes
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
            results.append((test_name, False))
    
    # Relatório final
    print("\n" + "=" * 50)
    print("📋 RELATÓRIO FINAL")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:15} {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os plugins avançados estão funcionando!")
    else:
        print("⚠️  Alguns plugins precisam de atenção")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
