#!/usr/bin/env python3
"""
Teste Seguro e Individual do G1 - Um comando por vez com controle de tempo.
Baseado na pesquisa do SDK oficial da Unitree.
"""

import time
import sys
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class G1SafeTester:
    """Testador seguro do G1 - um comando por vez."""
    
    def __init__(self):
        self.interface = "en11"
        self.robot_ip = "192.168.123.161"
        
        # Clientes SDK
        self.loco_client = None
        self.arm_client = None
        self.motion_switcher = None
        
        # Tempos de transição (em segundos)
        self.transition_times = {
            "damp": 3.0,
            "start": 5.0,
            "sit": 8.0,
            "zerotorque": 2.0,
            "highstand": 4.0,
            "lowstand": 4.0,
            "fsm_0": 3.0,
            "fsm_1": 3.0,
            "fsm_2": 5.0,
            "fsm_3": 8.0,
            "fsm_4": 5.0,
            "fsm_200": 5.0,
            "fsm_702": 10.0,
            "fsm_706": 8.0,
            "arm_action": 5.0
        }
        
        # Ações de braço com IDs corretos
        self.arm_actions = {
            99: "release_arm",
            1: "turn_back_wave", 
            11: "blow_kiss_with_both_hands_50hz",
            12: "blow_kiss_with_left_hand",
            13: "blow_kiss_with_right_hand",
            15: "both_hands_up",
            17: "clamp",
            18: "high_five_opt",
            19: "hug_opt",
            22: "refuse",
            23: "right_hand_up",
            24: "ultraman_ray",
            25: "wave_under_head",
            26: "wave_above_head",
            27: "shake_hand_opt",
            31: "extend_right_arm_forward",
            32: "right_hand_on_mouth",
            33: "right_hand_on_heart",
            34: "both_hands_up_deviate_right",
            35: "emphasize"
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
    
    def safe_command(self, command_name, command_func, wait_time=None):
        """Executa um comando de forma segura com confirmação."""
        print(f"\n🔄 Preparando para executar: {command_name}")
        print("⚠️  ATENÇÃO: Certifique-se de que não há obstáculos ao redor do robô!")
        
        confirm = input(f"Deseja executar '{command_name}'? (s/n): ").strip().lower()
        if confirm != 's':
            print("❌ Comando cancelado pelo usuário")
            return False
        
        try:
            print(f"🚀 Executando: {command_name}")
            result = command_func()
            print(f"✅ Resultado: {result}")
            
            if wait_time:
                print(f"⏳ Aguardando {wait_time} segundos para conclusão...")
                time.sleep(wait_time)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao executar {command_name}: {e}")
            return False
    
    def test_fsm_mode(self, fsm_id, mode_name):
        """Testa um modo FSM específico."""
        def fsm_command():
            return self.loco_client.SetFsmId(fsm_id)
        
        wait_time = self.transition_times.get(f"fsm_{fsm_id}", 5.0)
        return self.safe_command(f"FSM {fsm_id} ({mode_name})", fsm_command, wait_time)
    
    def test_loco_command(self, command_name, command_func):
        """Testa um comando de locomoção específico."""
        wait_time = self.transition_times.get(command_name, 5.0)
        return self.safe_command(command_name, command_func, wait_time)
    
    def test_arm_action(self, action_id, action_name):
        """Testa uma ação de braço específica."""
        def arm_command():
            return self.arm_client.ExecuteAction(action_id)
        
        wait_time = self.transition_times.get("arm_action", 5.0)
        success = self.safe_command(f"Braço {action_id} ({action_name})", arm_command, wait_time)
        
        if success and action_id != 99:  # Não executar release_arm novamente
            print("🔄 Voltando ao estado inicial dos braços...")
            time.sleep(1)
            self.arm_client.ExecuteAction(99)  # release_arm
            time.sleep(2)
        
        return success
    
    def interactive_menu(self):
        """Menu interativo para testes seguros."""
        print("\n🎯 MENU INTERATIVO - TESTE SEGURO G1")
        print("=" * 60)
        
        while True:
            print("\nEscolha uma categoria:")
            print("1. Verificar modo atual")
            print("2. Testar modos FSM (um por vez)")
            print("3. Testar comandos de locomoção (um por vez)")
            print("4. Testar ações de braço (um por vez)")
            print("5. Sequência segura básica")
            print("0. Sair")
            
            choice = input("\nDigite sua escolha (0-5): ").strip()
            
            if choice == "0":
                print("👋 Saindo...")
                break
            elif choice == "1":
                self.check_current_mode()
            elif choice == "2":
                self.menu_fsm_modes()
            elif choice == "3":
                self.menu_loco_commands()
            elif choice == "4":
                self.menu_arm_actions()
            elif choice == "5":
                self.safe_sequence()
            else:
                print("❌ Escolha inválida")
    
    def menu_fsm_modes(self):
        """Menu para testar modos FSM."""
        fsm_modes = {
            0: "Zero Torque",
            1: "Damping",
            2: "Squat", 
            3: "Seat",
            4: "Get Ready",
            200: "Start",
            702: "Lie2StandUp",
            706: "Squat2StandUp"
        }
        
        print("\n🤖 MODOS FSM DISPONÍVEIS:")
        for fsm_id, mode_name in fsm_modes.items():
            print(f"  {fsm_id}: {mode_name}")
        
        fsm_id = input("\nDigite o ID do FSM para testar (ou 'voltar'): ").strip()
        if fsm_id.lower() == 'voltar':
            return
        
        try:
            fsm_id = int(fsm_id)
            if fsm_id in fsm_modes:
                self.test_fsm_mode(fsm_id, fsm_modes[fsm_id])
            else:
                print("❌ ID FSM inválido")
        except ValueError:
            print("❌ ID deve ser um número")
    
    def menu_loco_commands(self):
        """Menu para testar comandos de locomoção."""
        loco_commands = [
            ("damp", lambda: self.loco_client.Damp()),
            ("start", lambda: self.loco_client.Start()),
            ("sit", lambda: self.loco_client.Sit()),
            ("zerotorque", lambda: self.loco_client.ZeroTorque()),
            ("highstand", lambda: self.loco_client.HighStand()),
            ("lowstand", lambda: self.loco_client.LowStand())
        ]
        
        print("\n🤖 COMANDOS DE LOCOMOÇÃO DISPONÍVEIS:")
        for i, (cmd_name, _) in enumerate(loco_commands, 1):
            print(f"  {i}: {cmd_name}")
        
        choice = input("\nDigite o número do comando (ou 'voltar'): ").strip()
        if choice.lower() == 'voltar':
            return
        
        try:
            choice = int(choice)
            if 1 <= choice <= len(loco_commands):
                cmd_name, cmd_func = loco_commands[choice - 1]
                self.test_loco_command(cmd_name, cmd_func)
            else:
                print("❌ Escolha inválida")
        except ValueError:
            print("❌ Escolha deve ser um número")
    
    def menu_arm_actions(self):
        """Menu para testar ações de braço."""
        print("\n🤖 AÇÕES DE BRAÇO DISPONÍVEIS:")
        for action_id, action_name in self.arm_actions.items():
            print(f"  {action_id}: {action_name}")
        
        action_id = input("\nDigite o ID da ação para testar (ou 'voltar'): ").strip()
        if action_id.lower() == 'voltar':
            return
        
        try:
            action_id = int(action_id)
            if action_id in self.arm_actions:
                self.test_arm_action(action_id, self.arm_actions[action_id])
            else:
                print("❌ ID de ação inválido")
        except ValueError:
            print("❌ ID deve ser um número")
    
    def safe_sequence(self):
        """Sequência segura básica para testar."""
        print("\n🚀 SEQUÊNCIA SEGURA BÁSICA")
        print("=" * 40)
        print("Esta sequência testa: Damp -> Start -> HighStand")
        print("Com tempos adequados entre cada comando")
        
        confirm = input("Deseja executar a sequência segura? (s/n): ").strip().lower()
        if confirm != 's':
            print("❌ Sequência cancelada")
            return
        
        # Sequência segura
        print("\n1️⃣ Executando Damp...")
        self.loco_client.Damp()
        time.sleep(3)
        
        print("\n2️⃣ Executando Start...")
        self.loco_client.Start()
        time.sleep(5)
        
        print("\n3️⃣ Executando HighStand...")
        self.loco_client.HighStand()
        time.sleep(4)
        
        print("✅ Sequência segura concluída!")

def main():
    """Função principal."""
    print("🤖 TESTE SEGURO E INDIVIDUAL G1")
    print("=" * 60)
    
    tester = G1SafeTester()
    
    if not tester.initialize_sdk():
        print("❌ Falha na inicialização do SDK")
        return
    
    print("\n✅ SDK inicializado com sucesso!")
    print("⚠️  ATENÇÃO: Este teste é SEGURO - um comando por vez com confirmação!")
    
    input("\nPressione Enter para continuar...")
    
    tester.interactive_menu()

if __name__ == "__main__":
    main()
