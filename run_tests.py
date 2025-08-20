#!/usr/bin/env python3
"""
Script para executar todos os testes do sistema t031a5.

Executa todos os testes na ordem correta e gera relatório.
"""

import sys
import asyncio
import subprocess
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def run_test(test_file: str, description: str) -> bool:
    """Executa um teste específico."""
    print(f"\n🧪 Executando: {description}")
    print("=" * 60)
    
    try:
        result = subprocess.run(
            [sys.executable, "tests/run_test.py", test_file],
            capture_output=False,
            text=True,
            timeout=300  # 5 minutos por teste
        )
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSOU")
            return True
        else:
            print(f"❌ {description} - FALHOU")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {description} - ERRO: {e}")
        return False


async def main():
    """Função principal de execução de testes."""
    print("🚀 Executando todos os testes do t031a5")
    print("=" * 60)
    
    # Lista de testes na ordem de execução
    tests = [
        ("test_system.py", "Teste dos Componentes Core"),
        ("test_cortex.py", "Teste do CortexRuntime"),
        ("test_llm_providers.py", "Teste dos Provedores LLM"),
        ("test_unitree_simple.py", "Teste do Módulo Unitree"),
        ("test_websim.py", "Teste da Interface WebSim"),
        ("test_cli.py", "Teste do CLI Completo"),
        ("test_logging_system.py", "Teste do Sistema de Logging"),
        ("test_integration.py", "Teste de Integração Completa"),
        ("test_real_g1_integration.py", "Teste de Integração com G1 Real"),
    ]
    
    results = []
    
    for test_file, description in tests:
        success = run_test(test_file, description)
        results.append((description, success))
    
    # Resultado final
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL DOS TESTES")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"Testes passaram: {passed}/{total}")
    
    # Lista detalhada
    print("\n📋 Detalhes:")
    for description, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"  {status} - {description}")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("O sistema t031a5 está funcionando perfeitamente!")
        print("\n💡 Para usar o sistema:")
        print("   python3 -m t031a5.cli run --config config/g1_integrated.json5")
        print("   Acesse: http://localhost:8080")
    else:
        print(f"\n❌ {total - passed} teste(s) falharam")
        print("Verifique os logs acima para detalhes")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
