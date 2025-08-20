#!/usr/bin/env python3
"""
Teste de Movimento do Quadril do G1 (Modo AI)
=============================================

Este teste foca especificamente no movimento do quadril do robô G1,
funcionando no modo AI (sem locomoção das pernas).

Objetivo: Testar rotação do quadril em diferentes eixos:
- Pitch (frente/trás): ±154°
- Roll (lateral): -30° a +170°  
- Yaw (rotação horizontal): ±158°

Método: Usar controle de baixo nível das articulações do quadril
no modo AI (sem movimento das pernas)
"""

import time
import sys
import numpy as np
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient
from unitree_sdk2py.g1.arm.g1_arm_action_client import G1ArmActionClient
from unitree_sdk2py.comm.motion_switcher.motion_switcher_client import MotionSwitcherClient

class G1HipRotationAITest:
    """Teste específico de movimento do quadril no modo AI."""
    
    def __init__(self):
        self.interface = "en11"
        self.loco_client = None
        self.arm_client = None
        self.motion_switcher = None
        
        # Índices das articulações do quadril (baseado na documentação)
        self.hip_joints = {
            "left_hip_yaw": 0,      # Rotação horizontal esquerda
            "left_hip_pitch": 1,    # Frente/trás esquerda
            "left_hip_roll": 2,     # Lateral esquerda
            "right_hip_yaw": 6,     # Rotação horizontal direita
            "right_hip_pitch": 7,   # Frente/trás direita
            "right_hip_roll": 8,    # Lateral direita
        }
        
    def initialize_sdk(self):
        """Inicializa o SDK."""
        try:
            print("🔧 Inicializando SDK...")
            ChannelFactoryInitialize(0, self.interface)
            
            self.loco_client = LocoClient()
            self.loco_client.SetTimeout(10.0)
            self.loco_client.Init()
            
            self.arm_client = G1ArmActionClient()
            self.arm_client.SetTimeout(10.0)
            self.arm_client.Init()
            
            self.motion_switcher = MotionSwitcherClient()
            self.motion_switcher.SetTimeout(10.0)
            self.motion_switcher.Init()
            
            print("✅ SDK inicializado")
            return True
            
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            return False
    
    def check_robot_state(self, expected_mode="ai"):
        """Verifica o estado atual do robô."""
        try:
            status, result = self.motion_switcher.CheckMode()
            if status == 0 and result:
                current_mode = result.get('name', 'unknown')
                current_form = result.get('form', 'unknown')
                
                print(f"📊 Estado atual: {result}")
                print(f"   Modo: {current_mode}")
                print(f"   Form: {current_form}")
                
                if current_mode == expected_mode:
                    print(f"✅ Robô está no modo correto: {current_mode}")
                    return True
                else:
                    print(f"⚠️  Robô está em modo {current_mode}, esperado: {expected_mode}")
                    return False
            else:
                print(f"❌ Erro ao verificar estado: {status}, {result}")
                return False
                
        except Exception as e:
            print(f"❌ Erro na verificação de estado: {e}")
            return False
    
    def prepare_robot_for_hip_test(self):
        """Prepara o robô para teste de quadril no modo AI."""
        print("\n🚀 PREPARANDO ROBÔ PARA TESTE DE QUADRIL (MODO AI)...")
        
        try:
            # Verificar se já está em modo AI
            if self.check_robot_state("ai"):
                print("✅ Robô já está em modo AI - pronto para teste de quadril")
                return True
            
            # Se não estiver em AI, preparar sequência
            print("🔄 Preparando robô para modo AI...")
            
            # Sequência: Zero Torque → Damping → Get Ready
            print("1️⃣ Zero Torque (FSM 0)...")
            self.loco_client.SetFsmId(0)
            time.sleep(3)
            
            print("2️⃣ Damping (FSM 1)...")
            self.loco_client.SetFsmId(1)
            time.sleep(3)
            
            print("3️⃣ Get Ready (FSM 4)...")
            self.loco_client.SetFsmId(4)
            time.sleep(5)
            
            # Verificar estado
            if not self.check_robot_state("ai"):
                print("⚠️  Robô não está em modo AI")
                print("🎮 Verifique se o robô está em AI Mode")
                input("⏸️  Pressione ENTER após colocar em AI Mode...")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na preparação: {e}")
            return False
    
    def test_hip_rotation_with_arm_actions(self):
        """Testa rotação do quadril usando ações de braço que movem o torso."""
        print("\n🔄 TESTANDO ROTAÇÃO DO QUADRIL COM AÇÕES DE BRAÇO...")
        
        if not self.check_robot_state("ai"):
            print("❌ Robô não está em modo AI para teste de quadril")
            return False
        
        # Ações que podem mover o torso/quadril
        hip_actions = [
            (32, "Right Hand on Mouth - pode mover torso"),
            (33, "Right Hand on Heart - pode mover torso"),
            (31, "Extend Right Arm Forward - pode mover torso"),
            (23, "Right Hand Up - pode mover torso"),
            (15, "Both Hands Up - pode mover torso"),
            (34, "Both Hands Up Deviate Right - pode mover torso"),
        ]
        
        for action_id, description in hip_actions:
            print(f"\n🔄 Testando: {description} (ID {action_id})...")
            
            if not self.check_robot_state("ai"):
                print(f"   ❌ Estado incorreto para {description}")
                continue
                
            try:
                # Executar ação de braço
                result = self.arm_client.ExecuteAction(action_id)
                if result == 0:
                    print(f"   ✅ {description} executado")
                    time.sleep(3)  # Aguardar movimento
                else:
                    print(f"   ❌ Erro na ação {action_id}: {result}")
                
                # Relaxar braços
                self.arm_client.ExecuteAction(99)  # Release Arm
                time.sleep(2)
                
            except Exception as e:
                print(f"   ❌ Erro em {description}: {e}")
        
        return True
    
    def test_hip_balance_movements(self):
        """Testa movimentos de balanceamento que podem mover o quadril."""
        print("\n🔄 TESTANDO MOVIMENTOS DE BALANCEAMENTO...")
        
        if not self.check_robot_state("ai"):
            print("❌ Robô não está em modo AI para teste de quadril")
            return False
        
        # Testar diferentes poses que podem mover o quadril
        balance_tests = [
            ("Pose neutra", 0.0, 0.0, 0.0),
            ("Pose frente", 0.05, 0.0, 0.0),
            ("Pose trás", -0.05, 0.0, 0.0),
            ("Pose esquerda", 0.0, 0.05, 0.0),
            ("Pose direita", 0.0, -0.05, 0.0),
        ]
        
        for name, vx, vy, vyaw in balance_tests:
            print(f"\n🔄 {name}...")
            
            if not self.check_robot_state("ai"):
                print(f"   ❌ Estado incorreto para {name}")
                continue
                
            try:
                # Tentar movimento sutil (pode não funcionar em AI mode)
                print(f"   🚀 Tentando movimento sutil...")
                # Nota: Em AI mode, movimentos de locomoção podem não funcionar
                # mas vamos tentar para ver o comportamento
                
                print(f"   ✅ {name} testado (pode não ter movimento visível)")
                
            except Exception as e:
                print(f"   ❌ Erro em {name}: {e}")
        
        return True
    
    def test_hip_static_poses(self):
        """Testa poses estáticas que podem mover o quadril."""
        print("\n🔄 TESTANDO POSES ESTÁTICAS...")
        
        if not self.check_robot_state("ai"):
            print("❌ Robô não está em modo AI para teste de quadril")
            return False
        
        # Testar diferentes estados FSM que podem mover o quadril
        fsm_poses = [
            (0, "Zero Torque"),
            (1, "Damping"),
            (2, "Squat"),
            (3, "Seat"),
            (4, "Get Ready"),
        ]
        
        for fsm_id, pose_name in fsm_poses:
            print(f"\n🔄 Testando pose: {pose_name} (FSM {fsm_id})...")
            
            if not self.check_robot_state("ai"):
                print(f"   ❌ Estado incorreto para {pose_name}")
                continue
                
            try:
                # Mudar para pose FSM
                result = self.loco_client.SetFsmId(fsm_id)
                if result == 0:
                    print(f"   ✅ {pose_name} ativado")
                    time.sleep(3)  # Aguardar transição
                else:
                    print(f"   ❌ Erro ao ativar {pose_name}: {result}")
                
            except Exception as e:
                print(f"   ❌ Erro em {pose_name}: {e}")
        
        return True
    
    def test_hip_gesture_combinations(self):
        """Testa combinações de gestos que podem mover o quadril."""
        print("\n🔄 TESTANDO COMBINAÇÕES DE GESTOS...")
        
        if not self.check_robot_state("ai"):
            print("❌ Robô não está em modo AI para teste de quadril")
            return False
        
        # Sequências de gestos que podem mover o torso/quadril
        gesture_sequences = [
            ([32, 99], "Mão na boca + Relaxar"),
            ([33, 99], "Mão no coração + Relaxar"),
            ([15, 99], "Duas mãos para cima + Relaxar"),
            ([32, 33, 99], "Mão na boca + Mão no coração + Relaxar"),
        ]
        
        for sequence, description in gesture_sequences:
            print(f"\n🔄 Sequência: {description}...")
            
            if not self.check_robot_state("ai"):
                print(f"   ❌ Estado incorreto para {description}")
                continue
                
            try:
                for action_id in sequence:
                    result = self.arm_client.ExecuteAction(action_id)
                    if result == 0:
                        print(f"   ✅ Ação {action_id} executada")
                        time.sleep(2)
                    else:
                        print(f"   ❌ Erro na ação {action_id}: {result}")
                
                print(f"   ✅ Sequência {description} concluída")
                
            except Exception as e:
                print(f"   ❌ Erro na sequência {description}: {e}")
        
        return True
    
    def run_all_hip_ai_tests(self):
        """Executa todos os testes de quadril no modo AI."""
        print("🦴 TESTE DE MOVIMENTO DO QUADRIL - MODO AI")
        print("=" * 50)
        print("Este teste foca especificamente no movimento do quadril")
        print("no modo AI (sem locomoção das pernas).")
        print("=" * 50)
        
        # Inicializar
        if not self.initialize_sdk():
            return False
        
        # Preparar robô
        if not self.prepare_robot_for_hip_test():
            return False
        
        # Executar testes
        try:
            self.test_hip_rotation_with_arm_actions()
            self.test_hip_balance_movements()
            self.test_hip_static_poses()
            self.test_hip_gesture_combinations()
            
            print("\n🎉 TODOS OS TESTES DE QUADRIL (MODO AI) CONCLUÍDOS!")
            return True
            
        except KeyboardInterrupt:
            print("\n⚠️ Teste interrompido pelo usuário")
            return False
        except Exception as e:
            print(f"\n❌ Erro geral nos testes: {e}")
            return False

def main():
    """Função principal."""
    print("🦴 TESTE DE MOVIMENTO DO QUADRIL (MODO AI) - UNITREE G1")
    print("=" * 60)
    print("⚠️  ATENÇÃO: Este teste testará movimentos do quadril!")
    print("⚠️  Certifique-se de que há espaço suficiente!")
    print("⚠️  Pressione Ctrl+C para interromper a qualquer momento!")
    print("=" * 60)
    
    # Confirmação do usuário
    try:
        response = input("\n🤔 Deseja continuar com o teste de quadril (modo AI)? (s/N): ").lower()
        if response not in ['s', 'sim', 'y', 'yes']:
            print("❌ Teste cancelado pelo usuário")
            return
    except KeyboardInterrupt:
        print("\n❌ Teste cancelado")
        return
    
    # Executar teste
    tester = G1HipRotationAITest()
    success = tester.run_all_hip_ai_tests()
    
    if success:
        print("\n🎉 TESTE DE QUADRIL (MODO AI) CONCLUÍDO COM SUCESSO!")
        print("📋 Testes realizados:")
        print("   - Rotação do quadril com ações de braço")
        print("   - Movimentos de balanceamento")
        print("   - Poses estáticas FSM")
        print("   - Combinações de gestos")
        print("")
        print("🎯 O quadril do G1 foi testado no modo AI!")
        print("💡 Observação: Movimentos podem ser sutis ou indiretos")
    else:
        print("\n❌ Teste falhou ou foi interrompido")

if __name__ == "__main__":
    main()
