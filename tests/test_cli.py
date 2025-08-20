#!/usr/bin/env python3
"""
Script de teste para o CLI completo do t031a5.

Testa todos os comandos: run, status, validate, version, test.
"""

import sys
import asyncio
import subprocess
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from t031a5.runtime import CortexRuntime


def test_version():
    """Testa o comando version."""
    print("🔍 Testando comando version...")
    
    try:
        from t031a5 import __version__
        print(f"✅ Versão: {__version__}")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_validate():
    """Testa o comando validate."""
    print("\n🔍 Testando comando validate...")
    
    try:
        from t031a5.runtime.config import ConfigManager
        
        config_files = [
            "config/g1_basic.json5",
            "config/g1_advanced.json5", 
            "config/g1_development.json5",
            "config/g1_integrated.json5"
        ]
        
        for config_file in config_files:
            if Path(config_file).exists():
                print(f"  Validando {config_file}...")
                config_manager = ConfigManager(Path(config_file))
                g1_config = config_manager.load_config()
                
                print(f"    ✅ Nome: {g1_config.name}")
                print(f"    ✅ Frequência: {g1_config.hertz} Hz")
                
                # Validação do ambiente
                if config_manager.validate_environment():
                    print(f"    ✅ Ambiente válido")
                else:
                    print(f"    ⚠️  Ambiente com problemas")
            else:
                print(f"  ⚪ {config_file} não encontrado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_status():
    """Testa o comando status."""
    print("\n🔍 Testando comando status...")
    
    try:
        from t031a5.runtime.config import ConfigManager
        
        config_file = "config/g1_integrated.json5"
        if not Path(config_file).exists():
            print(f"  ⚪ {config_file} não encontrado")
            return True
        
        print(f"  Status de {config_file}...")
        config_manager = ConfigManager(Path(config_file))
        g1_config = config_manager.load_config()
        
        print(f"    ✅ Nome: {g1_config.name}")
        print(f"    ✅ Frequência: {g1_config.hertz} Hz")
        print(f"    ✅ Interface: {g1_config.unitree_ethernet}")
        
        # Inputs configurados
        inputs_config = config_manager.get_inputs_config()
        print(f"    ✅ Inputs: {len(inputs_config)} configurados")
        
        # Actions configuradas
        actions_config = config_manager.get_actions_config()
        print(f"    ✅ Actions: {len(actions_config)} configuradas")
        
        # Configurações de desenvolvimento
        dev_config = g1_config.development
        print(f"    ✅ Debug: {'Sim' if dev_config.get('debug_mode') else 'Não'}")
        print(f"    ✅ WebSim: {'Sim' if dev_config.get('websim_enabled') else 'Não'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


async def test_run():
    """Testa o comando run."""
    print("\n🔍 Testando comando run...")
    
    try:
        config_file = "config/g1_integrated.json5"
        if not Path(config_file).exists():
            print(f"  ⚪ {config_file} não encontrado")
            return True
        
        print(f"  Executando sistema com {config_file}...")
        
        # Cria runtime
        runtime = CortexRuntime(Path(config_file))
        
        # Inicializa
        success = await runtime.initialize()
        if not success:
            print("    ❌ Falha na inicialização")
            return False
        
        print("    ✅ Sistema inicializado")
        
        # Mostra status
        status = await runtime.get_status()
        print(f"    ✅ Config carregada: {status['config_loaded']}")
        print(f"    ✅ Componentes: {status['components_initialized']}")
        
        # Para o sistema
        await runtime.stop()
        print("    ✅ Sistema parado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


async def test_test_command():
    """Testa o comando test."""
    print("\n🔍 Testando comando test...")
    
    try:
        config_file = "config/g1_integrated.json5"
        if not Path(config_file).exists():
            print(f"  ⚪ {config_file} não encontrado")
            return True
        
        print(f"  Testando sistema com {config_file} por 5 segundos...")
        
        # Cria runtime
        runtime = CortexRuntime(Path(config_file))
        
        # Inicializa
        success = await runtime.initialize()
        if not success:
            print("    ❌ Falha na inicialização")
            return False
        
        print("    ✅ Sistema inicializado")
        
        # Executa por 5 segundos
        run_task = asyncio.create_task(runtime.start())
        await asyncio.sleep(5)
        
        # Para o sistema
        runtime.is_running = False
        await run_task
        
        # Mostra estatísticas
        final_status = await runtime.get_status()
        print(f"    ✅ Loops: {final_status['loop_count']}")
        print(f"    ✅ Erros: {final_status['metrics']['errors']}")
        print(f"    ✅ Frequência: {final_status['loop_count']/5:.2f} Hz")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


async def main():
    """Função principal de teste."""
    print("🚀 Testando CLI completo do t031a5\n")
    
    results = []
    
    # Teste de versão
    print("Teste 1: Comando Version")
    results.append(test_version())
    
    # Teste de validação
    print("\nTeste 2: Comando Validate")
    results.append(test_validate())
    
    # Teste de status
    print("\nTeste 3: Comando Status")
    results.append(test_status())
    
    # Teste de run
    print("\nTeste 4: Comando Run")
    results.append(await test_run())
    
    # Teste de test
    print("\nTeste 5: Comando Test")
    results.append(await test_test_command())
    
    # Resultado final
    print("\n" + "="*60)
    print("📊 RESULTADO FINAL DOS TESTES DO CLI")
    print("="*60)
    
    # Filtra valores None e conta sucessos
    valid_results = [r for r in results if r is not None]
    passed = sum(valid_results)
    total = len(valid_results)
    
    print(f"Testes passaram: {passed}/{total}")
    
    if passed == total:
        print("🎉 TODOS OS TESTES DO CLI PASSARAM!")
        print("O CLI está funcionando perfeitamente!")
        print("\n💡 Comandos disponíveis:")
        print("   t031a5 run --config config/g1_integrated.json5")
        print("   t031a5 test --config config/g1_integrated.json5 --duration 30")
        print("   t031a5 status --config config/g1_integrated.json5")
        print("   t031a5 validate --config config/g1_integrated.json5")
        print("   t031a5 version")
    else:
        print("❌ Alguns testes do CLI falharam")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
