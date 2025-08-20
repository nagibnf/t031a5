#!/usr/bin/env python3
"""
Teste simples de comunicação com G1.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from t031a5.unitree.g1_interface import G1Interface, G1State

async def test_g1_connection():
    """Testa conexão básica com G1."""
    
    print("🔧 Testando comunicação com G1...")
    print("=" * 50)
    
    # Configuração básica
    config = {
        "robot_ip": "192.168.123.161",
        "robot_port": 8080,
        "local_interface": "en11",
        "local_ip": "192.168.123.99",
        "timeout": 10.0,
        "retry_attempts": 3
    }
    
    print(f"📍 IP do G1: {config['robot_ip']}")
    print(f"📍 Interface local: {config['local_interface']} ({config['local_ip']})")
    print(f"⏱️  Timeout: {config['timeout']}s")
    print()
    
    # Testar import do SDK primeiro
    print("🔍 Testando import do SDK...")
    try:
        from unitree_sdk2py import UnitreeSDK2Py
        print("✅ SDK importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar SDK: {e}")
        return
    
    # Criar interface
    g1_interface = G1Interface(config)
    
    try:
        print("\n🔄 Inicializando interface...")
        success = await g1_interface.initialize()
        
        if success:
            print("✅ Interface inicializada com sucesso!")
            print(f"📊 Estado: {g1_interface.state}")
            print(f"🔗 Conectado: {g1_interface.is_connected}")
            
            # Testar sensores
            print("\n📡 Testando sensores...")
            sensors = await g1_interface.get_sensors()
            print(f"✅ Sensores: {sensors}")
            
            # Testar estado
            print("\n🤖 Testando estado do robô...")
            state = await g1_interface.get_robot_state()
            print(f"✅ Estado: {state}")
            
        else:
            print("❌ Falha na inicialização da interface")
            
    except Exception as e:
        print(f"💥 Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n🛑 Parando interface...")
        await g1_interface.stop()
        print("✅ Teste concluído")

if __name__ == "__main__":
    asyncio.run(test_g1_connection())
