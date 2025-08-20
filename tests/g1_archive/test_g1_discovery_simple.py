#!/usr/bin/env python3
"""
Teste Simples de Descoberta de Movimentos G1.
Versão robusta que funciona melhor.
"""

import time
import sys
import json
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class G1SimpleDiscovery:
    """Descoberta simples de movimentos do G1."""
    
    def __init__(self):
        self.interface = "en11"
        self.robot_ip = "192.168.123.161"
        
        # Clientes SDK
        self.loco_client = None
        self.arm_client = None
        
        # Resultados
        self.results = {}
    
    def initialize_sdk(self):
        """Inicializa SDK de forma simples."""
        try:
            from unitree_sdk2py.core.channel import ChannelFactoryInitialize
            from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient
            from unitree_sdk2py.g1.arm.g1_arm_action_client import G1ArmActionClient
            
            print("🔧 Inicializando SDK...")
            ChannelFactoryInitialize(0, self.interface)
            print("✅ SDK inicializado")
            
            # Inicializar LocoClient
            self.loco_client = LocoClient()
            self.loco_client.SetTimeout(5.0)
            self.loco_client.Init()
            print("✅ LocoClient inicializado")
            
            # Inicializar ArmActionClient
            self.arm_client = G1ArmActionClient()
            self.arm_client.SetTimeout(5.0)
            self.arm_client.Init()
            print("✅ ArmActionClient inicializado")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            return False
    
    def setup_robot_state(self):
        """Configura estado básico do robô."""
        print("🚀 Configurando estado do robô...")
        
        try:
            # Zero Torque
            print("1️⃣ Zero Torque (FSM 0)...")
            self.loco_client.SetFsmId(0)
            time.sleep(2)
            
            # Damping
            print("2️⃣ Damping (FSM 1)...")
            self.loco_client.SetFsmId(1)
            time.sleep(2)
            
            # Get Ready
            print("3️⃣ Get Ready (FSM 4)...")
            self.loco_client.SetFsmId(4)
            time.sleep(3)
            
            print("✅ Estado configurado!")
            print("⚠️  AGORA use R1+X no controle físico para Main Operation Control")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao configurar estado: {e}")
            return False
    
    def test_arm_id(self, test_id):
        """Testa um ID de braço."""
        print(f"\n🔄 Testando Arm ID: {test_id}")
        
        try:
            result = self.arm_client.ExecuteAction(test_id)
            print(f"   Status: {result}")
            
            if result == 0:
                print(f"   ✅ ID {test_id} executado!")
                time.sleep(2)
                
                # Perguntar se funcionou
                response = input(f"   ❓ Funcionou? (s/n): ").strip().lower()
                
                if response in ['s', 'sim', 'y', 'yes']:
                    name = input(f"   📝 Nome: ").strip()
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
                    print("   🔄 Voltando ao estado inicial...")
                    self.arm_client.ExecuteAction(99)
                    time.sleep(1)
                
                return True
            else:
                print(f"   ❌ Falhou (Status: {result})")
                self.results[test_id] = {
                    "type": "arm",
                    "name": "unknown",
                    "status": f"failed_{result}"
                }
                return False
                
        except Exception as e:
            print(f"   ❌ ERRO: {e}")
            self.results[test_id] = {
                "type": "arm",
                "name": "unknown",
                "status": "error"
            }
            return False
    
    def test_fsm_id(self, test_id):
        """Testa um ID de FSM."""
        print(f"\n🔄 Testando FSM ID: {test_id}")
        
        try:
            result = self.loco_client.SetFsmId(test_id)
            print(f"   Status: {result}")
            
            if result == 0:
                print(f"   ✅ ID {test_id} executado!")
                time.sleep(3)
                
                # Perguntar se funcionou
                response = input(f"   ❓ Funcionou? (s/n): ").strip().lower()
                
                if response in ['s', 'sim', 'y', 'yes']:
                    name = input(f"   📝 Nome: ").strip()
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
                
                return True
            else:
                print(f"   ❌ Falhou (Status: {result})")
                self.results[test_id] = {
                    "type": "fsm",
                    "name": "unknown",
                    "status": f"failed_{result}"
                }
                return False
                
        except Exception as e:
            print(f"   ❌ ERRO: {e}")
            self.results[test_id] = {
                "type": "fsm",
                "name": "unknown",
                "status": "error"
            }
            return False
    
    def test_range(self, start_id, end_id, test_type="arm"):
        """Testa um range de IDs."""
        print(f"\n🎯 TESTANDO {test_type.upper()} IDs {start_id} a {end_id}")
        print("=" * 50)
        
        for test_id in range(start_id, end_id + 1):
            print(f"\n{'='*40}")
            print(f"🎯 ID {test_id} de {end_id}")
            print(f"{'='*40}")
            
            if test_type == "arm":
                self.test_arm_id(test_id)
            else:
                self.test_fsm_id(test_id)
            
            # Pausa entre testes
            input(f"\nPressione Enter para próximo ID...")
    
    def save_results(self):
        """Salva os resultados."""
        results_file = "g1_discovery_results.json"
        
        # Organizar resultados
        organized_results = {
            "results": self.results,
            "summary": {
                "total_tested": len(self.results),
                "working": len([m for m in self.results.values() if m["status"] == "working"]),
                "failed": len([m for m in self.results.values() if m["status"] != "working"])
            }
        }
        
        # Salvar em JSON
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(organized_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados salvos em: {results_file}")
        
        # Mostrar resumo
        print(f"\n📊 RESUMO:")
        print("=" * 20)
        print(f"Total testado: {organized_results['summary']['total_tested']}")
        print(f"Funcionais: {organized_results['summary']['working']}")
        print(f"Falharam: {organized_results['summary']['failed']}")
        
        # Mostrar funcionais
        working = [f"{id}: {data['name']}" for id, data in self.results.items() if data["status"] == "working"]
        if working:
            print(f"\n✅ FUNCIONAIS:")
            for movement in working:
                print(f"   {movement}")
    
    def run_discovery(self):
        """Executa a descoberta."""
        print("🔍 DESCOBERTA SIMPLES DE MOVIMENTOS G1")
        print("=" * 60)
        
        # Configurar estado
        if not self.setup_robot_state():
            print("❌ Falha ao configurar estado")
            return
        
        # Perguntar range
        try:
            start_id = int(input("\nID inicial: "))
            end_id = int(input("ID final: "))
            test_type = input("Tipo (fsm/arm): ").strip().lower()
            
            if test_type not in ['fsm', 'arm']:
                test_type = 'arm'
            
            print(f"\n🎯 Iniciando: {test_type.upper()} IDs {start_id} a {end_id}")
            
            self.test_range(start_id, end_id, test_type)
            
            # Salvar resultados
            self.save_results()
            
        except ValueError:
            print("❌ ID inválido")
        except KeyboardInterrupt:
            print("\n🛑 Interrompido")

def main():
    """Função principal."""
    print("🔍 DESCOBERTA SIMPLES G1")
    print("=" * 60)
    
    discovery = G1SimpleDiscovery()
    
    if not discovery.initialize_sdk():
        print("❌ Falha na inicialização")
        return
    
    print("\n✅ SDK inicializado!")
    print("🎯 OBJETIVO: Descobrir movimentos funcionais")
    
    input("\nPressione Enter para continuar...")
    
    discovery.run_discovery()

if __name__ == "__main__":
    main()
