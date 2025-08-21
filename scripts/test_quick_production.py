#!/usr/bin/env python3
"""
Teste Rápido de Produção - Sistema Híbrido + Componentes Core
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Adiciona paths
sys.path.insert(0, "/home/unitree/t031a5/src")

def test_hybrid_audio():
    """Testa sistema híbrido de áudio."""
    logger.info("🎤 Testando sistema híbrido de áudio...")
    
    try:
        from t031a5.audio.hybrid_microphone_manager import HybridMicrophoneManager
        
        manager = HybridMicrophoneManager({
            "sample_rate": 16000,
            "test_duration": 2,
            "auto_switch": True
        })
        
        results = manager.run_full_diagnostics()
        
        current_mic = manager.current_source.value if manager.current_source else "none"
        working_mics = []
        
        for source, test in results["tests"].items():
            if "quality_score" in test and test["quality_score"] >= 10:
                working_mics.append(f"{source}({test['quality_score']}/100)")
        
        has_dji = manager.current_source.value == "dji_external" if manager.current_source else False
        
        logger.info(f"✅ Microfone atual: {current_mic}")
        logger.info(f"✅ Funcionais: {working_mics}")
        logger.info(f"✅ DJI como principal: {has_dji}")
        
        return len(working_mics) > 0
        
    except Exception as e:
        logger.error(f"❌ Erro no sistema híbrido: {e}")
        return False

def test_g1_basic_connection():
    """Testa conexão básica com G1."""
    logger.info("🤖 Testando conexão básica G1...")
    
    try:
        from unitree_sdk2py.core.channel import ChannelFactoryInitialize
        
        ChannelFactoryInitialize(0, "eth0")
        logger.info("✅ Canal DDS inicializado")
        
        # Teste de ping básico
        import subprocess
        result = subprocess.run(['ping', '-c', '3', '192.168.123.161'], 
                              capture_output=True, timeout=10)
        
        if result.returncode == 0:
            logger.info("✅ G1 respondendo ao ping")
            return True
        else:
            logger.error("❌ G1 não responde ao ping")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro conexão G1: {e}")
        return False

def test_imports():
    """Testa imports dos módulos principais."""
    logger.info("📦 Testando imports dos módulos...")
    
    modules_to_test = [
        ("t031a5.audio.hybrid_microphone_manager", "HybridMicrophoneManager"),
        ("unitree_sdk2py.core.channel", "ChannelFactoryInitialize"),
        ("pyaudio", None),
        ("numpy", None)
    ]
    
    success_count = 0
    
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name] if class_name else [])
            if class_name:
                getattr(module, class_name)
            logger.info(f"✅ {module_name}")
            success_count += 1
        except ImportError as e:
            logger.error(f"❌ {module_name}: {e}")
        except AttributeError as e:
            logger.error(f"❌ {module_name}.{class_name}: {e}")
    
    return success_count >= 3  # Pelo menos 3 módulos funcionando

def main():
    """Executa teste rápido de produção."""
    logger.info("🚀 TESTE RÁPIDO DE PRODUÇÃO - SISTEMA HÍBRIDO")
    logger.info("=" * 60)
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    tests = [
        ("Imports Básicos", test_imports),
        ("Sistema Híbrido Audio", test_hybrid_audio),
        ("Conexão G1 Básica", test_g1_basic_connection)
    ]
    
    results = {}
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 EXECUTANDO: {test_name}")
        logger.info("-" * 40)
        
        try:
            success = test_func()
            results[test_name] = success
            
            if success:
                logger.info(f"✅ {test_name}: PASSOU")
                passed += 1
            else:
                logger.info(f"❌ {test_name}: FALHOU")
                
        except Exception as e:
            logger.error(f"❌ {test_name}: EXCEÇÃO - {e}")
            results[test_name] = False
    
    # Relatório final
    logger.info("\n" + "=" * 60)
    logger.info("📊 RELATÓRIO FINAL")
    logger.info("=" * 60)
    
    for test_name, success in results.items():
        status = "✅ PASSOU" if success else "❌ FALHOU"
        logger.info(f"{test_name}: {status}")
    
    success_rate = (passed / total) * 100
    logger.info(f"\n🎯 TAXA DE SUCESSO: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        logger.info("🎉 SISTEMA HÍBRIDO FUNCIONANDO ADEQUADAMENTE!")
    elif success_rate >= 60:
        logger.info("⚠️ Sistema funcionando com limitações")
    else:
        logger.info("❌ Sistema com problemas significativos")
    
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
