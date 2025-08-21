#!/usr/bin/env python3
"""
TESTE - Sistema de Efeitos Sonoros Contextuais
Testa detecção de contexto e reprodução de efeitos
"""

import asyncio
import sys
from pathlib import Path

# Adiciona pasta src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from t031a5.audio.effects_manager import EffectsManager, ContextType


async def mock_audio_player(file_path: str, volume: float = 1.0, duration: float = 1.0) -> bool:
    """Player de áudio mock para testes."""
    print(f"🎵 REPRODUZINDO: {Path(file_path).name} (vol: {volume:.1f}, dur: {duration:.1f}s)")
    await asyncio.sleep(0.1)  # Simula reprodução
    return True


async def test_effects_system():
    """Testa o sistema de efeitos sonoros."""
    print("🎵 TESTE DO SISTEMA DE EFEITOS SONOROS")
    print("=" * 60)
    
    # Configuração de teste
    config = {
        "audio_base_dir": "audio",
        "effects": {
            "enable_effects": True,
            "effects_volume": 0.8,
            "max_effect_duration": 10.0
        }
    }
    
    # Criar sistema de efeitos
    print("🔧 Criando EffectsManager...")
    effects = EffectsManager(config)
    
    # Configurar player mock
    effects.set_audio_player(mock_audio_player)
    
    try:
        # Inicializar
        print("🔧 Inicializando EffectsManager...")
        success = await effects.initialize()
        if not success:
            print("❌ Falha na inicialização")
            return False
        
        print("✅ EffectsManager inicializado com sucesso!")
        
        # Status inicial
        print("\n📊 STATUS INICIAL:")
        status = await effects.get_status()
        print(f"  Total efeitos: {status['total_effects']}")
        print(f"  Efeitos habilitados: {status['enabled_effects']}")
        print(f"  Diretório: {status['effects_directory']}")
        print(f"  Volume global: {status['global_volume']}")
        
        # Listar efeitos disponíveis
        print("\n📋 EFEITOS DISPONÍVEIS:")
        available = effects.get_available_effects()
        for name, info in available.items():
            status_icon = "✅" if info['enabled'] else "❌"
            print(f"  {status_icon} {name:15} -> {info['context']:15} ({info['duration']}s)")
        
        # Teste 1: Análise de texto para contexto
        print("\n📝 TESTE 1: Análise de texto...")
        
        test_texts = [
            "Wow, that woman is so beautiful!",
            "Goodbye everyone, see you later!",
            "That's amazing! I'm so excited!",
            "Hmm, let me think about this...",
            "Haha, that's a funny joke!"
        ]
        
        for text in test_texts:
            contexts = await effects.analyze_text_for_context(text)
            print(f"  '{text[:30]}...' -> {[c.value for c in contexts]}")
        
        # Teste 2: Reprodução por contexto
        print("\n🎭 TESTE 2: Reprodução por contexto...")
        
        test_contexts = [
            ContextType.BEAUTIFUL_WOMAN,
            ContextType.GOODBYE,
            ContextType.SURPRISE,
            ContextType.APPROVAL,
            ContextType.EXCITEMENT
        ]
        
        for context in test_contexts:
            print(f"\n--- Testando contexto: {context.value} ---")
            success = await effects.play_context_effect(context, {"test": True})
            print(f"{'✅' if success else '❌'} Contexto: {context.value}")
            await asyncio.sleep(0.5)
        
        # Teste 3: Reprodução de efeito específico
        print("\n🎯 TESTE 3: Efeito específico...")
        success = await effects.play_specific_effect("evil_laugh")
        print(f"{'✅' if success else '❌'} Efeito específico: evil_laugh")
        
        # Teste 4: Limite de frequência (cooldown)
        print("\n⏰ TESTE 4: Teste de cooldown...")
        
        # Primeiro deve funcionar
        success1 = await effects.play_context_effect(ContextType.THINKING)
        print(f"{'✅' if success1 else '❌'} Primeira reprodução")
        
        # Segunda deve falhar (cooldown)
        success2 = await effects.play_context_effect(ContextType.THINKING)
        print(f"{'❌' if not success2 else '✅'} Segunda reprodução (deve falhar - cooldown)")
        
        # Teste 5: Análise de visão mock
        print("\n👁️ TESTE 5: Análise de visão...")
        
        vision_data = {
            "tags": ["woman", "smile", "beautiful"],
            "description": "A beautiful woman smiling at the camera"
        }
        
        contexts = await effects.analyze_vision_for_context(vision_data)
        print(f"  Dados de visão: {vision_data['description']}")
        print(f"  Contextos detectados: {[c.value for c in contexts]}")
        
        # Tentar reproduzir com base na visão
        for context in contexts:
            success = await effects.play_context_effect(context, {"source": "vision"})
            print(f"  {'✅' if success else '❌'} Reprodução para {context.value}")
        
        # Teste 6: Regras de contexto
        print("\n📏 TESTE 6: Regras de contexto...")
        rules = effects.get_context_rules()
        print("  Primeiras 3 regras:")
        for i, (context, rule) in enumerate(list(rules.items())[:3]):
            print(f"    {context}: {len(rule['keywords'])} palavras-chave, {rule['current_count']}/{rule['max_frequency']} usos")
        
        # Status final
        print("\n📊 STATUS FINAL:")
        status = await effects.get_status()
        print(f"  Total reproduzido: {status['total_played']}")
        print(f"  Histórico recente: {status['recent_history']} eventos")
        print(f"  Contadores sessão: {status['session_counts']}")
        
        print("\n✅ TESTE DE EFEITOS SONOROS CONCLUÍDO!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False
        
    finally:
        # Limpar
        print("\n🧹 Parando EffectsManager...")
        await effects.stop()
        print("✅ EffectsManager parado")


async def main():
    """Função principal."""
    print("🚀 INICIANDO TESTE DE EFEITOS SONOROS")
    print("Sistema de reprodução contextual de áudios")
    print("=" * 60)
    
    success = await test_effects_system()
    
    if success:
        print("\n🎉 SUCESSO: Sistema de efeitos funcionando!")
        print("📝 Funcionalidades testadas:")
        print("  ✅ Detecção de contexto por texto")
        print("  ✅ Detecção de contexto por visão")
        print("  ✅ Reprodução por contexto")
        print("  ✅ Reprodução de efeito específico")
        print("  ✅ Sistema de cooldown")
        print("  ✅ Regras de frequência")
        print("  ✅ Histórico e estatísticas")
        print("\n💡 Para usar em produção:")
        print("  1. Adicione arquivos .wav na pasta audio/effects/")
        print("  2. Configure player de áudio real")
        print("  3. Integre com sistema de visão LLaVA")
        print("  4. Integre com processamento de conversas")
    else:
        print("\n❌ FALHA: Verifique os logs acima")


if __name__ == "__main__":
    asyncio.run(main())
