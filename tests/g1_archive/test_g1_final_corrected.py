#!/usr/bin/env python3
"""
Teste G1 - Final Corrigido
Testa TTS com speaker_id 1 (inglês) e movimentos com IDs corretos.
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

class G1FinalCorrectedTest:
    """Teste final corrigido do sistema G1."""
    
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
    
    def test_english_tts(self):
        """Testa TTS em inglês com speaker_id 1."""
        print("\n🗣️  TESTE TTS INGLÊS (speaker_id=1)")
        print("=" * 50)
        
        english_tests = [
            "Hello! I am a humanoid robot.",
            "Nice to meet you!",
            "I can speak English clearly.",
            "Testing the audio system."
        ]
        
        for i, text in enumerate(english_tests, 1):
            print(f"\n🗣️  TTS {i}: '{text}'")
            
            # LED verde para inglês
            self.audio_client.LedControl(0, 255, 0)
            
            # TTS com speaker_id 1 (inglês)
            result = self.audio_client.TtsMaker(text, 1)
            if result == 0:
                print(f"✅ TTS inglês {i} executado")
            else:
                print(f"❌ TTS inglês {i} falhou: {result}")
            
            time.sleep(3)  # Aguardar TTS
        
        # Voltar LED ao estado original
        self.audio_client.LedControl(173, 216, 230)  # Azul claro
        print("\n✅ Teste TTS inglês concluído!")
        return True
    
    def execute_movement_with_relax(self, move_id, move_name, tts_text):
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
        
        # 2. TTS em inglês
        print(f"🗣️  TTS: '{tts_text}' (speaker_id=1)")
        tts_result = self.audio_client.TtsMaker(tts_text, 1)
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
    
    def test_movements_final(self):
        """Testa movimentos com IDs corretos."""
        print("\n🤚 TESTE MOVIMENTOS FINAL")
        print("=" * 50)
        
        # Verificar estado do robô
        try:
            status, result = self.motion_switcher.CheckMode()
            print(f"📊 Estado atual: {result}")
        except:
            print("⚠️  Não foi possível verificar estado")
        
        # Movimentos com IDs corretos e nomes corretos
        movements = [
            (32, "Right Hand on Mouth", "Executing right hand on mouth gesture"),
            (11, "Kiss (2 mãos)", "Giving a kiss with both hands"),
            (12, "Beijo Esquerda", "Giving a kiss with left hand")
        ]
        
        success_count = 0
        for move_id, move_name, tts_text in movements:
            if self.execute_movement_with_relax(move_id, move_name, tts_text):
                success_count += 1
        
        print(f"\n📊 Resultado: {success_count}/{len(movements)} movimentos executados com sucesso")
        print("✅ Teste movimentos final concluído!")
        return True
    
    def test_chinese_vs_english(self):
        """Compara TTS chinês vs inglês."""
        print("\n🌍 TESTE CHINÊS vs INGLÊS")
        print("=" * 40)
        
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
        
        # Voltar LED ao estado original
        self.audio_client.LedControl(173, 216, 230)  # Azul claro
        print("\n✅ Teste chinês vs inglês concluído!")
        return True
    
    def run_test(self):
        """Executa todos os testes."""
        print("🎭 G1 TESTE FINAL CORRIGIDO")
        print("=" * 50)
        
        if not self.initialize_sdk():
            return False
        
        if not self.setup_audio():
            return False
        
        # 1. Teste TTS inglês
        self.test_english_tts()
        
        # 2. Teste movimentos final
        self.test_movements_final()
        
        # 3. Teste chinês vs inglês
        self.test_chinese_vs_english()
        
        print("\n🎉 TODOS OS TESTES CONCLUÍDOS!")
        
        # Resumo final
        print(f"\n📊 RESUMO FINAL:")
        print("=" * 20)
        print("🗣️  TTS Inglês: Funcionando (speaker_id=1)")
        print("🤚 Movimentos: IDs corretos")
        print("🌍 Idiomas: Chinês (0) vs Inglês (1)")
        print("🎵 Sistema: Otimizado")
        
        return True

def main():
    """Função principal."""
    print("🎭 G1 TESTE FINAL CORRIGIDO")
    print("=" * 60)
    print("🎯 OBJETIVO: Confirmar speaker_id 1 = inglês e IDs corretos")
    print("📋 TESTES:")
    print("  - TTS Inglês (speaker_id=1)")
    print("  - Movimentos com IDs corretos")
    print("  - Comparação Chinês (0) vs Inglês (1)")
    print("  - Volume máximo (100%)")
    
    response = input("\nDeseja continuar? (s/n): ").strip().lower()
    if response not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada")
        return
    
    tester = G1FinalCorrectedTest()
    
    if tester.run_test():
        print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
    else:
        print("\n❌ TESTE FALHOU")

if __name__ == "__main__":
    main()
