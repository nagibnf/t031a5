#!/usr/bin/env python3
"""
Script de teste para o CortexRuntime do sistema t031a5.

Testa o loop principal completo do sistema.
"""

import sys
import asyncio
import logging
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from t031a5.runtime.cortex import CortexRuntime

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_cortex_runtime():
    """Testa o CortexRuntime completo."""
    
    print("🤖 Testando CortexRuntime - Sistema Completo t031a5")
    print("=" * 60)
    
    try:
        # 1. Inicialização
        print("\n1. Inicializando CortexRuntime...")
        cortex = CortexRuntime(Path("config/g1_basic.json5"))
        
        success = await cortex.initialize()
        if success:
            print("✅ CortexRuntime inicializado com sucesso")
        else:
            print("❌ Falha na inicialização do CortexRuntime")
            return False
        
        # 2. Verificação de status inicial
        print("\n2. Verificando status inicial...")
        status = await cortex.get_status()
        print(f"✅ Status coletado:")
        print(f"   - Rodando: {status['is_running']}")
        print(f"   - Componentes inicializados: {status['components_initialized']}")
        print(f"   - Config carregado: {status['config_loaded']}")
        
        # 3. Teste do loop por alguns ciclos
        print("\n3. Iniciando loop principal por 10 segundos...")
        
        # Inicia o sistema em uma task separada
        async def run_for_duration():
            await cortex.start()
        
        async def stop_after_delay():
            await asyncio.sleep(10)  # Roda por 10 segundos
            print("\n⏰ Tempo limite atingido, parando sistema...")
            cortex.is_running = False
        
        # Executa ambas as tarefas simultaneamente
        await asyncio.gather(
            run_for_duration(),
            stop_after_delay(),
            return_exceptions=True
        )
        
        # 4. Verificação de status final
        print("\n4. Verificando status final...")
        final_status = await cortex.get_status()
        print(f"✅ Estatísticas finais:")
        print(f"   - Loops executados: {final_status['loop_count']}")
        print(f"   - Tempo médio por loop: {final_status['metrics']['avg_loop_time']*1000:.2f}ms")
        print(f"   - Erros: {final_status['metrics']['errors']}")
        print(f"   - Total de loops: {final_status['metrics']['total_loops']}")
        
        # 5. Teste de parada limpa
        print("\n5. Testando parada limpa...")
        await cortex.stop()
        print("✅ Sistema parado com sucesso")
        
        print("\n🎉 Teste do CortexRuntime concluído com sucesso!")
        print("O sistema está funcionando corretamente em loop completo!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
        logger.exception("Erro detalhado:")
        return False


async def test_emergency_stop():
    """Testa a funcionalidade de parada de emergência."""
    
    print("\n" + "="*60)
    print("🚨 Testando Parada de Emergência")
    print("="*60)
    
    try:
        # Inicializa sistema
        cortex = CortexRuntime(Path("config/g1_basic.json5"))
        await cortex.initialize()
        
        # Simula início do sistema
        cortex.is_running = True
        
        print("1. Sistema iniciado")
        print("2. Executando parada de emergência...")
        
        # Testa parada de emergência
        success = await cortex.emergency_stop()
        
        if success:
            print("✅ Parada de emergência executada com sucesso")
        else:
            print("❌ Falha na parada de emergência")
        
        print(f"3. Status após emergência: {'Parado' if not cortex.is_running else 'Ainda rodando'}")
        
        return success
        
    except Exception as e:
        print(f"❌ Erro no teste de emergência: {e}")
        return False


async def test_config_reload():
    """Testa o recarregamento de configuração."""
    
    print("\n" + "="*60)
    print("🔄 Testando Recarregamento de Configuração")
    print("="*60)
    
    try:
        # Inicializa sistema
        cortex = CortexRuntime(Path("config/g1_development.json5"))
        await cortex.initialize()
        
        print("1. Sistema inicializado com config de desenvolvimento")
        print(f"   Hertz inicial: {cortex.config.hertz}")
        
        # Muda para config básico
        cortex.config_manager.config_path = Path("config/g1_basic.json5")
        
        print("2. Recarregando configuração básica...")
        await cortex.reload_config()
        
        print(f"✅ Configuração recarregada")
        print(f"   Hertz atual: {cortex.config.hertz}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de reload: {e}")
        return False


if __name__ == "__main__":
    async def main():
        print("🚀 Iniciando testes do CortexRuntime\n")
        
        results = []
        
        # Teste principal
        print("Teste 1: Loop Principal")
        results.append(await test_cortex_runtime())
        
        # Teste de emergência
        print("\nTeste 2: Parada de Emergência")
        results.append(await test_emergency_stop())
        
        # Teste de reload
        print("\nTeste 3: Recarregamento de Configuração")
        results.append(await test_config_reload())
        
        # Resultado final
        print("\n" + "="*60)
        print("📊 RESULTADO FINAL DOS TESTES")
        print("="*60)
        
        # Filtra valores None e conta sucessos
        valid_results = [r for r in results if r is not None]
        passed = sum(valid_results)
        total = len(valid_results)
        
        print(f"Testes passaram: {passed}/{total}")
        
        if passed == total:
            print("🎉 TODOS OS TESTES PASSARAM!")
            print("O CortexRuntime está funcionando perfeitamente!")
        else:
            print("❌ Alguns testes falharam")
        
        return passed == total
    
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
