#!/usr/bin/env python3
"""
Teste simplificado para plugins avançados do G1.

Valida apenas a funcionalidade básica:
- Inicialização
- Status
- Parada
"""

import sys
import asyncio
import logging
from datetime import datetime
from pathlib import Path

# Adiciona src ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from t031a5.inputs.plugins.g1_vision import G1VisionInput
from t031a5.inputs.plugins.g1_gps import G1GPSInput
from t031a5.inputs.plugins.g1_state import G1StateInput
from t031a5.actions.g1_movement import G1MovementAction
from t031a5.actions.g1_arms import G1ArmsAction
from t031a5.actions.g1_audio import G1AudioAction


async def test_plugin_basic(plugin_class, config: dict, plugin_name: str):
    """Testa funcionalidade básica de um plugin."""
    print(f"\n🔧 Testando {plugin_name}...")
    
    try:
        # Inicializa plugin
        plugin = plugin_class(config)
        success = await plugin.initialize()
        
        if not success:
            print(f"❌ Falha na inicialização do {plugin_name}")
            return False
        
        print(f"✅ {plugin_name} inicializado")
        
        # Testa status
        status = await plugin.get_status()
        print(f"✅ Status: {status.get('status', 'unknown')}")
        
        # Testa health check
        try:
            health = await plugin.health_check()
            if isinstance(health, dict):
                print(f"✅ Health: {health.get('status', 'unknown')}")
            else:
                print(f"✅ Health: {'healthy' if health else 'unhealthy'}")
        except Exception as e:
            print(f"⚠️  Health check falhou: {e}")
        
        # Para plugin
        await plugin.stop()
        print(f"✅ {plugin_name} parado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste {plugin_name}: {e}")
        return False


async def main():
    """Função principal."""
    print("🚀 Testando Plugins Avançados do G1 (Básico)")
    print("=" * 50)
    
    # Configura logging
    logging.basicConfig(level=logging.INFO)
    
    # Configurações básicas
    basic_config = {
        "enabled": True,
        "mock_mode": True
    }
    
    # Lista de testes
    tests = [
        (G1VisionInput, basic_config, "G1Vision"),
        (G1GPSInput, basic_config, "G1GPS"),
        (G1StateInput, basic_config, "G1State"),
        (G1MovementAction, basic_config, "G1Movement"),
        (G1ArmsAction, basic_config, "G1Arms"),
        (G1AudioAction, basic_config, "G1Audio")
    ]
    
    # Executa testes
    results = []
    for plugin_class, config, name in tests:
        try:
            result = await test_plugin_basic(plugin_class, config, name)
            results.append((name, result))
        except Exception as e:
            print(f"❌ Erro no teste {name}: {e}")
            results.append((name, False))
    
    # Relatório final
    print("\n" + "=" * 50)
    print("📋 RELATÓRIO FINAL")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:15} {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os plugins avançados estão funcionando!")
    else:
        print("⚠️  Alguns plugins precisam de atenção")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
