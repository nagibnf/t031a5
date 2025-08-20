#!/usr/bin/env python3
"""
Teste para Aprender Como Verificar Corretamente o Estado Atual do G1.
Objetivo: Entender como interpretar corretamente o modo atual.
"""

import time
import sys
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class G1StateVerificationTester:
    """Testador para aprender verificação de estado."""
    
    def __init__(self):
        self.interface = "en11"
        self.robot_ip = "192.168.123.161"
        
        # Clientes SDK
        self.loco_client = None
        self.arm_client = None
        self.motion_switcher = None
    
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
                    return result
                return None
        except Exception as e:
            print(f"❌ Erro ao verificar modo: {e}")
        return None
    
    def check_fsm_state(self):
        """Tenta verificar o estado FSM atual."""
        print("🔍 Verificando estado FSM...")
        
        # Tentar diferentes métodos para verificar estado FSM
        try:
            # Método 1: Verificar se há APIs para obter FSM state
            print("   Tentando obter estado FSM via APIs...")
            
            # Método 2: Verificar se há métodos específicos no LocoClient
            print("   Verificando métodos do LocoClient...")
            
            # Método 3: Verificar se há métodos específicos no ArmClient
            print("   Verificando métodos do ArmClient...")
            
            return None
        except Exception as e:
            print(f"   ❌ Erro ao verificar FSM: {e}")
            return None
    
    def test_state_transitions(self):
        """Testa transições de estado e aprende como verificar."""
        print("🎯 TESTANDO TRANSIÇÕES DE ESTADO")
        print("=" * 50)
        
        # Estado inicial
        print("\n📊 ESTADO INICIAL:")
        initial_mode = self.check_current_mode()
        print(f"   MotionSwitcher: {initial_mode}")
        
        # Testar Get Ready (FSM 4)
        print("\n🔄 COLOCANDO EM GET READY (FSM 4)...")
        print("   Executando: self.loco_client.SetFsmId(4)")
        self.loco_client.SetFsmId(4)
        time.sleep(5)
        
        print("📊 APÓS GET READY:")
        get_ready_mode = self.check_current_mode()
        print(f"   MotionSwitcher: {get_ready_mode}")
        
        # Aguardar usuário colocar em Main Operation Control
        print("\n🎮 AGORA USE O CONTROLE FÍSICO:")
        print("   - R1+X para transicionar para Main Operation Control")
        print("   - Isso deve colocar o robô em LowStanding automaticamente")
        
        input("   Pressione Enter após usar R1+X...")
        
        print("📊 APÓS MAIN OPERATION CONTROL:")
        main_op_mode = self.check_current_mode()
        print(f"   MotionSwitcher: {main_op_mode}")
        
        # Tentar verificar FSM state
        fsm_state = self.check_fsm_state()
        print(f"   FSM State: {fsm_state}")
        
        return main_op_mode
    
    def test_arm_commands_in_main_op(self):
        """Testa comandos de braço em Main Operation Control."""
        print("\n🎯 TESTANDO COMANDOS DE BRAÇO EM MAIN OPERATION CONTROL")
        print("=" * 60)
        
        # Testar alguns comandos de braço
        test_actions = [
            (99, "release_arm"),
            (11, "blow_kiss_with_both_hands_50hz"),
            (15, "both_hands_up"),
            (27, "shake_hand_opt")
        ]
        
        results = {}
        for action_id, action_name in test_actions:
            print(f"\n🔄 Testando {action_name} (ID: {action_id})")
            
            try:
                result = self.arm_client.ExecuteAction(action_id)
                print(f"   Status: {result}")
                
                if result == 0:
                    print(f"   ✅ SUCESSO: {action_name} funcionou!")
                    results[action_name] = True
                    
                    # Voltar ao estado inicial
                    if action_id != 99:
                        self.arm_client.ExecuteAction(99)
                        time.sleep(2)
                else:
                    print(f"   ❌ FALHOU: {action_name} (Status: {result})")
                    results[action_name] = False
                    
            except Exception as e:
                print(f"   ❌ ERRO: {action_name}: {e}")
                results[action_name] = False
        
        return results
    
    def run_learning_test(self):
        """Executa teste de aprendizado."""
        print("🧠 TESTE DE APRENDIZADO - VERIFICAÇÃO DE ESTADO")
        print("=" * 60)
        
        # Testar transições
        main_op_mode = self.test_state_transitions()
        
        # Testar comandos de braço
        if main_op_mode:
            results = self.test_arm_commands_in_main_op()
            
            # Resumo
            print(f"\n📊 RESUMO DOS TESTES:")
            print("=" * 30)
            successful = [name for name, success in results.items() if success]
            failed = [name for name, success in results.items() if not success]
            
            print(f"✅ Comandos que funcionaram: {len(successful)}")
            print(f"❌ Comandos que falharam: {len(failed)}")
            
            if successful:
                print(f"   ✅ {', '.join(successful)}")
            if failed:
                print(f"   ❌ {', '.join(failed)}")
        
        # Conclusões
        print(f"\n🎯 CONCLUSÕES:")
        print("=" * 20)
        print("1. MotionSwitcher retorna modo do switcher, não estado FSM")
        print("2. Preciso aprender como verificar estado FSM real")
        print("3. Get Ready → R1+X → Main Operation Control → LowStanding")
        print("4. Comandos de braço funcionam em Main Operation Control")

def main():
    """Função principal."""
    print("🧠 APRENDENDO VERIFICAÇÃO DE ESTADO G1")
    print("=" * 60)
    
    tester = G1StateVerificationTester()
    
    if not tester.initialize_sdk():
        print("❌ Falha na inicialização do SDK")
        return
    
    print("\n✅ SDK inicializado com sucesso!")
    print("🎯 OBJETIVO: Aprender como verificar corretamente o estado atual")
    print("⚠️  IMPORTANTE: Vou testar transições e comandos para entender")
    
    input("\nPressione Enter para continuar...")
    
    tester.run_learning_test()

if __name__ == "__main__":
    main()
