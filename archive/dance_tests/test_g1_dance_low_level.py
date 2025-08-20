#!/usr/bin/env python3
"""
Teste de Dança em Baixo Nível: G1 DDS Dance
===========================================

Este teste faz o G1 dançar usando controle de baixo nível DDS,
movendo várias juntas de forma coordenada.
"""

import time
import sys
import numpy as np

from unitree_sdk2py.core.channel import ChannelPublisher, ChannelFactoryInitialize
from unitree_sdk2py.core.channel import ChannelSubscriber, ChannelFactoryInitialize
from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_
from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowState_
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_
from unitree_sdk2py.utils.crc import CRC
from unitree_sdk2py.comm.motion_switcher.motion_switcher_client import MotionSwitcherClient

G1_NUM_MOTOR = 29

# Gains para controle
Kp = [
    60, 60, 60, 100, 40, 40,      # legs
    60, 60, 60, 100, 40, 40,      # legs
    60, 40, 40,                   # waist
    40, 40, 40, 40,  40, 40, 40,  # arms
    40, 40, 40, 40,  40, 40, 40   # arms
]

Kd = [
    1, 1, 1, 2, 1, 1,     # legs
    1, 1, 1, 2, 1, 1,     # legs
    1, 1, 1,              # waist
    1, 1, 1, 1, 1, 1, 1,  # arms
    1, 1, 1, 1, 1, 1, 1   # arms 
]

class G1JointIndex:
    # Waist
    WaistYaw = 12
    
    # Arms
    LeftShoulderPitch = 15
    LeftShoulderRoll = 16
    LeftShoulderYaw = 17
    LeftElbow = 18
    LeftWristRoll = 19
    
    RightShoulderPitch = 22
    RightShoulderRoll = 23
    RightShoulderYaw = 24
    RightElbow = 25
    RightWristRoll = 26

class Mode:
    PR = 0  # Series Control for Pitch/Roll Joints
    AB = 1  # Parallel Control for A/B Joints

class G1DanceLowLevelTest:
    """Teste de dança em baixo nível para G1."""
    
    def __init__(self):
        self.interface = "en11"
        self.time_ = 0.0
        self.control_dt_ = 0.02  # [20ms]
        self.duration_ = 1.0    # [1 s por movimento]
        self.counter_ = 0
        self.mode_pr_ = Mode.PR
        self.mode_machine_ = 0
        self.low_cmd = unitree_hg_msg_dds__LowCmd_()  
        self.low_state = None 
        self.update_mode_machine_ = False
        self.crc = CRC()
        self.done = False
        self.dance_step = 0
        
    def initialize_sdk(self):
        """Inicializa o SDK."""
        try:
            print("🔧 Inicializando SDK...")
            ChannelFactoryInitialize(0, self.interface)
            print("✅ SDK inicializado")
            return True
            
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            return False
    
    def Init(self):
        """Inicializa publishers e subscribers."""
        try:
            print("🔧 Inicializando DDS...")
            
            # Motion Switcher
            self.msc = MotionSwitcherClient()
            self.msc.SetTimeout(5.0)
            self.msc.Init()

            # Verificar modo atual
            status, result = self.msc.CheckMode()
            print(f"📊 Modo atual: {result}")
            
            # Liberar modo se necessário
            while result and result.get('name'):
                print("🔄 Liberando modo atual...")
                self.msc.ReleaseMode()
                status, result = self.msc.CheckMode()
                time.sleep(1)

            # create publisher #
            self.lowcmd_publisher_ = ChannelPublisher("rt/lowcmd", LowCmd_)
            self.lowcmd_publisher_.Init()

            # create subscriber # 
            self.lowstate_subscriber = ChannelSubscriber("rt/lowstate", LowState_)
            self.lowstate_subscriber.Init(self.LowStateHandler, 10)
            
            print("✅ DDS inicializado")
            return True
            
        except Exception as e:
            print(f"❌ Erro na inicialização DDS: {e}")
            return False

    def LowStateHandler(self, msg: LowState_):
        """Handler para estados de baixo nível."""
        self.low_state = msg

        if self.update_mode_machine_ == False:
            self.mode_machine_ = self.low_state.mode_machine
            self.update_mode_machine_ = True
        
        self.counter_ +=1
        if (self.counter_ % 50 == 0) :  # A cada 1 segundo
            self.counter_ = 0
            print(f"📊 IMU RPY: {self.low_state.imu_state.rpy}")

    def LowCmdWrite(self):
        """Escreve comandos de dança."""
        if not self.low_state:
            return
            
        self.time_ += self.control_dt_

        # Configurar todos os motores
        for i in range(G1_NUM_MOTOR):
            self.low_cmd.mode_pr = Mode.PR
            self.low_cmd.mode_machine = self.mode_machine_
            self.low_cmd.motor_cmd[i].mode = 1  # 1:Enable, 0:Disable
            self.low_cmd.motor_cmd[i].tau = 0. 
            self.low_cmd.motor_cmd[i].dq = 0. 
            self.low_cmd.motor_cmd[i].kp = Kp[i] 
            self.low_cmd.motor_cmd[i].kd = Kd[i]
            
            # Manter posição atual para juntas não usadas na dança
            if i not in [G1JointIndex.WaistYaw, 
                        G1JointIndex.LeftShoulderPitch, G1JointIndex.LeftElbow,
                        G1JointIndex.RightShoulderPitch, G1JointIndex.RightElbow]:
                self.low_cmd.motor_cmd[i].q = self.low_state.motor_state[i].q

        # Sequência de dança
        if self.time_ < self.duration_:
            # [Step 1]: Balançar quadril
            print(f"🕺 Step 1: Balançar quadril (t={self.time_:.2f})")
            
            ratio = np.clip(self.time_ / self.duration_, 0.0, 1.0)
            waist_angle = 0.2 * np.sin(2.0 * np.pi * ratio * 2)  # 2 oscilações
            self.low_cmd.motor_cmd[G1JointIndex.WaistYaw].q = waist_angle
            
            # Braços em posição neutra
            self.low_cmd.motor_cmd[G1JointIndex.LeftShoulderPitch].q = 0.0
            self.low_cmd.motor_cmd[G1JointIndex.LeftElbow].q = 0.0
            self.low_cmd.motor_cmd[G1JointIndex.RightShoulderPitch].q = 0.0
            self.low_cmd.motor_cmd[G1JointIndex.RightElbow].q = 0.0

        elif self.time_ < self.duration_ * 2:
            # [Step 2]: Braços para cima
            print(f"🕺 Step 2: Braços para cima (t={self.time_:.2f})")
            
            ratio = np.clip((self.time_ - self.duration_) / self.duration_, 0.0, 1.0)
            
            # Braços subindo
            shoulder_angle = 0.5 * ratio  # ~28 graus
            elbow_angle = 0.3 * ratio     # ~17 graus
            
            self.low_cmd.motor_cmd[G1JointIndex.LeftShoulderPitch].q = shoulder_angle
            self.low_cmd.motor_cmd[G1JointIndex.LeftElbow].q = elbow_angle
            self.low_cmd.motor_cmd[G1JointIndex.RightShoulderPitch].q = shoulder_angle
            self.low_cmd.motor_cmd[G1JointIndex.RightElbow].q = elbow_angle
            
            # Quadril neutro
            self.low_cmd.motor_cmd[G1JointIndex.WaistYaw].q = 0.0

        elif self.time_ < self.duration_ * 3:
            # [Step 3]: Balançar braços
            print(f"🕺 Step 3: Balançar braços (t={self.time_:.2f})")
            
            ratio = np.clip((self.time_ - self.duration_ * 2) / self.duration_, 0.0, 1.0)
            
            # Braços balançando
            shoulder_angle = 0.3 * np.sin(2.0 * np.pi * ratio * 3)  # 3 oscilações
            elbow_angle = 0.2 * np.sin(2.0 * np.pi * ratio * 3 + np.pi/2)  # Fase diferente
            
            self.low_cmd.motor_cmd[G1JointIndex.LeftShoulderPitch].q = shoulder_angle
            self.low_cmd.motor_cmd[G1JointIndex.LeftElbow].q = elbow_angle
            self.low_cmd.motor_cmd[G1JointIndex.RightShoulderPitch].q = -shoulder_angle  # Oposto
            self.low_cmd.motor_cmd[G1JointIndex.RightElbow].q = -elbow_angle
            
            # Quadril neutro
            self.low_cmd.motor_cmd[G1JointIndex.WaistYaw].q = 0.0

        elif self.time_ < self.duration_ * 4:
            # [Step 4]: Dança completa - quadril + braços
            print(f"🕺 Step 4: Dança completa (t={self.time_:.2f})")
            
            ratio = np.clip((self.time_ - self.duration_ * 3) / self.duration_, 0.0, 1.0)
            
            # Quadril balançando
            waist_angle = 0.15 * np.sin(2.0 * np.pi * ratio * 4)  # 4 oscilações
            
            # Braços balançando em fase diferente
            shoulder_angle = 0.25 * np.sin(2.0 * np.pi * ratio * 4 + np.pi/4)
            elbow_angle = 0.15 * np.sin(2.0 * np.pi * ratio * 4 + np.pi/2)
            
            self.low_cmd.motor_cmd[G1JointIndex.WaistYaw].q = waist_angle
            self.low_cmd.motor_cmd[G1JointIndex.LeftShoulderPitch].q = shoulder_angle
            self.low_cmd.motor_cmd[G1JointIndex.LeftElbow].q = elbow_angle
            self.low_cmd.motor_cmd[G1JointIndex.RightShoulderPitch].q = -shoulder_angle
            self.low_cmd.motor_cmd[G1JointIndex.RightElbow].q = -elbow_angle

        elif self.time_ < self.duration_ * 5:
            # [Step 5]: Voltar à posição neutra
            print(f"🕺 Step 5: Voltar ao neutro (t={self.time_:.2f})")
            
            ratio = np.clip((self.time_ - self.duration_ * 4) / self.duration_, 0.0, 1.0)
            
            # Voltar tudo ao centro
            self.low_cmd.motor_cmd[G1JointIndex.WaistYaw].q = 0.0 * (1.0 - ratio)
            self.low_cmd.motor_cmd[G1JointIndex.LeftShoulderPitch].q = 0.0 * (1.0 - ratio)
            self.low_cmd.motor_cmd[G1JointIndex.LeftElbow].q = 0.0 * (1.0 - ratio)
            self.low_cmd.motor_cmd[G1JointIndex.RightShoulderPitch].q = 0.0 * (1.0 - ratio)
            self.low_cmd.motor_cmd[G1JointIndex.RightElbow].q = 0.0 * (1.0 - ratio)

        else:
            # Finalizar
            print(f"🕺 Finalizando dança (t={self.time_:.2f})")
            self.done = True
            return

        # Enviar comando
        self.low_cmd.crc = self.crc.Crc(self.low_cmd)
        self.lowcmd_publisher_.Write(self.low_cmd)

    def run_test(self):
        """Executa o teste de dança."""
        print("🕺 TESTE DE DANÇA EM BAIXO NÍVEL: G1")
        print("=" * 60)
        print("Este teste faz o G1 dançar usando controle DDS")
        print("movendo quadril e braços de forma coordenada.")
        print("=" * 60)
        
        if not self.initialize_sdk():
            return False
        
        if not self.Init():
            return False
        
        # Aguardar primeiro estado
        print("⏳ Aguardando primeiro estado...")
        while self.update_mode_machine_ == False:
            time.sleep(0.1)

        if self.update_mode_machine_ == True:
            print("✅ Primeiro estado recebido, iniciando dança...")
            
            # Loop principal de dança
            while not self.done:
                self.LowCmdWrite()
                time.sleep(self.control_dt_)
            
            print("✅ Dança concluída!")
            return True
        else:
            print("❌ Falha ao receber primeiro estado")
            return False

def main():
    """Função principal."""
    print("🕺 TESTE DE DANÇA EM BAIXO NÍVEL: G1")
    print("=" * 60)
    print("⚠️  ATENÇÃO: Este teste faz o G1 dançar!")
    print("⚠️  Pressione Ctrl+C para interromper a qualquer momento!")
    print("=" * 60)
    
    # Confirmação do usuário
    try:
        response = input("\n🤔 Deseja fazer o G1 dançar? (s/N): ").lower()
        if response not in ['s', 'sim', 'y', 'yes']:
            print("❌ Teste cancelado pelo usuário")
            return
    except KeyboardInterrupt:
        print("\n❌ Teste cancelado")
        return
    
    # Executar teste
    tester = G1DanceLowLevelTest()
    success = tester.run_test()
    
    if success:
        print("\n🎉 DANÇA CONCLUÍDA!")
        print("📋 O G1 dançou usando controle de baixo nível!")
    else:
        print("\n❌ Teste falhou ou foi interrompido")

if __name__ == "__main__":
    main()
