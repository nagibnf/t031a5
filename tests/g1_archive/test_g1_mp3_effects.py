#!/usr/bin/env python3
"""
Teste G1 - Conversão e Reprodução de MP3
Converte MP3 para WAV 16kHz mono e testa no robô.
"""

import time
import sys
import os
import subprocess
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.audio.g1_audio_client import AudioClient
from unitree_sdk2py.g1.arm.g1_arm_action_client import G1ArmActionClient

def convert_mp3_to_wav(input_mp3, output_wav):
    """Converte MP3 para WAV 16kHz mono usando ffmpeg."""
    try:
        print(f"🔄 Convertendo {input_mp3} para {output_wav}...")
        
        # Comando ffmpeg para converter para 16kHz mono WAV
        cmd = [
            'ffmpeg',
            '-i', input_mp3,
            '-ar', '16000',  # Sample rate 16kHz
            '-ac', '1',      # Mono
            '-f', 'wav',     # Formato WAV
            '-y',            # Sobrescrever arquivo existente
            output_wav
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Conversão concluída: {output_wav}")
            
            # Verificar tamanho do arquivo
            if os.path.exists(output_wav):
                size = os.path.getsize(output_wav)
                print(f"📊 Tamanho do arquivo WAV: {size:,} bytes")
                return True
            else:
                print("❌ Arquivo WAV não foi criado")
                return False
        else:
            print(f"❌ Erro na conversão: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao converter: {e}")
        return False

def read_wav(wav_file):
    """Lê arquivo WAV usando a função do SDK."""
    try:
        # Importar função do SDK
        sys.path.insert(0, str(Path(__file__).parent / "unitree_sdk2_python/example/g1/audio"))
        from wav import read_wav as sdk_read_wav
        
        # Ler WAV usando função do SDK
        pcm_list, sample_rate, num_channels, is_ok = sdk_read_wav(wav_file)
        
        print(f"📊 WAV Info:")
        print(f"  - Sample Rate: {sample_rate} Hz")
        print(f"  - Channels: {num_channels}")
        print(f"  - PCM Length: {len(pcm_list)} bytes")
        print(f"  - Read Success: {is_ok}")
        
        # Verificar se é compatível
        if not is_ok:
            print("❌ Falha ao ler WAV")
            return None
        if sample_rate != 16000:
            print("⚠️  WAV não é 16kHz!")
            return None
        if num_channels != 1:
            print("⚠️  WAV não é mono!")
            return None
        
        print(f"✅ WAV compatível com G1")
        print(f"📊 Duração: {len(pcm_list) / (sample_rate * 2):.2f} segundos")
        
        return pcm_list
        
    except Exception as e:
        print(f"❌ Erro ao ler WAV: {e}")
        return None

def play_pcm_stream(audio_client, pcm_data, stream_name="effects"):
    """Reproduz dados PCM no robô usando função do SDK."""
    try:
        # Importar função do SDK
        sys.path.insert(0, str(Path(__file__).parent / "unitree_sdk2_python/example/g1/audio"))
        from wav import play_pcm_stream as sdk_play_pcm_stream
        
        print(f"🎵 Reproduzindo áudio...")
        print(f"📊 Dados PCM: {len(pcm_data)} bytes")
        print(f"📊 Stream Name: {stream_name}")
        
        # Usar função do SDK
        sdk_play_pcm_stream(audio_client, pcm_data, stream_name, chunk_size=96000, sleep_time=0.1, verbose=True)
        
        print("✅ Áudio enviado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao reproduzir: {e}")
        return False

class G1MP3EffectsTest:
    """Teste de conversão e reprodução de MP3 no G1."""
    
    def __init__(self):
        self.interface = "en11"
        self.audio_client = None
        self.arm_client = None
        
    def initialize_sdk(self):
        """Inicializa o SDK."""
        try:
            print("🔧 Inicializando SDK...")
            ChannelFactoryInitialize(0, self.interface)
            print("✅ SDK inicializado")
            
            # Inicializar clientes
            self.audio_client = AudioClient()
            self.audio_client.SetTimeout(10.0)
            self.audio_client.Init()
            print("✅ AudioClient inicializado")
            
            self.arm_client = G1ArmActionClient()
            self.arm_client.SetTimeout(5.0)
            self.arm_client.Init()
            print("✅ ArmActionClient inicializado")
            
            return True
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            return False
    
    def setup_audio(self):
        """Configura o sistema de áudio."""
        try:
            print("🔊 Configurando áudio...")
            
            # Definir volume para 100% (máximo)
            volume_result = self.audio_client.SetVolume(100)
            if volume_result == 0:
                print("✅ Volume configurado para 100% (máximo)")
            else:
                print(f"⚠️  Erro ao configurar volume: {volume_result}")
            
            return True
        except Exception as e:
            print(f"❌ Erro na configuração de áudio: {e}")
            return False
    
    def test_mp3_conversion(self):
        """Testa conversão de MP3 para WAV."""
        print("\n🔄 TESTE CONVERSÃO MP3")
        print("=" * 40)
        
        # Caminhos dos arquivos
        input_mp3 = "./audio/effects/evil-laugh-89423.mp3"
        output_wav = "./audio/effects/evil-laugh-89423.wav"
        
        # Verificar se MP3 existe
        if not os.path.exists(input_mp3):
            print(f"❌ Arquivo MP3 não encontrado: {input_mp3}")
            return False
        
        print(f"📁 MP3 encontrado: {input_mp3}")
        
        # Converter MP3 para WAV
        if not convert_mp3_to_wav(input_mp3, output_wav):
            return False
        
        # Ler WAV convertido
        pcm_data = read_wav(output_wav)
        if pcm_data is None:
            return False
        
        return pcm_data
    
    def test_audio_playback(self, pcm_data):
        """Testa reprodução do áudio no robô."""
        print("\n🎵 TESTE REPRODUÇÃO ÁUDIO")
        print("=" * 40)
        
        # LED azul para indicar reprodução
        self.audio_client.LedControl(0, 0, 255)
        
        # Reproduzir áudio
        if play_pcm_stream(self.audio_client, pcm_data):
            print("✅ Reprodução concluída!")
            
            # Aguardar um pouco
            time.sleep(1)
            
            # Parar reprodução
            stop_result = self.audio_client.PlayStop("effects")
            if stop_result == 0:
                print("✅ Reprodução parada")
            else:
                print(f"⚠️  Erro ao parar reprodução: {stop_result}")
            
            # Voltar LED ao estado original
            self.audio_client.LedControl(173, 216, 230)
            
            return True
        else:
            print("❌ Falha na reprodução")
            return False
    
    def test_movement_with_audio(self, pcm_data):
        """Testa movimento com áudio."""
        print("\n🎭 TESTE MOVIMENTO + ÁUDIO")
        print("=" * 40)
        
        # 1. Relaxar braços
        print("🔄 Relaxando braços...")
        relax_result = self.arm_client.ExecuteAction(99)
        if relax_result == 0:
            print("✅ Braços relaxados")
        else:
            print(f"⚠️  Falha ao relaxar: {relax_result}")
        
        time.sleep(2)
        
        # 2. Executar movimento
        print("🤚 Executando movimento (ID 32)...")
        move_result = self.arm_client.ExecuteAction(32)
        if move_result == 0:
            print("✅ Movimento executado")
        else:
            print(f"❌ Movimento falhou: {move_result}")
            return False
        
        # 3. Aguardar e reproduzir áudio
        time.sleep(2)  # Aguardar movimento começar
        
        print("🎵 Reproduzindo áudio durante movimento...")
        self.audio_client.LedControl(255, 255, 0)  # Amarelo para áudio
        
        if play_pcm_stream(self.audio_client, pcm_data):
            print("✅ Áudio reproduzido durante movimento!")
        else:
            print("❌ Falha na reprodução do áudio")
        
        time.sleep(2)
        
        # 4. Parar áudio
        self.audio_client.PlayStop("effects")
        
        # 5. Relaxar novamente
        print("🔄 Relaxando braços...")
        self.arm_client.ExecuteAction(99)
        
        # 6. Voltar LED ao estado original
        self.audio_client.LedControl(173, 216, 230)
        
        return True
    
    def run_test(self):
        """Executa todos os testes."""
        print("🎵 G1 TESTE MP3 EFFECTS")
        print("=" * 50)
        
        if not self.initialize_sdk():
            return False
        
        if not self.setup_audio():
            return False
        
        # 1. Converter MP3 para WAV
        pcm_data = self.test_mp3_conversion()
        if pcm_data is None:
            return False
        
        # 2. Testar reprodução simples
        self.test_audio_playback(pcm_data)
        
        # 3. Testar movimento com áudio
        self.test_movement_with_audio(pcm_data)
        
        print("\n🎉 TODOS OS TESTES CONCLUÍDOS!")
        return True

def main():
    """Função principal."""
    print("🎵 G1 TESTE MP3 EFFECTS")
    print("=" * 60)
    print("🎯 OBJETIVO: Converter MP3 para WAV e testar no robô")
    print("📋 TESTES:")
    print("  - Conversão MP3 → WAV 16kHz mono")
    print("  - Reprodução de áudio")
    print("  - Movimento + Áudio sincronizado")
    print("  - Volume máximo (100%)")
    
    response = input("\nDeseja continuar? (s/n): ").strip().lower()
    if response not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada")
        return
    
    tester = G1MP3EffectsTest()
    
    if tester.run_test():
        print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
    else:
        print("\n❌ TESTE FALHOU")

if __name__ == "__main__":
    main()
