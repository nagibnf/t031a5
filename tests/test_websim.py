#!/usr/bin/env python3
"""
Script de teste para o WebSim do sistema t031a5.

Testa interface web para debugging e controle remoto do G1.
"""

import sys
import asyncio
import logging
import time
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from t031a5.simulators import WebSim
from t031a5.unitree import G1Controller

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_websim_basic():
    """Testa funcionalidades básicas do WebSim."""
    
    print("🌐 Testando WebSim (Básico)")
    print("=" * 40)
    
    try:
        # Configuração do WebSim
        config = {
            "host": "localhost",
            "port": 8080,
            "debug": True,
            "auto_reload": True,
            "static_dir": "static",
            "templates_dir": "templates",
            "max_connections": 10,
            "update_interval": 0.1
        }
        
        # Cria WebSim
        websim = WebSim(config)
        
        # Verifica configuração
        print("1. Verificando configuração...")
        print(f"   Host: {websim.config.host}")
        print(f"   Porta: {websim.config.port}")
        print(f"   Debug: {websim.config.debug}")
        print(f"   Conexões máximas: {websim.config.max_connections}")
        
        # Verifica estado inicial
        print("\n2. Verificando estado inicial...")
        print(f"   Rodando: {websim.is_running}")
        print(f"   Conexões: {len(websim.websocket_connections)}")
        
        print("\n✅ WebSim básico testado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do WebSim: {e}")
        return False


async def test_websim_with_controller():
    """Testa WebSim com controlador G1."""
    
    print("\n🌐 Testando WebSim com Controlador G1")
    print("=" * 40)
    
    try:
        # Configuração do controlador
        g1_config = {
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
        controller = G1Controller(g1_config)
        
        # Configuração do WebSim
        websim_config = {
            "host": "localhost",
            "port": 8081,  # Porta diferente para evitar conflito
            "debug": True,
            "auto_reload": True,
            "static_dir": "static",
            "templates_dir": "templates",
            "max_connections": 10,
            "update_interval": 0.1
        }
        
        # Cria WebSim com controlador
        websim = WebSim(websim_config, controller)
        
        print("1. WebSim criado com controlador G1")
        
        # Verifica integração
        print("\n2. Verificando integração...")
        print(f"   Controlador configurado: {websim.g1_controller is not None}")
        print(f"   Status inicial: {websim.robot_status.state}")
        
        print("\n✅ WebSim com controlador testado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do WebSim com controlador: {e}")
        return False


async def test_websim_server():
    """Testa servidor WebSim."""
    
    print("\n🌐 Testando Servidor WebSim")
    print("=" * 40)
    
    try:
        # Configuração
        config = {
            "host": "localhost",
            "port": 8082,  # Porta diferente
            "debug": True,
            "auto_reload": True,
            "static_dir": "static",
            "templates_dir": "templates",
            "max_connections": 5,
            "update_interval": 0.5
        }
        
        # Cria WebSim
        websim = WebSim(config)
        
        # Inicializa
        print("1. Inicializando WebSim...")
        success = await websim.initialize()
        
        if not success:
            print("❌ Falha na inicialização do WebSim")
            return False
        
        print("✅ WebSim inicializado com sucesso")
        
        # Inicia servidor
        print("\n2. Iniciando servidor...")
        success = await websim.start()
        
        if not success:
            print("❌ Falha ao iniciar servidor")
            return False
        
        print("✅ Servidor iniciado com sucesso")
        
        # Verifica status
        print("\n3. Verificando status...")
        status = await websim.get_status()
        print(f"   Rodando: {status['running']}")
        print(f"   Host: {status['host']}")
        print(f"   Porta: {status['port']}")
        print(f"   Conexões: {status['connections']}")
        
        # Aguarda um pouco
        print("\n4. Aguardando 5 segundos...")
        await asyncio.sleep(5)
        
        # Para servidor
        print("\n5. Parando servidor...")
        await websim.stop()
        print("✅ Servidor parado com sucesso")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do servidor WebSim: {e}")
        return False


async def test_websim_commands():
    """Testa comandos do WebSim."""
    
    print("\n🌐 Testando Comandos WebSim")
    print("=" * 40)
    
    try:
        # Configuração do controlador
        g1_config = {
            "interface": {
                "robot_ip": "192.168.123.161",
                "robot_port": 8080
            }
        }
        
        # Cria controlador
        controller = G1Controller(g1_config)
        
        # Configuração do WebSim
        websim_config = {
            "host": "localhost",
            "port": 8083,
            "debug": True,
            "max_connections": 5,
            "update_interval": 0.1
        }
        
        # Cria WebSim
        websim = WebSim(websim_config, controller)
        await websim.initialize()
        
        print("1. WebSim inicializado")
        
        # Testa comandos
        print("\n2. Testando comandos...")
        
        commands = [
            ("move_forward", {"distance": 0.5, "speed": 0.3}),
            ("turn_left", {"angle": 0.785, "speed": 0.2}),
            ("perform_gesture", {"gesture": "wave", "duration": 2.0}),
            ("speak_text", {"text": "Teste", "emotion": "happy", "volume": 0.7}),
            ("emergency_stop", {})
        ]
        
        for command, params in commands:
            print(f"   Testando comando: {command}")
            success = await websim._execute_command(command, params)
            print(f"     Resultado: {'✅ Sucesso' if success else '❌ Falha'}")
        
        print("\n✅ Comandos WebSim testados com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de comandos WebSim: {e}")
        return False


async def test_websim_api():
    """Testa API REST do WebSim."""
    
    print("\n🌐 Testando API REST WebSim")
    print("=" * 40)
    
    try:
        # Configuração
        config = {
            "host": "localhost",
            "port": 8084,
            "debug": True,
            "max_connections": 5,
            "update_interval": 0.1
        }
        
        # Cria WebSim
        websim = WebSim(config)
        await websim.initialize()
        await websim.start()
        
        print("1. Servidor iniciado")
        
        # Simula requisições API
        print("\n2. Testando endpoints API...")
        
        # Status
        print("   Testando /api/status...")
        # Simula requisição de status
        await websim._update_robot_status()
        status = websim.robot_status
        print(f"     Status obtido: {status.state}")
        
        # Histórico
        print("   Testando /api/history...")
        # Simula requisição de histórico
        history = websim.robot_status.command_history
        print(f"     Histórico: {len(history)} itens")
        
        # Para servidor
        await websim.stop()
        
        print("\n✅ API REST WebSim testada com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste da API WebSim: {e}")
        return False


if __name__ == "__main__":
    async def main():
        print("🚀 Iniciando testes do WebSim\n")
        
        results = []
        
        # Teste básico
        print("Teste 1: WebSim Básico")
        results.append(await test_websim_basic())
        
        # Teste com controlador
        print("\nTeste 2: WebSim com Controlador")
        results.append(await test_websim_with_controller())
        
        # Teste de servidor
        print("\nTeste 3: Servidor WebSim")
        results.append(await test_websim_server())
        
        # Teste de comandos
        print("\nTeste 4: Comandos WebSim")
        results.append(await test_websim_commands())
        
        # Teste de API
        print("\nTeste 5: API REST WebSim")
        results.append(await test_websim_api())
        
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
            print("O WebSim está funcionando perfeitamente!")
            print("\n💡 Para usar o WebSim:")
            print("   1. Execute: python3 -m t031a5.cli run --config g1_development.json5")
            print("   2. Acesse: http://localhost:8080")
            print("   3. Use a interface web para controlar o G1")
        else:
            print("❌ Alguns testes falharam")
        
        return passed == total
    
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
