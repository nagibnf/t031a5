#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from t031a5.llm.ollama_manager import OllamaManager

async def test_ollama():
    manager = OllamaManager()
    if await manager.initialize():
        print("✅ Ollama inicializado")
        
        print("\n📊 Testando performance...")
        results = await manager.test_performance()
        
        print("\n📋 RESULTADOS")
        if results["ollama"]["success"]:
            print(f"🖥️ Ollama: {results['ollama']['time']:.2f}s")
            print(f"   Resposta: {results['ollama']['response']}")
        else:
            print("❌ Ollama: Falhou")
            
        if results["openai"]["success"]:
            print(f"☁️ OpenAI: {results['openai']['time']:.2f}s")
            print(f"   Resposta: {results['openai']['response']}")
        else:
            print("❌ OpenAI: Falhou")
            
        await manager.cleanup()
    else:
        print("❌ Falha na inicialização")
    print("\n🎉 Teste concluído!")

if __name__ == "__main__":
    asyncio.run(test_ollama())
