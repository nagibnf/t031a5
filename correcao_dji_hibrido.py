#!/usr/bin/env python3
"""
🔧 CORREÇÃO SISTEMA HÍBRIDO DJI
Implementa captura com formato nativo correto: s24le 2ch 48000Hz
"""

import sys
import subprocess
import tempfile
import wave
import numpy as np
from pathlib import Path
import logging

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, "/home/unitree/t031a5/src")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CorrecaoDJIHibrido:
    """Correção do sistema híbrido com formato nativo DJI."""
    
    def __init__(self):
        self.dji_device = "alsa_input.usb-DJI_Technology_Co.__Ltd._DJI_MIC_MINI_XSP12345678B-01.analog-stereo"
    
    def capturar_dji_nativo(self, duracao=3.0):
        """Captura DJI com formato nativo correto."""
        try:
            logger.info(f"🎤 Capturando DJI formato nativo ({duracao}s)...")
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                # Comando correto para DJI
                cmd = [
                    "parecord",
                    "--device", self.dji_device,
                    "--format=s24le",    # 24-bit (formato nativo)
                    "--rate=48000",      # 48kHz (formato nativo)
                    "--channels=2",      # Stereo (formato nativo)
                    temp_file.name
                ]
                
                # Capturar por duração especificada
                process = subprocess.Popen(cmd)
                import time
                time.sleep(duracao)
                process.terminate()
                process.wait()
                
                if Path(temp_file.name).exists():
                    file_size = Path(temp_file.name).stat().st_size
                    logger.info(f"✅ Capturado: {file_size} bytes")
                    
                    if file_size > 1000:
                        # Converter para formato utilizável
                        audio_data = self.converter_s24le_para_mono16k(temp_file.name)
                        
                        # Limpeza
                        Path(temp_file.name).unlink()
                        
                        return audio_data, "dji_nativo"
                    else:
                        logger.warning("⚠️ Arquivo muito pequeno")
                        return None, "erro_tamanho"
                else:
                    logger.error("❌ Arquivo não criado")
                    return None, "erro_criacao"
                    
        except Exception as e:
            logger.error(f"❌ Erro captura DJI: {e}")
            return None, f"erro_{e}"
    
    def converter_s24le_para_mono16k(self, arquivo_s24le):
        """Converte arquivo s24le stereo 48kHz para mono 16kHz."""
        try:
            # Ler arquivo WAV s24le
            with wave.open(arquivo_s24le, 'rb') as wav_file:
                frames = wav_file.readframes(wav_file.getnframes())
                sample_width = wav_file.getsampwidth()  # Deve ser 3 (24-bit)
                framerate = wav_file.getframerate()    # Deve ser 48000
                nchannels = wav_file.getnchannels()    # Deve ser 2
                
                logger.info(f"📊 Arquivo original: {sample_width}bytes, {framerate}Hz, {nchannels}ch")
                
                if sample_width == 3:  # 24-bit
                    # Converter 24-bit para float32
                    audio_data = np.frombuffer(frames, dtype=np.uint8)
                    audio_data = audio_data.reshape(-1, 3)
                    
                    # Converter cada sample de 24-bit para float
                    samples = []
                    for i in range(0, len(audio_data), nchannels):
                        # Para cada frame stereo
                        frame_samples = []
                        for ch in range(min(nchannels, len(audio_data) - i)):
                            frame = audio_data[i + ch]
                            # Little endian 24-bit para int32
                            val = (frame[2] << 16) | (frame[1] << 8) | frame[0]
                            # Converter para signed
                            if val >= 2**23:
                                val -= 2**24
                            frame_samples.append(val)
                        
                        # Converter stereo para mono (média)
                        if len(frame_samples) == 2:
                            mono_sample = (frame_samples[0] + frame_samples[1]) / 2
                        else:
                            mono_sample = frame_samples[0]
                        
                        samples.append(mono_sample)
                    
                    # Normalizar para float32 (-1.0 a 1.0)
                    audio_data = np.array(samples, dtype=np.float32) / (2**23)
                    
                else:
                    # Fallback para outros formatos
                    if sample_width == 2:
                        audio_data = np.frombuffer(frames, dtype=np.int16)
                        audio_data = audio_data.astype(np.float32) / 32767
                    else:
                        logger.error(f"❌ Formato não suportado: {sample_width} bytes")
                        return None
                    
                    # Converter stereo para mono se necessário
                    if nchannels == 2:
                        audio_data = audio_data.reshape(-1, 2)
                        audio_data = np.mean(audio_data, axis=1)
                
                # Resample de 48kHz para 16kHz se necessário
                if framerate != 16000:
                    audio_data = self.resample_audio(audio_data, framerate, 16000)
                
                logger.info(f"✅ Convertido: {len(audio_data)} samples mono 16kHz")
                return audio_data
                
        except Exception as e:
            logger.error(f"❌ Erro na conversão: {e}")
            return None
    
    def resample_audio(self, audio_data, rate_orig, rate_dest):
        """Resample simples por decimação/interpolação."""
        try:
            if rate_orig == rate_dest:
                return audio_data
            
            # Calcular fator de conversão
            factor = rate_orig / rate_dest
            
            if factor == 3.0:  # 48000 -> 16000 (fator 3)
                # Decimação simples - pegar 1 a cada 3 samples
                resampled = audio_data[::3]
                logger.info(f"🔄 Decimação 3:1 - {len(audio_data)} -> {len(resampled)}")
                return resampled
            else:
                # Interpolação linear simples
                orig_indices = np.arange(len(audio_data))
                new_length = int(len(audio_data) / factor)
                new_indices = np.linspace(0, len(audio_data) - 1, new_length)
                resampled = np.interp(new_indices, orig_indices, audio_data)
                logger.info(f"🔄 Interpolação - {len(audio_data)} -> {len(resampled)}")
                return resampled.astype(np.float32)
                
        except Exception as e:
            logger.error(f"❌ Erro no resample: {e}")
            return audio_data  # Retorna original se falhar
    
    def testar_captura_corrigida(self, duracao=5.0):
        """Testa captura com correção aplicada."""
        logger.info("🔧 TESTE CAPTURA DJI CORRIGIDA")
        logger.info("="*50)
        logger.info("🗣️ FALE CLARAMENTE NO MICROFONE!")
        
        # Contador regressivo
        for i in range(3, 0, -1):
            logger.info(f"⏰ {i}...")
            import time
            time.sleep(1)
        
        logger.info("🔴 GRAVANDO...")
        
        # Capturar com método corrigido
        audio_data, status = self.capturar_dji_nativo(duracao)
        
        if audio_data is not None:
            # Analisar qualidade
            analise = self.analisar_audio(audio_data)
            
            # Salvar para teste
            filename = self.salvar_audio_teste(audio_data)
            
            if filename:
                logger.info("🔊 Reproduzindo áudio capturado...")
                subprocess.run(["paplay", filename], timeout=15)
                
                # Limpeza opcional
                keep = input("\n💾 Manter arquivo de teste? (s/n): ").lower().strip()
                if keep not in ['s', 'sim', 'y', 'yes']:
                    Path(filename).unlink()
                    logger.info("🗑️ Arquivo removido")
            
            return analise
        else:
            logger.error(f"❌ Falha na captura: {status}")
            return None
    
    def analisar_audio(self, audio_data):
        """Analisa qualidade do áudio."""
        try:
            rms = np.sqrt(np.mean(audio_data**2))
            peak = np.max(np.abs(audio_data))
            std = np.std(audio_data)
            
            # Zero crossings
            zero_crossings = np.sum(np.diff(np.sign(audio_data)) != 0)
            zcr = zero_crossings / len(audio_data)
            
            analise = {
                "samples": len(audio_data),
                "rms": rms,
                "peak": peak,
                "std": std,
                "zcr": zcr,
            }
            
            # Diagnóstico
            if rms < 0.001:
                analise["qualidade"] = "❌ SILÊNCIO/CHIADO"
            elif rms > 0.01 and std > 0.005:
                analise["qualidade"] = "✅ ÁUDIO REAL"
            elif rms > 0.005:
                analise["qualidade"] = "🔍 SINAL DETECTADO"
            else:
                analise["qualidade"] = "⚠️ BAIXO NÍVEL"
            
            logger.info(f"📊 ANÁLISE ÁUDIO:")
            logger.info(f"   📏 Samples: {analise['samples']:,}")
            logger.info(f"   📈 RMS: {analise['rms']:.6f}")
            logger.info(f"   📊 Peak: {analise['peak']:.6f}")
            logger.info(f"   📉 Std Dev: {analise['std']:.6f}")
            logger.info(f"   🔀 Zero Crossing: {analise['zcr']:.4f}")
            logger.info(f"   🎯 QUALIDADE: {analise['qualidade']}")
            
            return analise
            
        except Exception as e:
            logger.error(f"❌ Erro na análise: {e}")
            return None
    
    def salvar_audio_teste(self, audio_data, filename=None):
        """Salva áudio para teste."""
        try:
            if filename is None:
                import time
                timestamp = int(time.time())
                filename = f"dji_corrigido_{timestamp}.wav"
            
            # Converter para int16
            audio_int16 = (audio_data * 32767).astype(np.int16)
            
            # Salvar WAV
            with wave.open(filename, 'wb') as wav_file:
                wav_file.setnchannels(1)     # Mono
                wav_file.setsampwidth(2)     # 16-bit
                wav_file.setframerate(16000) # 16kHz
                wav_file.writeframes(audio_int16.tobytes())
            
            file_size = Path(filename).stat().st_size
            logger.info(f"💾 Áudio salvo: {filename} ({file_size} bytes)")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar: {e}")
            return None
    
    def integrar_no_sistema_hibrido(self):
        """Mostra como integrar no sistema híbrido."""
        logger.info("🔧 INTEGRAÇÃO NO SISTEMA HÍBRIDO:")
        logger.info("="*50)
        
        codigo_correcao = '''
# No HybridMicrophoneManager, substituir captura DJI:

def capture_dji_corrected(self, duration):
    """Captura DJI com formato nativo correto."""
    try:
        cmd = [
            "parecord",
            "--device", "alsa_input.usb-DJI_Technology_Co.__Ltd._DJI_MIC_MINI_XSP12345678B-01.analog-stereo",
            "--format=s24le",    # Formato nativo
            "--rate=48000",      # Taxa nativa  
            "--channels=2",      # Stereo nativo
            temp_file.name
        ]
        
        # Capturar e converter para mono 16kHz
        # ... [código de conversão] ...
        
        return audio_data_mono_16k
        
    except Exception as e:
        return None
'''
        
        logger.info(codigo_correcao)
        logger.info("="*50)

def main():
    """Função principal."""
    correcao = CorrecaoDJIHibrido()
    
    # Executar teste
    resultado = correcao.testar_captura_corrigida(5.0)
    
    if resultado and "✅" in resultado.get("qualidade", ""):
        logger.info("\n🎉 CORREÇÃO FUNCIONOU!")
        logger.info("DJI Mic 2 agora captura áudio real!")
        correcao.integrar_no_sistema_hibrido()
    else:
        logger.info("\n❌ Correção ainda não resolveu completamente")
        logger.info("Necessita investigação adicional")

if __name__ == "__main__":
    main()

