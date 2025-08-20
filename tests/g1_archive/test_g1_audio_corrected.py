#!/usr/bin/env python3
"""
Teste G1 - Sistema Áudio Corrigido
Testa TTS com speaker_id para inglês e movimentos com relaxamento.
"""

import time
import sys
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.audio.g1_audio_client import AudioClient
from unitree_sdk2py.g1.arm.g1_arm_action_client import G1ArmActionClient
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient
from unitree_sdk2py.comm.motion_switcher.motion_switcher_client import MotionSwitcherClient

class G1AudioCorrectedTest:
    """Teste corrigido do sistema de áudio do G1."""
    
    def __init__(self):
        self.interface = "en11"
        self.audio_client = None
        self.arm_client = None
        self.loco_client = None
        self.motion_switcher = None
        
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
            
            self.loco_client = LocoClient()
            self.loco_client.SetTimeout(5.0)
            self.loco_client.Init()
            print("✅ LocoClient inicializado")
            
            self.motion_switcher = MotionSwitcherClient()
            self.motion_switcher.SetTimeout(5.0)
            self.motion_switcher.Init()
            print("✅ MotionSwitcherClient inicializado")
            
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
    
    def test_speaker_ids(self):
        """Testa diferentes speaker_id para encontrar inglês."""
        print("\n🎭 TESTE SPEAKER ID")
        print("=" * 40)
        
        # Testar diferentes speaker_id
        speaker_tests = [
            (0, "Hello! This is test number one."),
            (1, "Hello! This is test number two."),
            (2, "Hello! This is test number three."),
            (3, "Hello! This is test number four."),
            (10, "Hello! This is test number five."),
            (100, "Hello! This is test number six.")
        ]
        
        for speaker_id, text in speaker_tests:
            print(f"\n🎭 Testando speaker_id: {speaker_id}")
            print(f"🗣️  TTS: '{text}'")
            
            # LED indicando qual speaker_id está sendo testado
            if speaker_id == 0:
                self.audio_client.LedControl(255, 0, 0)  # Vermelho
            elif speaker_id == 1:
                self.audio_client.LedControl(0, 255, 0)  # Verde
            elif speaker_id == 2:
                self.audio_client.LedControl(0, 0, 255)  # Azul
            elif speaker_id == 3:
                self.audio_client.LedControl(255, 255, 0)  # Amarelo
            elif speaker_id == 10:
                self.audio_client.LedControl(255, 0, 255)  # Magenta
            else:
                self.audio_client.LedControl(0, 255, 255)  # Ciano
            
            # Executar TTS
            result = self.audio_client.TtsMaker(text, speaker_id)
            if result == 0:
                print(f"✅ TTS com speaker_id {speaker_id} executado")
            else:
                print(f"❌ TTS com speaker_id {speaker_id} falhou: {result}")
            
            time.sleep(4)  # Aguardar TTS
        
        # Voltar LED ao estado original
        self.audio_client.LedControl(173, 216, 230)  # Azul claro
        print("\n✅ Teste speaker_id concluído!")
        return True
    
    def execute_movement_with_relax(self, move_id, move_name, tts_text, speaker_id=0):
        """Executa movimento com relaxamento antes e depois."""
        print(f"\n🤚 Movimento: {move_name} (ID {move_id})")
        
        # 1. Relaxar primeiro
        print("🔄 Relaxando braços...")
        try:
            relax_result = self.arm_client.ExecuteAction(99)  # release_arm
            if relax_result == 0:
                print("✅ Braços relaxados")
            else:
                print(f"⚠️  Falha ao relaxar: {relax_result}")
        except Exception as e:
            print(f"⚠️  Erro ao relaxar: {e}")
        
        time.sleep(2)  # Aguardar relaxamento
        
        # 2. TTS
        print(f"🗣️  TTS: '{tts_text}' (speaker_id={speaker_id})")
        tts_result = self.audio_client.TtsMaker(tts_text, speaker_id)
        if tts_result == 0:
            print("✅ TTS executado")
        else:
            print(f"❌ TTS falhou: {tts_result}")
        
        time.sleep(2)  # Aguardar TTS
        
        # 3. Executar movimento
        print(f"🤚 Executando movimento {move_id}...")
        try:
            move_result = self.arm_client.ExecuteAction(move_id)
            if move_result == 0:
                print(f"✅ Movimento {move_name} executado")
            else:
                print(f"❌ Movimento {move_name} falhou: {move_result}")
                return False
        except Exception as e:
            print(f"❌ Erro no movimento: {e}")
            return False
        
        time.sleep(3)  # Aguardar movimento
        
        # 4. Relaxar novamente
        print("🔄 Relaxando novamente...")
        try:
            relax_result = self.arm_client.ExecuteAction(99)  # release_arm
            if relax_result == 0:
                print("✅ Braços relaxados novamente")
            else:
                print(f"⚠️  Falha ao relaxar: {relax_result}")
        except Exception as e:
            print(f"⚠️  Erro ao relaxar: {e}")
        
        time.sleep(2)  # Aguardar relaxamento
        
        return True
    
    def test_movements_corrected(self):
        """Testa movimentos com relaxamento entre eles."""
        print("\n🤚 TESTE MOVIMENTOS CORRIGIDO")
        print("=" * 50)
        
        # Verificar estado do robô
        try:
            status, result = self.motion_switcher.CheckMode()
            print(f"📊 Estado atual: {result}")
        except:
            print("⚠️  Não foi possível verificar estado")
        
        # Testar com speaker_id 1 (possível inglês)
        movements = [
            (32, "Mão na boca", "Executing hand to mouth gesture", 1),
            (11, "Acenar", "Waving hello to you", 1),
            (12, "Aplaudir", "Clapping hands", 1)
        ]
        
        success_count = 0
        for move_id, move_name, tts_text, speaker_id in movements:
            if self.execute_movement_with_relax(move_id, move_name, tts_text, speaker_id):
                success_count += 1
        
        print(f"\n📊 Resultado: {success_count}/{len(movements)} movimentos executados com sucesso")
        print("✅ Teste movimentos corrigido concluído!")
        return True
    
    def test_english_vs_chinese(self):
        """Compara TTS em inglês vs chinês."""
        print("\n🌍 TESTE INGLÊS vs CHINÊS")
        print("=" * 40)
        
        # Teste em inglês com speaker_id 1
        print("\n🗣️  Teste em Inglês (speaker_id=1):")
        english_text = "Hello! I am a humanoid robot. Nice to meet you!"
        print(f"📝 Texto: '{english_text}'")
        
        self.audio_client.LedControl(0, 255, 0)  # Verde para inglês
        tts_result = self.audio_client.TtsMaker(english_text, 1)
        if tts_result == 0:
            print("✅ TTS inglês executado")
        else:
            print(f"❌ TTS inglês falhou: {tts_result}")
        
        time.sleep(4)
        
        # Teste em chinês com speaker_id 0
        print("\n🗣️  Teste em Chinês (speaker_id=0):")
        chinese_text = "你好！我是人形机器人。很高兴认识你！"
        print(f"📝 Texto: '{chinese_text}'")
        
        self.audio_client.LedControl(255, 0, 0)  # Vermelho para chinês
        tts_result = self.audio_client.TtsMaker(chinese_text, 0)
        if tts_result == 0:
            print("✅ TTS chinês executado")
        else:
            print(f"❌ TTS chinês falhou: {tts_result}")
        
        time.sleep(4)
        
        # Voltar LED ao estado original
        self.audio_client.LedControl(173, 216, 230)  # Azul claro
        print("\n✅ Teste inglês vs chinês concluído!")
        return True
    
    def run_test(self):
        """Executa todos os testes."""
        print("🎭 G1 SISTEMA ÁUDIO CORRIGIDO")
        print("=" * 50)
        
        if not self.initialize_sdk():
            return False
        
        if not self.setup_audio():
            return False
        
        # 1. Teste speaker_id
        self.test_speaker_ids()
        
        # 2. Teste movimentos corrigido
        self.test_movements_corrected()
        
        # 3. Teste inglês vs chinês
        self.test_english_vs_chinese()
        
        print("\n🎉 TODOS OS TESTES CONCLUÍDOS!")
        
        # Resumo final
        print(f"\n📊 RESUMO FINAL:")
        print("=" * 20)
        print("🎭 Speaker ID: Testado")
        print("🤚 Movimentos: Corrigidos")
        print("🌍 Idiomas: Comparados")
        print("🎵 Sistema: Otimizado")
        
        return True

def main():
    """Função principal."""
    print("🎭 G1 SISTEMA ÁUDIO CORRIGIDO")
    print("=" * 60)
    print("🎯 OBJETIVO: Testar speaker_id para inglês e corrigir movimentos")
    print("📋 TESTES:")
    print("  - Speaker ID (0, 1, 2, 3, 10, 100)")
    print("  - Movimentos com relaxamento")
    print("  - Comparação inglês vs chinês")
    print("  - Volume máximo (100%)")
    
    response = input("\nDeseja continuar? (s/n): ").strip().lower()
    if response not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada")
        return
    
    tester = G1AudioCorrectedTest()
    
    if tester.run_test():
        print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
    else:
        print("\n❌ TESTE FALHOU")

if __name__ == "__main__":
    main()
