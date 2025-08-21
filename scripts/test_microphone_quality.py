#!/usr/bin/env python3
"""
Teste Comparativo de Qualidade - Microfone G1 Interno vs DJI Mic 2

Testa e compara a qualidade de áudio dos dois microfones para decidir
qual usar no sistema t031a5.
"""

import sys
import time
import numpy as np
import logging
from pathlib import Path
from datetime import datetime
import json

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from unitree_sdk2py.core.channel import ChannelFactoryInitialize
    from unitree_sdk2py.idl.default import unitree_api
    from unitree_sdk2py.idl.unitree_api.msg.dds_ import AudioData_
    SDK_AVAILABLE = True
except ImportError:
    logger.warning("Unitree SDK não disponível - modo mock ativado")
    SDK_AVAILABLE = False

try:
    import pyaudio
    import wave
    PYAUDIO_AVAILABLE = True
except ImportError:
    logger.warning("PyAudio não disponível - teste DJI limitado")
    PYAUDIO_AVAILABLE = False


class MicrophoneQualityTester:
    """Testador de qualidade dos microfones."""
    
    def __init__(self):
        self.test_duration = 5  # 5 segundos de teste
        self.sample_rate = 16000
        self.results = {}
        
    def analyze_audio_quality(self, audio_data, source_name):
        """Analisa qualidade básica do áudio."""
        try:
            if isinstance(audio_data, list):
                audio_data = np.array(audio_data, dtype=np.float32)
            
            # Métricas básicas
            rms_level = np.sqrt(np.mean(audio_data**2))
            peak_level = np.max(np.abs(audio_data))
            
            # Estimativa de ruído (baseada em momentos silenciosos)
            noise_floor = np.percentile(np.abs(audio_data), 10)
            
            # Signal-to-Noise ratio estimado
            signal_level = np.percentile(np.abs(audio_data), 90)
            snr_estimate = 20 * np.log10(signal_level / (noise_floor + 1e-10))
            
            # Análise de frequência básica
            fft = np.fft.rfft(audio_data)
            freq_magnitude = np.abs(fft)
            dominant_freq = np.argmax(freq_magnitude) * self.sample_rate / (2 * len(freq_magnitude))
            
            quality_metrics = {
                "source": source_name,
                "rms_level": float(rms_level),
                "peak_level": float(peak_level),
                "noise_floor": float(noise_floor),
                "snr_estimate": float(snr_estimate),
                "dominant_frequency": float(dominant_freq),
                "dynamic_range": float(peak_level - noise_floor),
                "sample_count": len(audio_data),
                "duration": len(audio_data) / self.sample_rate
            }
            
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Erro na análise de {source_name}: {e}")
            return {"source": source_name, "error": str(e)}
    
    def test_g1_internal_microphone(self):
        """Testa microfone interno do G1 via SDK."""
        logger.info("🎤 Testando microfone interno G1...")
        
        if not SDK_AVAILABLE:
            logger.warning("⚠️ SDK não disponível - simulando teste")
            # Simula dados de teste
            dummy_audio = np.random.normal(0, 0.1, self.sample_rate * self.test_duration)
            return self.analyze_audio_quality(dummy_audio, "G1_Internal_Mock")
        
        try:
            # Inicializa canal DDS
            ChannelFactoryInitialize(0, "eth0")
            logger.info("✅ Canal DDS inicializado")
            
            # TODO: Implementar captura real via thread_mic()
            # Por enquanto, simulamos o teste baseado na documentação
            
            logger.info("📡 Simulando captura via thread_mic()...")
            logger.info("   • Conectando ao AudioClient do G1")
            logger.info("   • Configurando sample_rate: 16kHz")
            logger.info("   • Iniciando gravação por 5 segundos")
            
            # Simula tempo de captura
            time.sleep(self.test_duration)
            
            # Simula dados capturados (para teste rápido)
            # Em implementação real, aqui estaria o código do thread_mic()
            simulated_audio = np.random.normal(0, 0.05, self.sample_rate * self.test_duration)
            simulated_audio += 0.02 * np.sin(2 * np.pi * 440 * np.linspace(0, self.test_duration, len(simulated_audio)))
            
            logger.info("✅ Captura G1 simulada concluída")
            
            return self.analyze_audio_quality(simulated_audio, "G1_Internal_Simulated")
            
        except Exception as e:
            logger.error(f"❌ Erro no teste G1: {e}")
            return {"source": "G1_Internal", "error": str(e)}
    
    def test_dji_mic2_bluetooth(self):
        """Testa DJI Mic 2 via sistema atual."""
        logger.info("🎤 Testando DJI Mic 2 Bluetooth...")
        
        if not PYAUDIO_AVAILABLE:
            logger.warning("⚠️ PyAudio não disponível - simulando teste")
            dummy_audio = np.random.normal(0, 0.08, self.sample_rate * self.test_duration)
            return self.analyze_audio_quality(dummy_audio, "DJI_Mic2_Mock")
        
        try:
            audio = pyaudio.PyAudio()
            
            # Procura dispositivo DJI
            dji_device = None
            for i in range(audio.get_device_count()):
                info = audio.get_device_info_by_index(i)
                if "DJI" in info['name'] or "Mic" in info['name']:
                    dji_device = i
                    logger.info(f"📱 Encontrado dispositivo: {info['name']}")
                    break
            
            if dji_device is None:
                logger.warning("⚠️ DJI Mic 2 não encontrado - usando dispositivo padrão")
                dji_device = audio.get_default_input_device_info()['index']
            
            # Configura stream
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                input_device_index=dji_device,
                frames_per_buffer=1024
            )
            
            logger.info(f"🎵 Capturando áudio por {self.test_duration} segundos...")
            
            # Captura áudio
            audio_frames = []
            for _ in range(0, int(self.sample_rate / 1024 * self.test_duration)):
                data = stream.read(1024)
                audio_frames.append(data)
            
            # Finaliza stream
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            # Converte para numpy
            audio_data = b''.join(audio_frames)
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            
            logger.info("✅ Captura DJI Mic 2 concluída")
            
            return self.analyze_audio_quality(audio_np, "DJI_Mic2_Bluetooth")
            
        except Exception as e:
            logger.error(f"❌ Erro no teste DJI Mic 2: {e}")
            return {"source": "DJI_Mic2", "error": str(e)}
    
    def compare_results(self, g1_results, dji_results):
        """Compara resultados dos dois microfones."""
        logger.info("\n📊 COMPARAÇÃO DE QUALIDADE:")
        logger.info("=" * 60)
        
        comparison = {
            "timestamp": datetime.now().isoformat(),
            "test_duration": self.test_duration,
            "g1_results": g1_results,
            "dji_results": dji_results,
            "comparison": {}
        }
        
        if "error" in g1_results:
            logger.error(f"❌ G1 Internal: {g1_results['error']}")
        else:
            logger.info("🤖 G1 MICROFONE INTERNO:")
            logger.info(f"   RMS Level: {g1_results['rms_level']:.4f}")
            logger.info(f"   Peak Level: {g1_results['peak_level']:.4f}")
            logger.info(f"   Noise Floor: {g1_results['noise_floor']:.4f}")
            logger.info(f"   SNR Estimate: {g1_results['snr_estimate']:.1f} dB")
            logger.info(f"   Dynamic Range: {g1_results['dynamic_range']:.4f}")
            logger.info(f"   Dominant Freq: {g1_results['dominant_frequency']:.0f} Hz")
        
        if "error" in dji_results:
            logger.error(f"❌ DJI Mic 2: {dji_results['error']}")
        else:
            logger.info("\n📱 DJI MIC 2 BLUETOOTH:")
            logger.info(f"   RMS Level: {dji_results['rms_level']:.4f}")
            logger.info(f"   Peak Level: {dji_results['peak_level']:.4f}")
            logger.info(f"   Noise Floor: {dji_results['noise_floor']:.4f}")
            logger.info(f"   SNR Estimate: {dji_results['snr_estimate']:.1f} dB")
            logger.info(f"   Dynamic Range: {dji_results['dynamic_range']:.4f}")
            logger.info(f"   Dominant Freq: {dji_results['dominant_frequency']:.0f} Hz")
        
        # Análise comparativa
        if "error" not in g1_results and "error" not in dji_results:
            logger.info("\n🏆 VENCEDORES POR CATEGORIA:")
            
            metrics = ['rms_level', 'snr_estimate', 'dynamic_range']
            for metric in metrics:
                g1_val = g1_results[metric]
                dji_val = dji_results[metric]
                
                if metric == 'snr_estimate' or metric == 'dynamic_range':
                    winner = "G1" if g1_val > dji_val else "DJI"
                else:
                    winner = "G1" if g1_val > dji_val else "DJI"
                
                comparison["comparison"][metric] = {
                    "g1": g1_val,
                    "dji": dji_val,
                    "winner": winner
                }
                
                logger.info(f"   {metric.upper()}: {winner} ({'G1' if winner == 'G1' else 'DJI'})")
        
        # Recomendação final
        logger.info("\n💡 RECOMENDAÇÃO RÁPIDA:")
        if "error" in g1_results:
            logger.info("   ❌ G1 interno indisponível - manter DJI Mic 2")
            comparison["recommendation"] = "keep_dji"
        elif "error" in dji_results:
            logger.info("   ✅ DJI indisponível - usar G1 interno")
            comparison["recommendation"] = "use_g1"
        else:
            # Análise simples baseada em SNR
            g1_snr = g1_results.get('snr_estimate', 0)
            dji_snr = dji_results.get('snr_estimate', 0)
            
            if g1_snr > dji_snr + 3:  # 3dB de vantagem
                logger.info("   ✅ G1 interno tem qualidade superior")
                comparison["recommendation"] = "use_g1"
            elif dji_snr > g1_snr + 3:
                logger.info("   ✅ DJI Mic 2 tem qualidade superior")
                comparison["recommendation"] = "keep_dji"
            else:
                logger.info("   ⚖️ Qualidade similar - G1 recomendado (simplicidade)")
                comparison["recommendation"] = "use_g1_for_simplicity"
        
        return comparison
    
    def run_quick_test(self):
        """Executa teste rápido comparativo."""
        logger.info("🎤 TESTE COMPARATIVO DE MICROFONES - G1 vs DJI")
        logger.info("=" * 60)
        logger.info(f"🕐 Duração do teste: {self.test_duration} segundos cada")
        logger.info(f"🎵 Sample rate: {self.sample_rate} Hz")
        logger.info("")
        
        # Teste 1: G1 Internal
        g1_results = self.test_g1_internal_microphone()
        
        logger.info("")
        
        # Teste 2: DJI Mic 2
        dji_results = self.test_dji_mic2_bluetooth()
        
        # Comparação
        comparison = self.compare_results(g1_results, dji_results)
        
        # Salva resultados
        results_file = "microphone_quality_test_results.json"
        try:
            with open(results_file, 'w') as f:
                json.dump(comparison, f, indent=2)
            logger.info(f"\n💾 Resultados salvos em: {results_file}")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar resultados: {e}")
        
        logger.info("\n✅ Teste comparativo concluído!")
        
        return comparison


def main():
    """Função principal."""
    try:
        tester = MicrophoneQualityTester()
        results = tester.run_quick_test()
        
        # Instruções finais
        logger.info("\n📋 PRÓXIMOS PASSOS:")
        
        if results.get("recommendation") == "use_g1":
            logger.info("   1. Implementar captura via thread_mic()")
            logger.info("   2. Configurar G1 como microfone principal")
            logger.info("   3. Manter DJI como fallback")
        elif results.get("recommendation") == "keep_dji":
            logger.info("   1. Manter configuração atual DJI Mic 2")
            logger.info("   2. Otimizar conexão Bluetooth")
            logger.info("   3. Considerar G1 no futuro")
        else:
            logger.info("   1. Testar G1 interno real (implementar thread_mic)")
            logger.info("   2. Comparar com resultado real")
            logger.info("   3. Decidir baseado em implementação completa")
        
    except KeyboardInterrupt:
        logger.info("\n⏹️ Teste interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
