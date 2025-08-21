#!/usr/bin/env python3
"""
🔊 TESTE ÁUDIO COMPLETO COM BLUETOOTH
Detecta, conecta caixa Bluetooth e valida reprodução de áudio
"""

import sys
import subprocess
import tempfile
import wave
import numpy as np
from pathlib import Path
import logging
import time
import re

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, "/home/unitree/t031a5/src")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TesteAudioCompletoBluetooth:
    """Sistema completo de teste de áudio com gerenciamento Bluetooth."""
    
    def __init__(self):
        self.dji_device = "alsa_input.usb-DJI_Technology_Co.__Ltd._DJI_MIC_MINI_XSP12345678B-01.analog-stereo"
        self.anker_name = "Anker SoundCore"  # Nome comum da caixa
        self.anker_mac = None  # Será detectado automaticamente
        self.anker_sink = None  # PulseAudio sink
        
    def detectar_dispositivos_bluetooth(self):
        """Detecta dispositivos Bluetooth disponíveis."""
        try:
            logger.info("🔍 DETECTANDO DISPOSITIVOS BLUETOOTH...")
            
            # Listar dispositivos pareados
            result = subprocess.run(["bluetoothctl", "devices"], capture_output=True, text=True, timeout=10)
            
            dispositivos_pareados = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split(' ', 2)
                    if len(parts) >= 3 and parts[0] == "Device":
                        mac = parts[1]
                        nome = parts[2]
                        dispositivos_pareados.append({"mac": mac, "nome": nome})
                        logger.info(f"   📱 Pareado: {nome} ({mac})")
                        
                        # Detectar Anker
                        if "anker" in nome.lower() or "soundcore" in nome.lower():
                            self.anker_mac = mac
                            logger.info(f"   ✅ Anker detectado: {mac}")
            
            return dispositivos_pareados
            
        except Exception as e:
            logger.error(f"❌ Erro na detecção: {e}")
            return []
    
    def verificar_conexao_anker(self):
        """Verifica se a caixa Anker está conectada."""
        if not self.anker_mac:
            logger.warning("⚠️ MAC da caixa Anker não conhecido")
            return False
        
        try:
            logger.info(f"🔍 Verificando conexão Anker {self.anker_mac}...")
            
            result = subprocess.run(
                ["bluetoothctl", "info", self.anker_mac], 
                capture_output=True, text=True, timeout=10
            )
            
            conectado = "Connected: yes" in result.stdout
            logger.info(f"   📡 Status: {'✅ Conectado' if conectado else '❌ Desconectado'}")
            
            if conectado:
                # Verificar sink PulseAudio
                return self.detectar_sink_anker()
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro na verificação: {e}")
            return False
    
    def conectar_anker(self):
        """Conecta à caixa Anker."""
        if not self.anker_mac:
            logger.error("❌ MAC da caixa Anker não conhecido")
            return False
        
        try:
            logger.info(f"🔗 Conectando à caixa Anker {self.anker_mac}...")
            
            # Comando de conexão
            result = subprocess.run(
                ["bluetoothctl", "connect", self.anker_mac],
                capture_output=True, text=True, timeout=15
            )
            
            if result.returncode == 0 or "Connection successful" in result.stdout:
                logger.info("✅ Conexão estabelecida!")
                
                # Aguardar estabilização
                logger.info("⏳ Aguardando estabilização (3s)...")
                time.sleep(3)
                
                return self.detectar_sink_anker()
            else:
                logger.error(f"❌ Falha na conexão: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro na conexão: {e}")
            return False
    
    def detectar_sink_anker(self):
        """Detecta sink PulseAudio da caixa Anker."""
        try:
            logger.info("🔍 Detectando sink PulseAudio...")
            
            result = subprocess.run(
                ["pactl", "list", "sinks", "short"],
                capture_output=True, text=True, timeout=10
            )
            
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        sink_name = parts[1]
                        if "anker" in sink_name.lower() or "soundcore" in sink_name.lower():
                            self.anker_sink = sink_name
                            logger.info(f"✅ Sink encontrado: {sink_name}")
                            return True
            
            logger.warning("⚠️ Sink Anker não encontrado")
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro na detecção do sink: {e}")
            return False
    
    def processo_pareamento_interativo(self):
        """Processo interativo para parear nova caixa."""
        logger.info("🔧 PROCESSO DE PAREAMENTO INTERATIVO")
        logger.info("="*50)
        
        print("\n📋 INSTRUÇÕES PARA PAREAMENTO:")
        print("1. 🔊 Ligue sua caixa Anker SoundCore")
        print("2. 🔵 Ative o modo de pareamento (botão Bluetooth)")
        print("3. 🔍 Aguarde piscar azul/vermelho")
        print("4. ✅ Pressione ENTER quando pronto")
        
        input("\nPressione ENTER para iniciar escaneamento...")
        
        try:
            logger.info("🔍 Iniciando escaneamento...")
            
            # Iniciar scan
            subprocess.run(["bluetoothctl", "scan", "on"], timeout=5)
            
            logger.info("⏳ Escaneando por 10 segundos...")
            time.sleep(10)
            
            # Parar scan
            subprocess.run(["bluetoothctl", "scan", "off"], timeout=5)
            
            # Listar dispositivos descobertos
            result = subprocess.run(
                ["bluetoothctl", "devices"],
                capture_output=True, text=True, timeout=10
            )
            
            print("\n📱 DISPOSITIVOS ENCONTRADOS:")
            dispositivos = []
            for i, line in enumerate(result.stdout.strip().split('\n')):
                if line.strip():
                    parts = line.split(' ', 2)
                    if len(parts) >= 3 and parts[0] == "Device":
                        mac = parts[1]
                        nome = parts[2]
                        dispositivos.append({"mac": mac, "nome": nome})
                        print(f"{i+1}. {nome} ({mac})")
            
            if not dispositivos:
                logger.error("❌ Nenhum dispositivo encontrado")
                return False
            
            # Seleção
            while True:
                try:
                    escolha = input("\nEscolha o número da caixa Anker (ou 0 para cancelar): ")
                    escolha = int(escolha)
                    
                    if escolha == 0:
                        logger.info("❌ Cancelado pelo usuário")
                        return False
                    elif 1 <= escolha <= len(dispositivos):
                        dispositivo = dispositivos[escolha - 1]
                        break
                    else:
                        print("⚠️ Número inválido")
                except ValueError:
                    print("⚠️ Digite um número válido")
            
            # Parear dispositivo selecionado
            mac_selecionado = dispositivo["mac"]
            nome_selecionado = dispositivo["nome"]
            
            logger.info(f"🔗 Pareando com {nome_selecionado} ({mac_selecionado})...")
            
            # Pair
            result = subprocess.run(
                ["bluetoothctl", "pair", mac_selecionado],
                capture_output=True, text=True, timeout=20
            )
            
            if result.returncode != 0:
                logger.error(f"❌ Falha no pareamento: {result.stderr}")
                return False
            
            # Trust
            subprocess.run(["bluetoothctl", "trust", mac_selecionado], timeout=10)
            
            # Connect
            result = subprocess.run(
                ["bluetoothctl", "connect", mac_selecionado],
                capture_output=True, text=True, timeout=15
            )
            
            if result.returncode == 0:
                logger.info("✅ Pareamento e conexão bem-sucedidos!")
                self.anker_mac = mac_selecionado
                time.sleep(3)  # Aguardar estabilização
                return self.detectar_sink_anker()
            else:
                logger.error(f"❌ Falha na conexão: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no pareamento: {e}")
            return False
    
    def tocar_som_teste(self):
        """Toca um som de teste para validar áudio."""
        if not self.anker_sink:
            logger.error("❌ Sink Anker não disponível")
            return False
        
        try:
            logger.info("🔊 Tocando som de teste...")
            
            # Gerar tom de teste (440Hz - Lá)
            duration = 2.0  # 2 segundos
            sample_rate = 16000
            frequency = 440  # Hz
            
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            tone = np.sin(2 * np.pi * frequency * t) * 0.3  # Volume moderado
            
            # Fade in/out para evitar cliques
            fade_samples = int(0.1 * sample_rate)  # 0.1s fade
            tone[:fade_samples] *= np.linspace(0, 1, fade_samples)
            tone[-fade_samples:] *= np.linspace(1, 0, fade_samples)
            
            # Salvar como WAV
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                tone_int16 = (tone * 32767).astype(np.int16)
                
                with wave.open(temp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(tone_int16.tobytes())
                
                # Reproduzir no sink específico
                cmd = ["paplay", "--device", self.anker_sink, temp_file.name]
                result = subprocess.run(cmd, timeout=5)
                
                # Limpeza
                Path(temp_file.name).unlink()
                
                if result.returncode == 0:
                    logger.info("✅ Som de teste tocado")
                    
                    resposta = input("\n🎧 Você ouviu o tom de teste? (s/n): ").lower().strip()
                    if resposta in ['s', 'sim', 'y', 'yes']:
                        logger.info("✅ Áudio Bluetooth confirmado!")
                        return True
                    else:
                        logger.warning("⚠️ Som não ouvido - problema no áudio")
                        return False
                else:
                    logger.error("❌ Falha na reprodução do teste")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erro no som de teste: {e}")
            return False
    
    def configurar_audio_bluetooth(self):
        """Configura sistema de áudio Bluetooth completo."""
        logger.info("🔊 CONFIGURAÇÃO ÁUDIO BLUETOOTH")
        logger.info("="*50)
        
        # 1. Detectar dispositivos
        dispositivos = self.detectar_dispositivos_bluetooth()
        
        # 2. Verificar se Anker está conectado
        if self.anker_mac:
            if self.verificar_conexao_anker():
                logger.info("✅ Anker já conectado!")
            else:
                logger.info("🔗 Tentando reconectar...")
                if not self.conectar_anker():
                    logger.warning("⚠️ Falha na reconexão")
                    return self.processo_pareamento_interativo()
        else:
            logger.info("📱 Anker não pareado - iniciando pareamento...")
            if not self.processo_pareamento_interativo():
                return False
        
        # 3. Teste de áudio
        if not self.tocar_som_teste():
            logger.error("❌ Falha no teste de áudio")
            return False
        
        logger.info("✅ Sistema Bluetooth configurado e validado!")
        return True
    
    def capturar_dji_nativo(self, duracao=5.0):
        """Captura DJI com formato nativo correto."""
        try:
            logger.info(f"🎤 Capturando DJI formato nativo ({duracao}s)...")
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                cmd = [
                    "parecord",
                    "--device", self.dji_device,
                    "--format=s24le",
                    "--rate=48000",
                    "--channels=2",
                    temp_file.name
                ]
                
                process = subprocess.Popen(cmd)
                time.sleep(duracao)
                process.terminate()
                process.wait()
                
                if Path(temp_file.name).exists():
                    file_size = Path(temp_file.name).stat().st_size
                    logger.info(f"✅ Capturado: {file_size} bytes")
                    
                    if file_size > 1000:
                        audio_data = self.converter_s24le_para_mono16k(temp_file.name)
                        Path(temp_file.name).unlink()
                        return audio_data
                    
        except Exception as e:
            logger.error(f"❌ Erro captura DJI: {e}")
        
        return None
    
    def converter_s24le_para_mono16k(self, arquivo_s24le):
        """Converte s24le stereo 48kHz para mono 16kHz."""
        try:
            with wave.open(arquivo_s24le, 'rb') as wav_file:
                frames = wav_file.readframes(wav_file.getnframes())
                nchannels = wav_file.getnchannels()
                
                # Converter 24-bit para float32
                audio_data = np.frombuffer(frames, dtype=np.uint8)
                audio_data = audio_data.reshape(-1, 3)
                
                samples = []
                for i in range(0, len(audio_data), nchannels):
                    frame_samples = []
                    for ch in range(min(nchannels, len(audio_data) - i)):
                        frame = audio_data[i + ch]
                        val = (frame[2] << 16) | (frame[1] << 8) | frame[0]
                        if val >= 2**23:
                            val -= 2**24
                        frame_samples.append(val)
                    
                    if len(frame_samples) == 2:
                        mono_sample = (frame_samples[0] + frame_samples[1]) / 2
                    else:
                        mono_sample = frame_samples[0]
                    
                    samples.append(mono_sample)
                
                audio_data = np.array(samples, dtype=np.float32) / (2**23)
                
                # Resample 48kHz -> 16kHz (decimação 3:1)
                audio_data = audio_data[::3]
                
                return audio_data
                
        except Exception as e:
            logger.error(f"❌ Erro na conversão: {e}")
            return None
    
    def reproduzir_audio_bluetooth(self, audio_data):
        """Reproduz áudio via Bluetooth."""
        if not self.anker_sink:
            logger.error("❌ Sink Bluetooth não disponível")
            return False
        
        try:
            # Salvar áudio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                audio_int16 = (audio_data * 32767).astype(np.int16)
                
                with wave.open(temp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(16000)
                    wav_file.writeframes(audio_int16.tobytes())
                
                # Reproduzir via Bluetooth
                logger.info("🔊 Reproduzindo via Bluetooth...")
                cmd = ["paplay", "--device", self.anker_sink, temp_file.name]
                result = subprocess.run(cmd, timeout=15)
                
                # Limpeza
                Path(temp_file.name).unlink()
                
                return result.returncode == 0
                
        except Exception as e:
            logger.error(f"❌ Erro na reprodução: {e}")
            return False
    
    def executar_teste_completo(self):
        """Executa teste completo de áudio com Bluetooth."""
        logger.info("🎧 TESTE ÁUDIO COMPLETO - DJI + BLUETOOTH")
        logger.info("="*60)
        
        # 1. Configurar Bluetooth
        if not self.configurar_audio_bluetooth():
            logger.error("❌ Falha na configuração Bluetooth")
            return False
        
        logger.info("\n" + "="*60)
        
        # 2. Capturar áudio DJI
        logger.info("🎤 CAPTURA DE ÁUDIO DJI")
        logger.info("🗣️ FALE CLARAMENTE NO MICROFONE!")
        
        for i in range(3, 0, -1):
            logger.info(f"⏰ {i}...")
            time.sleep(1)
        
        logger.info("🔴 GRAVANDO...")
        audio_data = self.capturar_dji_nativo(5.0)
        
        if audio_data is None:
            logger.error("❌ Falha na captura de áudio")
            return False
        
        # 3. Analisar áudio
        rms = np.sqrt(np.mean(audio_data**2))
        peak = np.max(np.abs(audio_data))
        
        logger.info(f"📊 RMS: {rms:.6f}")
        logger.info(f"📊 Peak: {peak:.6f}")
        
        if rms < 0.005:
            logger.warning("⚠️ Áudio muito baixo - possível problema")
        else:
            logger.info("✅ Áudio com nível adequado")
        
        # 4. Reproduzir via Bluetooth
        logger.info("\n🔊 REPRODUZINDO VIA BLUETOOTH...")
        if self.reproduzir_audio_bluetooth(audio_data):
            logger.info("✅ Reprodução iniciada")
            
            # Confirmação do usuário
            resposta = input("\n🎧 O áudio foi reproduzido claramente? (s/n): ").lower().strip()
            if resposta in ['s', 'sim', 'y', 'yes']:
                logger.info("🎉 TESTE COMPLETO BEM-SUCEDIDO!")
                logger.info("✅ DJI Mic 2 + Bluetooth funcionando!")
                return True
            else:
                logger.warning("⚠️ Problema na qualidade do áudio")
                return False
        else:
            logger.error("❌ Falha na reprodução")
            return False

def main():
    """Função principal."""
    teste = TesteAudioCompletoBluetooth()
    resultado = teste.executar_teste_completo()
    
    if resultado:
        logger.info("\n🎯 SISTEMA PRONTO PARA INTEGRAÇÃO!")
    else:
        logger.info("\n🔧 Necessita ajustes adicionais")

if __name__ == "__main__":
    main()

