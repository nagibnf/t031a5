#!/usr/bin/env python3
"""
Teste G1 - Movimento + Áudio WAV
Executa movimento ID 32 e reproduz áudio WAV simultaneamente.
"""

import time
import sys
import struct
import array
import math
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.arm.g1_arm_action_client import G1ArmActionClient
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient
from unitree_sdk2py.g1.audio.g1_audio_client import AudioClient
from unitree_sdk2py.comm.motion_switcher.motion_switcher_client import MotionSwitcherClient

def create_portuguese_audio():
    """Cria áudio em português (simulado com beeps)."""
    # Parâmetros do áudio
    sample_rate = 16000
    duration = 4  # segundos
    
    # Sequência de tons para simular fala
    tones = [
        (440, 0.5),   # A4 - "Olá"
        (523, 0.5),   # C5 - "como"
        (587, 0.5),   # D5 - "você"
        (659, 0.5),   # E5 - "está"
        (523, 0.5),   # C5 - "?"
        (440, 0.5),   # A4 - "Movimento"
        (523, 0.5),   # C5 - "concluído"
        (440, 0.5),   # A4 - "!"
    ]
    
    # Gerar áudio
    samples = []
    samples_per_tone = int(sample_rate * duration / len(tones))
    
    for freq, amplitude in tones:
        for i in range(samples_per_tone):
            sample = int(amplitude * 0.2 * 32767 * math.sin(2 * math.pi * freq * i / sample_rate))
            samples.append(sample)
    
    # Converter para array
    audio_data = array.array('h', samples)
    
    # Salvar como WAV
    filename = "portuguese_audio.wav"
    
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

        print(f"✅ Áudio português criado: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Erro ao criar áudio: {e}")
        return None

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
    """Reproduz stream PCM de áudio."""
    pcm_data = bytes(pcm_list)
    stream_id = str(int(time.time() * 1000))
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

class G1MovementWAVTest:
    """Teste de movimento + áudio WAV no G1."""
    
    def __init__(self):
        self.interface = "en11"
        self.arm_client = None
        self.loco_client = None
        self.audio_client = None
        self.motion_switcher = None
        
    def initialize_sdk(self):
        """Inicializa o SDK."""
        try:
            print("🔧 Inicializando SDK...")
            ChannelFactoryInitialize(0, self.interface)
            print("✅ SDK inicializado")
            
            # Inicializar clientes
            self.arm_client = G1ArmActionClient()
            self.arm_client.SetTimeout(5.0)
            self.arm_client.Init()
            print("✅ ArmActionClient inicializado")
            
            self.loco_client = LocoClient()
            self.loco_client.SetTimeout(5.0)
            self.loco_client.Init()
            print("✅ LocoClient inicializado")
            
            self.audio_client = AudioClient()
            self.audio_client.SetTimeout(10.0)
            self.audio_client.Init()
            print("✅ AudioClient inicializado")
            
            self.motion_switcher = MotionSwitcherClient()
            self.motion_switcher.SetTimeout(5.0)
            self.motion_switcher.Init()
            print("✅ MotionSwitcherClient inicializado")
            
            return True
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            return False
    
    def check_current_state(self):
        """Verifica o estado atual do robô."""
        try:
            status, result = self.motion_switcher.CheckMode()
            print(f"📊 Status atual: {status}")
            
            if result:
                print(f"📊 Modo atual: {result}")
                if isinstance(result, dict) and result.get('name') == 'ai':
                    print("✅ Robô já está em Main Operation Control!")
                    return True
                else:
                    print(f"⚠️  Robô está em modo: {result}")
                    return False
            else:
                print("❌ Não foi possível verificar o modo atual")
                return False
        except Exception as e:
            print(f"❌ Erro ao verificar estado: {e}")
            return False
    
    def setup_main_operation_control(self):
        """Configura o robô para Main Operation Control se necessário."""
        if self.check_current_state():
            print("✅ Robô já está pronto para comandos!")
            return True
        
        print("🚀 Configurando Main Operation Control...")
        
        # Zero Torque → Damping → Get Ready
        print("1️⃣ Zero Torque...")
        self.loco_client.SetFsmId(0)
        time.sleep(2)
        
        print("2️⃣ Damping...")
        self.loco_client.SetFsmId(1)
        time.sleep(2)
        
        print("3️⃣ Get Ready...")
        self.loco_client.SetFsmId(4)
        time.sleep(3)
        
        print("4️⃣ Use R1+X no controle físico para Main Operation Control")
        input("Pressione Enter após R1+X...")
        
        return self.check_current_state()
    
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
    
    def execute_movement_32(self):
        """Executa o movimento ID 32 (mão na boca)."""
        try:
            print("🤚 Executando movimento ID 32 (mão na boca)...")
            result = self.arm_client.ExecuteAction(32)
            
            if result == 0:
                print("✅ Movimento ID 32 executado com sucesso!")
                return True
            else:
                print(f"❌ Movimento ID 32 falhou (Status: {result})")
                return False
        except Exception as e:
            print(f"❌ Erro no movimento: {e}")
            return False
    
    def release_arm(self):
        """Volta o braço ao estado inicial."""
        try:
            print("🔄 Voltando braço ao estado inicial...")
            result = self.arm_client.ExecuteAction(99)  # release_arm
            
            if result == 0:
                print("✅ Braço liberado com sucesso!")
                return True
            else:
                print(f"❌ Falha ao liberar braço (Status: {result})")
                return False
        except Exception as e:
            print(f"❌ Erro ao liberar braço: {e}")
            return False
    
    def test_led_effects(self):
        """Testa efeitos de LED."""
        try:
            print("💡 Testando LEDs...")
            
            # Vermelho
            self.audio_client.LedControl(255, 0, 0)
            time.sleep(1)
            
            # Verde
            self.audio_client.LedControl(0, 255, 0)
            time.sleep(1)
            
            # Azul
            self.audio_client.LedControl(0, 0, 255)
            time.sleep(1)
            
            # Voltar ao azul claro (estado original)
            self.audio_client.LedControl(173, 216, 230)  # Azul claro
            
            print("✅ LEDs testados com sucesso!")
            return True
        except Exception as e:
            print(f"❌ Erro nos LEDs: {e}")
            return False
    
    def test_movement_with_wav(self):
        """Teste principal: movimento + áudio WAV."""
        print("🎭 TESTE MOVIMENTO + ÁUDIO WAV")
        print("=" * 50)
        
        # 1. Criar áudio em português
        print("\n🎵 Criando áudio em português...")
        wav_file = create_portuguese_audio()
        if not wav_file:
            print("❌ Falha ao criar áudio")
            return False
        
        # 2. Preparar áudio (ler WAV)
        print("\n📖 Preparando áudio...")
        pcm_list, sample_rate, num_channels, is_ok = read_wav(wav_file)
        if not is_ok:
            print("❌ Falha ao ler arquivo WAV")
            return False
        
        # 3. Executar movimento primeiro
        print("\n🤚 Executando movimento ID 32...")
        movement_result = self.execute_movement_32()
        
        if movement_result:
            print("✅ Movimento executado!")
            
            # Aguardar quase o final do movimento (2 segundos)
            print("⏳ Aguardando quase o final do movimento...")
            time.sleep(2)
            
            # Iniciar áudio no final do movimento
            print("🎵 Iniciando áudio no final do movimento...")
            play_pcm_stream(self.audio_client, pcm_list, "portuguese_audio", verbose=True)
            
            # Aguardar conclusão do movimento
            print("⏳ Aguardando conclusão do movimento...")
            time.sleep(1)
            
            # Parar reprodução
            self.audio_client.PlayStop("portuguese_audio")
            
            # 4. LEDs
            print("\n💡 Teste LEDs")
            self.test_led_effects()
            
            # 5. Voltar ao estado inicial
            time.sleep(2)
            self.release_arm()
            
            # Limpar arquivo
            try:
                Path(wav_file).unlink()
                print(f"🗑️  Arquivo removido: {wav_file}")
            except:
                pass
            
            return True
        else:
            print("❌ Falha no movimento")
            # Parar áudio se movimento falhou
            self.audio_client.PlayStop("portuguese_audio")
            return False
    
    def run_test(self):
        """Executa o teste completo."""
        print("🎭 G1 TESTE MOVIMENTO + ÁUDIO WAV")
        print("=" * 50)
        
        if not self.initialize_sdk():
            return False
        
        if not self.setup_main_operation_control():
            return False
        
        if not self.setup_audio():
            return False
        
        return self.test_movement_with_wav()

def main():
    """Função principal."""
    print("🎭 G1 MOVIMENTO + ÁUDIO WAV - TESTE INTEGRADO")
    print("=" * 60)
    print("🎯 OBJETIVO: Testar movimento ID 32 + áudio WAV em português")
    print("📋 RECURSOS:")
    print("  - Movimento: ID 32 (mão na boca)")
    print("  - Áudio: WAV em português (simulado)")
    print("  - LEDs: Controle de cores")
    print("  - Volume: 100% (máximo)")
    
    response = input("\nDeseja continuar? (s/n): ").strip().lower()
    if response not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada")
        return
    
    tester = G1MovementWAVTest()
    
    if tester.run_test():
        print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
    else:
        print("\n❌ TESTE FALHOU")

if __name__ == "__main__":
    main()
