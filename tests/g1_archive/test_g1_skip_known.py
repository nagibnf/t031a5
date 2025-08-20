#!/usr/bin/env python3
"""
Teste G1 que Pula IDs Já Conhecidos.
Automaticamente pula movimentos já testados.
"""

import time
import sys
import json
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class G1SkipKnownDiscovery:
    """Descoberta que pula IDs já conhecidos."""
    
    def __init__(self):
        self.interface = "en11"
        self.robot_ip = "192.168.123.161"
        
        # Clientes SDK
        self.loco_client = None
        self.arm_client = None
        
        # Resultados
        self.results = {}
        self.known_working_ids = set()
        
        # Carregar resultados existentes
        self.load_existing_results()
    
    def load_existing_results(self):
        """Carrega resultados existentes."""
        try:
            with open("g1_discovery_results.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.results = data.get("results", {})
                
                # Extrair IDs funcionais
                for id_str, data in self.results.items():
                    if data["status"] == "working":
                        self.known_working_ids.add(int(id_str))
                
                print(f"📋 Carregados {len(self.results)} resultados existentes")
                print(f"✅ IDs funcionais conhecidos: {sorted(self.known_working_ids)}")
        except FileNotFoundError:
            print("📋 Nenhum resultado existente encontrado")
    
    def initialize_sdk(self):
        """Inicializa SDK."""
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
    
    def test_arm_id_skip_known(self, test_id):
        """Testa um ID de braço, pulando se já conhecido."""
        print(f"\n🔄 Testando Arm ID: {test_id}")
        
        # Verificar se já é conhecido
        if test_id in self.known_working_ids:
            print(f"   ⏭️  ID {test_id} já conhecido e funcional - PULANDO")
            return True
        
        # Verificar se já foi testado e falhou
        if str(test_id) in self.results and self.results[str(test_id)]["status"] != "working":
            print(f"   ⏭️  ID {test_id} já testado e falhou - PULANDO")
            return False
        
        try:
            result = self.arm_client.ExecuteAction(test_id)
            print(f"   Status: {result}")
            
            if result == 0:
                print(f"   ✅ ID {test_id} executado!")
                time.sleep(3)
                
                # Perguntar se funcionou
                response = input(f"   ❓ Funcionou? (s/n): ").strip().lower()
                
                if response in ['s', 'sim', 'y', 'yes']:
                    name = input(f"   📝 Nome: ").strip()
                    self.results[str(test_id)] = {
                        "type": "arm",
                        "name": name,
                        "status": "working"
                    }
                    self.known_working_ids.add(test_id)
                    print(f"   ✅ Salvo: {test_id} = '{name}'")
                else:
                    self.results[str(test_id)] = {
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
                self.results[str(test_id)] = {
                    "type": "arm",
                    "name": "unknown",
                    "status": f"failed_{result}"
                }
                return False
                
        except Exception as e:
            print(f"   ❌ ERRO: {e}")
            self.results[str(test_id)] = {
                "type": "arm",
                "name": "unknown",
                "status": "error"
            }
            return False
    
    def test_range_skip_known(self, start_id, end_id, test_type="arm"):
        """Testa um range de IDs, pulando os conhecidos."""
        print(f"\n🎯 TESTANDO {test_type.upper()} IDs {start_id} a {end_id}")
        print("=" * 50)
        
        skipped_count = 0
        tested_count = 0
        
        for test_id in range(start_id, end_id + 1):
            print(f"\n{'='*40}")
            print(f"🎯 ID {test_id} de {end_id}")
            print(f"{'='*40}")
            
            # Verificar se deve pular
            if test_id in self.known_working_ids:
                print(f"   ⏭️  ID {test_id} já conhecido - PULANDO")
                skipped_count += 1
                continue
            
            if str(test_id) in self.results and self.results[str(test_id)]["status"] != "working":
                print(f"   ⏭️  ID {test_id} já testado e falhou - PULANDO")
                skipped_count += 1
                continue
            
            tested_count += 1
            
            if test_type == "arm":
                self.test_arm_id_skip_known(test_id)
            else:
                # Implementar para FSM se necessário
                print(f"   ⏭️  FSM testing not implemented yet")
            
            # Pausa entre testes
            input(f"\nPressione Enter para próximo ID...")
        
        print(f"\n📊 RESUMO DO RANGE:")
        print(f"   Testados: {tested_count}")
        print(f"   Pulados: {skipped_count}")
    
    def show_working_movements(self):
        """Mostra movimentos funcionais descobertos."""
        working = [f"{id}: {data['name']}" for id, data in self.results.items() if data["status"] == "working"]
        if working:
            print(f"\n🎯 MOVIMENTOS FUNCIONAIS DESCOBERTOS ({len(working)}):")
            print("=" * 60)
            for movement in working:
                print(f"   {movement}")
        else:
            print("❌ Nenhum movimento funcional descoberto ainda")
    
    def suggest_next_ranges(self):
        """Sugere próximos ranges para testar."""
        print(f"\n🎯 SUGESTÕES DE PRÓXIMOS RANGES:")
        print("=" * 40)
        
        # Encontrar gaps nos IDs funcionais
        working_ids = sorted(self.known_working_ids)
        if working_ids:
            print(f"IDs funcionais: {working_ids}")
            
            # Sugerir ranges baseados nos gaps
            max_working = max(working_ids)
            print(f"Maior ID funcional: {max_working}")
            
            print(f"\n📋 SUGESTÕES:")
            print(f"   Arm Actions: {max_working + 1} a {max_working + 50}")
            print(f"   Arm Actions: {max_working + 51} a {max_working + 100}")
            print(f"   FSM States: 5 a 20")
            print(f"   FSM States: 201 a 300")
    
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
        print(f"\n📊 RESUMO FINAL:")
        print("=" * 20)
        print(f"Total testado: {organized_results['summary']['total_tested']}")
        print(f"Funcionais: {organized_results['summary']['working']}")
        print(f"Falharam: {organized_results['summary']['failed']}")
    
    def run_discovery(self):
        """Executa a descoberta."""
        print("🔍 DESCOBERTA G1 - PULA CONHECIDOS")
        print("=" * 60)
        
        # Mostrar movimentos já descobertos
        self.show_working_movements()
        
        # Sugerir próximos ranges
        self.suggest_next_ranges()
        
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
            print(f"⚠️  IDs conhecidos serão pulados automaticamente")
            
            self.test_range_skip_known(start_id, end_id, test_type)
            
            # Salvar resultados
            self.save_results()
            
        except ValueError:
            print("❌ ID inválido")
        except KeyboardInterrupt:
            print("\n🛑 Interrompido")

def main():
    """Função principal."""
    print("🔍 DESCOBERTA G1 - PULA CONHECIDOS")
    print("=" * 60)
    
    discovery = G1SkipKnownDiscovery()
    
    if not discovery.initialize_sdk():
        print("❌ Falha na inicialização")
        return
    
    print("\n✅ SDK inicializado!")
    print("🎯 OBJETIVO: Descobrir novos movimentos (pula conhecidos)")
    
    input("\nPressione Enter para continuar...")
    
    discovery.run_discovery()

if __name__ == "__main__":
    main()
