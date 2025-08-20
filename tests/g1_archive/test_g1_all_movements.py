#!/usr/bin/env python3
"""
Teste Interativo de Todos os Movimentos do G1.
Testa IDs de 0 a 100 para descobrir movimentos funcionais.
"""

import time
import sys
import json
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class G1MovementExplorer:
    """Explorador interativo de movimentos do G1."""
    
    def __init__(self):
        self.interface = "en11"
        self.robot_ip = "192.168.123.161"
        
        # Clientes SDK
        self.loco_client = None
        self.arm_client = None
        self.motion_switcher = None
        
        # Resultados
        self.discovered_movements = {}
        self.tested_ids = set()
        
        # IDs conhecidos para testar primeiro
        self.known_ids = [
            # FSM IDs
            0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
            200, 702, 706,
            # Arm Action IDs (conhecidos)
            99, 11, 12, 13, 15, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
            31, 32, 33, 34, 35
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
    
    def setup_main_operation_control(self):
        """Configura o robô para Main Operation Control."""
        print("🚀 CONFIGURANDO MAIN OPERATION CONTROL")
        print("=" * 50)
        
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
        
        print("4️⃣ Main Operation Control...")
        print("⚠️  IMPORTANTE: Para transicionar para Main Operation Control,")
        print("   você precisa usar o controle físico:")
        print("   - R1+X (do Get Ready)")
        
        # Aguardar confirmação do usuário
        input("\n🎮 Use o controle físico para transicionar para Main Operation Control, depois pressione Enter...")
        
        print("✅ Main Operation Control configurado!")
        return True
    
    def test_fsm_id(self, fsm_id):
        """Testa um ID de FSM."""
        print(f"\n🔄 Testando FSM ID: {fsm_id}")
        
        try:
            result = self.loco_client.SetFsmId(fsm_id)
            print(f"   Status: {result}")
            
            if result == 0:
                print(f"   ✅ FSM ID {fsm_id} executado com sucesso!")
                return True
            else:
                print(f"   ❌ FSM ID {fsm_id} falhou (Status: {result})")
                return False
                
        except Exception as e:
            print(f"   ❌ ERRO: FSM ID {fsm_id}: {e}")
            return False
    
    def test_arm_action_id(self, action_id):
        """Testa um ID de ação de braço."""
        print(f"\n🔄 Testando Arm Action ID: {action_id}")
        
        try:
            result = self.arm_client.ExecuteAction(action_id)
            print(f"   Status: {result}")
            
            if result == 0:
                print(f"   ✅ Arm Action ID {action_id} executado com sucesso!")
                return True
            else:
                print(f"   ❌ Arm Action ID {action_id} falhou (Status: {result})")
                return False
                
        except Exception as e:
            print(f"   ❌ ERRO: Arm Action ID {action_id}: {e}")
            return False
    
    def test_id_interactive(self, test_id, test_type="arm"):
        """Testa um ID interativamente."""
        print(f"\n{'='*60}")
        print(f"🎯 TESTANDO {test_type.upper()} ID: {test_id}")
        print(f"{'='*60}")
        
        # Executar o teste
        if test_type == "fsm":
            success = self.test_fsm_id(test_id)
        else:  # arm
            success = self.test_arm_action_id(test_id)
        
        if success:
            # Aguardar execução
            print(f"⏳ Aguardando execução do movimento...")
            time.sleep(3)
            
            # Perguntar se funcionou
            while True:
                response = input(f"\n❓ O movimento {test_type.upper()} ID {test_id} funcionou? (s/n): ").strip().lower()
                
                if response in ['s', 'sim', 'y', 'yes']:
                    # Pedir nome do movimento
                    name = input(f"📝 Qual é o nome deste movimento? ").strip()
                    
                    # Salvar resultado
                    self.discovered_movements[test_id] = {
                        "type": test_type,
                        "name": name,
                        "status": "working"
                    }
                    
                    print(f"✅ Movimento salvo: {test_type.upper()} ID {test_id} = '{name}'")
                    
                    # Voltar ao estado inicial se for arm action
                    if test_type == "arm" and test_id != 99:
                        print("🔄 Voltando ao estado inicial dos braços...")
                        self.arm_client.ExecuteAction(99)  # release_arm
                        time.sleep(2)
                    
                    return True
                    
                elif response in ['n', 'não', 'nao', 'no']:
                    # Salvar como não funcionou
                    self.discovered_movements[test_id] = {
                        "type": test_type,
                        "name": "unknown",
                        "status": "failed"
                    }
                    print(f"❌ Movimento {test_type.upper()} ID {test_id} marcado como não funcional")
                    return False
                    
                else:
                    print("❌ Resposta inválida. Digite 's' para sim ou 'n' para não.")
        
        else:
            # Se falhou na execução, marcar como falha
            self.discovered_movements[test_id] = {
                "type": test_type,
                "name": "unknown",
                "status": "execution_failed"
            }
            print(f"❌ Movimento {test_type.upper()} ID {test_id} falhou na execução")
            return False
    
    def test_range_interactive(self, start_id, end_id, test_type="arm"):
        """Testa um range de IDs interativamente."""
        print(f"\n🎯 TESTANDO RANGE: {test_type.upper()} IDs {start_id} a {end_id}")
        print("=" * 60)
        
        for test_id in range(start_id, end_id + 1):
            if test_id in self.tested_ids:
                print(f"⏭️  ID {test_id} já testado, pulando...")
                continue
            
            self.tested_ids.add(test_id)
            
            # Perguntar se quer testar este ID
            response = input(f"\n❓ Testar {test_type.upper()} ID {test_id}? (s/n/q para sair): ").strip().lower()
            
            if response in ['q', 'quit', 'sair', 'exit']:
                print("🛑 Teste interrompido pelo usuário")
                break
            elif response in ['n', 'não', 'nao', 'no']:
                print(f"⏭️  Pulando ID {test_id}")
                continue
            elif response in ['s', 'sim', 'y', 'yes']:
                self.test_id_interactive(test_id, test_type)
            else:
                print("❌ Resposta inválida. Digite 's' para sim, 'n' para não, ou 'q' para sair.")
                continue
            
            # Pausa entre testes
            input(f"\nPressione Enter para continuar...")
    
    def test_known_ids(self):
        """Testa IDs conhecidos primeiro."""
        print("🎯 TESTANDO IDs CONHECIDOS")
        print("=" * 40)
        
        # Testar FSM IDs primeiro
        fsm_ids = [id for id in self.known_ids if id < 100 or id in [200, 702, 706]]
        arm_ids = [id for id in self.known_ids if id >= 10 and id not in [200, 702, 706]]
        
        print(f"📋 FSM IDs para testar: {fsm_ids}")
        print(f"📋 Arm Action IDs para testar: {arm_ids}")
        
        # Testar FSM IDs
        for fsm_id in fsm_ids:
            if fsm_id not in self.tested_ids:
                self.tested_ids.add(fsm_id)
                self.test_id_interactive(fsm_id, "fsm")
                input(f"\nPressione Enter para continuar...")
        
        # Testar Arm Action IDs
        for arm_id in arm_ids:
            if arm_id not in self.tested_ids:
                self.tested_ids.add(arm_id)
                self.test_id_interactive(arm_id, "arm")
                input(f"\nPressione Enter para continuar...")
    
    def save_results(self):
        """Salva os resultados descobertos."""
        results_file = "g1_discovered_movements.json"
        
        # Organizar resultados
        organized_results = {
            "discovered_movements": self.discovered_movements,
            "tested_ids": list(self.tested_ids),
            "summary": {
                "total_tested": len(self.tested_ids),
                "working_movements": len([m for m in self.discovered_movements.values() if m["status"] == "working"]),
                "failed_movements": len([m for m in self.discovered_movements.values() if m["status"] != "working"])
            }
        }
        
        # Salvar em JSON
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(organized_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados salvos em: {results_file}")
        
        # Mostrar resumo
        print(f"\n📊 RESUMO DOS TESTES:")
        print("=" * 30)
        print(f"Total testado: {organized_results['summary']['total_tested']}")
        print(f"Movimentos funcionais: {organized_results['summary']['working_movements']}")
        print(f"Movimentos que falharam: {organized_results['summary']['failed_movements']}")
        
        # Mostrar movimentos funcionais
        working = [f"{id}: {data['name']}" for id, data in self.discovered_movements.items() if data["status"] == "working"]
        if working:
            print(f"\n✅ MOVIMENTOS FUNCIONAIS:")
            for movement in working:
                print(f"   {movement}")
    
    def run_exploration(self):
        """Executa a exploração completa."""
        print("🔍 EXPLORADOR DE MOVIMENTOS G1")
        print("=" * 60)
        
        # Configurar Main Operation Control
        if not self.setup_main_operation_control():
            print("❌ Falha ao configurar Main Operation Control")
            return
        
        # Testar IDs conhecidos primeiro
        print("\n🎯 FASE 1: TESTANDO IDs CONHECIDOS")
        self.test_known_ids()
        
        # Perguntar se quer testar range personalizado
        while True:
            print(f"\n🎯 FASE 2: TESTE DE RANGE PERSONALIZADO")
            print("=" * 50)
            
            try:
                start_id = int(input("Digite o ID inicial para testar (ou 0 para sair): "))
                if start_id == 0:
                    break
                
                end_id = int(input("Digite o ID final para testar: "))
                test_type = input("Tipo de teste (fsm/arm): ").strip().lower()
                
                if test_type not in ['fsm', 'arm']:
                    test_type = 'arm'  # padrão
                
                self.test_range_interactive(start_id, end_id, test_type)
                
            except ValueError:
                print("❌ ID inválido. Digite um número.")
            except KeyboardInterrupt:
                print("\n🛑 Teste interrompido pelo usuário")
                break
        
        # Salvar resultados
        self.save_results()

def main():
    """Função principal."""
    print("🔍 EXPLORADOR DE MOVIMENTOS G1")
    print("=" * 60)
    
    explorer = G1MovementExplorer()
    
    if not explorer.initialize_sdk():
        print("❌ Falha na inicialização do SDK")
        return
    
    print("\n✅ SDK inicializado com sucesso!")
    print("🎯 OBJETIVO: Descobrir todos os movimentos funcionais do G1")
    print("⚠️  IMPORTANTE: Você precisará usar o controle físico para Main Operation Control")
    
    input("\nPressione Enter para continuar...")
    
    explorer.run_exploration()

if __name__ == "__main__":
    main()
