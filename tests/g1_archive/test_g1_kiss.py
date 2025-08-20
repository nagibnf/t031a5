#!/usr/bin/env python3
"""
Teste para enviar comando de beijo para G1.
"""

import time
import sys
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_g1_kiss():
    """Testa envio de comando de beijo para G1."""
    
    print("💋 Enviando beijo para G1...")
    print("=" * 50)
    
    try:
        # Testar imports básicos
        print("🔍 Inicializando SDK...")
        
        from unitree_sdk2py.core.channel import ChannelFactoryInitialize
        from unitree_sdk2py.comm.motion_switcher.motion_switcher_client import MotionSwitcherClient
        
        print("✅ SDK importado")
        
        # Configuração básica
        config = {
            "robot_ip": "192.168.123.161",
            "robot_port": 8080,  # Voltando para porta padrão
            "local_interface": "en11",  # Interface correta (equivalente ao eth0)
            "local_ip": "192.168.123.99",
            "timeout": 10.0,
            "retry_attempts": 3
        }
        
        print(f"📍 IP do G1: {config['robot_ip']}")
        print(f"📍 Interface local: {config['local_interface']} ({config['local_ip']})")
        print(f"⏱️  Timeout: {config['timeout']}s")
        print()
        
        # Inicializar factory
        print("\n🔄 Inicializando factory...")
        ChannelFactoryInitialize(0, "en11")  # Usando interface en11
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
        
        if status == 3102:
            print("⚠️  Erro de comunicação - tentando continuar...")
        elif result and result.get('name'):
            print(f"✅ Modo atual: {result['name']}")
        
        # Listar métodos disponíveis
        print("\n🔍 Listando métodos disponíveis...")
        print("Métodos do MotionSwitcherClient:")
        methods = []
        for method in dir(msc):
            if not method.startswith('_'):
                methods.append(method)
                print(f"  - {method}")
        
        # Tentar enviar comando de beijo
        print("\n💋 Tentando enviar beijo...")
        
        # Tentar diferentes comandos baseados nos métodos disponíveis
        kiss_commands = [
            "kiss",
            "Kiss", 
            "KISS",
            "beijo",
            "Beijo",
            "kiss_action",
            "gesture_kiss",
            "gesture",
            "action"
        ]
        
        for cmd in kiss_commands:
            try:
                print(f"🎯 Tentando comando: {cmd}")
                
                # Tentar diferentes métodos
                if hasattr(msc, 'SendCommand'):
                    result = msc.SendCommand(cmd)
                    print(f"✅ Comando {cmd} enviado via SendCommand: {result}")
                    break
                elif hasattr(msc, 'SendGesture'):
                    result = msc.SendGesture(cmd)
                    print(f"✅ Comando {cmd} enviado via SendGesture: {result}")
                    break
                elif hasattr(msc, 'SendAction'):
                    result = msc.SendAction(cmd)
                    print(f"✅ Comando {cmd} enviado via SendAction: {result}")
                    break
                else:
                    print(f"❌ Nenhum método de envio encontrado")
                    break
                    
            except Exception as e:
                print(f"❌ Comando {cmd} falhou: {e}")
                continue
        
        # Tentar métodos específicos se disponíveis
        print("\n🔧 Tentando métodos específicos...")
        
        if 'SelectMode' in methods:
            try:
                print("🎯 Tentando SelectMode com 'kiss'...")
                result = msc.SelectMode("kiss")
                print(f"✅ SelectMode kiss: {result}")
            except Exception as e:
                print(f"❌ SelectMode kiss falhou: {e}")
            
            try:
                print("🎯 Tentando SelectMode com 'gesture'...")
                result = msc.SelectMode("gesture")
                print(f"✅ SelectMode gesture: {result}")
            except Exception as e:
                print(f"❌ SelectMode gesture falhou: {e}")
            
            try:
                print("🎯 Tentando SelectMode com 'action'...")
                result = msc.SelectMode("action")
                print(f"✅ SelectMode action: {result}")
            except Exception as e:
                print(f"❌ SelectMode action falhou: {e}")
        
        if 'RequestMode' in methods:
            try:
                print("🎯 Tentando RequestMode...")
                result = msc.RequestMode("kiss")
                print(f"✅ RequestMode kiss: {result}")
            except Exception as e:
                print(f"❌ RequestMode falhou: {e}")
        
        if 'ReleaseMode' in methods:
            try:
                print("🎯 Tentando ReleaseMode...")
                result = msc.ReleaseMode()
                print(f"✅ ReleaseMode: {result}")
            except Exception as e:
                print(f"❌ ReleaseMode falhou: {e}")
        
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
    test_g1_kiss()
