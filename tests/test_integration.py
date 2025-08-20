#!/usr/bin/env python3
"""
Script de teste para o sistema integrado t031a5.

Testa a integração completa: CortexRuntime + G1Controller + WebSim.
"""

import sys
import asyncio
import logging
import time
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from t031a5.runtime import CortexRuntime

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_system_initialization():
    """Testa a inicialização do sistema integrado."""
    
    print("🚀 Testando Inicialização do Sistema Integrado")
    print("=" * 50)
    
    try:
        # Cria CortexRuntime com configuração integrada
        cortex = CortexRuntime(config_path=Path("config/g1_integrated.json5"))
        
        print("1. Inicializando sistema completo...")
        success = await cortex.initialize()
        
        if not success:
            print("❌ Falha na inicialização do sistema")
            return False, None
        
        print("✅ Sistema inicializado com sucesso")
        
        # Verifica componentes
        print("\n2. Verificando componentes...")
        print(f"   ConfigManager: {'✅' if cortex.config_manager else '❌'}")
        print(f"   InputOrchestrator: {'✅' if cortex.input_orchestrator else '❌'}")
        print(f"   ActionOrchestrator: {'✅' if cortex.action_orchestrator else '❌'}")
        print(f"   Fuser: {'✅' if cortex.fuser else '❌'}")
        print(f"   LLMProvider: {'✅' if cortex.llm_provider else '❌'}")
        print(f"   G1Controller: {'✅' if cortex.g1_controller else '❌'}")
        print(f"   WebSim: {'✅' if cortex.websim else '❌'}")
        
        return True, cortex
        
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        return False, None


async def test_system_status():
    """Testa o status do sistema."""
    
    print("\n🔍 Testando Status do Sistema")
    print("=" * 50)
    
    try:
        cortex = CortexRuntime(config_path=Path("config/g1_integrated.json5"))
        await cortex.initialize()
        
        print("1. Obtendo status do sistema...")
        status = await cortex.get_status()
        
        print("✅ Status obtido com sucesso:")
        print(f"   Sistema rodando: {status['is_running']}")
        print(f"   Componentes inicializados: {status['components_initialized']}")
        print(f"   Config carregado: {status['config_loaded']}")
        print(f"   Loop count: {status['loop_count']}")
        
        # Status do G1Controller
        if status['g1_controller']:
            g1_status = status['g1_controller']
            print(f"   G1Controller: {g1_status['controller']['initialized']}")
            if 'interface' in g1_status:
                print(f"   G1 Interface: {g1_status['interface']['state']}")
        
        # Status do WebSim
        if status['websim']:
            websim_status = status['websim']
            print(f"   WebSim rodando: {websim_status['running']}")
            print(f"   WebSim port: {websim_status['port']}")
            print(f"   WebSim conexões: {websim_status['connections']}")
        
        await cortex.stop()
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de status: {e}")
        return False


async def test_system_runtime():
    """Testa o runtime do sistema."""
    
    print("\n⚡ Testando Runtime do Sistema")
    print("=" * 50)
    
    try:
        cortex = CortexRuntime(config_path=Path("config/g1_integrated.json5"))
        await cortex.initialize()
        
        print("1. Iniciando loop principal por 15 segundos...")
        
        # Inicia o loop em uma tarefa separada
        run_task = asyncio.create_task(cortex.start())
        
        # Deixa executar por um tempo
        for i in range(15):
            await asyncio.sleep(1)
            if i % 5 == 0:
                status = await cortex.get_status()
                print(f"   {i+1}s - Loops: {status['loop_count']}, Running: {status['is_running']}")
        
        # Para o sistema
        cortex.is_running = False
        await run_task
        
        print("\n2. Verificando estatísticas finais...")
        final_status = await cortex.get_status()
        print(f"   Loops executados: {final_status['loop_count']}")
        print(f"   Tempo médio por loop: {final_status['metrics']['avg_loop_time']*1000:.2f}ms")
        print(f"   Erros: {final_status['metrics']['errors']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de runtime: {e}")
        return False


async def test_emergency_stop():
    """Testa a parada de emergência."""
    
    print("\n🚨 Testando Parada de Emergência")
    print("=" * 50)
    
    try:
        cortex = CortexRuntime(config_path=Path("config/g1_integrated.json5"))
        await cortex.initialize()
        
        print("1. Iniciando sistema...")
        run_task = asyncio.create_task(cortex.start())
        
        # Deixa executar por um pouco
        await asyncio.sleep(3)
        
        print("2. Executando parada de emergência...")
        await cortex.emergency_stop()
        
        # Espera a tarefa terminar
        await run_task
        
        print("✅ Parada de emergência executada com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro na parada de emergência: {e}")
        return False


async def test_websim_integration():
    """Testa a integração com WebSim."""
    
    print("\n🌐 Testando Integração WebSim")
    print("=" * 50)
    
    try:
        cortex = CortexRuntime(config_path=Path("config/g1_integrated.json5"))
        await cortex.initialize()
        
        print("1. Verificando WebSim...")
        if not cortex.websim:
            print("❌ WebSim não foi inicializado")
            return False
        
        print("✅ WebSim inicializado")
        
        # Verifica se o servidor está rodando
        websim_status = await cortex.websim.get_status()
        print(f"   Servidor rodando: {websim_status['running']}")
        print(f"   URL: http://{websim_status['host']}:{websim_status['port']}")
        
        print("\n2. Testando comandos via WebSim...")
        
        # Testa alguns comandos
        commands = [
            ("move_forward", {"distance": 0.2, "speed": 0.3}),
            ("speak_text", {"text": "Sistema integrado funcionando!", "emotion": "happy", "volume": 0.7}),
            ("emergency_stop", {})
        ]
        
        for command, params in commands:
            print(f"   Executando: {command}")
            success = await cortex.websim._execute_command(command, params)
            print(f"     Resultado: {'✅' if success else '❌'}")
        
        await cortex.stop()
        print("\n✅ Integração WebSim testada com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro na integração WebSim: {e}")
        return False


if __name__ == "__main__":
    async def main():
        print("🚀 Iniciando testes do sistema integrado t031a5\n")
        
        results = []
        
        # Teste de inicialização
        print("Teste 1: Inicialização do Sistema")
        success, cortex = await test_system_initialization()
        results.append(success)
        if cortex:
            await cortex.stop()
        
        # Teste de status
        print("\nTeste 2: Status do Sistema")
        results.append(await test_system_status())
        
        # Teste de runtime
        print("\nTeste 3: Runtime do Sistema")
        results.append(await test_system_runtime())
        
        # Teste de emergência
        print("\nTeste 4: Parada de Emergência")
        results.append(await test_emergency_stop())
        
        # Teste de integração WebSim
        print("\nTeste 5: Integração WebSim")
        results.append(await test_websim_integration())
        
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
            print("O sistema integrado está funcionando perfeitamente!")
            print("\n💡 Para usar o sistema completo:")
            print("   1. Execute: python3 -m t031a5.cli run --config g1_integrated.json5")
            print("   2. Acesse: http://localhost:8080")
            print("   3. Use a interface web para controlar o G1")
            print("   4. O sistema t031a5 estará rodando em loop completo!")
        else:
            print("❌ Alguns testes falharam")
        
        return passed == total
    
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
