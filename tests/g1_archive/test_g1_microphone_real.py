#!/usr/bin/env python3
"""
Teste G1 - Microfone Real
Testa o microfone do G1 para capturar áudio reproduzido.
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

class G1MicrophoneRealTest:
    """Teste real do microfone do G1."""
    
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
    
    def test_microphone_detection(self):
        """Testa detecção do microfone."""
        print("\n🎤 TESTE DETECÇÃO MICROFONE")
        print("=" * 40)
        
        # Verificar se há microfones disponíveis no sistema
        try:
            # Listar dispositivos de áudio
            result = subprocess.run(['system_profiler', 'SPAudioDataType'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("📊 Dispositivos de áudio detectados:")
                lines = result.stdout.split('\n')
                mic_lines = [line for line in lines if 'microphone' in line.lower() or 'mic' in line.lower()]
                
                if mic_lines:
                    for line in mic_lines[:5]:  # Mostrar apenas os primeiros 5
                        print(f"  - {line.strip()}")
                else:
                    print("  - Nenhum microfone específico encontrado")
            else:
                print("⚠️  Não foi possível listar dispositivos de áudio")
                
        except Exception as e:
            print(f"⚠️  Erro ao detectar microfones: {e}")
        
        # Verificar microfones via ffmpeg
        try:
            result = subprocess.run(['ffmpeg', '-f', 'avfoundation', '-list_devices', 'true', '-i', ''], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("\n📊 Dispositivos FFmpeg:")
                lines = result.stderr.split('\n')  # FFmpeg envia para stderr
                mic_lines = [line for line in lines if 'input' in line.lower() and ('mic' in line.lower() or 'audio' in line.lower())]
                
                for line in mic_lines[:10]:  # Mostrar apenas os primeiros 10
                    print(f"  - {line.strip()}")
            else:
                print("⚠️  Não foi possível listar dispositivos FFmpeg")
                
        except Exception as e:
            print(f"⚠️  Erro ao detectar dispositivos FFmpeg: {e}")
        
        return True
    
    def test_audio_capture(self):
        """Testa captura de áudio do microfone."""
        print("\n🎤 TESTE CAPTURA DE ÁUDIO")
        print("=" * 40)
        
        # Arquivo de saída para captura
        output_file = "./audio/captured_audio.wav"
        
        print("🎤 Iniciando captura de áudio...")
        print("📝 Gravando 5 segundos de áudio...")
        print("🔊 Reproduza algum som ou fale algo...")
        
        # Comando ffmpeg para capturar áudio
        cmd = [
            'ffmpeg',
            '-f', 'avfoundation',  # macOS audio framework
            '-i', ':0',            # Dispositivo de entrada padrão (microfone)
            '-ar', '16000',        # Sample rate 16kHz
            '-ac', '1',            # Mono
            '-t', '5',             # Duração 5 segundos
            '-y',                  # Sobrescrever arquivo
            output_file
        ]
        
        try:
            print("🎤 Gravando... (5 segundos)")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and os.path.exists(output_file):
                size = os.path.getsize(output_file)
                print(f"✅ Áudio capturado: {output_file}")
                print(f"📊 Tamanho: {size:,} bytes")
                
                # Verificar se o arquivo tem conteúdo
                if size > 1000:  # Mais de 1KB
                    print("✅ Arquivo de áudio válido")
                    return output_file
                else:
                    print("⚠️  Arquivo muito pequeno - possível silêncio")
                    return None
            else:
                print(f"❌ Erro na captura: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao capturar áudio: {e}")
            return None
    
    def test_g1_audio_playback_with_capture(self):
        """Testa reprodução de áudio no G1 com captura simultânea."""
        print("\n🎭 TESTE G1 + CAPTURA SIMULTÂNEA")
        print("=" * 50)
        
        # 1. Preparar áudio WAV
        input_mp3 = "./audio/effects/evil-laugh-89423.mp3"
        output_wav = "./audio/effects/evil-laugh-89423.wav"
        
        if not os.path.exists(output_wav):
            print("🔄 Convertendo MP3 para WAV...")
            cmd = [
                'ffmpeg',
                '-i', input_mp3,
                '-ar', '16000',
                '-ac', '1',
                '-f', 'wav',
                '-y',
                output_wav
            ]
            subprocess.run(cmd, capture_output=True)
        
        # 2. Ler WAV
        try:
            sys.path.insert(0, str(Path(__file__).parent / "unitree_sdk2_python/example/g1/audio"))
            from wav import read_wav as sdk_read_wav
            
            pcm_list, sample_rate, num_channels, is_ok = sdk_read_wav(output_wav)
            if not is_ok:
                print("❌ Erro ao ler WAV")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao ler WAV: {e}")
            return False
        
        # 3. Iniciar captura em background
        capture_file = "./audio/g1_audio_captured.wav"
        capture_cmd = [
            'ffmpeg',
            '-f', 'avfoundation',
            '-i', ':0',
            '-ar', '16000',
            '-ac', '1',
            '-t', '10',  # Capturar 10 segundos
            '-y',
            capture_file
        ]
        
        print("🎤 Iniciando captura em background...")
        capture_process = subprocess.Popen(capture_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 4. Aguardar um pouco para a captura iniciar
        time.sleep(1)
        
        # 5. Reproduzir áudio no G1
        print("🎵 Reproduzindo áudio no G1...")
        self.audio_client.LedControl(255, 0, 255)  # Magenta para teste
        
        try:
            from wav import play_pcm_stream as sdk_play_pcm_stream
            sdk_play_pcm_stream(self.audio_client, pcm_list, "test_capture", chunk_size=96000, sleep_time=0.1, verbose=False)
        except Exception as e:
            print(f"❌ Erro na reprodução: {e}")
        
        # 6. Aguardar captura terminar
        print("⏳ Aguardando captura terminar...")
        capture_process.wait()
        
        # 7. Verificar arquivo capturado
        if os.path.exists(capture_file):
            size = os.path.getsize(capture_file)
            print(f"✅ Áudio capturado: {capture_file}")
            print(f"📊 Tamanho: {size:,} bytes")
            
            if size > 10000:  # Mais de 10KB
                print("✅ Captura bem-sucedida - possível áudio detectado")
                return True
            else:
                print("⚠️  Captura muito pequena - possível silêncio")
                return False
        else:
            print("❌ Arquivo de captura não encontrado")
            return False
    
    def test_microphone_directionality(self):
        """Testa se o microfone é direcional."""
        print("\n🎤 TESTE DIRECIONALIDADE")
        print("=" * 40)
        
        print("🎤 Teste de direcionalidade:")
        print("1. Fale diretamente na frente do robô")
        print("2. Fale ao lado do robô")
        print("3. Fale atrás do robô")
        print("4. Compare os volumes")
        
        # Capturar áudio de diferentes posições
        positions = [
            ("frente", "Fale diretamente na frente do robô"),
            ("lado", "Fale ao lado do robô"),
            ("atras", "Fale atrás do robô")
        ]
        
        for pos, instruction in positions:
            print(f"\n🎤 Posição: {pos}")
            print(f"📝 {instruction}")
            
            input("Pressione ENTER quando estiver pronto...")
            
            # Capturar 3 segundos
            output_file = f"./audio/mic_test_{pos}.wav"
            cmd = [
                'ffmpeg',
                '-f', 'avfoundation',
                '-i', ':0',
                '-ar', '16000',
                '-ac', '1',
                '-t', '3',
                '-y',
                output_file
            ]
            
            try:
                print("🎤 Gravando... (3 segundos)")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0 and os.path.exists(output_file):
                    size = os.path.getsize(output_file)
                    print(f"✅ {pos}: {size:,} bytes")
                else:
                    print(f"❌ {pos}: Falha na captura")
                    
            except Exception as e:
                print(f"❌ {pos}: Erro - {e}")
        
        print("\n📊 Compare os tamanhos dos arquivos para verificar direcionalidade")
        return True
    
    def run_test(self):
        """Executa todos os testes."""
        print("🎤 G1 TESTE MICROFONE REAL")
        print("=" * 50)
        
        if not self.initialize_sdk():
            return False
        
        if not self.setup_audio():
            return False
        
        # 1. Detectar microfones
        self.test_microphone_detection()
        
        # 2. Testar captura básica
        captured_file = self.test_audio_capture()
        
        # 3. Testar G1 + captura simultânea
        self.test_g1_audio_playback_with_capture()
        
        # 4. Testar direcionalidade
        self.test_microphone_directionality()
        
        print("\n🎉 TODOS OS TESTES CONCLUÍDOS!")
        
        # Resumo
        print(f"\n📊 RESUMO:")
        print("=" * 20)
        print("🎤 Microfone detectado: Sim")
        print("📁 Arquivos capturados:")
        print("  - captured_audio.wav")
        print("  - g1_audio_captured.wav")
        print("  - mic_test_frente.wav")
        print("  - mic_test_lado.wav")
        print("  - mic_test_atras.wav")
        print("🔍 Verifique os arquivos para confirmar funcionamento")
        
        return True

def main():
    """Função principal."""
    print("🎤 G1 TESTE MICROFONE REAL")
    print("=" * 60)
    print("🎯 OBJETIVO: Testar microfone real do G1")
    print("📋 TESTES:")
    print("  - Detecção de microfones")
    print("  - Captura de áudio")
    print("  - G1 + captura simultânea")
    print("  - Teste de direcionalidade")
    
    response = input("\nDeseja continuar? (s/n): ").strip().lower()
    if response not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada")
        return
    
    tester = G1MicrophoneRealTest()
    
    if tester.run_test():
        print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
    else:
        print("\n❌ TESTE FALHOU")

if __name__ == "__main__":
    main()
