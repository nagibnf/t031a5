#!/usr/bin/env python3
"""
Teste Baixo Nível: WAIST_YAW (ID 12) - DDS Control
==================================================

Este teste usa controle de baixo nível DDS para controlar
especificamente a junta WAIST_YAW (ID 12) do G1.
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
from unitree_sdk2py.utils.thread import RecurrentThread
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
    WaistRoll = 13        # NOTE: INVALID for g1 23dof/29dof with waist locked
    WaistPitch = 14       # NOTE: INVALID for g1 23dof/29dof with waist locked

class Mode:
    PR = 0  # Series Control for Pitch/Roll Joints
    AB = 1  # Parallel Control for A/B Joints

class G1WaistYawLowLevelTest:
    """Teste de baixo nível para WAIST_YAW."""
    
    def __init__(self):
        self.interface = "en11"
        self.time_ = 0.0
        self.control_dt_ = 0.002  # [2ms]
        self.duration_ = 2.0    # [2 s]
        self.counter_ = 0
        self.mode_pr_ = Mode.PR
        self.mode_machine_ = 0
        self.low_cmd = unitree_hg_msg_dds__LowCmd_()  
        self.low_state = None 
        self.update_mode_machine_ = False
        self.crc = CRC()
        self.done = False
        
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

    def Start(self):
        """Inicia o controle."""
        print("🚀 Iniciando controle...")
        
        self.lowCmdWriteThreadPtr = RecurrentThread(
            interval=self.control_dt_, target=self.LowCmdWrite, name="control"
        )
        
        # Aguardar primeiro estado
        while self.update_mode_machine_ == False:
            print("⏳ Aguardando primeiro estado...")
            time.sleep(1)

        if self.update_mode_machine_ == True:
            print("✅ Primeiro estado recebido, iniciando controle...")
            self.lowCmdWriteThreadPtr.Start()
            return True
        else:
            print("❌ Falha ao receber primeiro estado")
            return False

    def LowStateHandler(self, msg: LowState_):
        """Handler para estados de baixo nível."""
        self.low_state = msg

        if self.update_mode_machine_ == False:
            self.mode_machine_ = self.low_state.mode_machine
            self.update_mode_machine_ = True
        
        self.counter_ +=1
        if (self.counter_ % 500 == 0) :
            self.counter_ = 0
            print(f"📊 IMU RPY: {self.low_state.imu_state.rpy}")

    def LowCmdWrite(self):
        """Escreve comandos de baixo nível."""
        self.time_ += self.control_dt_

        if self.time_ < self.duration_ :
            # [Stage 1]: Mover WAIST_YAW para direita
            print(f"🔄 Stage 1: WAIST_YAW direita (t={self.time_:.2f})")
            
            # Configurar todos os motores
            for i in range(G1_NUM_MOTOR):
                self.low_cmd.mode_pr = Mode.PR
                self.low_cmd.mode_machine = self.mode_machine_
                self.low_cmd.motor_cmd[i].mode = 1  # 1:Enable, 0:Disable
                self.low_cmd.motor_cmd[i].tau = 0. 
                self.low_cmd.motor_cmd[i].dq = 0. 
                self.low_cmd.motor_cmd[i].kp = Kp[i] 
                self.low_cmd.motor_cmd[i].kd = Kd[i]
                
                # Manter posição atual para todos exceto WAIST_YAW
                if i != G1JointIndex.WaistYaw:
                    self.low_cmd.motor_cmd[i].q = self.low_state.motor_state[i].q
                else:
                    # Mover WAIST_YAW para direita
                    ratio = np.clip(self.time_ / self.duration_, 0.0, 1.0)
                    target_angle = 0.3  # ~17 graus para direita
                    current_angle = self.low_state.motor_state[i].q
                    self.low_cmd.motor_cmd[i].q = current_angle + ratio * target_angle

        elif self.time_ < self.duration_ * 2 :
            # [Stage 2]: Mover WAIST_YAW para esquerda
            print(f"🔄 Stage 2: WAIST_YAW esquerda (t={self.time_:.2f})")
            
            for i in range(G1_NUM_MOTOR):
                self.low_cmd.mode_pr = Mode.PR
                self.low_cmd.mode_machine = self.mode_machine_
                self.low_cmd.motor_cmd[i].mode = 1
                self.low_cmd.motor_cmd[i].tau = 0. 
                self.low_cmd.motor_cmd[i].dq = 0. 
                self.low_cmd.motor_cmd[i].kp = Kp[i] 
                self.low_cmd.motor_cmd[i].kd = Kd[i]
                
                if i != G1JointIndex.WaistYaw:
                    self.low_cmd.motor_cmd[i].q = self.low_state.motor_state[i].q
                else:
                    # Mover WAIST_YAW para esquerda
                    ratio = np.clip((self.time_ - self.duration_) / self.duration_, 0.0, 1.0)
                    target_angle = -0.3  # ~17 graus para esquerda
                    current_angle = self.low_state.motor_state[i].q
                    self.low_cmd.motor_cmd[i].q = current_angle + ratio * target_angle

        elif self.time_ < self.duration_ * 3 :
            # [Stage 3]: Voltar WAIST_YAW ao centro
            print(f"🔄 Stage 3: WAIST_YAW centro (t={self.time_:.2f})")
            
            for i in range(G1_NUM_MOTOR):
                self.low_cmd.mode_pr = Mode.PR
                self.low_cmd.mode_machine = self.mode_machine_
                self.low_cmd.motor_cmd[i].mode = 1
                self.low_cmd.motor_cmd[i].tau = 0. 
                self.low_cmd.motor_cmd[i].dq = 0. 
                self.low_cmd.motor_cmd[i].kp = Kp[i] 
                self.low_cmd.motor_cmd[i].kd = Kd[i]
                
                if i != G1JointIndex.WaistYaw:
                    self.low_cmd.motor_cmd[i].q = self.low_state.motor_state[i].q
                else:
                    # Voltar WAIST_YAW ao centro
                    ratio = np.clip((self.time_ - self.duration_ * 2) / self.duration_, 0.0, 1.0)
                    target_angle = 0.0  # Centro
                    current_angle = self.low_state.motor_state[i].q
                    self.low_cmd.motor_cmd[i].q = current_angle + ratio * (target_angle - current_angle)

        else:
            # [Stage 4]: Finalizar
            print(f"🔄 Stage 4: Finalizando (t={self.time_:.2f})")
            self.done = True
            return

        # Enviar comando
        self.low_cmd.crc = self.crc.Crc(self.low_cmd)
        self.lowcmd_publisher_.Write(self.low_cmd)

    def run_test(self):
        """Executa o teste completo."""
        print("🦴 TESTE BAIXO NÍVEL: WAIST_YAW")
        print("=" * 60)
        print("Este teste usa controle DDS de baixo nível")
        print("para controlar especificamente a junta WAIST_YAW.")
        print("=" * 60)
        
        if not self.initialize_sdk():
            return False
        
        if not self.Init():
            return False
        
        if not self.Start():
            return False
        
        # Aguardar conclusão
        print("⏳ Aguardando conclusão do teste...")
        while not self.done:
            time.sleep(0.1)
        
        print("✅ Teste concluído!")
        return True

def main():
    """Função principal."""
    print("🦴 TESTE BAIXO NÍVEL: WAIST_YAW")
    print("=" * 60)
    print("⚠️  ATENÇÃO: Este teste usa controle de baixo nível!")
    print("⚠️  Pressione Ctrl+C para interromper a qualquer momento!")
    print("=" * 60)
    
    # Confirmação do usuário
    try:
        response = input("\n🤔 Deseja testar WAIST_YAW em baixo nível? (s/N): ").lower()
        if response not in ['s', 'sim', 'y', 'yes']:
            print("❌ Teste cancelado pelo usuário")
            return
    except KeyboardInterrupt:
        print("\n❌ Teste cancelado")
        return
    
    # Executar teste
    tester = G1WaistYawLowLevelTest()
    success = tester.run_test()
    
    if success:
        print("\n🎉 TESTE BAIXO NÍVEL CONCLUÍDO!")
        print("📋 Agora sabemos se é possível controlar WAIST_YAW em baixo nível!")
    else:
        print("\n❌ Teste falhou ou foi interrompido")

if __name__ == "__main__":
    main()
