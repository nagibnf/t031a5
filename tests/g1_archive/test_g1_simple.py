#!/usr/bin/env python3
"""
Teste simples de comunicação com G1 usando SDK oficial.
"""

import time
import sys
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_g1_sdk():
    """Testa conexão básica com G1 usando SDK oficial."""
    
    print("🔧 Testando SDK G1...")
    print("=" * 50)
    
    try:
        # Testar imports básicos
        print("🔍 Testando imports...")
        
        from unitree_sdk2py.core.channel import ChannelFactoryInitialize
        print("✅ ChannelFactoryInitialize importado")
        
        from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_
        print("✅ LowState_ importado")
        
        from unitree_sdk2py.comm.motion_switcher.motion_switcher_client import MotionSwitcherClient
        print("✅ MotionSwitcherClient importado")
        
        # Inicializar factory
        print("\n🔄 Inicializando factory...")
        ChannelFactoryInitialize()
        print("✅ Factory inicializada")
        
        # Testar MotionSwitcherClient
        print("\n🤖 Testando MotionSwitcherClient...")
        msc = MotionSwitcherClient()
        msc.SetTimeout(5.0)
        msc.Init()
        print("✅ MotionSwitcherClient inicializado")
        
        # Verificar modo
        print("\n📊 Verificando modo atual...")
        status, result = msc.CheckMode()
        print(f"Status: {status}")
        print(f"Result: {result}")
        
        if result and result.get('name'):
            print(f"⚠️  Modo atual: {result['name']}")
            print("🔄 Liberando modo...")
            msc.ReleaseMode()
            time.sleep(1)
            
            status, result = msc.CheckMode()
            print(f"Status após liberação: {status}")
            print(f"Result após liberação: {result}")
        elif status == 3102:
            print("⚠️  Erro de comunicação com G1")
            print("💡 Possíveis causas:")
            print("   - G1 não está ligado")
            print("   - G1 não está no modo correto")
            print("   - Problema de rede")
            print("   - G1 precisa ser inicializado")
        else:
            print("✅ Nenhum modo ativo")
        
        print("\n✅ Teste do SDK concluído com sucesso!")
        
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        import traceback
        traceback.print_exc()
        
    except Exception as e:
        print(f"💥 Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_g1_sdk()
