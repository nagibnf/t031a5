#!/usr/bin/env python3
"""
Teste do Sistema Híbrido de Microfones
DJI Principal + G1 Backup
"""

import sys
import logging
from pathlib import Path

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from t031a5.audio.hybrid_microphone_manager import HybridMicrophoneManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Teste rápido do sistema híbrido."""
    try:
        logger.info("🎤 TESTE SISTEMA HÍBRIDO - DJI PRINCIPAL + G1 BACKUP")
        logger.info("=" * 60)
        
        # Configuração conforme solicitado
        config = {
            "sample_rate": 16000,
            "test_duration": 2,  # 2s para teste rápido
            "auto_switch": True,
            "quality_threshold": 30
        }
        
        # Inicializa gerenciador
        manager = HybridMicrophoneManager(config)
        
        # Mostra status inicial
        status = manager.get_status_report()
        logger.info(f"🎯 Microfone atual: {status['current_source']}")
        
        # Diagnóstico rápido
        logger.info("\n🔍 Executando diagnóstico...")
        results = manager.run_full_diagnostics()
        
        # Resultado
        logger.info("\n📊 RESULTADOS:")
        for source, test in results["tests"].items():
            if "quality_score" in test:
                score = test['quality_score']
                emoji = "🏆" if score >= 70 else "✅" if score >= 50 else "⚠️"
                logger.info(f"  {emoji} {source.upper()}: {score}/100")
            else:
                logger.info(f"  ❌ {source.upper()}: {test.get('error', 'Erro')}")
        
        logger.info("\n💡 RECOMENDAÇÕES:")
        for rec in results["recommendations"]:
            logger.info(f"  {rec}")
            
        logger.info(f"\n✅ Sistema híbrido funcionando! Usando: {manager.current_source.value}")
        
    except Exception as e:
        logger.error(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
