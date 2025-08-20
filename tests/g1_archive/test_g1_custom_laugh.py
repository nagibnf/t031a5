#!/usr/bin/env python3
"""
Movimento Personalizado G1 - Riso
Combina movimento "mão direita na boca" com movimento do cotovelo para simular riso.
Baseado no exemplo g1_arm5_sdk_dds_example.py
"""

import time
import sys
import numpy as np
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Imports do SDK
from unitree_sdk2py.core.channel import ChannelPublisher, ChannelFactoryInitialize
from unitree_sdk2py.core.channel import ChannelSubscriber
from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_
from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowState_
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_
from unitree_sdk2py.utils.crc import CRC
# from unitree_sdk2py.utils.thread import RecurrentThread  # Não funciona no macOS
from unitree_sdk2py.g1.arm.g1_arm_action_client import G1ArmActionClient

kPi = 3.141592654
kPi_2 = 1.57079632

class G1JointIndex:
    # Right arm
    RightShoulderPitch = 22
    RightShoulderRoll = 23
    RightShoulderYaw = 24
    RightElbow = 25
    RightWristRoll = 26
    RightWristPitch = 27  # NOTE: INVALID for g1 23dof
    RightWristYaw = 28    # NOTE: INVALID for g1 23dof
    
    kNotUsedJoint = 29 # NOTE: Weight

class G1LaughController:
    """Controlador para movimento de riso personalizado."""
    
    def __init__(self):
        self.interface = "en11"
        
        # Parâmetros de controle
        self.time_ = 0.0
        self.control_dt_ = 0.02  # 50Hz
        self.duration_stage = 1.0  # Duração de cada estágio
        self.counter_ = 0
        self.kp = 60.0
        self.kd = 1.5
        
        # Estados do sistema
        self.low_cmd = unitree_hg_msg_dds__LowCmd_()
        self.low_state = None
        self.first_update_low_state = False
        self.crc = CRC()
        self.done = False
        self.stage = 0
        
        # Cliente para arm actions
        self.arm_client = None
        
        # Posições para o movimento de riso
        # Baseado na posição "mão direita na boca" + movimento do cotovelo
        self.right_elbow_base = -0.8  # Posição base do cotovelo (flexionado)
        self.right_elbow_laugh = -0.6  # Posição do cotovelo durante riso (menos flexionado)
        
        # Juntas que vamos controlar
        self.controlled_joints = [G1JointIndex.RightElbow]
    
    def initialize_sdk(self):
        """Inicializa o SDK."""
        try:
            print("🔧 Inicializando SDK...")
            ChannelFactoryInitialize(0, self.interface)
            print("✅ SDK inicializado")
            
            # Inicializar ArmActionClient
            self.arm_client = G1ArmActionClient()
            self.arm_client.SetTimeout(5.0)
            self.arm_client.Init()
            print("✅ ArmActionClient inicializado")
            
            return True
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            return False
    
    def setup_main_operation_control(self):
        """Configura o robô para Main Operation Control."""
        try:
            from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient
            
            loco_client = LocoClient()
            loco_client.SetTimeout(5.0)
            loco_client.Init()
            
            print("🚀 Configurando Main Operation Control...")
            
            # Zero Torque → Damping → Get Ready
            print("1️⃣ Zero Torque...")
            loco_client.SetFsmId(0)
            time.sleep(2)
            
            print("2️⃣ Damping...")
            loco_client.SetFsmId(1)
            time.sleep(2)
            
            print("3️⃣ Get Ready...")
            loco_client.SetFsmId(4)
            time.sleep(3)
            
            print("4️⃣ Use R1+X no controle físico para Main Operation Control")
            input("Pressione Enter após R1+X...")
            
            return True
        except Exception as e:
            print(f"❌ Erro ao configurar estado: {e}")
            return False
    
    def execute_base_movement(self):
        """Executa o movimento base (mão direita na boca)."""
        try:
            print("🤚 Executando movimento base: mão direita na boca...")
            result = self.arm_client.ExecuteAction(32)  # right_hand_on_mouth
            
            if result == 0:
                print("✅ Movimento base executado com sucesso!")
                time.sleep(3)  # Aguardar execução
                return True
            else:
                print(f"❌ Movimento base falhou (Status: {result})")
                return False
        except Exception as e:
            print(f"❌ Erro no movimento base: {e}")
            return False
    
    def init_low_level_control(self):
        """Inicializa controle de baixo nível."""
        try:
            # Criar publisher para comandos
            self.arm_sdk_publisher = ChannelPublisher("rt/arm_sdk", LowCmd_)
            self.arm_sdk_publisher.Init()
            
            # Criar subscriber para estado
            self.lowstate_subscriber = ChannelSubscriber("rt/lowstate", LowState_)
            self.lowstate_subscriber.Init(self.low_state_handler, 10)
            
            print("✅ Controle de baixo nível inicializado")
            return True
        except Exception as e:
            print(f"❌ Erro no controle de baixo nível: {e}")
            return False
    
    def low_state_handler(self, msg: LowState_):
        """Handler para mensagens de estado."""
        self.low_state = msg
        if not self.first_update_low_state:
            self.first_update_low_state = True
    
    def start_laugh_control(self):
        """Inicia o controle do movimento de riso."""
        # Aguardar primeiro estado
        while not self.first_update_low_state:
            time.sleep(0.1)
        
        print("😂 Iniciando movimento de riso...")
        
        # Loop de controle simples (sem thread no macOS)
        while not self.done:
            self.laugh_control_loop()
            time.sleep(self.control_dt_)
    
    def laugh_control_loop(self):
        """Loop principal de controle do riso."""
        self.time_ += self.control_dt_
        
        # Habilitar arm_sdk
        self.low_cmd.motor_cmd[G1JointIndex.kNotUsedJoint].q = 1
        
        if self.time_ < self.duration_stage * 5:  # 5 segundos de riso
            # Movimento oscilatório do cotovelo para simular riso
            freq = 3.0  # Frequência do riso (3 Hz)
            amplitude = 0.2  # Amplitude do movimento
            
            # Posição oscilatória
            oscillation = amplitude * np.sin(2 * np.pi * freq * self.time_)
            target_elbow = self.right_elbow_base + oscillation
            
            # Aplicar comando ao cotovelo direito
            joint = G1JointIndex.RightElbow
            if self.low_state:
                self.low_cmd.motor_cmd[joint].tau = 0.0
                self.low_cmd.motor_cmd[joint].q = target_elbow
                self.low_cmd.motor_cmd[joint].dq = 0.0
                self.low_cmd.motor_cmd[joint].kp = self.kp
                self.low_cmd.motor_cmd[joint].kd = self.kd
            
            # Debug info
            if int(self.time_ * 10) % 10 == 0:  # A cada 0.1s
                print(f"😂 Rindo... Cotovelo: {target_elbow:.3f} rad")
        
        elif self.time_ < self.duration_stage * 6:  # Retornar ao estado inicial
            # Voltar suavemente ao estado inicial
            ratio = (self.time_ - self.duration_stage * 5) / self.duration_stage
            ratio = np.clip(ratio, 0.0, 1.0)
            
            joint = G1JointIndex.RightElbow
            if self.low_state:
                initial_pos = self.low_state.motor_state[joint].q
                self.low_cmd.motor_cmd[joint].tau = 0.0
                self.low_cmd.motor_cmd[joint].q = (1.0 - ratio) * self.right_elbow_base + ratio * initial_pos
                self.low_cmd.motor_cmd[joint].dq = 0.0
                self.low_cmd.motor_cmd[joint].kp = self.kp
                self.low_cmd.motor_cmd[joint].kd = self.kd
            
            print("🔄 Retornando ao estado inicial...")
        
        elif self.time_ < self.duration_stage * 7:  # Desabilitar arm_sdk
            ratio = (self.time_ - self.duration_stage * 6) / self.duration_stage
            self.low_cmd.motor_cmd[G1JointIndex.kNotUsedJoint].q = 1.0 - ratio
            print("📴 Desabilitando arm_sdk...")
        
        else:
            # Finalizar
            self.done = True
            print("✅ Movimento de riso concluído!")
        
        # Enviar comando
        self.low_cmd.crc = self.crc.Crc(self.low_cmd)
        self.arm_sdk_publisher.Write(self.low_cmd)
    
    def run_laugh_sequence(self):
        """Executa a sequência completa de riso."""
        print("😂 G1 MOVIMENTO PERSONALIZADO - RISO")
        print("=" * 50)
        
        # 1. Configurar Main Operation Control
        if not self.setup_main_operation_control():
            return False
        
        # 2. Executar movimento base (mão na boca)
        if not self.execute_base_movement():
            return False
        
        # 3. Inicializar controle de baixo nível
        if not self.init_low_level_control():
            return False
        
        # 4. Iniciar movimento de riso
        self.start_laugh_control()
        
        # 5. Aguardar conclusão (já acontece no start_laugh_control)
        
        # 6. Voltar ao estado inicial dos braços
        print("🔄 Voltando ao estado inicial dos braços...")
        self.arm_client.ExecuteAction(99)  # release_arm
        time.sleep(2)
        
        print("🎉 Sequência de riso concluída com sucesso!")
        return True

def main():
    """Função principal."""
    print("😂 G1 MOVIMENTO PERSONALIZADO - RISO")
    print("=" * 50)
    print("🎯 OBJETIVO: Combinar 'mão direita na boca' com movimento de cotovelo")
    print("⚠️  AVISO: Certifique-se de que não há obstáculos ao redor do robô")
    
    # Confirmação de segurança
    response = input("Deseja continuar? (s/n): ").strip().lower()
    if response not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada")
        return
    
    # Criar controlador
    controller = G1LaughController()
    
    # Inicializar SDK
    if not controller.initialize_sdk():
        print("❌ Falha na inicialização do SDK")
        return
    
    # Executar sequência
    controller.run_laugh_sequence()

if __name__ == "__main__":
    main()
