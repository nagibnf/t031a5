#!/usr/bin/env python3
"""
Teste G1 - Movimento + Áudio
Executa movimento ID 32 (mão na boca) e toca áudio simultaneamente.
"""

import time
import sys
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.arm.g1_arm_action_client import G1ArmActionClient
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient
from unitree_sdk2py.g1.audio.g1_audio_client import AudioClient
from unitree_sdk2py.comm.motion_switcher.motion_switcher_client import MotionSwitcherClient

class G1MovementAudioTest:
    """Teste de movimento + áudio no G1."""
    
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
    
    def test_tts(self, text="Olá! Executando movimento de mão na boca."):
        """Testa TTS (Text-to-Speech)."""
        try:
            print(f"🗣️  Executando TTS: '{text}'")
            result = self.audio_client.TtsMaker(text, 0)  # speaker_id = 0
            
            if result == 0:
                print("✅ TTS executado com sucesso!")
                return True
            else:
                print(f"❌ TTS falhou (código: {result})")
                return False
        except Exception as e:
            print(f"❌ Erro no TTS: {e}")
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
    
    def test_movement_with_audio(self):
        """Teste principal: movimento + áudio."""
        print("🎭 TESTE MOVIMENTO + ÁUDIO")
        print("=" * 50)
        
        # 1. Configurar áudio
        if not self.setup_audio():
            return False
        
        # 2. Executar movimento primeiro (sem áudio)
        print("\n🤚 Executando movimento ID 32...")
        movement_result = self.execute_movement_32()
        
        if movement_result:
            print("✅ Movimento executado!")
            
            # Aguardar conclusão do movimento
            print("⏳ Aguardando conclusão do movimento...")
            time.sleep(3)
            
            # 3. TTS apenas no final (com aguardo para processamento)
            print("\n🗣️  TTS no final do movimento")
            tts_result = self.test_tts("Movimento concluído! Agora testando os LEDs.")
            
            # Aguardar TTS processar (TTS é assíncrono)
            print("⏳ Aguardando TTS processar...")
            time.sleep(5)
            
            # 4. LEDs + TTS
            print("\n💡 Teste LEDs")
            self.test_led_effects()
            
            # 5. Voltar ao estado inicial
            time.sleep(2)
            self.release_arm()
            
            # 6. TTS final (com aguardo)
            self.test_tts("Teste concluído com sucesso!")
            time.sleep(3)  # Aguardar TTS final
            
            return True
        else:
            print("❌ Falha no movimento")
            return False
    
    def run_test(self):
        """Executa o teste completo."""
        print("🎭 G1 TESTE MOVIMENTO + ÁUDIO")
        print("=" * 50)
        
        if not self.initialize_sdk():
            return False
        
        if not self.setup_main_operation_control():
            return False
        
        return self.test_movement_with_audio()

def main():
    """Função principal."""
    print("🎭 G1 MOVIMENTO + ÁUDIO - TESTE INTEGRADO")
    print("=" * 60)
    print("🎯 OBJETIVO: Testar movimento ID 32 + TTS + LEDs")
    print("📋 RECURSOS:")
    print("  - Movimento: ID 32 (mão na boca)")
    print("  - Áudio: TTS nativo do G1")
    print("  - LEDs: Controle de cores")
    
    response = input("Deseja continuar? (s/n): ").strip().lower()
    if response not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada")
        return
    
    tester = G1MovementAudioTest()
    
    if tester.run_test():
        print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
    else:
        print("\n❌ TESTE FALHOU")

if __name__ == "__main__":
    main()
