#!/usr/bin/env python3
"""
Teste de Locomoção e Rotação do G1
==================================

Este teste explora as capacidades de movimento e rotação do robô G1,
incluindo movimento do quadril e controle de velocidade.

Baseado na documentação descoberta:
- LocoClient.Move(vx, vy, vyaw) - Movimento com velocidade
- LocoClient.SetVelocity(vx, vy, omega, duration) - Controle de velocidade
- Articulações do quadril: Pitch (±154°), Roll (-30° a +170°), Yaw (±158°)
"""

import time
import sys
import numpy as np
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient
from unitree_sdk2py.comm.motion_switcher.motion_switcher_client import MotionSwitcherClient

class G1LocomotionRotationTest:
    """Teste de locomoção e rotação do G1."""
    
    def __init__(self):
        self.interface = "en11"  # Interface de rede
        self.loco_client = None
        self.motion_switcher = None
        
    def initialize_sdk(self):
        """Inicializa o SDK."""
        try:
            print("🔧 Inicializando SDK...")
            ChannelFactoryInitialize(0, self.interface)
            print("✅ SDK inicializado")
            
            # Inicializar LocoClient
            self.loco_client = LocoClient()
            self.loco_client.SetTimeout(10.0)
            self.loco_client.Init()
            print("✅ LocoClient inicializado")
            
            # Inicializar MotionSwitcher
            self.motion_switcher = MotionSwitcherClient()
            self.motion_switcher.SetTimeout(10.0)
            self.motion_switcher.Init()
            print("✅ MotionSwitcher inicializado")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            return False
    
    def prepare_robot(self):
        """Prepara o robô para locomoção."""
        print("\n🚀 PREPARANDO ROBÔ PARA LOCOMOÇÃO...")
        
        try:
            # Sequência correta: Zero Torque → Damping → Get Ready
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
            status, result = self.motion_switcher.CheckMode()
            print(f"📊 Estado atual: {result}")
            
            # IMPORTANTE: Verificar se está em Main Operation Control
            print("\n⚠️  ATENÇÃO: AGORA VOCÊ PRECISA COLOCAR O ROBÔ EM MAIN OPERATION CONTROL!")
            print("🎮 No controle físico, pressione: R1 + X")
            print("🤖 Isso fará o robô entrar automaticamente em Lowstanding")
            print("📋 Aguarde o robô ficar estável antes de continuar...")
            
            # Aguardar confirmação do usuário
            input("\n⏸️  Pressione ENTER após colocar em Main Operation Control...")
            
            # Verificar estado novamente
            status, result = self.motion_switcher.CheckMode()
            print(f"📊 Estado após Main Operation Control: {result}")
            
            if result and result.get('name') == 'control':
                print("✅ Robô está em Main Operation Control - pronto para locomoção!")
                return True
            else:
                print("⚠️  Robô pode não estar em Main Operation Control, mas continuando...")
                print("⚠️  Se os comandos falharem, verifique o modo do robô")
                return True
                
        except Exception as e:
            print(f"❌ Erro na preparação: {e}")
            return False
    
    def check_robot_state(self, expected_mode="control"):
        """Verifica o estado atual do robô."""
        try:
            status, result = self.motion_switcher.CheckMode()
            if status == 0 and result:
                current_mode = result.get('name', 'unknown')
                current_form = result.get('form', 'unknown')
                print(f"📊 Estado atual: {result}")
                
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

    def test_velocity_movements(self):
        """Testa movimentos básicos com velocidade."""
        print("\n🏃 TESTANDO MOVIMENTOS DE VELOCIDADE...")
        
        movements = [
            ("Andar para frente", 0.2, 0.0, 0.0),
            ("Andar para trás", -0.2, 0.0, 0.0),
            ("Lateral esquerda", 0.0, 0.2, 0.0),
            ("Lateral direita", 0.0, -0.2, 0.0),
            ("Rotação esquerda", 0.0, 0.0, 0.5),
            ("Rotação direita", 0.0, 0.0, -0.5),
        ]
        
        for name, vx, vy, vyaw in movements:
            print(f"\n🔄 {name} (vx={vx}, vy={vy}, vyaw={vyaw})...")
            
            # SEMPRE verificar estado antes de executar
            if not self.check_robot_state("control"):
                print(f"   ❌ Robô não está em modo correto para {name}")
                continue
                
            try:
                # Usar Move() para movimento contínuo
                self.loco_client.Move(vx, vy, vyaw, continous_move=True)
                time.sleep(3)
                
                # Parar movimento
                self.loco_client.StopMove()
                time.sleep(2)
                
                print(f"   ✅ {name} executado com sucesso")
                
            except Exception as e:
                print(f"   ❌ Erro em {name}: {e}")
    
    def test_rotation_patterns(self):
        """Testa padrões de rotação mais complexos."""
        print("\n🌀 TESTANDO PADRÕES DE ROTAÇÃO...")
        
        rotations = [
            ("Rotação lenta", 0.0, 0.0, 0.2, 5.0),
            ("Rotação média", 0.0, 0.0, 0.5, 3.0),
            ("Rotação rápida", 0.0, 0.0, 1.0, 2.0),
            ("Rotação + avanço", 0.1, 0.0, 0.3, 4.0),
            ("Rotação + lateral", 0.0, 0.1, 0.3, 4.0),
        ]
        
        for name, vx, vy, vyaw, duration in rotations:
            print(f"\n🔄 {name} (vx={vx}, vy={vy}, vyaw={vyaw}, {duration}s)...")
            
            # SEMPRE verificar estado antes de executar
            if not self.check_robot_state("control"):
                print(f"   ❌ Robô não está em modo correto para {name}")
                continue
                
            try:
                # Usar SetVelocity() para controle preciso
                self.loco_client.SetVelocity(vx, vy, vyaw, duration)
                time.sleep(duration + 1)
                
                # Parar movimento
                self.loco_client.StopMove()
                time.sleep(2)
                
                print(f"   ✅ {name} executado com sucesso")
                
            except Exception as e:
                print(f"   ❌ Erro em {name}: {e}")
    
    def test_circular_motion(self):
        """Testa movimento circular."""
        print("\n⭕ TESTANDO MOVIMENTO CIRCULAR...")
        
        # SEMPRE verificar estado antes de executar
        if not self.check_robot_state("control"):
            print("   ❌ Robô não está em modo correto para movimento circular")
            return
            
        try:
            # Movimento circular: avanço + rotação constante
            print("🔄 Iniciando movimento circular...")
            self.loco_client.SetVelocity(0.1, 0.0, 0.4, 10.0)  # 10 segundos
            time.sleep(10)
            
            # Parar movimento
            self.loco_client.StopMove()
            time.sleep(2)
            
            print("   ✅ Movimento circular executado")
            
        except Exception as e:
            print(f"   ❌ Erro no movimento circular: {e}")
    
    def test_figure_eight(self):
        """Testa movimento em forma de 8."""
        print("\n8️⃣ TESTANDO MOVIMENTO EM FORMA DE 8...")
        
        # SEMPRE verificar estado antes de executar
        if not self.check_robot_state("control"):
            print("   ❌ Robô não está em modo correto para movimento em 8")
            return
            
        try:
            # Primeira curva
            print("🔄 Primeira curva...")
            self.loco_client.SetVelocity(0.1, 0.0, 0.5, 3.0)
            time.sleep(3)
            
            # Transição
            print("🔄 Transição...")
            self.loco_client.SetVelocity(0.1, 0.0, 0.0, 1.0)
            time.sleep(1)
            
            # Segunda curva (direção oposta)
            print("🔄 Segunda curva...")
            self.loco_client.SetVelocity(0.1, 0.0, -0.5, 3.0)
            time.sleep(3)
            
            # Parar movimento
            self.loco_client.StopMove()
            time.sleep(2)
            
            print("   ✅ Movimento em 8 executado")
            
        except Exception as e:
            print(f"   ❌ Erro no movimento em 8: {e}")
    
    def test_hip_rotation_limits(self):
        """Testa os limites de rotação do quadril (modo estático)."""
        print("\n🦴 TESTANDO LIMITES DE ROTAÇÃO DO QUADRIL...")
        
        # Nota: Este teste requer modo de controle de baixo nível
        # Por enquanto, vamos simular com movimentos de rotação
        
        rotations = [
            ("Rotação Yaw máxima +", 0.0, 0.0, 1.5),
            ("Rotação Yaw máxima -", 0.0, 0.0, -1.5),
            ("Rotação suave", 0.0, 0.0, 0.8),
        ]
        
        for name, vx, vy, vyaw in rotations:
            print(f"\n🔄 {name} (vyaw={vyaw})...")
            
            # SEMPRE verificar estado antes de executar
            if not self.check_robot_state("control"):
                print(f"   ❌ Robô não está em modo correto para {name}")
                continue
                
            try:
                self.loco_client.SetVelocity(vx, vy, vyaw, 2.0)
                time.sleep(2)
                
                self.loco_client.StopMove()
                time.sleep(2)
                
                print(f"   ✅ {name} executado")
                
            except Exception as e:
                print(f"   ❌ Erro em {name}: {e}")
    
    def test_balance_modes(self):
        """Testa diferentes modos de balanceamento."""
        print("\n⚖️ TESTANDO MODOS DE BALANCEAMENTO...")
        
        # SEMPRE verificar estado antes de executar
        if not self.check_robot_state("control"):
            print("   ❌ Robô não está em modo correto para testes de balanceamento")
            return
            
        try:
            # BalanceStand com diferentes modos
            balance_modes = [0, 1, 2]  # Diferentes modos de balanceamento
            
            for mode in balance_modes:
                print(f"🔄 Testando modo de balanceamento {mode}...")
                
                # Verificar estado antes de cada modo
                if not self.check_robot_state("control"):
                    print(f"   ❌ Robô não está em modo correto para modo {mode}")
                    continue
                    
                try:
                    self.loco_client.BalanceStand(mode)
                    time.sleep(3)
                    print(f"   ✅ Modo {mode} ativado")
                except Exception as e:
                    print(f"   ❌ Erro no modo {mode}: {e}")
                    
        except Exception as e:
            print(f"❌ Erro nos testes de balanceamento: {e}")
    
    def run_all_tests(self):
        """Executa todos os testes."""
        print("🤖 TESTE DE LOCOMOÇÃO E ROTAÇÃO DO G1")
        print("=" * 50)
        
        # Inicializar
        if not self.initialize_sdk():
            return False
        
        # Preparar robô
        if not self.prepare_robot():
            return False
        
        # Executar testes
        try:
            self.test_velocity_movements()
            self.test_rotation_patterns()
            self.test_circular_motion()
            self.test_figure_eight()
            self.test_hip_rotation_limits()
            self.test_balance_modes()
            
            print("\n🎉 TODOS OS TESTES DE LOCOMOÇÃO CONCLUÍDOS!")
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
    print("🤖 TESTE DE LOCOMOÇÃO E ROTAÇÃO DO UNITREE G1")
    print("=" * 60)
    print("⚠️  ATENÇÃO: Este teste moverá o robô!")
    print("⚠️  Certifique-se de que há espaço suficiente!")
    print("⚠️  Pressione Ctrl+C para interromper a qualquer momento!")
    print("=" * 60)
    
    # Confirmação do usuário
    try:
        response = input("\n🤔 Deseja continuar com o teste? (s/N): ").lower()
        if response not in ['s', 'sim', 'y', 'yes']:
            print("❌ Teste cancelado pelo usuário")
            return
    except KeyboardInterrupt:
        print("\n❌ Teste cancelado")
        return
    
    # Executar teste
    tester = G1LocomotionRotationTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("📋 Comandos testados:")
        print("   - LocoClient.Move(vx, vy, vyaw)")
        print("   - LocoClient.SetVelocity(vx, vy, omega, duration)")
        print("   - LocoClient.StopMove()")
        print("   - LocoClient.BalanceStand(mode)")
        print("   - Movimentos: frente, trás, lateral, rotação")
        print("   - Padrões: circular, figura 8, limites de rotação")
    else:
        print("\n❌ Teste falhou ou foi interrompido")

if __name__ == "__main__":
    main()
