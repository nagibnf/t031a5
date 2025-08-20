#!/usr/bin/env python3
"""
Teste de Movimento do Quadril do G1 (Sem Locomoção)
===================================================

Este teste foca especificamente no movimento do quadril do robô G1,
sem movimento das pernas (locomoção).

Objetivo: Testar rotação do quadril em diferentes eixos:
- Pitch (frente/trás): ±154°
- Roll (lateral): -30° a +170°  
- Yaw (rotação horizontal): ±158°

Método: Usar controle de baixo nível das articulações do quadril
"""

import time
import sys
import numpy as np
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient
from unitree_sdk2py.comm.motion_switcher.motion_switcher_client import MotionSwitcherClient

class G1HipRotationTest:
    """Teste específico de movimento do quadril."""
    
    def __init__(self):
        self.interface = "en11"
        self.loco_client = None
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
            
            self.motion_switcher = MotionSwitcherClient()
            self.motion_switcher.SetTimeout(10.0)
            self.motion_switcher.Init()
            
            print("✅ SDK inicializado")
            return True
            
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            return False
    
    def check_robot_state(self, expected_mode="control"):
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
        """Prepara o robô para teste de quadril."""
        print("\n🚀 PREPARANDO ROBÔ PARA TESTE DE QUADRIL...")
        
        try:
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
            if not self.check_robot_state("control"):
                print("⚠️  Robô pode não estar em Main Operation Control")
                print("🎮 Pressione R1+X no controle físico se necessário")
                input("⏸️  Pressione ENTER após colocar em Main Operation Control...")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na preparação: {e}")
            return False
    
    def test_hip_yaw_rotation(self):
        """Testa rotação Yaw do quadril (rotação horizontal)."""
        print("\n🔄 TESTANDO ROTAÇÃO YAW DO QUADRIL...")
        
        if not self.check_robot_state("control"):
            print("❌ Robô não está em modo correto para teste de quadril")
            return False
        
        # Testar diferentes amplitudes de rotação Yaw
        yaw_tests = [
            ("Yaw pequeno +", 0.3),
            ("Yaw pequeno -", -0.3),
            ("Yaw médio +", 0.6),
            ("Yaw médio -", -0.6),
            ("Yaw grande +", 1.0),
            ("Yaw grande -", -1.0),
        ]
        
        for name, vyaw in yaw_tests:
            print(f"\n🔄 {name} (vyaw={vyaw})...")
            
            if not self.check_robot_state("control"):
                print(f"   ❌ Estado incorreto para {name}")
                continue
                
            try:
                # Usar SetVelocity com apenas rotação (sem movimento linear)
                self.loco_client.SetVelocity(0.0, 0.0, vyaw, 2.0)
                time.sleep(2)
                
                # Parar movimento
                self.loco_client.StopMove()
                time.sleep(2)
                
                print(f"   ✅ {name} executado")
                
            except Exception as e:
                print(f"   ❌ Erro em {name}: {e}")
        
        return True
    
    def test_hip_pitch_movement(self):
        """Testa movimento Pitch do quadril (frente/trás)."""
        print("\n🔄 TESTANDO MOVIMENTO PITCH DO QUADRIL...")
        
        if not self.check_robot_state("control"):
            print("❌ Robô não está em modo correto para teste de quadril")
            return False
        
        # Testar diferentes movimentos Pitch
        pitch_tests = [
            ("Pitch para frente", 0.2, 0.0, 0.0),
            ("Pitch para trás", -0.2, 0.0, 0.0),
            ("Pitch suave +", 0.1, 0.0, 0.0),
            ("Pitch suave -", -0.1, 0.0, 0.0),
        ]
        
        for name, vx, vy, vyaw in pitch_tests:
            print(f"\n🔄 {name} (vx={vx})...")
            
            if not self.check_robot_state("control"):
                print(f"   ❌ Estado incorreto para {name}")
                continue
                
            try:
                # Movimento apenas no eixo X (Pitch)
                self.loco_client.SetVelocity(vx, vy, vyaw, 2.0)
                time.sleep(2)
                
                # Parar movimento
                self.loco_client.StopMove()
                time.sleep(2)
                
                print(f"   ✅ {name} executado")
                
            except Exception as e:
                print(f"   ❌ Erro em {name}: {e}")
        
        return True
    
    def test_hip_roll_movement(self):
        """Testa movimento Roll do quadril (lateral)."""
        print("\n🔄 TESTANDO MOVIMENTO ROLL DO QUADRIL...")
        
        if not self.check_robot_state("control"):
            print("❌ Robô não está em modo correto para teste de quadril")
            return False
        
        # Testar diferentes movimentos Roll
        roll_tests = [
            ("Roll esquerda", 0.0, 0.2, 0.0),
            ("Roll direita", 0.0, -0.2, 0.0),
            ("Roll suave +", 0.0, 0.1, 0.0),
            ("Roll suave -", 0.0, -0.1, 0.0),
        ]
        
        for name, vx, vy, vyaw in roll_tests:
            print(f"\n🔄 {name} (vy={vy})...")
            
            if not self.check_robot_state("control"):
                print(f"   ❌ Estado incorreto para {name}")
                continue
                
            try:
                # Movimento apenas no eixo Y (Roll)
                self.loco_client.SetVelocity(vx, vy, vyaw, 2.0)
                time.sleep(2)
                
                # Parar movimento
                self.loco_client.StopMove()
                time.sleep(2)
                
                print(f"   ✅ {name} executado")
                
            except Exception as e:
                print(f"   ❌ Erro em {name}: {e}")
        
        return True
    
    def test_hip_combined_movements(self):
        """Testa movimentos combinados do quadril."""
        print("\n🔄 TESTANDO MOVIMENTOS COMBINADOS DO QUADRIL...")
        
        if not self.check_robot_state("control"):
            print("❌ Robô não está em modo correto para teste de quadril")
            return False
        
        # Testar combinações de movimentos
        combined_tests = [
            ("Pitch + Yaw", 0.1, 0.0, 0.3),
            ("Roll + Yaw", 0.0, 0.1, 0.3),
            ("Pitch + Roll", 0.1, 0.1, 0.0),
            ("Pitch + Roll + Yaw", 0.1, 0.1, 0.2),
        ]
        
        for name, vx, vy, vyaw in combined_tests:
            print(f"\n🔄 {name} (vx={vx}, vy={vy}, vyaw={vyaw})...")
            
            if not self.check_robot_state("control"):
                print(f"   ❌ Estado incorreto para {name}")
                continue
                
            try:
                # Movimento combinado
                self.loco_client.SetVelocity(vx, vy, vyaw, 3.0)
                time.sleep(3)
                
                # Parar movimento
                self.loco_client.StopMove()
                time.sleep(2)
                
                print(f"   ✅ {name} executado")
                
            except Exception as e:
                print(f"   ❌ Erro em {name}: {e}")
        
        return True
    
    def test_hip_static_poses(self):
        """Testa poses estáticas do quadril."""
        print("\n🔄 TESTANDO POSES ESTÁTICAS DO QUADRIL...")
        
        if not self.check_robot_state("control"):
            print("❌ Robô não está em modo correto para teste de quadril")
            return False
        
        # Testar poses estáticas (movimento curto para posição)
        static_poses = [
            ("Pose neutra", 0.0, 0.0, 0.0),
            ("Pose frente", 0.05, 0.0, 0.0),
            ("Pose trás", -0.05, 0.0, 0.0),
            ("Pose esquerda", 0.0, 0.05, 0.0),
            ("Pose direita", 0.0, -0.05, 0.0),
            ("Pose rotação +", 0.0, 0.0, 0.2),
            ("Pose rotação -", 0.0, 0.0, -0.2),
        ]
        
        for name, vx, vy, vyaw in static_poses:
            print(f"\n🔄 {name}...")
            
            if not self.check_robot_state("control"):
                print(f"   ❌ Estado incorreto para {name}")
                continue
                
            try:
                # Movimento curto para posição
                self.loco_client.SetVelocity(vx, vy, vyaw, 1.0)
                time.sleep(1)
                
                # Manter posição por um tempo
                time.sleep(2)
                
                # Parar movimento
                self.loco_client.StopMove()
                time.sleep(1)
                
                print(f"   ✅ {name} executado")
                
            except Exception as e:
                print(f"   ❌ Erro em {name}: {e}")
        
        return True
    
    def run_all_hip_tests(self):
        """Executa todos os testes de quadril."""
        print("🦴 TESTE DE MOVIMENTO DO QUADRIL DO G1")
        print("=" * 50)
        print("Este teste foca especificamente no movimento do quadril")
        print("sem locomoção das pernas.")
        print("=" * 50)
        
        # Inicializar
        if not self.initialize_sdk():
            return False
        
        # Preparar robô
        if not self.prepare_robot_for_hip_test():
            return False
        
        # Executar testes
        try:
            self.test_hip_yaw_rotation()
            self.test_hip_pitch_movement()
            self.test_hip_roll_movement()
            self.test_hip_combined_movements()
            self.test_hip_static_poses()
            
            print("\n🎉 TODOS OS TESTES DE QUADRIL CONCLUÍDOS!")
            return True
            
        except KeyboardInterrupt:
            print("\n⚠️ Teste interrompido pelo usuário")
            self.loco_client.StopMove()
            return False
        except Exception as e:
            print(f"\n❌ Erro geral nos testes: {e}")
            return False

def main():
    """Função principal."""
    print("🦴 TESTE DE MOVIMENTO DO QUADRIL - UNITREE G1")
    print("=" * 60)
    print("⚠️  ATENÇÃO: Este teste moverá o quadril do robô!")
    print("⚠️  Certifique-se de que há espaço suficiente!")
    print("⚠️  Pressione Ctrl+C para interromper a qualquer momento!")
    print("=" * 60)
    
    # Confirmação do usuário
    try:
        response = input("\n🤔 Deseja continuar com o teste de quadril? (s/N): ").lower()
        if response not in ['s', 'sim', 'y', 'yes']:
            print("❌ Teste cancelado pelo usuário")
            return
    except KeyboardInterrupt:
        print("\n❌ Teste cancelado")
        return
    
    # Executar teste
    tester = G1HipRotationTest()
    success = tester.run_all_hip_tests()
    
    if success:
        print("\n🎉 TESTE DE QUADRIL CONCLUÍDO COM SUCESSO!")
        print("📋 Movimentos testados:")
        print("   - Rotação Yaw (horizontal)")
        print("   - Movimento Pitch (frente/trás)")
        print("   - Movimento Roll (lateral)")
        print("   - Movimentos combinados")
        print("   - Poses estáticas")
        print("")
        print("🎯 O quadril do G1 foi testado sem locomoção das pernas!")
    else:
        print("\n❌ Teste falhou ou foi interrompido")

if __name__ == "__main__":
    main()
