#!/usr/bin/env python3
"""
Debug da Qualidade do DJI Mic 2
Investigação detalhada do problema de threshold
"""

import sys
import time
import numpy as np
import logging
import subprocess
from pathlib import Path
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Adiciona paths
sys.path.insert(0, "/home/unitree/t031a5/src")

def analyze_audio_detailed(audio_data, source_name):
    """Análise detalhada de qualidade de áudio."""
    try:
        rms_level = np.sqrt(np.mean(audio_data**2))
        peak_level = np.max(np.abs(audio_data))
        noise_floor = np.percentile(np.abs(audio_data), 10)
        signal_level = np.percentile(np.abs(audio_data), 90)
        
        # SNR
        if noise_floor > 0:
            snr_estimate = 20 * np.log10(signal_level / noise_floor)
        else:
            snr_estimate = float('inf') if signal_level > 0 else 0
        
        # Score usando algoritmo do sistema híbrido
        rms_score = min(rms_level * 1000, 30)
        snr_score = min(max(snr_estimate - 10, 0) * 1.5, 40)
        peak_score = min(peak_level * 30, 30)
        total_score = int(min(rms_score + snr_score + peak_score, 100))
        
        has_signal = rms_level > 0.001
        
        logger.info(f"\n📊 ANÁLISE DETALHADA - {source_name}:")
        logger.info(f"   📐 RMS Level: {rms_level:.6f}")
        logger.info(f"   📈 Peak Level: {peak_level:.6f}")
        logger.info(f"   📉 Noise Floor: {noise_floor:.6f}")
        logger.info(f"   📊 Signal Level: {signal_level:.6f}")
        logger.info(f"   🎯 SNR: {snr_estimate:.1f} dB")
        logger.info(f"   ✅ Has Signal: {'SIM' if has_signal else 'NÃO'}")
        logger.info(f"   🎯 Score Breakdown:")
        logger.info(f"      RMS Score: {rms_score:.1f}/30")
        logger.info(f"      SNR Score: {snr_score:.1f}/40")
        logger.info(f"      Peak Score: {peak_score:.1f}/30")
        logger.info(f"   📊 TOTAL SCORE: {total_score}/100")
        
        # Diagnóstico
        if total_score < 30:
            logger.info(f"   ❌ ABAIXO DO THRESHOLD (30)")
            if rms_level < 0.005:
                logger.info(f"   🔍 PROBLEMA: RMS muito baixo - sem áudio suficiente")
            if snr_estimate < 10:
                logger.info(f"   🔍 PROBLEMA: SNR baixo - muito ruído")
            if peak_level < 0.01:
                logger.info(f"   🔍 PROBLEMA: Peak baixo - sem picos de sinal")
        else:
            logger.info(f"   ✅ ACIMA DO THRESHOLD")
        
        return {
            "rms_level": rms_level,
            "peak_level": peak_level,
            "snr_estimate": snr_estimate,
            "noise_floor": noise_floor,
            "signal_level": signal_level,
            "has_signal": has_signal,
            "quality_score": total_score,
            "breakdown": {
                "rms_score": rms_score,
                "snr_score": snr_score,
                "peak_score": peak_score
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na análise: {e}")
        return None

def test_dji_capture_silent():
    """Testa captura DJI em ambiente silencioso."""
    logger.info("🔇 TESTE 1: DJI em ambiente silencioso")
    
    try:
        # DJI device info
        result = subprocess.run(['pactl', 'list', 'sources', 'short'], 
                              capture_output=True, text=True, timeout=5)
        
        dji_device = None
        for line in result.stdout.split('\n'):
            if 'DJI' in line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    dji_device = parts[1]
                    break
        
        if not dji_device:
            logger.error("❌ DJI não encontrado")
            return None
        
        logger.info(f"✅ DJI encontrado: {dji_device}")
        
        # Garante que está desmutado
        subprocess.run(['pactl', 'set-source-mute', dji_device, '0'], timeout=3)
        logger.info("🔧 DJI desmutado")
        
        # Captura 3 segundos
        logger.info("📢 Mantendo silêncio... capturando 3 segundos")
        
        cmd = [
            'timeout', '3s',
            'parec',
            '--device', dji_device,
            '--format=s16le',
            '--rate=16000',
            '--channels=1',
            '--latency-msec=50'
        ]
        
        result = subprocess.run(cmd, capture_output=True, timeout=5)
        
        if result.returncode == 0 and result.stdout:
            audio_np = np.frombuffer(result.stdout, dtype=np.int16).astype(np.float32) / 32768.0
            logger.info(f"✅ Capturado: {len(audio_np)} amostras")
            return analyze_audio_detailed(audio_np, "DJI Silent")
        else:
            logger.error(f"❌ Falha na captura: {result.stderr}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        return None

def test_dji_capture_with_speech():
    """Testa captura DJI com fala."""
    logger.info("🗣️ TESTE 2: DJI com fala")
    
    try:
        # DJI device info
        result = subprocess.run(['pactl', 'list', 'sources', 'short'], 
                              capture_output=True, text=True, timeout=5)
        
        dji_device = None
        for line in result.stdout.split('\n'):
            if 'DJI' in line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    dji_device = parts[1]
                    break
        
        if not dji_device:
            logger.error("❌ DJI não encontrado")
            return None
        
        # Captura com fala
        logger.info("📢 FALE ALGO durante os próximos 3 segundos...")
        time.sleep(1)  # Delay para pessoa se preparar
        
        cmd = [
            'timeout', '3s',
            'parec',
            '--device', dji_device,
            '--format=s16le',
            '--rate=16000',
            '--channels=1',
            '--latency-msec=50'
        ]
        
        result = subprocess.run(cmd, capture_output=True, timeout=5)
        
        if result.returncode == 0 and result.stdout:
            audio_np = np.frombuffer(result.stdout, dtype=np.int16).astype(np.float32) / 32768.0
            logger.info(f"✅ Capturado: {len(audio_np)} amostras")
            return analyze_audio_detailed(audio_np, "DJI With Speech")
        else:
            logger.error(f"❌ Falha na captura: {result.stderr}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        return None

def test_hybrid_system_debug():
    """Testa sistema híbrido com debug."""
    logger.info("🔍 TESTE 3: Sistema híbrido com debug")
    
    try:
        from t031a5.audio.hybrid_microphone_manager import HybridMicrophoneManager
        
        # Manager com debug
        manager = HybridMicrophoneManager({
            "sample_rate": 16000,
            "test_duration": 2,
            "auto_switch": True,
            "quality_threshold": 20  # Threshold mais baixo para debug
        })
        
        logger.info(f"🎯 Microfone atual: {manager.current_source.value}")
        
        # Teste específico do DJI
        logger.info("🧪 Testando qualidade DJI diretamente...")
        dji_quality = manager.test_microphone_quality(manager.current_source)
        
        if dji_quality:
            logger.info(f"\n📊 RESULTADO SISTEMA HÍBRIDO:")
            logger.info(f"   Quality Score: {dji_quality.quality_score}/100")
            logger.info(f"   RMS Level: {dji_quality.rms_level:.6f}")
            logger.info(f"   SNR: {dji_quality.snr_estimate:.1f} dB")
            logger.info(f"   Has Signal: {dji_quality.has_signal}")
            logger.info(f"   Timestamp: {dji_quality.timestamp}")
            
            return dji_quality
        else:
            logger.error("❌ Sistema híbrido falhou")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro sistema híbrido: {e}")
        return None

def suggest_threshold_adjustment(test_results):
    """Sugere ajuste de threshold baseado nos resultados."""
    logger.info("\n💡 ANÁLISE E SUGESTÕES:")
    logger.info("=" * 50)
    
    scores = []
    for result in test_results:
        if result and "quality_score" in result:
            scores.append(result["quality_score"])
    
    if not scores:
        logger.info("❌ Nenhum score válido - problema na captura")
        return
    
    max_score = max(scores)
    min_score = min(scores)
    avg_score = sum(scores) / len(scores)
    
    logger.info(f"📊 SCORES OBTIDOS:")
    logger.info(f"   Máximo: {max_score}/100")
    logger.info(f"   Mínimo: {min_score}/100")
    logger.info(f"   Média: {avg_score:.1f}/100")
    
    current_threshold = 30
    
    if max_score < current_threshold:
        suggested_threshold = max(int(max_score * 0.8), 10)
        logger.info(f"\n🎯 RECOMENDAÇÃO:")
        logger.info(f"   Threshold atual: {current_threshold}")
        logger.info(f"   Threshold sugerido: {suggested_threshold}")
        logger.info(f"   Motivo: Melhor score ({max_score}) < threshold atual")
        
        return suggested_threshold
    else:
        logger.info(f"\n✅ THRESHOLD ATUAL OK:")
        logger.info(f"   Scores atendem o threshold de {current_threshold}")
        return current_threshold

def main():
    """Debug completo da qualidade do DJI."""
    logger.info("🔍 DEBUG COMPLETO - QUALIDADE DJI MIC 2")
    logger.info("=" * 60)
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    results = []
    
    # Teste 1: Ambiente silencioso
    result1 = test_dji_capture_silent()
    if result1:
        results.append(result1)
    
    # Pequena pausa
    time.sleep(2)
    
    # Teste 2: Com fala
    result2 = test_dji_capture_with_speech() 
    if result2:
        results.append(result2)
    
    # Teste 3: Sistema híbrido
    result3 = test_hybrid_system_debug()
    if result3:
        results.append({
            "quality_score": result3.quality_score,
            "rms_level": result3.rms_level,
            "snr_estimate": result3.snr_estimate
        })
    
    # Análise final
    suggested_threshold = suggest_threshold_adjustment(results)
    
    logger.info("\n🎯 PRÓXIMOS PASSOS:")
    if suggested_threshold and suggested_threshold < 30:
        logger.info(f"1. Ajustar threshold para {suggested_threshold}")
        logger.info("2. Testar novamente o sistema híbrido")
        logger.info("3. Validar com sistema de produção")
    else:
        logger.info("1. Investigar ambiente acústico")
        logger.info("2. Verificar configuração DJI")
        logger.info("3. Testar em condições ideais")
    
    logger.info("\n✅ Debug concluído!")

if __name__ == "__main__":
    main()
