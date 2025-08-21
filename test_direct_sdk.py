#!/usr/bin/env python3
"""
Teste direto com SDK Unitree - bypassing nossa abstração
"""
import time
import sys
sys.path.append('/home/unitree/t031a5/unitree_sdk2_python')

from unitree_sdk2_python.core.channel import ChannelPublisher, ChannelFactoryInitialize
from unitree_sdk2_python.idl.default import unitree_go_msg_dds__SportModeCmd_
from unitree_sdk2_python.idl.unitree_go.msg.dds_ import SportModeCmd_

def test_direct_movement():
    print("🔧 Inicializando canal direto...")
    
    try:
        # Inicializar com interface eth0
        ChannelFactoryInitialize(0, "eth0")
        
        # Criar publisher para comandos
        pub = ChannelPublisher("rt/sportmodeCmd", SportModeCmd_)
        pub.Init()
        
        print("✅ Canal inicializado")
        
        # Criar comando para movimento
        cmd = SportModeCmd_()
        
        # Teste comando básico - ID 32
        print("🤚 Enviando comando de movimento ID 32...")
        cmd.mode = 1  # Sport mode
        cmd.gait_type = 0
        cmd.speed_level = 0
        cmd.foot_raise_height = 0.08
        cmd.body_height = 0.0
        cmd.position = [0, 0]
        cmd.euler = [0, 0, 0]
        cmd.velocity = [0, 0]
        cmd.yaw_speed = 0.0
        cmd.bms_cmd = 0
        cmd.path_point = []
        
        # Enviar comando
        for i in range(10):
            pub.Write(cmd)
            print(f"  Comando enviado {i+1}/10")
            time.sleep(0.1)
        
        print("✅ Comandos enviados")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_sdk()
