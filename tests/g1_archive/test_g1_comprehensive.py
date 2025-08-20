#!/usr/bin/env python3
"""
Teste Abrangente do G1 - Explorando todos os modos FSM, comandos de braço e locomoção.
Baseado na pesquisa do SDK oficial da Unitree.
"""

import time
import sys
import json
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class G1ComprehensiveTester:
    """Testador abrangente do G1 - todos os modos e comandos."""
    
    def __init__(self):
        self.interface = "en11"
        self.robot_ip = "192.168.123.161"
        
        # Clientes SDK
        self.loco_client = None
        self.arm_client = None
        self.motion_switcher = None
        
        # Mapeamento FSM baseado no SDK
        self.fsm_modes = {
            0: "Zero Torque",
            1: "Damping", 
            2: "Squat",
            3: "Seat",
            4: "Get Ready",
            5: "Vazio",
            6: "Vazio", 
            200: "Start",
            702: "Lie2StandUp",
            706: "Squat2StandUp"
        }
        
        # Comandos de braço baseados no SDK
        self.arm_actions = {
            0: "release arm",
            1: "shake hand", 
            2: "high five",
            3: "hug",
            4: "high wave",
            5: "clap",
            6: "face wave",
            7: "left kiss",
            8: "heart",
            9: "right heart",
            10: "hands up",
            11: "x-ray",
            12: "right hand up",
            13: "reject",
            14: "right kiss",
            15: "two-hand kiss"
        }
        
        # Modos de locomoção
        self.loco_commands = {
            "damp": "Damping",
            "start": "Start",
            "squat2standup": "Squat to Stand Up",
            "lie2standup": "Lie to Stand Up", 
            "sit": "Sit",
            "standup2squat": "Stand Up to Squat",
            "zerotorque": "Zero Torque",
            "highstand": "High Stand",
            "lowstand": "Low Stand",
            "move_forward": "Move Forward",
            "move_lateral": "Move Lateral", 
            "move_rotate": "Move Rotate",
            "wave_hand": "Wave Hand",
            "shake_hand": "Shake Hand"
        }
        
        # Modos do MotionSwitcher
        self.motion_switcher_modes = {
            "ai": "AI Mode",
            "normal": "Normal Mode", 
            "advanced": "Advanced Mode",
            "ai-w": "AI Wheeled Mode"
        }
    
    def initialize_sdk(self):
        """Inicializa todos os clientes SDK."""
        try:
            from unitree_sdk2py.core.channel import ChannelFactoryInitialize
            from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient
            from unitree_sdk2py.g1.arm.g1_arm_action_client import G1ArmActionClient
            from unitree_sdk2py.comm.motion_switcher.motion_switcher_client import MotionSwitcherClient
            
            print("🔧 Inicializando SDK...")
            ChannelFactoryInitialize(0, self.interface)
            print("✅ SDK inicializado com interface en11")
            
            # Inicializar LocoClient
            self.loco_client = LocoClient()
            self.loco_client.SetTimeout(10.0)
            self.loco_client.Init()
            print("✅ LocoClient inicializado")
            
            # Inicializar ArmActionClient
            self.arm_client = G1ArmActionClient()
            self.arm_client.SetTimeout(10.0)
            self.arm_client.Init()
            print("✅ ArmActionClient inicializado")
            
            # Inicializar MotionSwitcherClient
            self.motion_switcher = MotionSwitcherClient()
            self.motion_switcher.SetTimeout(10.0)
            self.motion_switcher.Init()
            print("✅ MotionSwitcherClient inicializado")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            return False
    
    def check_current_mode(self):
        """Verifica o modo atual do G1."""
        try:
            if self.motion_switcher:
                status, result = self.motion_switcher.CheckMode()
                print(f"📊 MotionSwitcher Status: {status}")
                if result:
                    print(f"📊 Modo Atual: {result}")
                return status == 0
        except Exception as e:
            print(f"❌ Erro ao verificar modo: {e}")
        return False
    
    def test_fsm_modes(self):
        """Testa todos os modos FSM conhecidos."""
        print("\n🤖 TESTANDO MODOS FSM")
        print("=" * 50)
        
        for fsm_id, mode_name in self.fsm_modes.items():
            print(f"\n🔄 Testando FSM {fsm_id}: {mode_name}")
            try:
                result = self.loco_client.SetFsmId(fsm_id)
                print(f"   Status: {result}")
                time.sleep(2)  # Aguardar transição
            except Exception as e:
                print(f"   ❌ Erro: {e}")
    
    def test_arm_actions(self):
        """Testa todos os comandos de braço."""
        print("\n🤖 TESTANDO COMANDOS DE BRAÇO")
        print("=" * 50)
        
        for action_id, action_name in self.arm_actions.items():
            print(f"\n🔄 Testando Ação {action_id}: {action_name}")
            try:
                result = self.arm_client.ExecuteAction(action_id)
                print(f"   Status: {result}")
                time.sleep(3)  # Aguardar execução
                
                # Voltar ao estado inicial
                if action_id != 0:  # Não executar "release arm" novamente
                    print("   🔄 Voltando ao estado inicial...")
                    self.arm_client.ExecuteAction(0)  # release arm
                    time.sleep(1)
                    
            except Exception as e:
                print(f"   ❌ Erro: {e}")
    
    def test_loco_commands(self):
        """Testa comandos de locomoção."""
        print("\n🤖 TESTANDO COMANDOS DE LOCOMOÇÃO")
        print("=" * 50)
        
        # Testar comandos básicos
        basic_commands = [
            ("damp", lambda: self.loco_client.Damp()),
            ("start", lambda: self.loco_client.Start()),
            ("sit", lambda: self.loco_client.Sit()),
            ("zerotorque", lambda: self.loco_client.ZeroTorque()),
            ("highstand", lambda: self.loco_client.HighStand()),
            ("lowstand", lambda: self.loco_client.LowStand())
        ]
        
        for cmd_name, cmd_func in basic_commands:
            print(f"\n🔄 Testando: {cmd_name}")
            try:
                result = cmd_func()
                print(f"   Status: {result}")
                time.sleep(2)
            except Exception as e:
                print(f"   ❌ Erro: {e}")
        
        # Testar movimentos
        print("\n🔄 Testando movimentos...")
        movements = [
            ("forward", 0.2, 0, 0),
            ("lateral", 0, 0.2, 0),
            ("rotate", 0, 0, 0.2)
        ]
        
        for move_name, vx, vy, vyaw in movements:
            print(f"\n🔄 Movimento: {move_name}")
            try:
                self.loco_client.Move(vx, vy, vyaw)
                time.sleep(3)
                self.loco_client.StopMove()
                time.sleep(1)
            except Exception as e:
                print(f"   ❌ Erro: {e}")
    
    def test_motion_switcher_modes(self):
        """Testa modos do MotionSwitcher."""
        print("\n🤖 TESTANDO MODOS MOTION SWITCHER")
        print("=" * 50)
        
        for mode_name, mode_desc in self.motion_switcher_modes.items():
            print(f"\n🔄 Testando modo: {mode_name} ({mode_desc})")
            try:
                result = self.motion_switcher.SelectMode(mode_name)
                print(f"   Status: {result}")
                time.sleep(2)
                
                # Verificar modo atual
                status, current_mode = self.motion_switcher.CheckMode()
                if current_mode:
                    print(f"   Modo atual: {current_mode}")
                    
            except Exception as e:
                print(f"   ❌ Erro: {e}")
    
    def get_action_list(self):
        """Obtém lista completa de ações disponíveis."""
        print("\n📋 OBTENDO LISTA DE AÇÕES")
        print("=" * 50)
        
        try:
            code, action_list = self.arm_client.GetActionList()
            if code == 0 and action_list:
                print("✅ Lista de ações obtida:")
                print(json.dumps(action_list, indent=2))
            else:
                print(f"❌ Erro ao obter lista: {code}")
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    def interactive_menu(self):
        """Menu interativo para testes."""
        print("\n🎯 MENU INTERATIVO - TESTE ABRANGENTE G1")
        print("=" * 60)
        
        while True:
            print("\nEscolha uma opção:")
            print("1. Verificar modo atual")
            print("2. Testar todos os modos FSM")
            print("3. Testar todos os comandos de braço")
            print("4. Testar comandos de locomoção")
            print("5. Testar modos MotionSwitcher")
            print("6. Obter lista de ações")
            print("7. Teste completo (todos)")
            print("0. Sair")
            
            choice = input("\nDigite sua escolha (0-7): ").strip()
            
            if choice == "0":
                print("👋 Saindo...")
                break
            elif choice == "1":
                self.check_current_mode()
            elif choice == "2":
                self.test_fsm_modes()
            elif choice == "3":
                self.test_arm_actions()
            elif choice == "4":
                self.test_loco_commands()
            elif choice == "5":
                self.test_motion_switcher_modes()
            elif choice == "6":
                self.get_action_list()
            elif choice == "7":
                print("🚀 Executando teste completo...")
                self.check_current_mode()
                self.test_fsm_modes()
                self.test_arm_actions()
                self.test_loco_commands()
                self.test_motion_switcher_modes()
                self.get_action_list()
            else:
                print("❌ Escolha inválida")

def main():
    """Função principal."""
    print("🤖 TESTE ABRANGENTE G1 - EXPLORANDO SDK")
    print("=" * 60)
    
    tester = G1ComprehensiveTester()
    
    if not tester.initialize_sdk():
        print("❌ Falha na inicialização do SDK")
        return
    
    print("\n✅ SDK inicializado com sucesso!")
    print("⚠️  ATENÇÃO: Certifique-se de que não há obstáculos ao redor do robô!")
    
    input("\nPressione Enter para continuar...")
    
    tester.interactive_menu()

if __name__ == "__main__":
    main()
