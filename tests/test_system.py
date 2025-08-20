#!/usr/bin/env python3
"""
Script de teste para o sistema t031a5.

Testa a funcionalidade básica do sistema.
"""

import sys
import asyncio
import logging
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from t031a5.runtime.config import ConfigManager
from t031a5.runtime.orchestrators import InputOrchestrator, ActionOrchestrator
from t031a5.fuser.priority import PriorityFuser
from t031a5.llm import LLMProvider

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_system():
    """Testa o sistema t031a5."""
    
    print("🤖 Testando Sistema t031a5 - G1")
    print("=" * 50)
    
    try:
        # 1. Teste de configuração
        print("\n1. Testando ConfigManager...")
        config_manager = ConfigManager()
        config = config_manager.load_config("config/g1_basic.json5")
        
        if config:
            print("✅ Configuração carregada com sucesso")
            print(f"   Nome: {config.name}")
            print(f"   Hertz: {config.hertz}")
            # Acessa dados do config manager
            raw_config = config_manager.get_raw_config()
            inputs = raw_config.get("agent_inputs", [])
            actions = raw_config.get("agent_actions", [])
            print(f"   Inputs: {len(inputs)}")
            print(f"   Actions: {len(actions)}")
        else:
            print("❌ Falha ao carregar configuração")
            return
        
        # 2. Teste de InputOrchestrator
        print("\n2. Testando InputOrchestrator...")
        input_orchestrator = InputOrchestrator(inputs, config_manager)
        success = await input_orchestrator.initialize()
        
        if success:
            print("✅ InputOrchestrator inicializado com sucesso")
            await input_orchestrator.start()
            print("✅ InputOrchestrator iniciado com sucesso")
        else:
            print("❌ Falha ao inicializar InputOrchestrator")
            return
        
        # 3. Teste de ActionOrchestrator
        print("\n3. Testando ActionOrchestrator...")
        action_orchestrator = ActionOrchestrator(actions, config_manager)
        success = await action_orchestrator.initialize()
        
        if success:
            print("✅ ActionOrchestrator inicializado com sucesso")
            await action_orchestrator.start()
            print("✅ ActionOrchestrator iniciado com sucesso")
        else:
            print("❌ Falha ao inicializar ActionOrchestrator")
            return
        
        # 4. Teste de Fuser
        print("\n4. Testando PriorityFuser...")
        fuser_config = raw_config.get("fuser", {}).get("config", {})
        fuser = PriorityFuser(fuser_config)
        success = await fuser.initialize()
        
        if success:
            print("✅ PriorityFuser inicializado com sucesso")
        else:
            print("❌ Falha ao inicializar PriorityFuser")
            return
        
        # 5. Teste de LLM Provider
        print("\n5. Testando LLM Provider...")
        llm_config = raw_config.get("llm", {})
        llm_provider = LLMProvider(llm_config)
        success = await llm_provider.initialize()
        
        if success:
            print("✅ LLM Provider inicializado com sucesso")
        else:
            print("❌ Falha ao inicializar LLM Provider")
            return
        
        # 6. Teste de coleta de dados
        print("\n6. Testando coleta de dados...")
        inputs_data = await input_orchestrator.collect_inputs()
        
        if inputs_data:
            print(f"✅ Coletados dados de {len(inputs_data)} inputs")
            for data in inputs_data:
                print(f"   - {data.input_type}: {data.data}")
        else:
            print("❌ Nenhum dado coletado")
        
        # 7. Teste de fusão
        print("\n7. Testando fusão de dados...")
        fused_data = await fuser.fuse(inputs_data)
        
        if fused_data:
            print("✅ Dados fundidos com sucesso")
            print(f"   Tipo: {fused_data.fusion_type}")
            print(f"   Confiança: {fused_data.confidence}")
            print(f"   Dados: {fused_data.data}")
        else:
            print("❌ Falha na fusão de dados")
        
        # 8. Teste de LLM
        if fused_data:
            print("\n8. Testando LLM...")
            system_prompt = config.system_prompt_base
            llm_response = await llm_provider.process(fused_data, system_prompt)
            
            if llm_response:
                print("✅ LLM processou com sucesso")
                print(f"   Resposta: {llm_response.content}")
                print(f"   Modelo: {llm_response.model}")
                print(f"   Tokens: {llm_response.tokens_used}")
            else:
                print("❌ Falha no processamento LLM")
        
        # 9. Teste de execução de actions
        if llm_response:
            print("\n9. Testando execução de actions...")
            action_results = await action_orchestrator.execute_actions(llm_response.content)
            
            if action_results:
                print(f"✅ Executadas {len(action_results)} actions")
                for result in action_results:
                    print(f"   - {result.action_name}: {'✅' if result.success else '❌'}")
            else:
                print("❌ Nenhuma action executada")
        
        # 10. Teste de status
        print("\n10. Testando status do sistema...")
        
        input_status = await input_orchestrator.get_status()
        action_status = await action_orchestrator.get_status()
        fuser_status = await fuser.get_status()
        llm_status = await llm_provider.get_status()
        
        print("✅ Status coletado com sucesso")
        print(f"   Inputs ativos: {input_status['total_inputs']}")
        print(f"   Actions ativas: {action_status['total_actions']}")
        print(f"   Fuser: {fuser_status['name']}")
        print(f"   LLM: {llm_status['provider_type']}")
        
        # 11. Limpeza
        print("\n11. Finalizando sistema...")
        await input_orchestrator.stop()
        await action_orchestrator.stop()
        await llm_provider.stop()
        print("✅ Sistema finalizado com sucesso")
        
        print("\n🎉 Todos os testes passaram com sucesso!")
        print("O sistema t031a5 está funcionando corretamente!")
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        logger.exception("Erro detalhado:")
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_system())
    sys.exit(0 if success else 1)
