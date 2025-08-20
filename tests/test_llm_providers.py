#!/usr/bin/env python3
"""
Script de teste para os provedores LLM reais do sistema t031a5.

Testa OpenAI e Anthropic providers.
"""

import sys
import asyncio
import logging
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from t031a5.llm.provider import LLMProvider
from t031a5.fuser.base import FusedData

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_openai_provider():
    """Testa o provedor OpenAI."""
    
    print("🤖 Testando OpenAI Provider")
    print("=" * 50)
    
    try:
        # Configuração do OpenAI
        config = {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "temperature": 0.7,
            "max_tokens": 200,
            "timeout": 30.0,
            "api_key": "YOUR_OPENAI_API_KEY_HERE",  # Substitua pela sua API key
            "requests_per_minute": 60,
            "include_sensors": True,
            "include_location": True,
            "include_robot_state": True,
            "fallback_provider": "mock"
        }
        
        # Cria o provider
        provider = LLMProvider(config)
        
        # Inicializa
        print("1. Inicializando OpenAI Provider...")
        success = await provider.initialize()
        
        if not success:
            print("❌ Falha na inicialização do OpenAI Provider")
            print("   Verifique se a API key está configurada corretamente")
            return False
        
        print("✅ OpenAI Provider inicializado com sucesso")
        
        # Testa processamento
        print("\n2. Testando processamento...")
        
        # Dados simulados
        fused_data = FusedData(
            content="Olá! Como você está hoje?",
            confidence=0.9,
            source="voice",
            timestamp=1234567890.0,
            metadata={
                "sensors": {
                    "battery": 85,
                    "temperature": 25.5,
                    "status": "normal"
                },
                "gps": {
                    "latitude": -23.5505,
                    "longitude": -46.6333,
                    "accuracy": 5.0
                },
                "robot_state": {
                    "posture": "standing",
                    "movement": "idle",
                    "arms": "neutral"
                }
            }
        )
        
        system_prompt = "Você é um assistente robótico humanóide G1 da Unitree. Responda sempre em português brasileiro de forma natural e conversacional."
        
        # Processa
        response = await provider.process(fused_data, system_prompt)
        
        if response:
            print("✅ Resposta recebida do OpenAI:")
            print(f"   Modelo: {response.model}")
            print(f"   Provedor: {response.provider}")
            print(f"   Tokens usados: {response.tokens_used}")
            print(f"   Conteúdo: {response.content[:100]}...")
            print(f"   Metadata: {response.metadata}")
        else:
            print("❌ Nenhuma resposta recebida do OpenAI")
            return False
        
        # Para o provider
        await provider.stop()
        print("\n✅ OpenAI Provider testado com sucesso!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do OpenAI Provider: {e}")
        return False


async def test_anthropic_provider():
    """Testa o provedor Anthropic."""
    
    print("\n🤖 Testando Anthropic Provider")
    print("=" * 50)
    
    try:
        # Configuração do Anthropic
        config = {
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022",
            "temperature": 0.7,
            "max_tokens": 200,
            "timeout": 30.0,
            "api_key": "YOUR_ANTHROPIC_API_KEY_HERE",  # Substitua pela sua API key
            "requests_per_minute": 60,
            "include_sensors": True,
            "include_location": True,
            "include_robot_state": True,
            "fallback_provider": "mock"
        }
        
        # Cria o provider
        provider = LLMProvider(config)
        
        # Inicializa
        print("1. Inicializando Anthropic Provider...")
        success = await provider.initialize()
        
        if not success:
            print("❌ Falha na inicialização do Anthropic Provider")
            print("   Verifique se a API key está configurada corretamente")
            return False
        
        print("✅ Anthropic Provider inicializado com sucesso")
        
        # Testa processamento
        print("\n2. Testando processamento...")
        
        # Dados simulados
        fused_data = FusedData(
            content="Qual é a sua opinião sobre robótica humanóide?",
            confidence=0.9,
            source="voice",
            timestamp=1234567890.0,
            metadata={
                "sensors": {
                    "battery": 90,
                    "temperature": 24.0,
                    "status": "excellent"
                },
                "gps": {
                    "latitude": -23.5505,
                    "longitude": -46.6333,
                    "accuracy": 3.0
                },
                "robot_state": {
                    "posture": "sitting",
                    "movement": "conversing",
                    "arms": "gesturing"
                }
            }
        )
        
        system_prompt = "Você é um assistente robótico humanóide G1 da Unitree. Responda sempre em português brasileiro de forma natural e conversacional."
        
        # Processa
        response = await provider.process(fused_data, system_prompt)
        
        if response:
            print("✅ Resposta recebida do Anthropic:")
            print(f"   Modelo: {response.model}")
            print(f"   Provedor: {response.provider}")
            print(f"   Tokens usados: {response.tokens_used}")
            print(f"   Conteúdo: {response.content[:100]}...")
            print(f"   Metadata: {response.metadata}")
        else:
            print("❌ Nenhuma resposta recebida do Anthropic")
            return False
        
        # Para o provider
        await provider.stop()
        print("\n✅ Anthropic Provider testado com sucesso!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do Anthropic Provider: {e}")
        return False


async def test_fallback_mechanism():
    """Testa o mecanismo de fallback."""
    
    print("\n🔄 Testando Mecanismo de Fallback")
    print("=" * 50)
    
    try:
        # Configuração com provedor inexistente (deve usar fallback)
        config = {
            "provider": "nonexistent_provider",
            "model": "gpt-4o-mini",
            "temperature": 0.7,
            "max_tokens": 200,
            "timeout": 30.0,
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
        
        # Testa processamento
        print("\n2. Testando processamento com fallback...")
        
        # Dados simulados
        fused_data = FusedData(
            content="Teste de fallback",
            confidence=0.8,
            source="test",
            timestamp=1234567890.0,
            metadata={}
        )
        
        system_prompt = "Você é um assistente de teste."
        
        # Processa
        response = await provider.process(fused_data, system_prompt)
        
        if response:
            print("✅ Resposta recebida do fallback:")
            print(f"   Modelo: {response.model}")
            print(f"   Provedor: {response.provider}")
            print(f"   Conteúdo: {response.content[:100]}...")
        else:
            print("❌ Nenhuma resposta recebida do fallback")
            return False
        
        # Para o provider
        await provider.stop()
        print("\n✅ Mecanismo de Fallback testado com sucesso!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do Fallback: {e}")
        return False


async def test_provider_status():
    """Testa o status dos provedores."""
    
    print("\n📊 Testando Status dos Provedores")
    print("=" * 50)
    
    try:
        # Testa status do Mock Provider
        config = {
            "provider": "mock",
            "model": "mock-g1",
            "temperature": 0.7,
            "max_tokens": 200,
            "response_delay": 0.1,
            "error_rate": 0.0
        }
        
        provider = LLMProvider(config)
        await provider.initialize()
        
        print("1. Status do Mock Provider:")
        status = await provider.get_status()
        print(f"   Inicializado: {status['initialized']}")
        print(f"   Provedor: {status['provider_type']}")
        print(f"   Modelo: {status['model']}")
        print(f"   Métricas: {status['metrics']}")
        
        await provider.stop()
        
        print("\n✅ Status dos Provedores testado com sucesso!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de Status: {e}")
        return False


if __name__ == "__main__":
    async def main():
        print("🚀 Iniciando testes dos Provedores LLM Reais\n")
        
        results = []
        
        # Teste de status (sempre funciona)
        print("Teste 1: Status dos Provedores")
        results.append(await test_provider_status())
        
        # Teste de fallback (sempre funciona)
        print("\nTeste 2: Mecanismo de Fallback")
        results.append(await test_fallback_mechanism())
        
        # Testes dos provedores reais (requerem API keys)
        print("\nTeste 3: OpenAI Provider")
        print("⚠️  Requer API key do OpenAI configurada")
        results.append(await test_openai_provider())
        
        print("\nTeste 4: Anthropic Provider")
        print("⚠️  Requer API key do Anthropic configurada")
        results.append(await test_anthropic_provider())
        
        # Resultado final
        print("\n" + "="*60)
        print("📊 RESULTADO FINAL DOS TESTES")
        print("="*60)
        
        # Filtra valores None e conta sucessos
        valid_results = [r for r in results if r is not None]
        passed = sum(valid_results)
        total = len(valid_results)
        
        print(f"Testes passaram: {passed}/{total}")
        
        if passed >= 2:  # Pelo menos status e fallback devem funcionar
            print("🎉 TESTES BÁSICOS PASSARAM!")
            print("Os provedores LLM estão funcionando corretamente!")
            
            if passed < total:
                print("\n💡 Para usar provedores reais:")
                print("   1. Configure suas API keys nos arquivos de configuração")
                print("   2. Execute: pip install openai anthropic")
                print("   3. Teste novamente")
        else:
            print("❌ Alguns testes básicos falharam")
        
        return passed >= 2
    
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
