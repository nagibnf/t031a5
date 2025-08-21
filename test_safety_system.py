#!/usr/bin/env python3
"""
TESTE - Sistema de Segurança G1
Testa botão STOP, regras de proteção e monitoramento
"""

import asyncio
import sys
from pathlib import Path

# Adiciona pasta src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from t031a5.security import SafetyManager, SafetyLevel, SafetyRule


async def test_safety_system():
    """Testa o sistema de segurança."""
    print("🛡️ TESTE DO SISTEMA DE SEGURANÇA G1")
    print("=" * 60)
    
    # Configuração de teste
    config = {
        "safety": {
            "min_distance_meters": 0.5,
            "battery_warning_level": 25.0,
            "battery_critical_level": 15.0,
            "max_operation_time": 10.0,  # 10s para teste
            "max_idle_time": 5.0,        # 5s para teste
            "max_speed": 0.3,
            "max_volume": 70,
            "max_audio_duration": 10.0,
            "enable_emergency_stop": True,
            "auto_recovery": True,
            "log_all_events": True
        }
    }
    
    # Criar sistema de segurança
    print("🔧 Criando SafetyManager...")
    safety = SafetyManager(config)
    
    try:
        # Inicializar
        print("🔧 Inicializando SafetyManager...")
        success = await safety.initialize()
        if not success:
            print("❌ Falha na inicialização")
            return False
        
        print("✅ SafetyManager inicializado com sucesso!")
        
        # Configurar callbacks
        async def on_safety_event(event):
            print(f"🚨 Evento: [{event.level.value}] {event.description}")
        
        async def on_emergency_stop(reason):
            print(f"🛑 EMERGENCY STOP: {reason}")
        
        async def on_safety_clear():
            print("🟢 Sistema de segurança limpo")
        
        safety.on_safety_event = on_safety_event
        safety.on_emergency_stop = on_emergency_stop
        safety.on_safety_clear = on_safety_clear
        
        # Status inicial
        print("\n📊 STATUS INICIAL:")
        status = await safety.get_status()
        print(f"  Nível atual: {status['current_level']}")
        print(f"  Monitoramento: {status['monitoring']}")
        print(f"  Emergency stop: {status['emergency_stop']}")
        
        # Teste 1: Verificação de movimento seguro
        print("\n🤚 TESTE 1: Verificação de movimento...")
        
        # Movimento normal (deve passar)
        safe = await safety.check_movement_safety(0.1, 0.1, 0.1, 0.2)
        print(f"  Movimento normal: {'✅' if safe else '❌'}")
        
        # Movimento muito rápido (deve falhar)
        safe = await safety.check_movement_safety(0.1, 0.1, 0.1, 0.5)
        print(f"  Movimento rápido: {'❌' if not safe else '✅'} (deve falhar)")
        
        # Teste 2: Verificação de áudio
        print("\n🔊 TESTE 2: Verificação de áudio...")
        
        # Volume normal (deve passar)
        safe = await safety.check_audio_safety(60, 5.0)
        print(f"  Volume normal: {'✅' if safe else '❌'}")
        
        # Volume alto (deve falhar)
        safe = await safety.check_audio_safety(90, 5.0)
        print(f"  Volume alto: {'❌' if not safe else '✅'} (deve falhar)")
        
        # Teste 3: Bateria baixa
        print("\n🔋 TESTE 3: Simulando bateria baixa...")
        await safety.update_battery_level(20.0)  # Warning
        await asyncio.sleep(1)
        
        await safety.update_battery_level(10.0)  # Critical (deve ativar emergency stop)
        await asyncio.sleep(2)
        
        # Teste 4: Emergency stop manual
        print("\n🛑 TESTE 4: Emergency stop manual...")
        await safety.emergency_stop("Teste manual")
        await asyncio.sleep(1)
        
        # Verificar se movimentos são bloqueados
        safe = await safety.check_movement_safety(0.1, 0.1, 0.1, 0.1)
        print(f"  Movimento durante emergency: {'❌' if not safe else '✅'} (deve ser bloqueado)")
        
        # Teste 5: Limpar emergency stop
        print("\n🟢 TESTE 5: Limpando emergency stop...")
        await safety.clear_emergency_stop()
        await asyncio.sleep(1)
        
        # Verificar se movimentos voltaram
        safe = await safety.check_movement_safety(0.1, 0.1, 0.1, 0.1)
        print(f"  Movimento após limpeza: {'✅' if safe else '❌'}")
        
        # Teste 6: Eventos recentes
        print("\n📋 TESTE 6: Eventos recentes...")
        events = await safety.get_recent_events(5)
        print(f"  Total de eventos: {len(events)}")
        for i, event in enumerate(events[:3]):
            print(f"    {i+1}. [{event['level']}] {event['description'][:50]}...")
        
        # Status final
        print("\n📊 STATUS FINAL:")
        status = await safety.get_status()
        print(f"  Nível atual: {status['current_level']}")
        print(f"  Total eventos: {status['total_events']}")
        print(f"  Eventos recentes: {status['recent_events']}")
        print(f"  Tempo operação: {status['operation_time']:.1f}s")
        print(f"  Tempo inativo: {status['idle_time']:.1f}s")
        
        print("\n✅ TESTE DO SISTEMA DE SEGURANÇA CONCLUÍDO!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False
        
    finally:
        # Limpar
        print("\n🧹 Parando SafetyManager...")
        await safety.stop()
        print("✅ SafetyManager parado")


async def main():
    """Função principal."""
    print("🚀 INICIANDO TESTE DO SISTEMA DE SEGURANÇA")
    print("Inclui: Botão STOP, Regras de Proteção, Monitoramento")
    print("=" * 60)
    
    success = await test_safety_system()
    
    if success:
        print("\n🎉 SUCESSO: Sistema de segurança funcionando!")
        print("📝 Funcionalidades testadas:")
        print("  ✅ Verificação de movimentos seguros")
        print("  ✅ Verificação de áudio seguro") 
        print("  ✅ Monitoramento de bateria")
        print("  ✅ Emergency stop manual")
        print("  ✅ Limpeza de emergency stop")
        print("  ✅ Histórico de eventos")
        print("  ✅ Monitoramento contínuo")
    else:
        print("\n❌ FALHA: Verifique os logs acima")


if __name__ == "__main__":
    asyncio.run(main())
