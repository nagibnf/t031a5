#!/usr/bin/env python3
"""
Verificar estado real do G1
"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def check_g1_status():
    try:
        # Verificar estado via SDK direto
        from unitree_sdk2_python.core.channel import ChannelSubscriber, ChannelFactoryInitialize
        from unitree_sdk2_python.idl.default import unitree_go_msg_dds__LowState_
        from unitree_sdk2_python.idl.unitree_go.msg.dds_ import LowState_
        
        print("🔧 Inicializando canal DDS...")
        ChannelFactoryInitialize(0, "eth0")
        
        print("🔍 Verificando estado do G1...")
        sub = ChannelSubscriber("rt/lowstate", LowState_)
        sub.Init()
        
        # Aguardar alguns estados
        for i in range(5):
            msg = sub.Read()
            if msg[0]:
                state = msg[1]
                print(f"Estado {i+1}: mode={getattr(state, 'mode', 'N/A')}")
                print(f"          motor_state={getattr(state, 'motor_state', 'N/A')}")
                print(f"          foot_force={getattr(state, 'foot_force', 'N/A')}")
                await asyncio.sleep(1)
            else:
                print(f"Estado {i+1}: Sem dados")
                await asyncio.sleep(1)
                
    except Exception as e:
        print(f"❌ Erro ao verificar estado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_g1_status())
