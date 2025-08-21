#!/usr/bin/env python3
"""
🎧 TESTE INTEGRADO: DJI CAPTURA → ANKER REPRODUÇÃO
Captura áudio DJI formato nativo + reprodução via Anker Bluetooth
"""

import subprocess
import tempfile
import wave
import numpy as np
import time
import logging
import sys
from pathlib import Path
from scipy.signal import decimate

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, "/home/unitree/t031a5/src")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurações
DJI_DEVICE = "alsa_input.usb-DJI_Technology_Co.__Ltd._DJI_MIC_MINI_XSP12345678B-01.analog-stereo"
ANKER_MAC = "F4:2B:7D:2B:D1:B6"
ANKER_NAME = "soundcore Motion 300"

class AudioIntegrado:
    """Sistema integrado DJI + Anker."""
    
    def __init__(self):
        self.anker_conectada = False
        
    def conectar_anker(self):
        """Conecta caixa Anker."""
        try:
            logger.info(f"🔗 Conectando {ANKER_NAME}...")
            
            result = subprocess.run(
                ["bluetoothctl", "connect", ANKER_MAC],
                capture_output=True, text=True, timeout=10
            )
            
            # Aceitar qualquer resultado (às vezes já está conectada)
            logger.info("✅ Comando de conexão executado")
            time.sleep(2)
            self.anker_conectada = True
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Problema na conexão: {e}")
            self.anker_conectada = True  # Tentar mesmo assim
            return True
    
    def capturar_dji_nativo(self, duracao=5.0):
        """Captura DJI com formato nativo s24le."""
        try:
            logger.info(f"🎤 Capturando DJI ({duracao}s) - formato nativo...")
            
            # Arquivo temporário para captura RAW
            with tempfile.NamedTemporaryFile(suffix=".raw", delete=False) as temp_raw:
                cmd = [
                    "parecord",
                    "--device", DJI_DEVICE,
                    "--format=s24le",
                    "--rate=48000", 
                    "--channels=2",
                    temp_raw.name
                ]
                
                # Iniciar captura em background
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # Aguardar duração
                time.sleep(duracao)
                
                # Parar captura
                process.terminate()
                process.wait()
                
                # Verificar arquivo
                if not Path(temp_raw.name).exists():
                    logger.error("❌ Arquivo de captura não criado")
                    return None
                
                file_size = Path(temp_raw.name).stat().st_size
                logger.info(f"✅ Capturado: {file_size} bytes")
                
                if file_size < 1000:
                    logger.error("❌ Arquivo muito pequeno")
                    Path(temp_raw.name).unlink()
                    return None
                
                # Converter para formato utilizável
                audio_data = self.converter_s24le_para_mono16k(temp_raw.name)
                
                # Limpeza
                Path(temp_raw.name).unlink()
                
                return audio_data
                
        except Exception as e:
            logger.error(f"❌ Erro na captura: {e}")
            return None
    
    def converter_s24le_para_mono16k(self, arquivo_raw):
        """Converte s24le stereo 48kHz → mono 16kHz."""
        try:
            # Ler dados RAW como bytes
            with open(arquivo_raw, 'rb') as f:
                raw_bytes = f.read()
            
            logger.info(f"📊 Dados RAW: {len(raw_bytes)} bytes")
            
            # s24le = 3 bytes por sample, 2 canais = 6 bytes por frame
            bytes_per_frame = 6
            num_frames = len(raw_bytes) // bytes_per_frame
            
            # Extrair samples
            samples = []
            for i in range(num_frames):
                frame_start = i * bytes_per_frame
                
                # Canal esquerdo (3 bytes)
                left_bytes = raw_bytes[frame_start:frame_start+3]
                # Canal direito (3 bytes)  
                right_bytes = raw_bytes[frame_start+3:frame_start+6]
                
                # Converter 3 bytes para int (little endian, signed)
                def bytes_to_int24(b):
                    val = b[0] | (b[1] << 8) | (b[2] << 16)
                    if val >= 2**23:
                        val -= 2**24
                    return val
                
                if len(left_bytes) == 3 and len(right_bytes) == 3:
                    left = bytes_to_int24(left_bytes)
                    right = bytes_to_int24(right_bytes)
                    
                    # Média dos canais (mono)
                    mono = (left + right) / 2
                    samples.append(mono)
            
            # Converter para array NumPy normalizado
            audio_data = np.array(samples, dtype=np.float32) / (2**23)
            
            logger.info(f"📊 Convertido: {len(audio_data)} samples 48kHz mono")
            
            # Decimar 48kHz → 16kHz (fator 3)
            if len(audio_data) > 0:
                audio_16k = decimate(audio_data, 3)
                logger.info(f"📊 Decimado: {len(audio_16k)} samples 16kHz")
                return audio_16k
            else:
                logger.error("❌ Nenhum sample válido")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro na conversão: {e}")
            return None
    
    def analisar_audio(self, audio_data):
        """Analisa qualidade do áudio."""
        if audio_data is None or len(audio_data) == 0:
            return False
        
        rms = np.sqrt(np.mean(audio_data**2))
        peak = np.max(np.abs(audio_data))
        
        # Zero Crossing Rate
        zcr = np.mean(np.abs(np.diff(np.sign(audio_data)))) / 2
        
        logger.info(f"📊 RMS: {rms:.6f}")
        logger.info(f"📊 Peak: {peak:.6f}")
        logger.info(f"📊 ZCR: {zcr:.4f}")
        
        # Critérios de qualidade
        if rms > 0.005 and peak > 0.01 and zcr > 0.01:
            logger.info("✅ Áudio com qualidade adequada")
            return True
        else:
            logger.warning("⚠️ Áudio suspeito - níveis baixos")
            return False
    
    def reproduzir_via_anker(self, audio_data, sample_rate=16000):
        """Reproduz áudio via Anker."""
        try:
            logger.info("🔊 Reproduzindo via Anker...")
            
            # Salvar como WAV
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                audio_int16 = (audio_data * 32767).astype(np.int16)
                
                with wave.open(temp_wav.name, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(audio_int16.tobytes())
                
                # Reproduzir via paplay (sink padrão = Anker se conectada)
                result = subprocess.run(
                    ["paplay", temp_wav.name],
                    timeout=15
                )
                
                # Limpeza
                Path(temp_wav.name).unlink()
                
                if result.returncode == 0:
                    logger.info("✅ Reprodução concluída")
                    return True
                else:
                    logger.error(f"❌ Falha na reprodução: {result.returncode}")
                    return False
                
        except Exception as e:
            logger.error(f"❌ Erro na reprodução: {e}")
            return False
    
    def executar_teste_completo(self):
        """Executa teste completo: captura + análise + reprodução."""
        logger.info("🎧 TESTE INTEGRADO: DJI → ANKER")
        logger.info("="*60)
        
        # 1. Conectar Anker
        logger.info("📋 Passo 1: Conectar Anker")
        if not self.conectar_anker():
            logger.warning("⚠️ Problemas com Anker, mas continuando...")
        
        # 2. Instruções ao usuário
        logger.info("\n📋 Passo 2: Preparar captura")
        logger.info("🗣️  PREPARE-SE PARA FALAR NO DJI MIC!")
        logger.info("💡 Diga uma frase clara em português")
        logger.info("📢 Exemplo: 'Olá, este é um teste do microfone DJI'")
        
        # Contagem regressiva
        for i in range(3, 0, -1):
            logger.info(f"⏰ Iniciando em {i}...")
            time.sleep(1)
        
        # 3. Capturar áudio
        logger.info("\n🔴 GRAVANDO (5 segundos)...")
        audio_data = self.capturar_dji_nativo(5.0)
        
        if audio_data is None:
            logger.error("❌ Falha na captura")
            return False
        
        # 4. Analisar
        logger.info("\n📋 Passo 3: Análise de qualidade")
        if not self.analisar_audio(audio_data):
            logger.warning("⚠️ Qualidade duvidosa, mas prosseguindo...")
        
        # 5. Reproduzir
        logger.info("\n📋 Passo 4: Reprodução via Anker")
        logger.info("🔊 Reproduzindo o que foi capturado...")
        
        if self.reproduzir_via_anker(audio_data):
            # 6. Confirmação
            logger.info("\n🎯 TESTE CONCLUÍDO!")
            print("\n" + "="*60)
            print("🎧 RESULTADO DO TESTE:")
            print("   🎤 Você ouviu sua própria voz claramente?")
            print("   🔊 O áudio estava limpo, sem chiados?")
            print("   📢 A qualidade estava adequada?")
            print("="*60)
            
            resposta = input("Digite 's' se TUDO funcionou perfeitamente: ").lower().strip()
            
            if resposta in ['s', 'sim', 'y', 'yes']:
                logger.info("🎉 SUCESSO TOTAL!")
                logger.info("✅ Sistema DJI → Anker funcionando!")
                logger.info("🚀 PRONTO PARA INTEGRAÇÃO NO SISTEMA!")
                return True
            else:
                logger.warning("⚠️ Ainda há problemas a resolver")
                return False
        else:
            logger.error("❌ Falha na reprodução")
            return False

def main():
    """Função principal."""
    sistema = AudioIntegrado()
    resultado = sistema.executar_teste_completo()
    
    if resultado:
        logger.info("\n🎯 SISTEMA VALIDADO - PRÓXIMA ETAPA: STT/LLM/TTS REAIS")
    else:
        logger.info("\n🔧 Necessário investigar problemas restantes")

if __name__ == "__main__":
    main()
