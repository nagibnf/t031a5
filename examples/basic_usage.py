#!/usr/bin/env python3
"""
Exemplo básico de uso do sistema t031a5.

Este exemplo demonstra como usar o sistema básico do G1.
"""

import asyncio
import logging
from pathlib import Path

from t031a5.runtime import CortexRuntime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def main():
    """Função principal do exemplo."""
    logger.info("🚀 Iniciando exemplo básico do t031a5")
    
    # Caminho para a configuração básica
    config_path = Path("config/g1_basic.json5")
    
    if not config_path.exists():
        logger.error(f"Arquivo de configuração não encontrado: {config_path}")
        logger.info("Execute este exemplo a partir do diretório raiz do projeto")
        return
    
    # Cria e inicializa o runtime
    runtime = CortexRuntime(config_path)
    
    try:
        # Inicializa o sistema
        logger.info("Inicializando sistema...")
        success = await runtime.initialize()
        
        if not success:
            logger.error("Falha na inicialização do sistema")
            return
        
        logger.info("✅ Sistema inicializado com sucesso!")
        
        # Mostra status do sistema
        status = runtime.get_status()
        logger.info(f"Status do sistema: {status}")
        
        # Executa por alguns segundos
        logger.info("Executando sistema por 10 segundos...")
        logger.info("Pressione Ctrl+C para parar")
        
        # Inicia o sistema em background
        task = asyncio.create_task(runtime.start())
        
        # Aguarda 10 segundos ou até interrupção
        try:
            await asyncio.wait_for(asyncio.sleep(10), timeout=10)
        except asyncio.TimeoutError:
            pass
        
        # Para o sistema
        logger.info("Parando sistema...")
        await runtime.stop()
        
        # Cancela a task se ainda estiver rodando
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        logger.info("✅ Exemplo concluído com sucesso!")
        
    except KeyboardInterrupt:
        logger.info("Interrupção recebida, parando...")
        await runtime.stop()
    except Exception as e:
        logger.error(f"Erro no exemplo: {e}")
        await runtime.stop()


if __name__ == "__main__":
    asyncio.run(main())
