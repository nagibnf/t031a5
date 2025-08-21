#!/usr/bin/env python3
"""
🔍 VERIFICAÇÃO RÁPIDA DO SISTEMA t031a5
Script único para verificar se tudo está funcionando
"""

import asyncio
import sys
from pathlib import Path

# Adicionar paths
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

async def verificar_componentes():
    """Verifica componentes essenciais."""
    
    print("🔍 VERIFICAÇÃO SISTEMA t031a5")
    print("=" * 40)
    
    verificacoes = []
    
    # 1. Verificar G1 conectividade
    print("🤖 Verificando G1 Tobias...")
    try:
        import subprocess
        result = subprocess.run(['ping', '-c', '1', '192.168.123.161'], 
                              capture_output=True, timeout=5)
        if result.returncode == 0:
            print("   ✅ G1 Tobias acessível (192.168.123.161)")
            verificacoes.append(True)
        else:
            print("   ❌ G1 Tobias não acessível")
            verificacoes.append(False)
    except:
        print("   ⚠️ Não foi possível verificar G1")
        verificacoes.append(False)
    
    # 2. Verificar áudio DJI
    print("🎤 Verificando DJI Mic...")
    try:
        from t031a5.audio.audio_manager_definitivo import AudioManagerDefinitivo
        audio_mgr = AudioManagerDefinitivo()
        dispositivos = audio_mgr.listar_dispositivos_audio()
        
        dji_encontrado = any("DJI" in str(d) for d in dispositivos.get("sources", []))
        if dji_encontrado:
            print("   ✅ DJI Mic detectado")
            verificacoes.append(True)
        else:
            print("   ⚠️ DJI Mic não detectado")
            verificacoes.append(False)
    except Exception as e:
        print(f"   ❌ Erro ao verificar áudio: {e}")
        verificacoes.append(False)
    
    # 3. Verificar LLM
    print("🧠 Verificando LLM...")
    try:
        from t031a5.llm.ollama_manager import OllamaManager
        llm = OllamaManager()
        status = await llm.health_check()
        if status:
            print("   ✅ Ollama disponível")
            verificacoes.append(True)
        else:
            print("   ⚠️ Ollama não disponível")
            verificacoes.append(False)
    except Exception as e:
        print(f"   ❌ Erro ao verificar LLM: {e}")
        verificacoes.append(False)
    
    # 4. Verificar configuração
    print("⚙️ Verificando configuração...")
    config_path = Path("config/g1_production.json5")
    if config_path.exists():
        print("   ✅ Configuração de produção encontrada")
        verificacoes.append(True)
    else:
        print("   ❌ Configuração não encontrada")
        verificacoes.append(False)
    
    # Resultado final
    print("\n" + "=" * 40)
    sucessos = sum(verificacoes)
    total = len(verificacoes)
    
    if sucessos == total:
        print("🎉 SISTEMA PRONTO PARA PRODUÇÃO!")
        print("▶️  Execute: python t031a5_main.py")
    elif sucessos >= total * 0.75:
        print("⚠️  Sistema parcialmente operacional")
        print("🔧 Verifique os componentes com erro")
    else:
        print("❌ Sistema não está pronto")
        print("🛠️  Resolva os problemas antes de continuar")
    
    print(f"\n📊 Status: {sucessos}/{total} componentes OK")
    return sucessos == total

if __name__ == "__main__":
    resultado = asyncio.run(verificar_componentes())
    sys.exit(0 if resultado else 1)
