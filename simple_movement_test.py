#!/usr/bin/env python3
"""
Teste Simples de Movimento - Diagnóstico
"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from t031a5.unitree.g1_controller import G1Controller, G1Language, G1Emotion

async def test_simple():
    config = {
        "interface": {"interface": "eth0", "timeout": 10.0},
        "default_volume": 100,
        "default_speaker_id": 1
    }
    
    controller = G1Controller(config)
    
    try:
        print("🔧 Inicializando...")
        success = await controller.initialize()
        print(f"Inicialização: {'✅' if success else '❌'}")
        
        if not success:
            print("❌ Falha na inicialização - parando")
            return
        
        print("��️ Testando TTS...")
        await controller.speak("TTS test working", G1Language.ENGLISH)
        await asyncio.sleep(2)
        
        print("🤚 Testando movimento simples (ID 99 - release_arm)...")
        success = await controller.execute_gesture(99, wait_time=2.0)
        print(f"Movimento 99: {'✅' if success else '❌'}")
        
        print("🤚 Testando movimento (ID 32 - right_hand_on_mouth)...")
        success = await controller.execute_gesture(32, wait_time=3.0)
        print(f"Movimento 32: {'✅' if success else '❌'}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await controller.stop()

if __name__ == "__main__":
    asyncio.run(test_simple())
