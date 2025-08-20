#!/usr/bin/env python3
"""
Teste Específico para Main Operation Control - Estado Correto para Comandos de Braço.
Implementa a sequência correta: Get Ready → Main Operation Control
"""

import time
import sys
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class G1MainOperationTester:
    """Testador específico para Main Operation Control."""
    
    def __init__(self):
        self.interface = "en11"
        self.robot_ip = "192.168.123.161"
        
        # Clientes SDK
        self.loco_client = None
        self.arm_client = None
        self.motion_switcher = None
        
        # Ações de braço para testar
        self.test_actions = [
            (99, "release_arm"),
            (11, "blow_kiss_with_both_hands_50hz"),
            (12, "blow_kiss_with_left_hand"),
            (13, "blow_kiss_with_right_hand"),
            (15, "both_hands_up"),
            (17, "clamp"),
            (18, "high_five_opt"),
            (19, "hug_opt"),
            (22, "refuse"),
            (23, "right_hand_up"),
            (24, "ultraman_ray"),
            (25, "wave_under_head"),
            (26, "wave_above_head"),
            (27, "shake_hand_opt"),
            (31, "extend_right_arm_forward"),
            (32, "right_hand_on_mouth"),
            (33, "right_hand_on_heart"),
            (34, "both_hands_up_deviate_right"),
            (35, "emphasize")
        ]
    
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
    
    def setup_main_operation_control(self):
        """Configura o robô para Main Operation Control - ESTADO CORRETO para braços."""
        print("🚀 CONFIGURANDO MAIN OPERATION CONTROL")
        print("=" * 50)
        
        # Verificar estado inicial
        print("📊 Estado inicial:")
        initial_mode = self.check_current_mode()
        
        # Sequência correta: Zero Torque → Damping → Get Ready → Main Operation Control
        print("\n1️⃣ Zero Torque (FSM 0)...")
        self.loco_client.SetFsmId(0)
        time.sleep(3)
        
        print("2️⃣ Damping (FSM 1)...")
        self.loco_client.SetFsmId(1)
        time.sleep(3)
        
        print("3️⃣ Get Ready (FSM 4)...")
        self.loco_client.SetFsmId(4)
        time.sleep(5)
        
        # Verificar se estamos em Get Ready
        get_ready_mode = self.check_current_mode()
        print(f"📊 Modo após Get Ready: {get_ready_mode}")
        
        print("4️⃣ Main Operation Control...")
        print("⚠️  IMPORTANTE: Para transicionar para Main Operation Control,")
        print("   você precisa usar o controle físico:")
        print("   - R1+X (do Get Ready)")
        print("   - L2+R2 (do Get Ready)")
        print("   - L2+DOWN (do Squat)")
        
        # Aguardar confirmação do usuário
        input("\n🎮 Use o controle físico para transicionar para Main Operation Control, depois pressione Enter...")
        
        # Verificar estado final
        final_mode = self.check_current_mode()
        print(f"📊 Modo após transição: {final_mode}")
        
        return True
    
    def test_arm_action(self, action_id, action_name):
        """Testa uma ação de braço específica."""
        print(f"\n🔄 Testando {action_name} (ID: {action_id})")
        
        try:
            result = self.arm_client.ExecuteAction(action_id)
            print(f"   Status: {result}")
            
            if result == 0:
                print(f"   ✅ SUCESSO: {action_name} funcionou!")
                time.sleep(3)  # Aguardar execução
                
                # Voltar ao estado inicial dos braços
                if action_id != 99:  # Não executar release_arm novamente
                    print("   🔄 Voltando ao estado inicial dos braços...")
                    self.arm_client.ExecuteAction(99)  # release_arm
                    time.sleep(2)
                
                return True
            else:
                print(f"   ❌ FALHOU: {action_name} (Status: {result})")
                return False
                
        except Exception as e:
            print(f"   ❌ ERRO: {action_name}: {e}")
            return False
    
    def test_all_arm_actions(self):
        """Testa todas as ações de braço em Main Operation Control."""
        print("\n🎯 TESTANDO TODAS AS AÇÕES DE BRAÇO")
        print("=" * 50)
        
        results = {}
        
        for action_id, action_name in self.test_actions:
            success = self.test_arm_action(action_id, action_name)
            results[action_name] = success
            
            # Pausa entre ações
            input(f"\nPressione Enter para testar próxima ação...")
        
        return results
    
    def print_results(self, results):
        """Imprime resultados dos testes."""
        print(f"\n{'='*20} RESULTADOS FINAIS {'='*20}")
        
        successful = [name for name, success in results.items() if success]
        failed = [name for name, success in results.items() if not success]
        
        print(f"✅ AÇÕES QUE FUNCIONARAM ({len(successful)}):")
        for action in successful:
            print(f"   ✅ {action}")
        
        print(f"\n❌ AÇÕES QUE FALHARAM ({len(failed)}):")
        for action in failed:
            print(f"   ❌ {action}")
        
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"   Total testado: {len(results)}")
        print(f"   Sucessos: {len(successful)} ({len(successful)/len(results)*100:.1f}%)")
        print(f"   Falhas: {len(failed)} ({len(failed)/len(results)*100:.1f}%)")
        
        # Análise de dependências
        if failed:
            print(f"\n🔍 ANÁLISE DE FALHAS:")
            print("   Possíveis causas:")
            print("   - Algumas ações podem precisar de estados específicos (LowStand, HighStand)")
            print("   - Algumas ações podem estar desabilitadas")
            print("   - Algumas ações podem precisar de configurações adicionais")
    
    def run_test(self):
        """Executa o teste completo."""
        print("🤖 TESTE MAIN OPERATION CONTROL - COMANDOS DE BRAÇO")
        print("=" * 60)
        
        # Configurar Main Operation Control
        if not self.setup_main_operation_control():
            print("❌ Falha ao configurar Main Operation Control")
            return
        
        # Confirmar se está pronto para testar
        print("\n🎯 PRONTO PARA TESTAR COMANDOS DE BRAÇO")
        print("⚠️  Certifique-se de que o robô está em Main Operation Control")
        
        confirm = input("Deseja testar todos os comandos de braço? (s/n): ").strip().lower()
        if confirm != 's':
            print("❌ Teste cancelado")
            return
        
        # Testar todas as ações
        results = self.test_all_arm_actions()
        
        # Mostrar resultados
        self.print_results(results)

def main():
    """Função principal."""
    print("🤖 TESTE MAIN OPERATION CONTROL G1")
    print("=" * 60)
    
    tester = G1MainOperationTester()
    
    if not tester.initialize_sdk():
        print("❌ Falha na inicialização do SDK")
        return
    
    print("\n✅ SDK inicializado com sucesso!")
    print("🎯 OBJETIVO: Testar comandos de braço em Main Operation Control")
    print("⚠️  IMPORTANTE: Você precisará usar o controle físico para transicionar")
    
    input("\nPressione Enter para continuar...")
    
    tester.run_test()

if __name__ == "__main__":
    main()
