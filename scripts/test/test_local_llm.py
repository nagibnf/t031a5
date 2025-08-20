#!/usr/bin/env python3
"""
Teste de LLM Local - Sistema t031a5

Testa Llama-3.1-8B-Instruct no Jetson Orin NX 16GB
"""

import asyncio
import sys
from pathlib import Path

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from t031a5.llm.local_manager import LocalLLMManager


async def test_local_llm():
    """Testa sistema de LLM local."""
    print("🧠 TESTE DE LLM LOCAL - SISTEMA t031a5")
    print("=" * 50)
    
    manager = LocalLLMManager()
    
    print("🔧 Inicializando...")
    if await manager.initialize():
        print("✅ Sistema inicializado")
        
        # Teste de performance
        print("\n📊 Testando performance...")
        results = await manager.test_performance()
        
        print("\n📋 RESULTADOS")
        print("=" * 20)
        
        if results["local"]["success"]:
            print(f"🖥️ LLM Local: {results['local']['time']:.2f}s")
            print(f"   Resposta: {results['local']['response']}")
        else:
            print("❌ LLM Local: Falha")
        
        if results["openai"]["success"]:
            print(f"☁️ OpenAI: {results['openai']['time']:.2f}s")
            print(f"   Resposta: {results['openai']['response']}")
        else:
            print("❌ OpenAI: Falha")
        
        await manager.cleanup()
    else:
        print("❌ Falha ao inicializar sistema")
    
    print("\n🎉 Teste concluído!")


if __name__ == "__main__":
    asyncio.run(test_local_llm())
