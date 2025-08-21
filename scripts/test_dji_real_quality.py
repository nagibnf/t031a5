#!/usr/bin/env python3
"""
Teste CORRETO de Qualidade - DJI Mic 2 via PulseAudio

Acessa o DJI Mic 2 corretamente via PulseAudio para teste real de qualidade.
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

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    logger.warning("PyAudio não disponível")
    PYAUDIO_AVAILABLE = False


class DJIMicRealTester:
    """Testador correto do DJI Mic 2."""
    
    def __init__(self):
        self.test_duration = 5
        self.sample_rate = 16000
        
    def find_dji_device_pulse(self):
        """Encontra dispositivo DJI no PulseAudio."""
        try:
            # Executa pactl para listar sources
            result = subprocess.run(['pactl', 'list', 'sources', 'short'], 
                                  capture_output=True, text=True)
            
            sources = result.stdout.strip().split('\n')
            dji_source = None
            
            for source in sources:
                if 'DJI' in source or 'dji' in source:
                    parts = source.split('\t')
                    dji_source = {
                        'index': int(parts[0]),
                        'name': parts[1],
                        'driver': parts[2],
                        'format': parts[3],
                        'status': parts[4]
                    }
                    break
            
            return dji_source
            
        except Exception as e:
            logger.error(f"Erro ao procurar DJI no PulseAudio: {e}")
            return None
    
    def test_dji_via_pulse_direct(self):
        """Testa DJI via comando direto parec."""
        logger.info("🎤 Testando DJI Mic 2 via PulseAudio direto...")
        
        dji_source = self.find_dji_device_pulse()
        if not dji_source:
            logger.error("❌ DJI source não encontrado no PulseAudio")
            return None
        
        logger.info(f"✅ DJI encontrado: {dji_source['name']}")
        logger.info(f"   Formato: {dji_source['format']}")
        logger.info(f"   Status: {dji_source['status']}")
        
        try:
            # Grava áudio via parec (PulseAudio record)
            output_file = "/tmp/dji_test_audio.wav"
            cmd = [
                'parec',
                '--device', dji_source['name'],
                '--format=s16le',
                '--rate=16000',
                '--channels=1',
                f'--latency-msec=50',
                f'--record-time={self.test_duration}',
                output_file
            ]
            
            logger.info(f"🎵 Gravando {self.test_duration}s do DJI...")
            logger.info(f"   Comando: {' '.join(cmd)}")
            
            # Executa gravação
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.test_duration + 2)
            
            if result.returncode == 0:
                logger.info("✅ Gravação DJI concluída")
                
                # Analisa arquivo gerado
                return self.analyze_wav_file(output_file, "DJI_Mic2_PulseAudio")
            else:
                logger.error(f"❌ Erro na gravação: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro no teste DJI direto: {e}")
            return None
    
    def test_dji_via_pyaudio_corrected(self):
        """Testa DJI via PyAudio com configuração correta."""
        logger.info("🎤 Testando DJI Mic 2 via PyAudio corrigido...")
        
        if not PYAUDIO_AVAILABLE:
            logger.warning("⚠️ PyAudio não disponível")
            return None
        
        try:
            audio = pyaudio.PyAudio()
            
            # Procura especificamente por DJI no nome do dispositivo
            dji_device_index = None
            for i in range(audio.get_device_count()):
                info = audio.get_device_info_by_index(i)
                device_name = info['name'].lower()
                
                if 'dji' in device_name and info['maxInputChannels'] > 0:
                    dji_device_index = i
                    logger.info(f"✅ DJI encontrado: {info['name']}")
                    logger.info(f"   Index: {i}")
                    logger.info(f"   Channels: {info['maxInputChannels']}")
                    logger.info(f"   Sample Rate: {info['defaultSampleRate']}")
                    break
            
            if dji_device_index is None:
                logger.warning("⚠️ DJI não encontrado via PyAudio - usando PulseAudio")
                audio.terminate()
                return self.test_dji_via_pulse_direct()
            
            # Configura stream com parâmetros específicos
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                input_device_index=dji_device_index,
                frames_per_buffer=1024
            )
            
            logger.info(f"🎵 Capturando áudio DJI por {self.test_duration} segundos...")
            
            # Captura áudio
            audio_frames = []
            frames_to_capture = int(self.sample_rate / 1024 * self.test_duration)
            
            for frame in range(frames_to_capture):
                try:
                    data = stream.read(1024, exception_on_overflow=False)
                    audio_frames.append(data)
                except Exception as e:
                    logger.warning(f"Erro no frame {frame}: {e}")
                    continue
            
            # Finaliza stream
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            if not audio_frames:
                logger.error("❌ Nenhum frame de áudio capturado")
                return None
            
            # Converte para numpy
            audio_data = b''.join(audio_frames)
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            
            logger.info("✅ Captura DJI via PyAudio concluída")
            logger.info(f"   Frames capturados: {len(audio_frames)}")
            logger.info(f"   Amostras: {len(audio_np)}")
            
            return self.analyze_audio_quality(audio_np, "DJI_Mic2_PyAudio_Corrected")
            
        except Exception as e:
            logger.error(f"❌ Erro no teste DJI via PyAudio: {e}")
            if 'audio' in locals():
                audio.terminate()
            return None
    
    def analyze_wav_file(self, wav_path, source_name):
        """Analisa arquivo WAV gerado."""
        try:
            import wave
            
            with wave.open(wav_path, 'rb') as wav_file:
                frames = wav_file.readframes(wav_file.getnframes())
                audio_np = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
            
            return self.analyze_audio_quality(audio_np, source_name)
            
        except Exception as e:
            logger.error(f"Erro ao analisar WAV: {e}")
            return {"source": source_name, "error": str(e)}
    
    def analyze_audio_quality(self, audio_data, source_name):
        """Analisa qualidade do áudio."""
        try:
            # Métricas básicas
            rms_level = np.sqrt(np.mean(audio_data**2))
            peak_level = np.max(np.abs(audio_data))
            
            # Análise de ruído
            noise_floor = np.percentile(np.abs(audio_data), 10)
            signal_level = np.percentile(np.abs(audio_data), 90)
            
            # SNR
            if noise_floor > 0:
                snr_estimate = 20 * np.log10(signal_level / noise_floor)
            else:
                snr_estimate = float('inf') if signal_level > 0 else 0
            
            # Análise de frequência
            fft = np.fft.rfft(audio_data)
            freq_magnitude = np.abs(fft)
            dominant_freq = np.argmax(freq_magnitude) * self.sample_rate / (2 * len(freq_magnitude))
            
            quality_metrics = {
                "source": source_name,
                "rms_level": float(rms_level),
                "peak_level": float(peak_level),
                "noise_floor": float(noise_floor),
                "signal_level": float(signal_level),
                "snr_estimate": float(snr_estimate),
                "dominant_frequency": float(dominant_freq),
                "dynamic_range": float(peak_level - noise_floor),
                "sample_count": len(audio_data),
                "duration": len(audio_data) / self.sample_rate,
                "has_signal": rms_level > 0.001,  # Detecta se há sinal real
                "quality_score": self.calculate_quality_score(rms_level, snr_estimate, peak_level)
            }
            
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Erro na análise de {source_name}: {e}")
            return {"source": source_name, "error": str(e)}
    
    def calculate_quality_score(self, rms, snr, peak):
        """Calcula score de qualidade (0-100)."""
        try:
            # Score baseado em múltiplos fatores
            rms_score = min(rms * 100, 30)  # RMS contribui até 30 pontos
            snr_score = min(max(snr - 10, 0) * 2, 40)  # SNR contribui até 40 pontos  
            peak_score = min(peak * 30, 30)  # Peak contribui até 30 pontos
            
            total_score = rms_score + snr_score + peak_score
            return min(total_score, 100)
            
        except:
            return 0
    
    def run_real_dji_test(self):
        """Executa teste real do DJI Mic 2."""
        logger.info("🎤 TESTE REAL DJI MIC 2 - CORRIGIDO")
        logger.info("=" * 50)
        
        # Testa via PulseAudio (mais confiável)
        pulse_result = self.test_dji_via_pulse_direct()
        
        # Testa via PyAudio (como backup)
        pyaudio_result = self.test_dji_via_pyaudio_corrected()
        
        # Mostra resultados
        logger.info("\n📊 RESULTADOS CORRIGIDOS:")
        logger.info("=" * 40)
        
        if pulse_result and "error" not in pulse_result:
            logger.info("🎵 DJI VIA PULSEAUDIO:")
            logger.info(f"   RMS Level: {pulse_result['rms_level']:.4f}")
            logger.info(f"   Peak Level: {pulse_result['peak_level']:.4f}")
            logger.info(f"   SNR: {pulse_result['snr_estimate']:.1f} dB")
            logger.info(f"   Quality Score: {pulse_result['quality_score']:.1f}/100")
            logger.info(f"   Has Signal: {'✅' if pulse_result['has_signal'] else '❌'}")
        
        if pyaudio_result and "error" not in pyaudio_result:
            logger.info("\n🎵 DJI VIA PYAUDIO:")
            logger.info(f"   RMS Level: {pyaudio_result['rms_level']:.4f}")
            logger.info(f"   Peak Level: {pyaudio_result['peak_level']:.4f}")
            logger.info(f"   SNR: {pyaudio_result['snr_estimate']:.1f} dB")
            logger.info(f"   Quality Score: {pyaudio_result['quality_score']:.1f}/100")
            logger.info(f"   Has Signal: {'✅' if pyaudio_result['has_signal'] else '❌'}")
        
        # Recomendação baseada em resultados reais
        logger.info("\n💡 AVALIAÇÃO CORRIGIDA:")
        
        best_result = pulse_result if pulse_result and pulse_result.get('has_signal') else pyaudio_result
        
        if best_result and best_result.get('has_signal'):
            score = best_result.get('quality_score', 0)
            if score > 70:
                logger.info("   ✅ DJI Mic 2 tem EXCELENTE qualidade")
                recommendation = "dji_excellent"
            elif score > 50:
                logger.info("   ✅ DJI Mic 2 tem BOA qualidade")
                recommendation = "dji_good"
            else:
                logger.info("   ⚠️ DJI Mic 2 funciona mas qualidade básica")
                recommendation = "dji_basic"
        else:
            logger.info("   ❌ DJI Mic 2 não está capturando áudio corretamente")
            recommendation = "dji_problem"
        
        logger.info("\n🎯 COMPARAÇÃO G1 vs DJI:")
        logger.info("   • DJI: Qualidade testada em ambiente real")
        logger.info("   • G1 Interno: Qualidade ainda não testada (requer implementação)")
        logger.info("   • Recomendação: Testar ambos lado a lado quando G1 estiver implementado")
        
        return {
            "pulse_result": pulse_result,
            "pyaudio_result": pyaudio_result,
            "recommendation": recommendation,
            "timestamp": datetime.now().isoformat()
        }


def main():
    """Função principal."""
    try:
        tester = DJIMicRealTester()
        results = tester.run_real_dji_test()
        
        logger.info("\n✅ Teste DJI REAL concluído!")
        logger.info("\n📋 PRÓXIMOS PASSOS:")
        logger.info("   1. Comparar com implementação G1 interno")
        logger.info("   2. Decidir baseado em testes reais")
        logger.info("   3. Sistema híbrido inteligente")
        
    except KeyboardInterrupt:
        logger.info("\n⏹️ Teste interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
