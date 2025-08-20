#!/usr/bin/env python3
"""
Teste G1 - Reprodução de Áudio WAV
Testa reprodução de arquivos WAV no G1.
"""

import time
import sys
import struct
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.audio.g1_audio_client import AudioClient

def read_wav(filename):
    """Lê arquivo WAV e retorna dados PCM."""
    try:
        with open(filename, 'rb') as f:
            def read(fmt):
                return struct.unpack(fmt, f.read(struct.calcsize(fmt)))

            # === Chunk Header ===
            chunk_id, = read('<I')
            if chunk_id != 0x46464952:  # "RIFF"
                print(f"[ERROR] chunk_id != 'RIFF': {hex(chunk_id)}")
                return [], -1, -1, False

            _chunk_size, = read('<I')
            format_tag, = read('<I')
            if format_tag != 0x45564157:  # "WAVE"
                print(f"[ERROR] format != 'WAVE': {hex(format_tag)}")
                return [], -1, -1, False

            # === Subchunk1: fmt ===
            subchunk1_id, = read('<I')
            subchunk1_size, = read('<I')

            if subchunk1_id == 0x4B4E554A:  # JUNK
                f.seek(subchunk1_size, 1)
                subchunk1_id, = read('<I')
                subchunk1_size, = read('<I')

            if subchunk1_id != 0x20746D66:  # "fmt "
                print(f"[ERROR] subchunk1_id != 'fmt ': {hex(subchunk1_id)}")
                return [], -1, -1, False

            if subchunk1_size not in [16, 18]:
                print(f"[ERROR] subchunk1_size != 16 or 18: {subchunk1_size}")
                return [], -1, -1, False

            audio_format, = read('<H')
            if audio_format != 1:
                print(f"[ERROR] audio_format != PCM (1): {audio_format}")
                return [], -1, -1, False

            num_channels, = read('<H')
            sample_rate, = read('<I')
            byte_rate, = read('<I')
            block_align, = read('<H')
            bits_per_sample, = read('<H')

            expected_byte_rate = sample_rate * num_channels * bits_per_sample // 8
            if byte_rate != expected_byte_rate:
                print(f"[ERROR] byte_rate mismatch: got {byte_rate}, expected {expected_byte_rate}")
                return [], -1, -1, False

            expected_align = num_channels * bits_per_sample // 8
            if block_align != expected_align:
                print(f"[ERROR] block_align mismatch: got {block_align}, expected {expected_align}")
                return [], -1, -1, False

            if bits_per_sample != 16:
                print(f"[ERROR] Only 16-bit samples supported, got {bits_per_sample}")
                return [], -1, -1, False

            if subchunk1_size == 18:
                extra_size, = read('<H')
                if extra_size != 0:
                    print(f"[ERROR] extra_size != 0: {extra_size}")
                    return [], -1, -1, False

            # === Subchunk2: data ===
            while True:
                subchunk2_id, subchunk2_size = read('<II')
                if subchunk2_id == 0x61746164:  # "data"
                    break
                f.seek(subchunk2_size, 1)

            raw_pcm = f.read(subchunk2_size)
            if len(raw_pcm) != subchunk2_size:
                print("[ERROR] Failed to read full PCM data")
                return [], -1, -1, False

            return list(raw_pcm), sample_rate, num_channels, True

    except Exception as e:
        print(f"[ERROR] read_wave() failed: {e}")
        return [], -1, -1, False

def play_pcm_stream(client, pcm_list, stream_name="example", chunk_size=96000, sleep_time=1.0, verbose=False):
    """
    Reproduz stream PCM de áudio (formato 16-bit little-endian), enviando dados em chunks.
    """
    pcm_data = bytes(pcm_list)
    stream_id = str(int(time.time() * 1000))  # ID único baseado no timestamp
    offset = 0
    chunk_index = 0
    total_size = len(pcm_data)

    print(f"🎵 Iniciando reprodução: {total_size} bytes, {len(pcm_data)//2} amostras")

    while offset < total_size:
        remaining = total_size - offset
        current_chunk_size = min(chunk_size, remaining)
        chunk = pcm_data[offset:offset + current_chunk_size]

        if verbose:
            print(f"[CHUNK {chunk_index}] offset = {offset}, size = {current_chunk_size} bytes")

        # Enviar o chunk
        ret_code, _ = client.PlayStream(stream_name, stream_id, chunk)
        if ret_code != 0:
            print(f"❌ Falha ao enviar chunk {chunk_index}, código: {ret_code}")
            break
        else:
            print(f"✅ Chunk {chunk_index} enviado com sucesso")

        offset += current_chunk_size
        chunk_index += 1
        time.sleep(sleep_time)

    print(f"🎵 Reprodução concluída: {chunk_index} chunks enviados")

def create_test_wav():
    """Cria um arquivo WAV de teste simples."""
    import array
    import math
    
    # Parâmetros do áudio
    sample_rate = 16000
    duration = 3  # segundos
    frequency = 440  # Hz (nota A4)
    amplitude = 0.3
    
    # Gerar onda senoidal
    samples = []
    for i in range(sample_rate * duration):
        sample = int(amplitude * 32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
        samples.append(sample)
    
    # Converter para array
    audio_data = array.array('h', samples)
    
    # Salvar como WAV
    filename = "test_audio.wav"
    
    try:
        subchunk2_size = len(audio_data) * 2
        chunk_size = 36 + subchunk2_size

        with open(filename, 'wb') as f:
            # RIFF chunk
            f.write(struct.pack('<I', 0x46464952))  # "RIFF"
            f.write(struct.pack('<I', chunk_size))
            f.write(struct.pack('<I', 0x45564157))  # "WAVE"

            # fmt subchunk
            f.write(struct.pack('<I', 0x20746D66))  # "fmt "
            f.write(struct.pack('<I', 16))          # PCM
            f.write(struct.pack('<H', 1))           # PCM format
            f.write(struct.pack('<H', 1))           # mono
            f.write(struct.pack('<I', sample_rate))
            f.write(struct.pack('<I', sample_rate * 2))  # byte_rate
            f.write(struct.pack('<H', 2))                # block_align
            f.write(struct.pack('<H', 16))               # bits per sample

            # data subchunk
            f.write(struct.pack('<I', 0x61746164))  # "data"
            f.write(struct.pack('<I', subchunk2_size))
            f.write(audio_data.tobytes())

        print(f"✅ Arquivo WAV criado: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Erro ao criar WAV: {e}")
        return None

class G1AudioWAVTest:
    """Teste de reprodução de áudio WAV no G1."""
    
    def __init__(self):
        self.interface = "en11"
        self.audio_client = None
        
    def initialize_sdk(self):
        """Inicializa o SDK."""
        try:
            print("🔧 Inicializando SDK...")
            ChannelFactoryInitialize(0, self.interface)
            print("✅ SDK inicializado")
            
            self.audio_client = AudioClient()
            self.audio_client.SetTimeout(10.0)
            self.audio_client.Init()
            print("✅ AudioClient inicializado")
            
            return True
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            return False
    
    def setup_audio(self):
        """Configura o sistema de áudio."""
        try:
            print("🔊 Configurando áudio...")
            
            # Verificar volume atual
            volume_code, volume_data = self.audio_client.GetVolume()
            if volume_code == 0:
                print(f"📊 Volume atual: {volume_data}")
            
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
    
    def test_wav_playback(self, wav_file):
        """Testa reprodução de arquivo WAV."""
        try:
            print(f"\n🎵 TESTE REPRODUÇÃO WAV: {wav_file}")
            print("=" * 50)
            
            # Ler arquivo WAV
            print("📖 Lendo arquivo WAV...")
            pcm_list, sample_rate, num_channels, is_ok = read_wav(wav_file)
            
            if not is_ok:
                print("❌ Falha ao ler arquivo WAV")
                return False
            
            print(f"📊 Informações do áudio:")
            print(f"  - Sample Rate: {sample_rate} Hz")
            print(f"  - Canais: {num_channels}")
            print(f"  - Dados PCM: {len(pcm_list)} bytes")
            
            # Verificar formato
            if sample_rate != 16000 or num_channels != 1:
                print("❌ Formato não suportado (deve ser 16kHz mono)")
                return False
            
            # Reproduzir áudio
            print("🎵 Iniciando reprodução...")
            play_pcm_stream(self.audio_client, pcm_list, "test_audio", verbose=True)
            
            # Aguardar um pouco
            time.sleep(2)
            
            # Parar reprodução
            print("⏹️  Parando reprodução...")
            self.audio_client.PlayStop("test_audio")
            
            print("✅ Reprodução WAV concluída!")
            return True
            
        except Exception as e:
            print(f"❌ Erro na reprodução WAV: {e}")
            return False
    
    def test_tts_vs_wav(self):
        """Compara TTS vs reprodução WAV."""
        print("\n🔄 COMPARAÇÃO TTS vs WAV")
        print("=" * 50)
        
        # 1. Teste TTS
        print("🗣️  Teste TTS:")
        start_time = time.time()
        tts_result = self.audio_client.TtsMaker("Teste de TTS em português", 0)
        tts_start_time = time.time() - start_time
        print(f"⏱️  TTS iniciado em {tts_start_time:.2f}s")
        
        # Aguardar TTS
        time.sleep(5)
        
        # 2. Teste WAV
        print("\n🎵 Teste WAV:")
        wav_file = create_test_wav()
        if wav_file:
            start_time = time.time()
            wav_success = self.test_wav_playback(wav_file)
            wav_time = time.time() - start_time
            print(f"⏱️  WAV executado em {wav_time:.2f}s")
            
            # Limpar arquivo temporário
            try:
                Path(wav_file).unlink()
                print(f"🗑️  Arquivo temporário removido: {wav_file}")
            except:
                pass
        
        print(f"\n📊 COMPARAÇÃO:")
        print(f"  TTS: {tts_result} (início: {tts_start_time:.2f}s)")
        print(f"  WAV: {'✅' if wav_success else '❌'} (total: {wav_time:.2f}s)")
    
    def run_test(self):
        """Executa o teste completo."""
        print("🎵 G1 TESTE ÁUDIO WAV")
        print("=" * 50)
        
        if not self.initialize_sdk():
            return False
        
        if not self.setup_audio():
            return False
        
        # Teste 1: WAV gerado
        wav_file = create_test_wav()
        if wav_file:
            self.test_wav_playback(wav_file)
            
            # Limpar arquivo temporário
            try:
                Path(wav_file).unlink()
                print(f"🗑️  Arquivo temporário removido: {wav_file}")
            except:
                pass
        
        # Teste 2: Comparação TTS vs WAV
        self.test_tts_vs_wav()
        
        return True

def main():
    """Função principal."""
    print("🎵 G1 ÁUDIO WAV - TESTE DE REPRODUÇÃO")
    print("=" * 60)
    print("🎯 OBJETIVO: Testar reprodução de arquivos WAV")
    print("📋 RECURSOS:")
    print("  - Criação de WAV de teste (440Hz, 3s)")
    print("  - Reprodução via PlayStream")
    print("  - Comparação TTS vs WAV")
    
    response = input("\nDeseja continuar? (s/n): ").strip().lower()
    if response not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada")
        return
    
    tester = G1AudioWAVTest()
    
    if tester.run_test():
        print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
    else:
        print("\n❌ TESTE FALHOU")

if __name__ == "__main__":
    main()
