#!/usr/bin/env python3
"""
🤖 SISTEMA t031a5 - ARQUIVO PRINCIPAL ÚNICO
Sistema conversacional contínuo baseado na arquitetura OM1

ARQUITETURA CONTÍNUA:
Inputs → Fuser → LLM → Actions → [LOOP INFINITO]

STATUS: Sistema "VIVO" - sem step-by-step, apenas conversação fluida
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

# Adicionar paths
sys.path.insert(0, str(Path(__file__).parent / "src"))

from t031a5.runtime.cortex import CortexRuntime

# Configurar logging limpo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)

# Suprimir logs excessivos
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

async def main():
    """Sistema principal t031a5 - Loop conversacional contínuo."""
    
    print("🤖 SISTEMA t031a5 - G1 TOBIAS")
    print("=" * 50)
    print("🎯 MODO: Sistema conversacional VIVO (contínuo)")
    print("📋 BASE: Arquitetura OM1 - inputs→fuser→llm→actions")
    print("🔄 STATUS: Loop infinito - sem step-by-step")
    print("=" * 50)
    
    # Configuração de produção
    config_path = Path("config/g1_production.json5")
    
    if not config_path.exists():
        print(f"❌ Configuração não encontrada: {config_path}")
        print("💡 Executando: python scripts/create_config.py")
        return
    
    # Inicializar sistema
    cortex = CortexRuntime(config_path)
    
    try:
        print("🔧 Inicializando componentes...")
        success = await cortex.initialize()
        
        if not success:
            print("❌ Falha na inicialização")
            return
        
        print("✅ Sistema inicializado com sucesso")
        print("")
        print("🔄 INICIANDO LOOP CONVERSACIONAL CONTÍNUO...")
        print("   - Inputs: DJI Mic + Câmera + Sensores")
        print("   - Fuser: NLDB multimodal")
        print("   - LLM: Processamento inteligente")
        print("   - Actions: Fala + Gestos + LEDs")
        print("")
        print("🛑 Pressione Ctrl+C para parar")
        print("-" * 50)
        
        # LOOP PRINCIPAL CONTÍNUO (como OM1)
        await cortex.start()
        
    except KeyboardInterrupt:
        print("\n🛑 Parando sistema...")
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await cortex.stop()
        print("✅ Sistema parado com segurança")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Sistema interrompido pelo usuário")
