#!/usr/bin/env python3
"""
Movimento Completo G1 - Riso Construído do Zero
Posiciona o braço direito na posição "mão na boca" e adiciona movimento de riso.
Controle completo de baixo nível para todas as juntas do braço direito.
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

class G1CompleteLaughController:
    """Controlador completo para movimento de riso construído do zero."""
    
    def __init__(self):
        self.interface = "en11"
        
        # Parâmetros de controle
        self.time_ = 0.0
        self.control_dt_ = 0.02  # 50Hz
        self.duration_stage = 2.0  # Duração de cada estágio
        self.kp = 60.0
        self.kd = 1.5
        
        # Estados do sistema
        self.low_cmd = unitree_hg_msg_dds__LowCmd_()
        self.low_state = None
        self.first_update_low_state = False
        self.crc = CRC()
        self.done = False
        self.stage = 0
        
        # Posições para o movimento "mão na boca" + riso
        # Baseado na análise do movimento ID 32 - POSIÇÕES CORRIGIDAS
        self.right_arm_positions = {
            G1JointIndex.RightShoulderPitch: 0.5,   # Ombro para frente (corrigido)
            G1JointIndex.RightShoulderRoll: 0.3,    # Ombro para fora (corrigido)
            G1JointIndex.RightShoulderYaw: 0.0,     # Ombro neutro
            G1JointIndex.RightElbow: -1.2,          # Cotovelo flexionado (corrigido)
            G1JointIndex.RightWristRoll: 0.0        # Pulso neutro
        }
        
        # Posição relaxada (estado inicial) - MANTENDO POSIÇÕES ATUAIS
        self.relaxed_positions = None  # Será definido dinamicamente
        
        # Juntas que vamos controlar (APENAS braço direito)
        self.controlled_joints = [
            G1JointIndex.RightShoulderPitch,
            G1JointIndex.RightShoulderRoll, 
            G1JointIndex.RightShoulderYaw,
            G1JointIndex.RightElbow,
            G1JointIndex.RightWristRoll
        ]
    
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
    
    def check_current_state(self):
        """Verifica o estado atual do robô."""
        try:
            from unitree_sdk2py.comm.motion_switcher.motion_switcher_client import MotionSwitcherClient
            
            motion_switcher = MotionSwitcherClient()
            motion_switcher.SetTimeout(5.0)
            motion_switcher.Init()
            
            status, result = motion_switcher.CheckMode()
            print(f"📊 Status atual: {status}")
            
            if result:
                print(f"📊 Modo atual: {result}")
                # Verificar se já está em Main Operation Control
                if isinstance(result, dict) and result.get('name') == 'ai':
                    print("✅ Robô já está em Main Operation Control!")
                    return True
                else:
                    print(f"⚠️  Robô está em modo: {result}")
                    return False
            else:
                print("❌ Não foi possível verificar o modo atual")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao verificar estado: {e}")
            return False
    
    def setup_main_operation_control(self):
        """Configura o robô para Main Operation Control se necessário."""
        try:
            # Primeiro verificar se já está no estado correto
            if self.check_current_state():
                print("✅ Robô já está pronto para comandos de braço!")
                return True
            
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
            
            # Verificar novamente se chegou ao estado correto
            if self.check_current_state():
                print("✅ Robô configurado com sucesso!")
                return True
            else:
                print("⚠️  Robô pode não estar no estado correto, mas continuando...")
                return True
            
        except Exception as e:
            print(f"❌ Erro ao configurar estado: {e}")
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
    
    def get_current_positions(self):
        """Obtém posições atuais das juntas."""
        if not self.low_state:
            return None
        
        current_pos = {}
        for joint in self.controlled_joints:
            current_pos[joint] = self.low_state.motor_state[joint].q
        
        return current_pos
    
    def interpolate_position(self, start_pos, end_pos, ratio):
        """Interpola entre duas posições."""
        return (1.0 - ratio) * start_pos + ratio * end_pos
    
    def apply_joint_command(self, joint, target_pos):
        """Aplica comando para uma junta específica."""
        if self.low_state:
            self.low_cmd.motor_cmd[joint].tau = 0.0
            self.low_cmd.motor_cmd[joint].q = target_pos
            self.low_cmd.motor_cmd[joint].dq = 0.0
            self.low_cmd.motor_cmd[joint].kp = self.kp
            self.low_cmd.motor_cmd[joint].kd = self.kd
    
    def apply_all_joints_safe(self, target_positions):
        """Aplica comandos para todas as juntas de forma segura."""
        if not self.low_state:
            return
        
        # Aplicar apenas para as juntas controladas (braço direito)
        for joint in self.controlled_joints:
            if joint in target_positions:
                self.apply_joint_command(joint, target_positions[joint])
        
        # Manter outras juntas em suas posições atuais (não afetar braço esquerdo)
        for i in range(len(self.low_cmd.motor_cmd)):
            if i not in self.controlled_joints:
                # Manter posição atual para juntas não controladas
                self.low_cmd.motor_cmd[i].tau = 0.0
                self.low_cmd.motor_cmd[i].q = self.low_state.motor_state[i].q
                self.low_cmd.motor_cmd[i].dq = 0.0
                self.low_cmd.motor_cmd[i].kp = 0.0  # Sem controle ativo
                self.low_cmd.motor_cmd[i].kd = 0.0
    
    def ensure_arm_relaxed(self):
        """Garante que o braço direito esteja relaxado antes de iniciar movimento."""
        print("🔄 Verificando e relaxando braço direito...")
        
        # Posições relaxadas ideais para o braço direito
        ideal_relaxed = {
            G1JointIndex.RightShoulderPitch: 0.0,
            G1JointIndex.RightShoulderRoll: 0.0,
            G1JointIndex.RightShoulderYaw: 0.0,
            G1JointIndex.RightElbow: 0.0,
            G1JointIndex.RightWristRoll: 0.0
        }
        
        current_pos = self.get_current_positions()
        if not current_pos:
            print("❌ Não foi possível obter posições atuais")
            return False
        
        print(f"📊 Posições atuais: {current_pos}")
        
        # Verificar se o braço já está relaxado (tolerância de 0.1 rad)
        tolerance = 0.1
        arm_is_relaxed = True
        
        for joint in self.controlled_joints:
            diff = abs(current_pos[joint] - ideal_relaxed[joint])
            if diff > tolerance:
                arm_is_relaxed = False
                print(f"⚠️  Junta {joint} não relaxada: {current_pos[joint]:.3f} rad (deve ser ~{ideal_relaxed[joint]:.3f})")
        
        if arm_is_relaxed:
            print("✅ Braço direito já está relaxado!")
            self.relaxed_positions = current_pos.copy()
            return True
        
        # Relaxar o braço gradualmente
        print("🔄 Relaxando braço direito...")
        
        # Tempo para relaxamento
        relax_time = 3.0  # 3 segundos
        start_time = 0.0
        
        while start_time < relax_time:
            start_time += self.control_dt_
            ratio = np.clip(start_time / relax_time, 0.0, 1.0)
            
            # Habilitar arm_sdk
            self.low_cmd.motor_cmd[G1JointIndex.kNotUsedJoint].q = 1
            
            # Interpolar para posições relaxadas
            target_positions = {}
            for joint in self.controlled_joints:
                start_pos = current_pos[joint]
                end_pos = ideal_relaxed[joint]
                target_positions[joint] = self.interpolate_position(start_pos, end_pos, ratio)
            
            # Aplicar comandos
            self.apply_all_joints_safe(target_positions)
            
            # Enviar comando
            self.low_cmd.crc = self.crc.Crc(self.low_cmd)
            self.arm_sdk_publisher.Write(self.low_cmd)
            
            time.sleep(self.control_dt_)
            
            if int(start_time * 10) % 10 == 0:  # A cada 0.1s
                print(f"🔄 Relaxando... {ratio*100:.1f}%")
        
        # Aguardar um pouco para estabilizar
        time.sleep(1.0)
        
        # Verificar posições finais
        final_pos = self.get_current_positions()
        if final_pos:
            print(f"📊 Posições após relaxamento: {final_pos}")
            self.relaxed_positions = final_pos.copy()
        
        print("✅ Braço direito relaxado com sucesso!")
        return True
    
    def start_complete_control(self):
        """Inicia o controle completo do movimento."""
        # Aguardar primeiro estado
        while not self.first_update_low_state:
            time.sleep(0.1)
        
        print("🎭 Iniciando movimento completo de riso...")
        
        # PRIMEIRO: Garantir que o braço esteja relaxado
        if not self.ensure_arm_relaxed():
            print("❌ Falha ao relaxar o braço")
            return False
        
        # Obter posições iniciais (agora relaxadas)
        initial_positions = self.get_current_positions()
        if not initial_positions:
            print("❌ Não foi possível obter posições iniciais")
            return False
        
        print(f"📊 Posições iniciais (relaxadas): {initial_positions}")
        
        # Loop principal de controle
        while not self.done:
            self.complete_control_loop(initial_positions)
            time.sleep(self.control_dt_)
        
        return True
    
    def complete_control_loop(self, initial_positions):
        """Loop principal de controle completo."""
        self.time_ += self.control_dt_
        
        # Habilitar arm_sdk
        self.low_cmd.motor_cmd[G1JointIndex.kNotUsedJoint].q = 1
        
        # Estágio 1: Mover para posição "mão na boca" (0-2s)
        if self.time_ < self.duration_stage:
            ratio = np.clip(self.time_ / self.duration_stage, 0.0, 1.0)
            print(f"🤚 Movendo para posição 'mão na boca'... {ratio*100:.1f}%")
            
            # Calcular posições interpoladas para braço direito
            target_positions = {}
            for joint in self.controlled_joints:
                start_pos = initial_positions[joint]
                end_pos = self.right_arm_positions[joint]
                target_positions[joint] = self.interpolate_position(start_pos, end_pos, ratio)
            
            # Aplicar comandos de forma segura
            self.apply_all_joints_safe(target_positions)
        
        # Estágio 2: Movimento de riso (2-7s)
        elif self.time_ < self.duration_stage + 5.0:
            laugh_time = self.time_ - self.duration_stage
            freq = 3.0  # Frequência do riso (3 Hz)
            amplitude = 0.15  # Amplitude do movimento do cotovelo
            
            # Movimento oscilatório apenas no cotovelo
            oscillation = amplitude * np.sin(2 * np.pi * freq * laugh_time)
            elbow_target = self.right_arm_positions[G1JointIndex.RightElbow] + oscillation
            
            # Calcular posições para braço direito
            target_positions = self.right_arm_positions.copy()
            target_positions[G1JointIndex.RightElbow] = elbow_target
            
            # Aplicar comandos de forma segura
            self.apply_all_joints_safe(target_positions)
            
            # Debug info
            if int(laugh_time * 10) % 10 == 0:  # A cada 0.1s
                print(f"😂 Rindo... Cotovelo: {elbow_target:.3f} rad")
        
        # Estágio 3: Retornar ao estado relaxado (7-9s) - COMO NO EXEMPLO OFICIAL
        elif self.time_ < self.duration_stage * 2 + 5.0:
            return_time = self.time_ - (self.duration_stage + 5.0)
            ratio = np.clip(return_time / self.duration_stage, 0.0, 1.0)
            print(f"🔄 Retornando ao estado relaxado... {ratio*100:.1f}%")
            
            # MÉTODO DO EXEMPLO OFICIAL: usar posições atuais do low_state
            if self.low_state:
                for joint in self.controlled_joints:
                    # Transição suave para posição atual (que é naturalmente relaxada)
                    current_pos = self.low_state.motor_state[joint].q
                    self.low_cmd.motor_cmd[joint].tau = 0.0
                    self.low_cmd.motor_cmd[joint].q = (1.0 - ratio) * current_pos
                    self.low_cmd.motor_cmd[joint].dq = 0.0
                    self.low_cmd.motor_cmd[joint].kp = self.kp
                    self.low_cmd.motor_cmd[joint].kd = self.kd
        
        # Estágio 4: Desabilitar arm_sdk (9-10s) - COMO NO EXEMPLO OFICIAL
        elif self.time_ < self.duration_stage * 2 + 6.0:
            disable_time = self.time_ - (self.duration_stage * 2 + 5.0)
            ratio = np.clip(disable_time / self.duration_stage, 0.0, 1.0)
            
            # Desabilitar arm_sdk gradualmente (como no exemplo oficial)
            self.low_cmd.motor_cmd[G1JointIndex.kNotUsedJoint].q = 1.0 - ratio
            
            # Manter juntas em posições atuais durante desabilitação
            if self.low_state:
                for joint in self.controlled_joints:
                    current_pos = self.low_state.motor_state[joint].q
                    self.low_cmd.motor_cmd[joint].tau = 0.0
                    self.low_cmd.motor_cmd[joint].q = current_pos
                    self.low_cmd.motor_cmd[joint].dq = 0.0
                    self.low_cmd.motor_cmd[joint].kp = self.kp
                    self.low_cmd.motor_cmd[joint].kd = self.kd
            
            print("📴 Desabilitando arm_sdk...")
        
        else:
            # Finalizar
            self.done = True
            print("✅ Movimento completo concluído!")
        
        # Enviar comando
        self.low_cmd.crc = self.crc.Crc(self.low_cmd)
        self.arm_sdk_publisher.Write(self.low_cmd)
    
    def run_complete_sequence(self):
        """Executa a sequência completa."""
        print("🎭 G1 MOVIMENTO COMPLETO - RISO CONSTRUÍDO DO ZERO")
        print("=" * 60)
        
        # 1. Configurar Main Operation Control
        if not self.setup_main_operation_control():
            return False
        
        # 2. Inicializar controle de baixo nível
        if not self.init_low_level_control():
            return False
        
        # 3. Iniciar movimento completo
        if not self.start_complete_control():
            return False
        
        print("🎉 Sequência completa concluída com sucesso!")
        return True

def main():
    """Função principal."""
    print("🎭 G1 MOVIMENTO COMPLETO - RISO CONSTRUÍDO DO ZERO")
    print("=" * 60)
    print("🎯 OBJETIVO: Construir movimento 'mão na boca' + riso do zero")
    print("⚠️  AVISO: Certifique-se de que não há obstáculos ao redor do robô")
    
    # Confirmação de segurança
    response = input("Deseja continuar? (s/n): ").strip().lower()
    if response not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada")
        return
    
    # Criar controlador
    controller = G1CompleteLaughController()
    
    # Inicializar SDK
    if not controller.initialize_sdk():
        print("❌ Falha na inicialização do SDK")
        return
    
    # Executar sequência
    controller.run_complete_sequence()

if __name__ == "__main__":
    main()
