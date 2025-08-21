#!/usr/bin/env python3
"""
🎤 TESTE DJI FORMATO NATIVO
Testa captura com formato exato: s24le 2ch 48000Hz
"""

import sys
import time
import subprocess
import tempfile
import wave
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TesteDJIFormtoNativo:
    """Teste específico do formato nativo DJI."""
    
    def __init__(self):
        self.dji_device = "alsa_input.usb-DJI_Technology_Co.__Ltd._DJI_MIC_MINI_XSP12345678B-01.analog-stereo"
    
    def testar_formato_nativo_parecord(self, duracao=5):
        """Testa com formato nativo exato do DJI."""
        try:
            logger.info(f"🎤 TESTE FORMATO NATIVO DJI ({duracao}s)")
            logger.info("Formato: s24le 2ch 48000Hz (nativo)")
            logger.info("🗣️ FALE CLARAMENTE NO MICROFONE!")
            
            # Contador regressivo
            for i in range(3, 0, -1):
                logger.info(f"⏰ {i}...")
                time.sleep(1)
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                logger.info("🔴 GRAVANDO com formato nativo...")
                
                # Usar formato EXATO do DJI
                cmd = [
                    "parecord",
                    "--device", self.dji_device,
                    "--format=s24le",    # 24-bit como detectado
                    "--rate=48000",      # 48kHz como detectado
                    "--channels=2",      # Stereo como detectado
                    temp_file.name
                ]
                
                logger.info(f"Comando: {' '.join(cmd)}")
                
                process = subprocess.Popen(cmd, stderr=subprocess.PIPE)
                time.sleep(duracao)
                process.terminate()
                stdout, stderr = process.communicate()
                
                if stderr:
                    logger.info(f"stderr: {stderr.decode()}")
                
                if Path(temp_file.name).exists():
                    file_size = Path(temp_file.name).stat().st_size
                    logger.info(f"✅ Arquivo criado: {file_size} bytes")
                    
                    if file_size > 1000:  # Pelo menos 1KB
                        # Reproduzir
                        logger.info("🔊 Reproduzindo...")
                        subprocess.run(["paplay", temp_file.name], timeout=15)
                        
                        # Analisar
                        return self.analisar_arquivo_s24le(temp_file.name)
                    else:
                        logger.warning("⚠️ Arquivo muito pequeno")
                        return None
                else:
                    logger.error("❌ Arquivo não criado")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erro: {e}")
            return None
    
    def testar_com_sox_conversao(self, duracao=5):
        """Testa captura nativa + conversão com SOX."""
        try:
            logger.info(f"🎤 TESTE COM SOX CONVERSÃO ({duracao}s)")
            logger.info("🗣️ FALE CLARAMENTE NO MICROFONE!")
            
            for i in range(3, 0, -1):
                logger.info(f"⏰ {i}...")
                time.sleep(1)
            
            with tempfile.NamedTemporaryFile(suffix=".raw", delete=False) as temp_raw:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                    logger.info("🔴 GRAVANDO raw s24le...")
                    
                    # Capturar raw
                    cmd = [
                        "parecord",
                        "--device", self.dji_device,
                        "--format=s24le",
                        "--rate=48000", 
                        "--channels=2",
                        "--raw",
                        temp_raw.name
                    ]
                    
                    process = subprocess.Popen(cmd)
                    time.sleep(duracao)
                    process.terminate()
                    process.wait()
                    
                    raw_size = Path(temp_raw.name).stat().st_size
                    logger.info(f"📁 Raw capturado: {raw_size} bytes")
                    
                    if raw_size > 1000:
                        # Converter com SOX
                        logger.info("🔄 Convertendo com SOX...")
                        sox_cmd = [
                            "sox",
                            "-t", "raw",
                            "-r", "48000",
                            "-c", "2", 
                            "-b", "24",
                            "-e", "signed-integer",
                            "-L",  # Little endian
                            temp_raw.name,
                            "-r", "16000",  # Converter para 16kHz
                            "-c", "1",      # Converter para mono
                            "-b", "16",     # Converter para 16-bit
                            temp_wav.name
                        ]
                        
                        result = subprocess.run(sox_cmd, capture_output=True)
                        
                        if result.returncode == 0:
                            wav_size = Path(temp_wav.name).stat().st_size
                            logger.info(f"✅ WAV convertido: {wav_size} bytes")
                            
                            # Reproduzir
                            logger.info("🔊 Reproduzindo convertido...")
                            subprocess.run(["paplay", temp_wav.name], timeout=15)
                            
                            return self.analisar_arquivo_wav(temp_wav.name)
                        else:
                            logger.error(f"❌ SOX falhou: {result.stderr.decode()}")
                            return None
                    else:
                        logger.warning("⚠️ Raw muito pequeno")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ Erro SOX: {e}")
            return None
    
    def testar_diretamente_alsa_card(self, duracao=5):
        """Testa diretamente com card ALSA do DJI."""
        try:
            logger.info(f"🎤 TESTE DIRETO ALSA CARD DJI ({duracao}s)")
            logger.info("🗣️ FALE CLARAMENTE NO MICROFONE!")
            
            for i in range(3, 0, -1):
                logger.info(f"⏰ {i}...")
                time.sleep(1)
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                logger.info("🔴 GRAVANDO com arecord direto...")
                
                # Usar card 0 (DJI MIC MINI) diretamente
                cmd = [
                    "arecord",
                    "-D", "hw:0,0",      # Card 0, device 0 (DJI)
                    "-f", "S24_LE",      # 24-bit
                    "-r", "48000",       # 48kHz
                    "-c", "2",           # Stereo
                    "-t", "wav",
                    temp_file.name
                ]
                
                logger.info(f"Comando: {' '.join(cmd)}")
                
                process = subprocess.Popen(cmd, stderr=subprocess.PIPE)
                time.sleep(duracao)
                process.terminate()
                stdout, stderr = process.communicate()
                
                if stderr:
                    logger.info(f"stderr: {stderr.decode()}")
                
                if Path(temp_file.name).exists():
                    file_size = Path(temp_file.name).stat().st_size
                    logger.info(f"✅ Arquivo ALSA criado: {file_size} bytes")
                    
                    if file_size > 1000:
                        # Reproduzir
                        logger.info("🔊 Reproduzindo ALSA...")
                        subprocess.run(["aplay", temp_file.name], timeout=15)
                        
                        return self.analisar_arquivo_wav(temp_file.name)
                    else:
                        logger.warning("⚠️ Arquivo ALSA muito pequeno")
                        return None
                else:
                    logger.error("❌ Arquivo ALSA não criado")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erro ALSA direto: {e}")
            return None
    
    def analisar_arquivo_s24le(self, filename):
        """Analisa arquivo s24le."""
        try:
            # Ler como WAV
            with wave.open(filename, 'rb') as wav_file:
                frames = wav_file.readframes(wav_file.getnframes())
                sample_width = wav_file.getsampwidth()
                framerate = wav_file.getframerate()
                nchannels = wav_file.getnchannels()
                
                logger.info(f"📊 ARQUIVO WAV:")
                logger.info(f"   Sample Width: {sample_width} bytes")
                logger.info(f"   Frame Rate: {framerate} Hz")
                logger.info(f"   Channels: {nchannels}")
                logger.info(f"   Frames: {wav_file.getnframes()}")
                
                # Converter para análise
                if sample_width == 3:  # 24-bit
                    # Expandir para 32-bit para análise
                    audio_data = np.frombuffer(frames, dtype=np.uint8)
                    audio_data = audio_data.reshape(-1, 3)
                    
                    # Converter 24-bit para float
                    samples = []
                    for frame in audio_data:
                        # Little endian 24-bit para int32
                        val = (frame[2] << 24) | (frame[1] << 16) | (frame[0] << 8)
                        val = val.astype(np.int32) >> 8  # Shift para 24-bit signed
                        samples.append(val)
                    
                    audio_data = np.array(samples, dtype=np.float32) / (2**23)
                else:
                    # 16-bit normal
                    audio_data = np.frombuffer(frames, dtype=np.int16)
                    audio_data = audio_data.astype(np.float32) / 32767
                
                # Se stereo, converter para mono (média)
                if nchannels == 2:
                    audio_data = audio_data.reshape(-1, 2)
                    audio_data = np.mean(audio_data, axis=1)
                
                return self.analisar_audio_data(audio_data, framerate, filename)
                
        except Exception as e:
            logger.error(f"❌ Erro na análise s24le: {e}")
            return None
    
    def analisar_arquivo_wav(self, filename):
        """Analisa arquivo WAV normal."""
        try:
            with wave.open(filename, 'rb') as wav_file:
                frames = wav_file.readframes(wav_file.getnframes())
                sample_width = wav_file.getsampwidth()
                framerate = wav_file.getframerate()
                nchannels = wav_file.getnchannels()
                
                # Converter baseado no sample width
                if sample_width == 1:
                    audio_data = np.frombuffer(frames, dtype=np.uint8)
                    audio_data = (audio_data.astype(np.float32) - 128) / 128
                elif sample_width == 2:
                    audio_data = np.frombuffer(frames, dtype=np.int16)
                    audio_data = audio_data.astype(np.float32) / 32767
                else:
                    audio_data = np.frombuffer(frames, dtype=np.int32)
                    audio_data = audio_data.astype(np.float32) / 2147483647
                
                # Se stereo, converter para mono
                if nchannels == 2:
                    audio_data = audio_data.reshape(-1, 2)
                    audio_data = np.mean(audio_data, axis=1)
                
                return self.analisar_audio_data(audio_data, framerate, filename)
                
        except Exception as e:
            logger.error(f"❌ Erro na análise WAV: {e}")
            return None
    
    def analisar_audio_data(self, audio_data, framerate, filename):
        """Analisa dados de áudio."""
        try:
            rms = np.sqrt(np.mean(audio_data**2))
            peak = np.max(np.abs(audio_data))
            std = np.std(audio_data)
            
            # Zero crossings
            zero_crossings = np.sum(np.diff(np.sign(audio_data)) != 0)
            zcr = zero_crossings / len(audio_data)
            
            # Energia de alta frequência
            diff = np.diff(audio_data)
            high_freq_energy = np.mean(diff**2)
            
            analise = {
                "arquivo": filename,
                "samples": len(audio_data),
                "duracao": len(audio_data) / framerate,
                "rms": rms,
                "peak": peak,
                "std": std,
                "zcr": zcr,
                "high_freq_energy": high_freq_energy,
            }
            
            # Diagnóstico melhorado
            if rms < 0.0001:
                analise["diagnostico"] = "SILÊNCIO TOTAL"
                analise["qualidade"] = "❌ SEM ÁUDIO"
            elif rms < 0.001 and std < 0.001:
                analise["diagnostico"] = "CHIADO/RUÍDO BAIXO"
                analise["qualidade"] = "⚠️ POSSÍVEL CHIADO"
            elif rms > 0.01 and std > 0.005 and zcr > 0.1:
                analise["diagnostico"] = "ÁUDIO REAL DETECTADO"
                analise["qualidade"] = "✅ ÁUDIO REAL"
            elif rms > 0.005:
                analise["diagnostico"] = "SINAL DETECTADO"
                analise["qualidade"] = "🔍 PRECISA VERIFICAÇÃO"
            else:
                analise["diagnostico"] = "INCERTO"
                analise["qualidade"] = "❓ ANÁLISE MANUAL"
            
            logger.info(f"📊 ANÁLISE COMPLETA:")
            logger.info(f"   📏 Samples: {analise['samples']:,}")
            logger.info(f"   ⏱️ Duração: {analise['duracao']:.2f}s")
            logger.info(f"   📈 RMS: {analise['rms']:.6f}")
            logger.info(f"   📊 Peak: {analise['peak']:.6f}")
            logger.info(f"   📉 Std Dev: {analise['std']:.6f}")
            logger.info(f"   🔀 Zero Crossing: {analise['zcr']:.4f}")
            logger.info(f"   ⚡ High Freq: {analise['high_freq_energy']:.6f}")
            logger.info(f"   🎯 RESULTADO: {analise['qualidade']}")
            logger.info(f"   📋 DIAGNÓSTICO: {analise['diagnostico']}")
            
            return analise
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de dados: {e}")
            return None
    
    def executar_testes_completos(self):
        """Executa todos os testes."""
        logger.info("🎤 TESTE FORMATO NATIVO DJI MIC 2")
        logger.info("="*60)
        
        resultados = {}
        
        # Teste 1: Formato nativo parecord
        logger.info("1️⃣ TESTE FORMATO NATIVO PARECORD")
        logger.info("-"*40)
        resultado1 = self.testar_formato_nativo_parecord(5)
        resultados["parecord_nativo"] = resultado1
        
        logger.info("\n" + "="*60)
        
        # Teste 2: SOX conversão
        logger.info("2️⃣ TESTE SOX CONVERSÃO")
        logger.info("-"*40)
        resultado2 = self.testar_com_sox_conversao(5)
        resultados["sox_conversao"] = resultado2
        
        logger.info("\n" + "="*60)
        
        # Teste 3: ALSA direto
        logger.info("3️⃣ TESTE ALSA DIRETO")
        logger.info("-"*40)
        resultado3 = self.testar_diretamente_alsa_card(5)
        resultados["alsa_direto"] = resultado3
        
        # Resumo final
        logger.info("\n" + "="*60)
        logger.info("📋 RESUMO FINAL DOS TESTES:")
        logger.info("="*60)
        
        for teste, resultado in resultados.items():
            if resultado:
                logger.info(f"   🧪 {teste}: {resultado['qualidade']}")
            else:
                logger.info(f"   ❌ {teste}: FALHOU")
        
        # Recomendação
        melhores = [nome for nome, res in resultados.items() if res and "✅" in res.get("qualidade", "")]
        
        if melhores:
            logger.info(f"\n✅ MÉTODO(S) FUNCIONANDO: {', '.join(melhores)}")
        else:
            logger.info("\n❌ NENHUM MÉTODO FUNCIONOU")
            logger.info("🔧 POSSÍVEIS PROBLEMAS:")
            logger.info("   - DJI Mic não está funcionando corretamente")
            logger.info("   - Drivers USB/Audio com problema")
            logger.info("   - Configuração PulseAudio/ALSA incorreta")
            logger.info("   - Hardware do microfone com defeito")
        
        logger.info("="*60)

def main():
    """Função principal."""
    teste = TesteDJIFormtoNativo()
    teste.executar_testes_completos()

if __name__ == "__main__":
    main()

