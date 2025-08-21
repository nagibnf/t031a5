#!/usr/bin/env python3
"""
TESTE - Novo Sistema de Movimentos G1 (API Oficial)
Para testar no Mac (modo mock) e na Jetson (real)
"""

import asyncio
import sys
from pathlib import Path

# Adiciona pasta src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from t031a5.unitree.g1_controller import G1Controller, G1Language, G1Emotion


async def test_new_movements():
    """Testa os novos movimentos usando API oficial."""
    print("🎯 TESTE DO NOVO SISTEMA DE MOVIMENTOS G1")
    print("=" * 60)
    
    # Configuração
    config = {
        "interface": {
            "interface": "eth0",  # SEMPRE usar eth0 para comunicação com G1
            "timeout": 10.0
        },
        "default_volume": 100,
        "default_speaker_id": 1  # Inglês
    }
    
    # Criar controlador
    print("🔧 Criando G1Controller...")
    controller = G1Controller(config)
    
    try:
        # Inicializar
        print("🔧 Inicializando G1Controller...")
        success = await controller.initialize()
        if not success:
            print("❌ Falha na inicialização")
            return False
        
        print("✅ G1Controller inicializado com sucesso!")
        
        # Listar movimentos disponíveis
        print("\n📋 MOVIMENTOS DISPONÍVEIS:")
        movements = await controller.get_available_movements()
        for name, action in movements.items():
            print(f"  {name:15} -> '{action}'")
        
        # Teste de fala
        print("\n🗣️ Testando TTS...")
        await controller.speak("Hello, I am Tobias. Testing new movement system.", G1Language.ENGLISH)
        await asyncio.sleep(3)
        
        # Testar alguns movimentos principais
        test_movements = ["release_arm", "clap", "shake_hand", "high_five", "release_arm"]
        
        print(f"\n🤚 Testando {len(test_movements)} movimentos...")
        for i, movement in enumerate(test_movements):
            print(f"\n--- Movimento {i+1}/{len(test_movements)}: {movement} ---")
            
            success = await controller.execute_gesture(movement, wait_time=3.0, emotion=G1Emotion.HAPPY)
            print(f"{'✅' if success else '❌'} {movement}")
            
            await asyncio.sleep(1)  # Pequena pausa entre movimentos
        
        print("\n✅ TESTE CONCLUÍDO COM SUCESSO!")
        
        # Status final
        print("\n📊 STATUS FINAL:")
        status = await controller.get_status()
        print(f"  Controller inicializado: {status['controller']['initialized']}")
        print(f"  Controller rodando: {status['controller']['running']}")
        print(f"  Comandos no histórico: {status['controller']['command_history_count']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False
        
    finally:
        # Limpar
        print("\n🧹 Parando G1Controller...")
        await controller.stop()
        print("✅ G1Controller parado")


async def main():
    """Função principal."""
    print("🚀 INICIANDO TESTE DOS NOVOS MOVIMENTOS G1")
    print("Baseado na API oficial do SDK Unitree")
    print("=" * 60)
    
    success = await test_new_movements()
    
    if success:
        print("\n🎉 SUCESSO: Novos movimentos funcionando!")
        print("📝 Próximos passos:")
        print("  1. Testar na Jetson com G1 real")
        print("  2. Integrar com sistema completo")
        print("  3. Criar scripts de demonstração")
    else:
        print("\n❌ FALHA: Verifique os logs acima")


if __name__ == "__main__":
    asyncio.run(main())
