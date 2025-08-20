#!/usr/bin/env python3
"""
Teste Rápido de Range de IDs do G1.
Para testar ranges específicos rapidamente.
"""

import time
import sys
import json
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class G1QuickRangeTester:
    """Testador rápido de range de IDs."""
    
    def __init__(self):
        self.interface = "en11"
        self.robot_ip = "192.168.123.161"
        
        # Clientes SDK
        self.loco_client = None
        self.arm_client = None
        self.motion_switcher = None
        
        # Resultados
        self.results = {}
    
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
    
    def test_arm_range(self, start_id, end_id):
        """Testa um range de IDs de braço rapidamente."""
        print(f"\n🎯 TESTANDO ARM RANGE: {start_id} a {end_id}")
        print("=" * 50)
        
        for test_id in range(start_id, end_id + 1):
            print(f"\n🔄 Testando Arm Action ID: {test_id}")
            
            try:
                result = self.arm_client.ExecuteAction(test_id)
                print(f"   Status: {result}")
                
                if result == 0:
                    print(f"   ✅ Arm Action ID {test_id} executado com sucesso!")
                    
                    # Aguardar execução
                    time.sleep(2)
                    
                    # Perguntar se funcionou
                    response = input(f"   ❓ Funcionou? (s/n): ").strip().lower()
                    
                    if response in ['s', 'sim', 'y', 'yes']:
                        name = input(f"   📝 Nome do movimento: ").strip()
                        self.results[test_id] = {
                            "type": "arm",
                            "name": name,
                            "status": "working"
                        }
                        print(f"   ✅ Salvo: {test_id} = '{name}'")
                    else:
                        self.results[test_id] = {
                            "type": "arm",
                            "name": "unknown",
                            "status": "failed"
                        }
                        print(f"   ❌ Marcado como falha")
                    
                    # Voltar ao estado inicial
                    if test_id != 99:
                        self.arm_client.ExecuteAction(99)  # release_arm
                        time.sleep(1)
                else:
                    print(f"   ❌ Arm Action ID {test_id} falhou (Status: {result})")
                    self.results[test_id] = {
                        "type": "arm",
                        "name": "unknown",
                        "status": "execution_failed"
                    }
                    
            except Exception as e:
                print(f"   ❌ ERRO: Arm Action ID {test_id}: {e}")
                self.results[test_id] = {
                    "type": "arm",
                    "name": "unknown",
                    "status": "error"
                }
            
            # Pausa entre testes
            input(f"   Pressione Enter para continuar...")
    
    def test_fsm_range(self, start_id, end_id):
        """Testa um range de IDs de FSM rapidamente."""
        print(f"\n🎯 TESTANDO FSM RANGE: {start_id} a {end_id}")
        print("=" * 50)
        
        for test_id in range(start_id, end_id + 1):
            print(f"\n🔄 Testando FSM ID: {test_id}")
            
            try:
                result = self.loco_client.SetFsmId(test_id)
                print(f"   Status: {result}")
                
                if result == 0:
                    print(f"   ✅ FSM ID {test_id} executado com sucesso!")
                    
                    # Aguardar execução
                    time.sleep(3)
                    
                    # Perguntar se funcionou
                    response = input(f"   ❓ Funcionou? (s/n): ").strip().lower()
                    
                    if response in ['s', 'sim', 'y', 'yes']:
                        name = input(f"   📝 Nome do estado: ").strip()
                        self.results[test_id] = {
                            "type": "fsm",
                            "name": name,
                            "status": "working"
                        }
                        print(f"   ✅ Salvo: {test_id} = '{name}'")
                    else:
                        self.results[test_id] = {
                            "type": "fsm",
                            "name": "unknown",
                            "status": "failed"
                        }
                        print(f"   ❌ Marcado como falha")
                else:
                    print(f"   ❌ FSM ID {test_id} falhou (Status: {result})")
                    self.results[test_id] = {
                        "type": "fsm",
                        "name": "unknown",
                        "status": "execution_failed"
                    }
                    
            except Exception as e:
                print(f"   ❌ ERRO: FSM ID {test_id}: {e}")
                self.results[test_id] = {
                    "type": "fsm",
                    "name": "unknown",
                    "status": "error"
                }
            
            # Pausa entre testes
            input(f"   Pressione Enter para continuar...")
    
    def save_results(self):
        """Salva os resultados."""
        results_file = "g1_quick_test_results.json"
        
        # Organizar resultados
        organized_results = {
            "results": self.results,
            "summary": {
                "total_tested": len(self.results),
                "working_movements": len([m for m in self.results.values() if m["status"] == "working"]),
                "failed_movements": len([m for m in self.results.values() if m["status"] != "working"])
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
        working = [f"{id}: {data['name']}" for id, data in self.results.items() if data["status"] == "working"]
        if working:
            print(f"\n✅ MOVIMENTOS FUNCIONAIS:")
            for movement in working:
                print(f"   {movement}")
    
    def run_quick_test(self):
        """Executa teste rápido."""
        print("⚡ TESTE RÁPIDO DE RANGE G1")
        print("=" * 60)
        
        # Configurar Main Operation Control
        if not self.setup_main_operation_control():
            print("❌ Falha ao configurar Main Operation Control")
            return
        
        # Perguntar range para testar
        try:
            start_id = int(input("\nDigite o ID inicial: "))
            end_id = int(input("Digite o ID final: "))
            test_type = input("Tipo de teste (fsm/arm): ").strip().lower()
            
            if test_type not in ['fsm', 'arm']:
                test_type = 'arm'  # padrão
            
            print(f"\n🎯 Iniciando teste: {test_type.upper()} IDs {start_id} a {end_id}")
            
            if test_type == "fsm":
                self.test_fsm_range(start_id, end_id)
            else:
                self.test_arm_range(start_id, end_id)
            
            # Salvar resultados
            self.save_results()
            
        except ValueError:
            print("❌ ID inválido. Digite um número.")
        except KeyboardInterrupt:
            print("\n🛑 Teste interrompido pelo usuário")

def main():
    """Função principal."""
    print("⚡ TESTE RÁPIDO DE RANGE G1")
    print("=" * 60)
    
    tester = G1QuickRangeTester()
    
    if not tester.initialize_sdk():
        print("❌ Falha na inicialização do SDK")
        return
    
    print("\n✅ SDK inicializado com sucesso!")
    print("🎯 OBJETIVO: Teste rápido de range de IDs")
    print("⚠️  IMPORTANTE: Você precisará usar o controle físico para Main Operation Control")
    
    input("\nPressione Enter para continuar...")
    
    tester.run_quick_test()

if __name__ == "__main__":
    main()
