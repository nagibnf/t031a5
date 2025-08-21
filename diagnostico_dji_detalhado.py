#!/usr/bin/env python3
"""
🔍 DIAGNÓSTICO DETALHADO - PROBLEMA CAPTURA DJI MIC 2
Investigar por que DJI está produzindo apenas chiado ao invés de áudio real
"""

import sys
import time
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

class DiagnosticoDJI:
    """Diagnóstico detalhado do problema de captura DJI Mic 2."""
    
    def __init__(self):
        self.dji_device = None
        self.resultados = {}
    
    def detectar_dji_device(self):
        """Detecta dispositivo DJI específico."""
        try:
            result = subprocess.run(
                ["pactl", "list", "sources", "short"], 
                capture_output=True, text=True, timeout=10
            )
            
            for line in result.stdout.strip().split('\n'):
                if 'dji' in line.lower():
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        self.dji_device = parts[1]  # Nome do dispositivo
                        logger.info(f"✅ DJI detectado: {self.dji_device}")
                        return True
            
            logger.error("❌ DJI Mic não encontrado")
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro na detecção: {e}")
            return False
    
    def verificar_configuracao_dji(self):
        """Verifica configuração detalhada do DJI."""
        if not self.dji_device:
            return False
        
        try:
            logger.info("🔍 CONFIGURAÇÃO DETALHADA DO DJI...")
            
            # Informações do source
            result = subprocess.run(
                ["pactl", "list", "sources"], 
                capture_output=True, text=True, timeout=10
            )
            
            # Procurar seção do DJI
            in_dji_section = False
            dji_info = []
            
            for line in result.stdout.split('\n'):
                if self.dji_device in line:
                    in_dji_section = True
                    dji_info.append(line)
                elif in_dji_section:
                    if line.startswith('Source #') or line.startswith('\t'):
                        dji_info.append(line)
                    else:
                        break
            
            for info in dji_info:
                logger.info(f"   {info.strip()}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na verificação: {e}")
            return False
    
    def testar_captura_direta_parecord(self, duracao=3):
        """Testa captura direta com parecord."""
        if not self.dji_device:
            return None
        
        try:
            logger.info(f"🎤 TESTE DIRETO parecord ({duracao}s)...")
            logger.info("🗣️ FALE NO MICROFONE AGORA!")
            
            # Contador regressivo
            for i in range(3, 0, -1):
                logger.info(f"⏰ {i}...")
                time.sleep(1)
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                logger.info("🔴 GRAVANDO com parecord...")
                
                # Comando parecord direto
                cmd = [
                    "parecord",
                    "--device", self.dji_device,
                    "--format=s16le",   # 16-bit
                    "--rate=16000",     # 16kHz
                    "--channels=1",     # Mono
                    temp_file.name
                ]
                
                process = subprocess.Popen(cmd)
                time.sleep(duracao)
                process.terminate()
                process.wait()
                
                if Path(temp_file.name).exists():
                    file_size = Path(temp_file.name).stat().st_size
                    logger.info(f"✅ Arquivo criado: {file_size} bytes")
                    
                    # Reproduzir
                    logger.info("🔊 Reproduzindo...")
                    subprocess.run(["paplay", temp_file.name], timeout=10)
                    
                    # Analisar arquivo
                    return self.analisar_arquivo_wav(temp_file.name)
                else:
                    logger.error("❌ Arquivo não criado")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erro parecord: {e}")
            return None
    
    def testar_diferentes_formatos(self):
        """Testa diferentes formatos de captura."""
        if not self.dji_device:
            return
        
        formatos = [
            ("s16le", "16-bit LE"),
            ("s24le", "24-bit LE"),
            ("s32le", "32-bit LE"),
            ("float32le", "Float 32-bit LE")
        ]
        
        rates = [16000, 44100, 48000]
        channels = [1, 2]
        
        logger.info("🧪 TESTANDO DIFERENTES FORMATOS...")
        
        for formato, desc in formatos:
            for rate in rates:
                for ch in channels:
                    try:
                        logger.info(f"🔧 Testando: {desc}, {rate}Hz, {ch}ch")
                        
                        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                            cmd = [
                                "parecord",
                                "--device", self.dji_device,
                                f"--format={formato}",
                                f"--rate={rate}",
                                f"--channels={ch}",
                                temp_file.name
                            ]
                            
                            process = subprocess.Popen(cmd, stderr=subprocess.PIPE)
                            time.sleep(1)  # Captura rápida
                            process.terminate()
                            stdout, stderr = process.communicate()
                            
                            if Path(temp_file.name).exists():
                                file_size = Path(temp_file.name).stat().st_size
                                if file_size > 100:  # Pelo menos alguns bytes
                                    logger.info(f"   ✅ {desc} {rate}Hz {ch}ch: {file_size} bytes")
                                    
                                    # Cleanup
                                    Path(temp_file.name).unlink()
                                    
                                    # Se funcionou, usar este formato
                                    return formato, rate, ch
                                else:
                                    logger.info(f"   ❌ {desc} {rate}Hz {ch}ch: arquivo vazio")
                            else:
                                logger.info(f"   ❌ {desc} {rate}Hz {ch}ch: não criou arquivo")
                                
                    except Exception as e:
                        logger.info(f"   ❌ {desc} {rate}Hz {ch}ch: erro - {e}")
        
        return None
    
    def testar_arecord_alsa(self, duracao=3):
        """Testa captura com arecord (ALSA direto)."""
        try:
            logger.info(f"🎤 TESTE DIRETO arecord ALSA ({duracao}s)...")
            
            # Listar dispositivos ALSA
            result = subprocess.run(["arecord", "-l"], capture_output=True, text=True)
            logger.info("📋 DISPOSITIVOS ALSA:")
            for line in result.stdout.split('\n'):
                if line.strip():
                    logger.info(f"   {line}")
            
            # Tentar captura com device padrão primeiro
            logger.info("🗣️ FALE NO MICROFONE AGORA!")
            
            for i in range(3, 0, -1):
                logger.info(f"⏰ {i}...")
                time.sleep(1)
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                logger.info("🔴 GRAVANDO com arecord...")
                
                cmd = [
                    "arecord",
                    "-D", "default",  # Usar device padrão
                    "-f", "S16_LE",   # 16-bit
                    "-r", "16000",    # 16kHz
                    "-c", "1",        # Mono
                    "-t", "wav",      # Formato WAV
                    temp_file.name
                ]
                
                process = subprocess.Popen(cmd)
                time.sleep(duracao)
                process.terminate()
                process.wait()
                
                if Path(temp_file.name).exists():
                    file_size = Path(temp_file.name).stat().st_size
                    logger.info(f"✅ Arquivo ALSA criado: {file_size} bytes")
                    
                    # Reproduzir
                    logger.info("🔊 Reproduzindo ALSA...")
                    subprocess.run(["aplay", temp_file.name], timeout=10)
                    
                    return self.analisar_arquivo_wav(temp_file.name)
                else:
                    logger.error("❌ Arquivo ALSA não criado")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erro arecord: {e}")
            return None
    
    def analisar_arquivo_wav(self, filename):
        """Analisa arquivo WAV em detalhes."""
        try:
            with wave.open(filename, 'rb') as wav_file:
                frames = wav_file.readframes(wav_file.getnframes())
                sample_width = wav_file.getsampwidth()
                framerate = wav_file.getframerate()
                nchannels = wav_file.getnchannels()
                
                # Converter para numpy
                if sample_width == 1:
                    audio_data = np.frombuffer(frames, dtype=np.uint8)
                    audio_data = (audio_data.astype(np.float32) - 128) / 128
                elif sample_width == 2:
                    audio_data = np.frombuffer(frames, dtype=np.int16)
                    audio_data = audio_data.astype(np.float32) / 32767
                else:
                    audio_data = np.frombuffer(frames, dtype=np.int32)
                    audio_data = audio_data.astype(np.float32) / 2147483647
                
                # Análise
                rms = np.sqrt(np.mean(audio_data**2))
                peak = np.max(np.abs(audio_data))
                std = np.std(audio_data)
                
                # Detectar padrões de chiado
                # Chiado geralmente tem alta frequência mas baixa variação
                diff = np.diff(audio_data)
                high_freq_energy = np.mean(diff**2)
                
                # Zero crossings
                zero_crossings = np.sum(np.diff(np.sign(audio_data)) != 0)
                zcr = zero_crossings / len(audio_data)
                
                # Análise espectral básica
                fft = np.fft.fft(audio_data[:min(4096, len(audio_data))])
                magnitude = np.abs(fft)
                dominant_freq = np.argmax(magnitude)
                
                analise = {
                    "arquivo": filename,
                    "tamanho_bytes": Path(filename).stat().st_size,
                    "samples": len(audio_data),
                    "duracao": len(audio_data) / framerate,
                    "sample_rate": framerate,
                    "channels": nchannels,
                    "rms": rms,
                    "peak": peak,
                    "std": std,
                    "zcr": zcr,
                    "high_freq_energy": high_freq_energy,
                    "dominant_freq": dominant_freq,
                }
                
                # Diagnóstico
                if rms < 0.001:
                    analise["diagnostico"] = "SILÊNCIO - Sem sinal"
                elif std < 0.001 and rms > 0.001:
                    analise["diagnostico"] = "CHIADO/RUÍDO - Sinal constante sem variação"
                elif zcr > 0.3 and high_freq_energy > 0.01:
                    analise["diagnostico"] = "POSSÍVEL CHIADO - Alta frequência dominante"
                elif rms > 0.01 and std > 0.01:
                    analise["diagnostico"] = "ÁUDIO REAL - Variação adequada"
                else:
                    analise["diagnostico"] = "INCERTO - Necessita análise manual"
                
                logger.info(f"📊 ANÁLISE DETALHADA:")
                logger.info(f"   📏 Tamanho: {analise['tamanho_bytes']} bytes")
                logger.info(f"   ⏱️ Duração: {analise['duracao']:.2f}s")
                logger.info(f"   📈 RMS: {analise['rms']:.6f}")
                logger.info(f"   📊 Peak: {analise['peak']:.6f}")
                logger.info(f"   📉 Std Dev: {analise['std']:.6f}")
                logger.info(f"   🔀 Zero Crossing Rate: {analise['zcr']:.4f}")
                logger.info(f"   ⚡ High Freq Energy: {analise['high_freq_energy']:.6f}")
                logger.info(f"   🎯 DIAGNÓSTICO: {analise['diagnostico']}")
                
                return analise
                
        except Exception as e:
            logger.error(f"❌ Erro na análise: {e}")
            return None
    
    def verificar_volume_microfone(self):
        """Verifica e ajusta volume do microfone."""
        if not self.dji_device:
            return
        
        try:
            logger.info("🔊 VERIFICANDO VOLUME DO MICROFONE...")
            
            # Verificar se está mutado
            result = subprocess.run(
                ["pactl", "get-source-mute", self.dji_device],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0:
                mute_status = result.stdout.strip()
                logger.info(f"   🔇 Status mute: {mute_status}")
                
                if "yes" in mute_status.lower():
                    logger.info("   🔊 Desmutando microfone...")
                    subprocess.run(["pactl", "set-source-mute", self.dji_device, "0"])
            
            # Verificar volume
            result = subprocess.run(
                ["pactl", "get-source-volume", self.dji_device],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0:
                volume_info = result.stdout.strip()
                logger.info(f"   🎚️ Volume atual: {volume_info}")
                
                # Definir volume para 100%
                logger.info("   📈 Definindo volume para 100%...")
                subprocess.run(["pactl", "set-source-volume", self.dji_device, "100%"])
            
        except Exception as e:
            logger.error(f"❌ Erro no volume: {e}")
    
    def executar_diagnostico_completo(self):
        """Executa diagnóstico completo do problema DJI."""
        logger.info("🔍 DIAGNÓSTICO COMPLETO - PROBLEMA DJI MIC 2")
        logger.info("="*60)
        
        # 1. Detectar DJI
        if not self.detectar_dji_device():
            logger.error("❌ DJI não detectado - verificar conexão")
            return
        
        # 2. Verificar configuração
        logger.info("="*60)
        self.verificar_configuracao_dji()
        
        # 3. Verificar volume
        logger.info("="*60)
        self.verificar_volume_microfone()
        
        # 4. Teste diferentes formatos
        logger.info("="*60)
        formato_ok = self.testar_diferentes_formatos()
        if formato_ok:
            logger.info(f"✅ Formato funcionando: {formato_ok}")
        
        # 5. Teste parecord direto
        logger.info("="*60)
        resultado_pa = self.testar_captura_direta_parecord(3)
        
        # 6. Teste arecord ALSA
        logger.info("="*60)
        resultado_alsa = self.testar_arecord_alsa(3)
        
        # 7. Resumo final
        logger.info("="*60)
        logger.info("📋 RESUMO DO DIAGNÓSTICO:")
        
        if resultado_pa:
            logger.info(f"   🎤 PulseAudio: {resultado_pa['diagnostico']}")
        else:
            logger.info("   ❌ PulseAudio: Falhou")
        
        if resultado_alsa:
            logger.info(f"   🎤 ALSA: {resultado_alsa['diagnostico']}")
        else:
            logger.info("   ❌ ALSA: Falhou")
        
        # Recomendações
        logger.info("\n💡 RECOMENDAÇÕES:")
        if resultado_pa and "REAL" in resultado_pa['diagnostico']:
            logger.info("   ✅ Use PulseAudio parecord")
        elif resultado_alsa and "REAL" in resultado_alsa['diagnostico']:
            logger.info("   ✅ Use ALSA arecord")
        else:
            logger.info("   ⚠️ Problema de hardware ou configuração")
            logger.info("   🔧 Verificar: conexão física, drivers, configuração")
        
        logger.info("="*60)

def main():
    """Função principal."""
    diagnostico = DiagnosticoDJI()
    diagnostico.executar_diagnostico_completo()

if __name__ == "__main__":
    main()

