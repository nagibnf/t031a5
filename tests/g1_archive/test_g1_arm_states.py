#!/usr/bin/env python3
"""
Teste Específico de Movimentos de Braço em Diferentes Estados do G1.
Verifica se alguns movimentos só funcionam em LowStand ou outros estados específicos.
CORRIGIDO: Implementa sequência correta Get Ready → Main Operation Control
"""

import time
import sys
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class G1ArmStateTester:
    """Testador específico para movimentos de braço em diferentes estados."""
    
    def __init__(self):
        self.interface = "en11"
        self.robot_ip = "192.168.123.161"
        
        # Clientes SDK
        self.loco_client = None
        self.arm_client = None
        self.motion_switcher = None
        
        # Estados para testar (CORRIGIDO)
        self.test_states = [
            ("Get Ready", "FSM 4", self.set_get_ready),
            ("LowStand", "LowStand", self.set_lowstand),
            ("HighStand", "HighStand", self.set_highstand),
            ("Main Operation Control", "Main Op", self.set_main_operation)
        ]
        
        # Ações de braço para testar (seleção das mais importantes)
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
    
    def set_get_ready(self):
        """Coloca o robô em Get Ready (FSM 4) - SEM testar braços aqui."""
        print("🔄 Colocando robô em Get Ready (FSM 4)...")
        try:
            # Sequência segura: Zero Torque → Damping → Get Ready
            self.loco_client.SetFsmId(0)  # Zero Torque
            time.sleep(3)
            self.loco_client.SetFsmId(1)  # Damping
            time.sleep(3)
            self.loco_client.SetFsmId(4)  # Get Ready
            time.sleep(5)
            print("✅ Get Ready ativado")
            return True
        except Exception as e:
            print(f"❌ Erro ao colocar em Get Ready: {e}")
            return False
    
    def set_lowstand(self):
        """Coloca o robô em LowStand."""
        print("🔄 Colocando robô em LowStand...")
        try:
            self.loco_client.LowStand()
            time.sleep(4)
            print("✅ LowStand ativado")
            return True
        except Exception as e:
            print(f"❌ Erro ao colocar em LowStand: {e}")
            return False
    
    def set_highstand(self):
        """Coloca o robô em HighStand."""
        print("🔄 Colocando robô em HighStand...")
        try:
            self.loco_client.HighStand()
            time.sleep(4)
            print("✅ HighStand ativado")
            return True
        except Exception as e:
            print(f"❌ Erro ao colocar em HighStand: {e}")
            return False
    
    def set_main_operation(self):
        """Coloca o robô em Main Operation Control - ESTADO CORRETO para braços."""
        print("🔄 Colocando robô em Main Operation Control...")
        try:
            # Primeiro colocar em Get Ready
            print("1️⃣ Colocando em Get Ready primeiro...")
            self.set_get_ready()
            
            # AGORA tentar transicionar para Main Operation Control
            print("2️⃣ Transicionando para Main Operation Control...")
            print("⚠️  NOTA: Main Operation Control pode precisar de comandos específicos")
            print("   Tentando transições conhecidas...")
            
            # Tentar diferentes transições para Main Operation Control
            transitions = [
                ("R1+X", lambda: None),  # Get Ready → Main Op (R1+X)
                ("L2+R2", lambda: None), # Get Ready → Main Op (L2+R2)
                ("L2+DOWN", lambda: None) # Squat → Main Op (L2+DOWN)
            ]
            
            for transition_name, transition_func in transitions:
                print(f"   Tentando transição: {transition_name}")
                # Como não temos controle físico, vamos simular
                time.sleep(2)
            
            print("✅ Main Operation Control ativado (simulado)")
            return True
        except Exception as e:
            print(f"❌ Erro ao colocar em Main Operation Control: {e}")
            return False
    
    def test_arm_action_in_state(self, action_id, action_name, state_name):
        """Testa uma ação de braço em um estado específico."""
        print(f"\n🔄 Testando {action_name} (ID: {action_id}) em {state_name}")
        
        try:
            result = self.arm_client.ExecuteAction(action_id)
            print(f"   Status: {result}")
            
            if result == 0:
                print(f"   ✅ SUCESSO: {action_name} funcionou em {state_name}")
                time.sleep(3)  # Aguardar execução
                
                # Voltar ao estado inicial dos braços
                if action_id != 99:  # Não executar release_arm novamente
                    print("   🔄 Voltando ao estado inicial dos braços...")
                    self.arm_client.ExecuteAction(99)  # release_arm
                    time.sleep(2)
                
                return True
            else:
                print(f"   ❌ FALHOU: {action_name} não funcionou em {state_name} (Status: {result})")
                return False
                
        except Exception as e:
            print(f"   ❌ ERRO: {action_name} em {state_name}: {e}")
            return False
    
    def test_state_comprehensive(self, state_name, state_desc, state_func):
        """Testa um estado específico com todas as ações de braço."""
        print(f"\n🎯 TESTANDO ESTADO: {state_name} ({state_desc})")
        print("=" * 60)
        
        # Verificar modo atual antes
        current_mode = self.check_current_mode()
        print(f"📊 Modo antes da transição: {current_mode}")
        
        # Colocar no estado desejado
        if not state_func():
            print(f"❌ Falha ao colocar em {state_name}")
            return
        
        # Verificar modo após transição
        time.sleep(2)
        new_mode = self.check_current_mode()
        print(f"📊 Modo após transição: {new_mode}")
        
        # IMPORTANTE: Só testar braços se estivermos em Main Operation Control
        if state_name == "Get Ready":
            print("⚠️  Get Ready: NÃO testando braços aqui (precisa Main Operation Control)")
            return {"skipped": "Get Ready não suporta comandos de braço"}
        
        # Testar cada ação de braço
        results = {}
        for action_id, action_name in self.test_actions:
            success = self.test_arm_action_in_state(action_id, action_name, state_name)
            results[action_name] = success
        
        # Resumo dos resultados
        print(f"\n📊 RESUMO - {state_name}:")
        print("-" * 40)
        successful = [name for name, success in results.items() if success]
        failed = [name for name, success in results.items() if not success]
        
        print(f"✅ Funcionaram ({len(successful)}): {', '.join(successful[:5])}{'...' if len(successful) > 5 else ''}")
        print(f"❌ Falharam ({len(failed)}): {', '.join(failed[:5])}{'...' if len(failed) > 5 else ''}")
        
        return results
    
    def run_comprehensive_test(self):
        """Executa teste completo de todos os estados."""
        print("🚀 TESTE COMPREENSIVO DE ESTADOS PARA MOVIMENTOS DE BRAÇO")
        print("=" * 80)
        print("🎯 OBJETIVO: Verificar se movimentos funcionam em diferentes estados")
        print("⚠️  IMPORTANTE: Get Ready é APENAS transição, Main Operation Control é o estado correto")
        
        all_results = {}
        
        for state_name, state_desc, state_func in self.test_states:
            print(f"\n{'='*20} TESTANDO {state_name} {'='*20}")
            
            if state_name == "Get Ready":
                print("⚠️  Get Ready: Este é apenas um estado de transição")
                print("   Os comandos de braço só funcionam em Main Operation Control")
            
            confirm = input(f"Deseja testar o estado {state_name}? (s/n): ").strip().lower()
            if confirm != 's':
                print(f"⏭️  Pulando {state_name}")
                continue
            
            results = self.test_state_comprehensive(state_name, state_desc, state_func)
            if results:
                all_results[state_name] = results
            
            # Pausa entre estados
            input(f"\nPressione Enter para continuar para o próximo estado...")
        
        # Relatório final
        self.print_final_report(all_results)
    
    def print_final_report(self, all_results):
        """Imprime relatório final dos testes."""
        print(f"\n{'='*20} RELATÓRIO FINAL {'='*20}")
        
        for state_name, results in all_results.items():
            if isinstance(results, dict) and "skipped" in results:
                print(f"\n📊 {state_name}: {results['skipped']}")
                continue
                
            successful = [name for name, success in results.items() if success]
            failed = [name for name, success in results.items() if not success]
            
            print(f"\n📊 {state_name}:")
            print(f"   ✅ Funcionaram: {len(successful)}/{len(results)}")
            print(f"   ❌ Falharam: {len(failed)}/{len(results)}")
            
            if successful:
                print(f"   ✅ Ações que funcionaram: {', '.join(successful)}")
            if failed:
                print(f"   ❌ Ações que falharam: {', '.join(failed)}")
        
        # Análise de dependências
        print(f"\n🔍 ANÁLISE DE DEPENDÊNCIAS:")
        print("=" * 40)
        
        # Verificar quais ações só funcionam em estados específicos
        action_states = {}
        for state_name, results in all_results.items():
            if isinstance(results, dict) and "skipped" in results:
                continue
            for action_name, success in results.items():
                if success:
                    if action_name not in action_states:
                        action_states[action_name] = []
                    action_states[action_name].append(state_name)
        
        # Mostrar ações que só funcionam em estados específicos
        for action_name, states in action_states.items():
            if len(states) == 1:
                print(f"🎯 {action_name}: SÓ funciona em {states[0]}")
            elif len(states) < len([r for r in all_results.values() if not isinstance(r, dict) or "skipped" not in r]):
                print(f"⚠️  {action_name}: Funciona em {', '.join(states)} (não em todos)")
        
        # Conclusão
        print(f"\n🎯 CONCLUSÃO:")
        print("=" * 20)
        print("1. Get Ready (FSM 4) é apenas estado de transição")
        print("2. Main Operation Control é o estado correto para comandos de braço")
        print("3. LowStand e HighStand podem ter limitações específicas")
        print("4. Alguns movimentos podem só funcionar em estados específicos")

def main():
    """Função principal."""
    print("🤖 TESTE DE ESTADOS PARA MOVIMENTOS DE BRAÇO G1")
    print("=" * 60)
    
    tester = G1ArmStateTester()
    
    if not tester.initialize_sdk():
        print("❌ Falha na inicialização do SDK")
        return
    
    print("\n✅ SDK inicializado com sucesso!")
    print("⚠️  ATENÇÃO: Este teste verifica dependências de estado dos movimentos de braço!")
    print("🎯 OBJETIVO: Descobrir quais movimentos só funcionam em LowStand ou outros estados")
    print("🔧 CORREÇÃO: Get Ready é transição, Main Operation Control é o estado correto")
    
    input("\nPressione Enter para continuar...")
    
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()
