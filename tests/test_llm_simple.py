#!/usr/bin/env python3
"""
Teste simples para os provedores LLM do sistema t031a5.
"""

import sys
import asyncio
import logging
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from t031a5.llm.provider import LLMProvider

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_mock_provider():
    """Testa o provedor Mock."""
    
    print("🤖 Testando Mock Provider")
    print("=" * 40)
    
    try:
        # Configuração do Mock
        config = {
            "provider": "mock",
            "model": "mock-g1",
            "temperature": 0.7,
            "max_tokens": 200,
            "response_delay": 0.1,
            "error_rate": 0.0
        }
        
        # Cria o provider
        provider = LLMProvider(config)
        
        # Inicializa
        print("1. Inicializando Mock Provider...")
        success = await provider.initialize()
        
        if not success:
            print("❌ Falha na inicialização do Mock Provider")
            return False
        
        print("✅ Mock Provider inicializado com sucesso")
        
        # Testa status
        print("\n2. Verificando status...")
        status = await provider.get_status()
        print(f"   Inicializado: {status.get('initialized', False)}")
        print(f"   Provedor: {status.get('provider_type', 'unknown')}")
        print(f"   Modelo: {status.get('model', 'unknown')}")
        
        # Para o provider
        await provider.stop()
        print("\n✅ Mock Provider testado com sucesso!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do Mock Provider: {e}")
        return False


async def test_fallback_mechanism():
    """Testa o mecanismo de fallback."""
    
    print("\n🔄 Testando Mecanismo de Fallback")
    print("=" * 40)
    
    try:
        # Configuração com provedor inexistente (deve usar fallback)
        config = {
            "provider": "nonexistent_provider",
            "model": "gpt-4o-mini",
            "temperature": 0.7,
            "max_tokens": 200,
            "fallback_provider": "mock"
        }
        
        # Cria o provider
        provider = LLMProvider(config)
        
        # Inicializa
        print("1. Inicializando Provider com fallback...")
        success = await provider.initialize()
        
        if not success:
            print("❌ Falha na inicialização do Provider")
            return False
        
        print("✅ Provider inicializado com sucesso (usando fallback)")
        
        # Verifica status
        status = await provider.get_status()
        print(f"   Provedor usado: {status.get('provider_type', 'unknown')}")
        
        # Para o provider
        await provider.stop()
        print("\n✅ Mecanismo de Fallback testado com sucesso!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do Fallback: {e}")
        return False


if __name__ == "__main__":
    async def main():
        print("🚀 Iniciando testes simples dos Provedores LLM\n")
        
        results = []
        
        # Teste do Mock Provider
        print("Teste 1: Mock Provider")
        results.append(await test_mock_provider())
        
        # Teste de fallback
        print("\nTeste 2: Mecanismo de Fallback")
        results.append(await test_fallback_mechanism())
        
        # Resultado final
        print("\n" + "="*50)
        print("📊 RESULTADO FINAL DOS TESTES")
        print("="*50)
        
        # Filtra valores None e conta sucessos
        valid_results = [r for r in results if r is not None]
        passed = sum(valid_results)
        total = len(valid_results)
        
        print(f"Testes passaram: {passed}/{total}")
        
        if passed == total:
            print("🎉 TODOS OS TESTES PASSARAM!")
            print("Os provedores LLM básicos estão funcionando corretamente!")
        else:
            print("❌ Alguns testes falharam")
        
        return passed == total
    
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
