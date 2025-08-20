#!/usr/bin/env python3
"""
Teste G1 - Sistema Áudio Completo
Testa TTS, LEDs e movimento de forma clara e visível.
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

class G1AudioSystemTest:
    """Teste completo do sistema de áudio do G1."""
    
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
    
    def test_tts_sequence(self):
        """Teste sequência de TTS com feedback visual."""
        print("\n🗣️  TESTE SEQUÊNCIA TTS")
        print("=" * 40)
        
        messages = [
            "Teste número um",
            "Teste número dois", 
            "Teste número três",
            "Sistema funcionando"
        ]
        
        colors = [
            (255, 0, 0),    # Vermelho
            (0, 255, 0),    # Verde
            (0, 0, 255),    # Azul
            (255, 255, 0)   # Amarelo
        ]
        
        for i, (message, color) in enumerate(zip(messages, colors), 1):
            print(f"\n🗣️  TTS {i}: '{message}'")
            
            # LED indicando qual TTS está tocando
            self.audio_client.LedControl(color[0], color[1], color[2])
            
            # Executar TTS
            result = self.audio_client.TtsMaker(message, 0)
            if result == 0:
                print(f"✅ TTS {i} executado")
            else:
                print(f"❌ TTS {i} falhou: {result}")
            
            # Aguardar
            time.sleep(3)
        
        # Voltar LED ao estado original
        self.audio_client.LedControl(173, 216, 230)  # Azul claro
        print("\n✅ Sequência TTS concluída!")
        return True
    
    def test_movement_with_tts(self):
        """Testa movimento com TTS."""
        print("\n🤚 TESTE MOVIMENTO + TTS")
        print("=" * 40)
        
        # Verificar estado do robô
        try:
            status, result = self.motion_switcher.CheckMode()
            print(f"📊 Estado atual: {result}")
        except:
            print("⚠️  Não foi possível verificar estado")
        
        movements = [
            (32, "Mão na boca", "Executando mão na boca"),
            (11, "Acenar", "Acenando para você"),
            (99, "Relaxar", "Voltando ao estado relaxado")
        ]
        
        for move_id, move_name, tts_text in movements:
            print(f"\n🤚 Movimento: {move_name} (ID {move_id})")
            
            # TTS antes do movimento
            print(f"🗣️  TTS: '{tts_text}'")
            tts_result = self.audio_client.TtsMaker(tts_text, 0)
            if tts_result == 0:
                print("✅ TTS executado")
            else:
                print(f"❌ TTS falhou: {tts_result}")
            
            time.sleep(2)  # Aguardar TTS
            
            # Executar movimento
            print(f"🤚 Executando movimento {move_id}...")
            try:
                move_result = self.arm_client.ExecuteAction(move_id)
                if move_result == 0:
                    print(f"✅ Movimento {move_name} executado")
                else:
                    print(f"❌ Movimento {move_name} falhou: {move_result}")
            except Exception as e:
                print(f"❌ Erro no movimento: {e}")
            
            time.sleep(3)  # Aguardar movimento
        
        print("\n✅ Teste movimento + TTS concluído!")
    
    def test_visual_feedback(self):
        """Testa feedback visual com LEDs."""
        print("\n💡 TESTE FEEDBACK VISUAL")
        print("=" * 40)
        
        # Sequência de cores com TTS explicativo
        led_tests = [
            ((255, 0, 0), "LED vermelho ativado"),
            ((0, 255, 0), "LED verde ativado"),
            ((0, 0, 255), "LED azul ativado"),
            ((255, 255, 0), "LED amarelo ativado"),
            ((255, 0, 255), "LED magenta ativado"),
            ((0, 255, 255), "LED ciano ativado"),
            ((173, 216, 230), "Voltando ao estado original")
        ]
        
        for i, (color, description) in enumerate(led_tests, 1):
            print(f"\n💡 Teste {i}: {description}")
            
            # TTS
            tts_result = self.audio_client.TtsMaker(description, 0)
            if tts_result == 0:
                print("✅ TTS executado")
            
            # LED
            self.audio_client.LedControl(color[0], color[1], color[2])
            print(f"💡 LED: RGB({color[0]}, {color[1]}, {color[2]})")
            
            time.sleep(2)
        
        print("\n✅ Teste visual concluído!")
    
    def run_test(self):
        """Executa todos os testes."""
        print("🎭 G1 SISTEMA ÁUDIO COMPLETO")
        print("=" * 50)
        
        if not self.initialize_sdk():
            return False
        
        if not self.setup_audio():
            return False
        
        # 1. Teste sequência TTS
        self.test_tts_sequence()
        
        # 2. Teste movimento + TTS
        self.test_movement_with_tts()
        
        # 3. Teste feedback visual
        self.test_visual_feedback()
        
        print("\n🎉 TODOS OS TESTES CONCLUÍDOS!")
        
        # Resumo final
        print(f"\n📊 RESUMO FINAL:")
        print("=" * 20)
        print("🗣️  TTS: Testado")
        print("🤚 Movimentos: Testados")
        print("💡 LEDs: Testados")
        print("🎵 Sistema: Funcionando")
        
        return True

def main():
    """Função principal."""
    print("🎭 G1 SISTEMA ÁUDIO - TESTE COMPLETO")
    print("=" * 60)
    print("🎯 OBJETIVO: Testar sistema de áudio, TTS, movimento e LEDs")
    print("📋 TESTES:")
    print("  - Sequência TTS com feedback visual")
    print("  - Movimentos com narração TTS")
    print("  - Feedback visual colorido")
    print("  - Volume máximo (100%)")
    
    response = input("\nDeseja continuar? (s/n): ").strip().lower()
    if response not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada")
        return
    
    tester = G1AudioSystemTest()
    
    if tester.run_test():
        print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
    else:
        print("\n❌ TESTE FALHOU")

if __name__ == "__main__":
    main()
