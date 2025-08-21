#!/usr/bin/env python3
"""
Teste Individual de TODOS os Movimentos G1
Validação completa de IDs e métodos de ativação
"""

import asyncio
import sys
import time
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from t031a5.unitree.g1_controller import G1Controller, G1Language, G1Emotion

class MovementValidator:
    """Validador individual de movimentos G1."""
    
    def __init__(self):
        self.controller = None
        self.results = {}
        
        # Configuração com interface correta
        self.config = {
            "interface": {
                "interface": "eth0",
                "timeout": 10.0
            },
            "default_volume": 100,
            "default_speaker_id": 1  # Inglês
        }
        
        # Lista completa de IDs para testar
        self.movement_ids = [
            # Estados FSM
            0, 1, 2, 3, 4, 5, 6, 200, 702, 706,
            # Movimentos de braços (segundo documentação)
            11, 12, 13, 15, 17, 18, 19, 22, 23, 24, 25, 26, 27, 31, 32, 33, 34, 35, 99,
            # IDs suspeitos que podem estar trocados
            10, 14, 16, 20, 21, 28, 29, 30, 36, 37, 38, 39, 40
        ]
    
    async def run_complete_validation(self):
        """Executa validação completa de todos os movimentos."""
        print("�� VALIDAÇÃO COMPLETA DE MOVIMENTOS G1")
        print("=" * 60)
        
        try:
            # 1. Inicialização
            print("\n🔧 1. INICIALIZANDO...")
            success = await self._initialize()
            if not success:
                return False
            
            # 2. Teste individual de cada ID
            print(f"\n🤚 2. TESTANDO {len(self.movement_ids)} MOVIMENTOS...")
            await self._test_all_movements()
            
            # 3. Relatório final
            print("\n📊 3. RELATÓRIO FINAL...")
            self._generate_report()
            
            # 4. Limpeza
            print("\n🧹 4. FINALIZANDO...")
            await self._cleanup()
            
            return True
            
        except Exception as e:
            print(f"\n❌ Erro na validação: {e}")
            await self._cleanup()
            return False
    
    async def _initialize(self) -> bool:
        """Inicializa o sistema."""
        try:
            print("  �� Criando controlador...")
            self.controller = G1Controller(self.config)
            
            print("  🔧 Inicializando...")
            success = await self.controller.initialize()
            
            if success:
                print("  ✅ Inicializado com sucesso")
                return True
            else:
                print("  ❌ Falha na inicialização")
                return False
                
        except Exception as e:
            print(f"  ❌ Erro: {e}")
            return False
    
    async def _test_all_movements(self):
        """Testa todos os movimentos individualmente."""
        for i, movement_id in enumerate(self.movement_ids):
            print(f"\n🔍 [{i+1:2d}/{len(self.movement_ids)}] Testando movimento ID {movement_id}")
            
            try:
                # Sempre relaxar antes
                await self.controller.execute_gesture(99, wait_time=1.0)
                await asyncio.sleep(1.0)
                
                # Anunciar teste
                await self.controller.speak(f"Testing movement {movement_id}", G1Language.ENGLISH)
                await asyncio.sleep(1.0)
                
                # Executar movimento
                start_time = time.time()
                success = await self.controller.execute_gesture(movement_id, wait_time=3.0)
                execution_time = time.time() - start_time
                
                # Registrar resultado
                self.results[movement_id] = {
                    "success": success,
                    "execution_time": execution_time,
                    "description": "Unknown"
                }
                
                status = "✅" if success else "❌"
                print(f"    {status} ID {movement_id}: {execution_time:.2f}s")
                
                # Relaxar depois
                await self.controller.execute_gesture(99, wait_time=1.0)
                await asyncio.sleep(2.0)
                
            except Exception as e:
                print(f"    ❌ ID {movement_id}: Erro - {e}")
                self.results[movement_id] = {
                    "success": False,
                    "execution_time": 0,
                    "error": str(e),
                    "description": "Error"
                }
                await asyncio.sleep(1.0)
    
    def _generate_report(self):
        """Gera relatório final dos testes."""
        working = [id for id, result in self.results.items() if result["success"]]
        not_working = [id for id, result in self.results.items() if not result["success"]]
        
        print(f"\n📊 RESULTADOS:")
        print(f"   ✅ Funcionando: {len(working)} movimentos")
        print(f"   ❌ Não funcionando: {len(not_working)} movimentos")
        print(f"   📈 Taxa de sucesso: {len(working)/(len(working)+len(not_working))*100:.1f}%")
        
        print(f"\n✅ MOVIMENTOS FUNCIONANDO:")
        for movement_id in sorted(working):
            time_taken = self.results[movement_id]["execution_time"]
            print(f"   ID {movement_id:3d}: {time_taken:.2f}s")
        
        print(f"\n❌ MOVIMENTOS NÃO FUNCIONANDO:")
        for movement_id in sorted(not_working):
            error = self.results[movement_id].get("error", "Failed")
            print(f"   ID {movement_id:3d}: {error}")
        
        # Salvar resultado em arquivo
        with open("movement_validation_results.txt", "w") as f:
            f.write("RESULTADOS DA VALIDAÇÃO DE MOVIMENTOS G1\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Funcionando: {working}\n")
            f.write(f"Não funcionando: {not_working}\n")
            f.write(f"Taxa de sucesso: {len(working)/(len(working)+len(not_working))*100:.1f}%\n")
        
        print(f"\n💾 Resultados salvos em: movement_validation_results.txt")
    
    async def _cleanup(self):
        """Limpa recursos."""
        try:
            if self.controller:
                print("  🧹 Parando...")
                await self.controller.stop()
                print("  ✅ Parado")
                
        except Exception as e:
            print(f"  ❌ Erro limpeza: {e}")

async def main():
    """Função principal."""
    print("🎯 Validação Completa de Movimentos G1")
    print("=" * 60)
    
    validator = MovementValidator()
    success = await validator.run_complete_validation()
    
    if success:
        print("\n🎉 VALIDAÇÃO CONCLUÍDA!")
        print("📋 Verifique o arquivo movement_validation_results.txt")
    else:
        print("\n❌ FALHA NA VALIDAÇÃO")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
