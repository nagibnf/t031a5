#!/usr/bin/env python3
"""
🔊 TESTE SOM ANKER - SIMPLES E DIRETO
Conecta e reproduz som na caixa Anker SoundCore
"""

import subprocess
import tempfile
import wave
import numpy as np
import time
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurações conhecidas da Anker
ANKER_MAC = "F4:2B:7D:2B:D1:B6"  # MAC detectado anteriormente
ANKER_NAME = "soundcore Motion 300"

def conectar_anker():
    """Conecta à caixa Anker."""
    try:
        logger.info(f"🔗 Conectando à {ANKER_NAME}...")
        
        # Comando direto de conexão
        result = subprocess.run(
            ["bluetoothctl", "connect", ANKER_MAC],
            capture_output=True, text=True, timeout=10
        )
        
        # Verificar resultado
        if result.returncode == 0 or "Connection successful" in result.stdout or "Already connected" in result.stderr:
            logger.info("✅ Anker conectada!")
            time.sleep(2)  # Aguardar estabilização
            return True
        else:
            logger.warning(f"⚠️ Resultado conexão: {result.stdout} {result.stderr}")
            # Tentar mesmo assim - às vezes funciona
            time.sleep(2)
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro na conexão: {e}")
        return False

def detectar_sink_anker():
    """Detecta sink PulseAudio da Anker."""
    try:
        logger.info("🔍 Procurando sink da Anker...")
        
        result = subprocess.run(
            ["pactl", "list", "sinks", "short"],
            capture_output=True, text=True, timeout=5
        )
        
        # Procurar sink com "anker", "soundcore" ou "motion"
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                parts = line.split('\t')
                if len(parts) >= 2:
                    sink_name = parts[1]
                    sink_lower = sink_name.lower()
                    
                    if any(keyword in sink_lower for keyword in ["anker", "soundcore", "motion", "bluez"]):
                        logger.info(f"✅ Sink encontrado: {sink_name}")
                        return sink_name
        
        # Fallback: usar sink padrão se não encontrar específico
        logger.warning("⚠️ Sink específico não encontrado, usando padrão")
        return None
        
    except Exception as e:
        logger.error(f"❌ Erro na detecção do sink: {e}")
        return None

def gerar_som_teste():
    """Gera som de teste (tom + beep)."""
    try:
        duration = 3.0  # 3 segundos
        sample_rate = 44100
        
        # Tom principal (440Hz - Lá)
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        tone = np.sin(2 * np.pi * 440 * t) * 0.4
        
        # Beep no final (800Hz)
        beep_duration = 0.5
        beep_samples = int(sample_rate * beep_duration)
        t_beep = np.linspace(0, beep_duration, beep_samples, False)
        beep = np.sin(2 * np.pi * 800 * t_beep) * 0.6
        
        # Combinar
        audio = np.concatenate([tone[:-beep_samples], beep])
        
        # Fade in/out
        fade_samples = int(0.1 * sample_rate)
        audio[:fade_samples] *= np.linspace(0, 1, fade_samples)
        audio[-fade_samples:] *= np.linspace(1, 0, fade_samples)
        
        return audio, sample_rate
        
    except Exception as e:
        logger.error(f"❌ Erro na geração: {e}")
        return None, None

def reproduzir_som(audio_data, sample_rate, sink_name=None):
    """Reproduz som via PulseAudio."""
    try:
        # Salvar como WAV temporário
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            audio_int16 = (audio_data * 32767).astype(np.int16)
            
            with wave.open(temp_file.name, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_int16.tobytes())
            
            # Comando de reprodução
            if sink_name:
                cmd = ["paplay", "--device", sink_name, temp_file.name]
                logger.info(f"🔊 Reproduzindo via sink específico: {sink_name}")
            else:
                cmd = ["paplay", temp_file.name]
                logger.info("🔊 Reproduzindo via sink padrão")
            
            # Executar
            result = subprocess.run(cmd, timeout=10)
            
            # Limpeza
            Path(temp_file.name).unlink()
            
            if result.returncode == 0:
                logger.info("✅ Som reproduzido!")
                return True
            else:
                logger.error(f"❌ Falha na reprodução (código: {result.returncode})")
                return False
                
    except Exception as e:
        logger.error(f"❌ Erro na reprodução: {e}")
        return False

def main():
    """Função principal."""
    logger.info("🔊 TESTE SOM ANKER - VERSÃO SIMPLES")
    logger.info("="*50)
    
    # 1. Conectar Anker
    logger.info("📋 Passo 1: Conectar caixa")
    if not conectar_anker():
        logger.warning("⚠️ Problemas na conexão, mas continuando...")
    
    # 2. Detectar sink
    logger.info("\n📋 Passo 2: Detectar sink de áudio")
    sink = detectar_sink_anker()
    
    # 3. Gerar som
    logger.info("\n📋 Passo 3: Gerar som de teste")
    audio, rate = gerar_som_teste()
    
    if audio is None:
        logger.error("❌ Falha na geração do som")
        return False
    
    logger.info(f"✅ Som gerado: {len(audio)} samples, {rate}Hz")
    
    # 4. Reproduzir
    logger.info("\n📋 Passo 4: Reproduzir som")
    logger.info("🎵 Reproduzindo: Tom 440Hz (3s) + Beep 800Hz")
    
    sucesso = reproduzir_som(audio, rate, sink)
    
    if sucesso:
        logger.info("\n🎉 TESTE CONCLUÍDO!")
        print("\n" + "="*50)
        print("🎧 VOCÊ OUVIU O SOM? ")
        print("   📢 Tom grave (440Hz) seguido de beep agudo (800Hz)?")
        print("="*50)
        
        resposta = input("Digite 's' se ouviu claramente: ").lower().strip()
        if resposta in ['s', 'sim']:
            logger.info("✅ SUCESSO! Anker funcionando!")
            return True
        else:
            logger.warning("⚠️ Som não foi ouvido corretamente")
            return False
    else:
        logger.error("❌ Falha no teste")
        return False

if __name__ == "__main__":
    main()
