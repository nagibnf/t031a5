#!/usr/bin/env python3
"""
Descobrir o que cada ID realmente faz no G1
"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from t031a5.unitree.g1_controller import G1Controller, G1Language

async def discover_movements():
    config = {
        "interface": {"interface": "eth0", "timeout": 10.0},
        "default_volume": 100,
        "default_speaker_id": 1
    }
    
    controller = G1Controller(config)
    
    # IDs suspeitos para testar primeiro
    test_ids = [11, 12, 13, 15, 17, 18, 19, 22, 23, 24, 25, 26, 27, 31, 32, 33, 34, 35, 99]
    
    try:
        await controller.initialize()
        
        for movement_id in test_ids:
            print(f"\n🔍 TESTANDO ID {movement_id}")
            
            # Anunciar qual ID vai testar
            await controller.speak(f"Testing I D {movement_id}", G1Language.ENGLISH)
            await asyncio.sleep(2)
            
            # Executar movimento
            print(f"   Executando movimento ID {movement_id}...")
            success = await controller.execute_gesture(movement_id, wait_time=4.0)
            
            # Pedir para descrever o que viu
            await controller.speak("What did you see?", G1Language.ENGLISH)
            await asyncio.sleep(2)
            
            print(f"   ID {movement_id}: {'✅' if success else '❌'}")
            print(f"   👆 DESCREVA O MOVIMENTO QUE VIU PARA ID {movement_id}")
            
            # Pausa para observação
            await asyncio.sleep(3)
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        await controller.stop()

if __name__ == "__main__":
    asyncio.run(discover_movements())
