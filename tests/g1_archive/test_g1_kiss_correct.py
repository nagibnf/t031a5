#!/usr/bin/env python3
"""
Teste para enviar comando de beijo correto para G1.
"""

import time
import sys
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_g1_kiss_correct():
    """Testa envio de comando de beijo correto para G1."""
    
    print("💋 Enviando beijo correto para G1...")
    print("=" * 50)
    
    try:
        # Testar imports básicos
        print("🔍 Inicializando SDK...")
        
        from unitree_sdk2py.core.channel import ChannelFactoryInitialize
        from unitree_sdk2py.comm.motion_switcher.motion_switcher_client import MotionSwitcherClient
        
        print("✅ SDK importado")
        
        # Inicializar factory com interface correta
        print("\n🔄 Inicializando factory...")
        ChannelFactoryInitialize(0, "en11")  # Interface en11
        print("✅ Factory inicializada")
        
        # Testar MotionSwitcherClient
        print("\n🤖 Conectando com G1...")
        msc = MotionSwitcherClient()
        msc.SetTimeout(5.0)
        msc.Init()
        print("✅ MotionSwitcherClient inicializado")
        
        # Verificar modo
        print("\n📊 Verificando modo atual...")
        status, result = msc.CheckMode()
        print(f"Status: {status}")
        print(f"Result: {result}")
        
        if status == 0 and result and result.get('name'):
            print(f"✅ Modo atual: {result['name']}")
        else:
            print("⚠️  Modo não detectado - tentando continuar...")
        
        # Tentar enviar comando de beijo usando SelectMode
        print("\n💋 Tentando enviar beijo...")
        
        # Comandos de beijo descobertos
        kiss_commands = [
            "left kiss",      # ID 7
            "right kiss",     # ID 14  
            "two-hand kiss",  # ID 15
            "kiss",           # Genérico
            "heart",          # ID 8 (alternativa)
        ]
        
        for cmd in kiss_commands:
            try:
                print(f"🎯 Tentando comando: '{cmd}'")
                result = msc.SelectMode(cmd)
                print(f"✅ Comando '{cmd}' enviado: {result}")
                
                # Aguardar um pouco para ver se o G1 se mexe
                print("⏳ Aguardando 3 segundos...")
                time.sleep(3)
                
            except Exception as e:
                print(f"❌ Comando '{cmd}' falhou: {e}")
                continue
        
        print("\n✅ Teste de beijo concluído!")
        
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        import traceback
        traceback.print_exc()
        
    except Exception as e:
        print(f"💥 Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_g1_kiss_correct()
