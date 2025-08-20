#!/usr/bin/env python3
"""
Investigação TTS G1 - Idioma, Speaker ID e Volume
Testa diferentes configurações de TTS para entender como funciona.
"""

import time
import sys
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.audio.g1_audio_client import AudioClient

class G1TTSInvestigation:
    """Investigação detalhada do TTS do G1."""
    
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
    
    def test_volume_levels(self):
        """Testa diferentes níveis de volume."""
        print("\n🔊 TESTE DE VOLUMES")
        print("=" * 40)
        
        volumes = [30, 50, 70, 85, 100]
        
        for volume in volumes:
            print(f"\n📊 Configurando volume: {volume}%")
            result = self.audio_client.SetVolume(volume)
            
            if result == 0:
                print(f"✅ Volume {volume}% configurado")
                
                # Verificar volume atual
                vol_code, vol_data = self.audio_client.GetVolume()
                if vol_code == 0:
                    print(f"📊 Volume confirmado: {vol_data}")
                
                # Teste TTS com este volume
                test_text = f"Teste de volume {volume} por cento"
                print(f"🗣️  TTS: '{test_text}'")
                
                tts_result = self.audio_client.TtsMaker(test_text, 0)
                if tts_result == 0:
                    print("✅ TTS executado")
                else:
                    print(f"❌ TTS falhou: {tts_result}")
                
                time.sleep(3)  # Aguardar TTS
            else:
                print(f"❌ Falha ao configurar volume {volume}%: {result}")
    
    def test_speaker_ids(self):
        """Testa diferentes speaker_id."""
        print("\n🎭 TESTE DE SPEAKER ID")
        print("=" * 40)
        
        # Configurar volume alto para teste
        self.audio_client.SetVolume(85)
        
        speaker_ids = [0, 1, 2, 3, 10, 100]
        test_text = "Teste de speaker ID"
        
        for speaker_id in speaker_ids:
            print(f"\n🎭 Testando speaker_id: {speaker_id}")
            print(f"🗣️  TTS: '{test_text}' (speaker_id={speaker_id})")
            
            tts_result = self.audio_client.TtsMaker(test_text, speaker_id)
            if tts_result == 0:
                print(f"✅ TTS com speaker_id {speaker_id} executado")
            else:
                print(f"❌ TTS com speaker_id {speaker_id} falhou: {tts_result}")
            
            time.sleep(3)  # Aguardar TTS
    
    def test_languages(self):
        """Testa diferentes idiomas."""
        print("\n🌍 TESTE DE IDIOMAS")
        print("=" * 40)
        
        # Configurar volume alto
        self.audio_client.SetVolume(85)
        
        # Testes em diferentes idiomas
        language_tests = [
            ("Português", "Olá! Como você está? Teste de português."),
            ("English", "Hello! How are you? English test."),
            ("Español", "¡Hola! ¿Cómo estás? Prueba en español."),
            ("Français", "Bonjour! Comment allez-vous? Test en français."),
            ("Deutsch", "Hallo! Wie geht es dir? Deutsch Test."),
            ("中文", "你好！你好吗？中文测试。"),
            ("日本語", "こんにちは！お元気ですか？日本語テスト。"),
            ("한국어", "안녕하세요! 어떻게 지내세요? 한국어 테스트."),
        ]
        
        for lang_name, text in language_tests:
            print(f"\n🌍 Testando: {lang_name}")
            print(f"🗣️  TTS: '{text}'")
            
            tts_result = self.audio_client.TtsMaker(text, 0)
            if tts_result == 0:
                print(f"✅ TTS em {lang_name} executado")
            else:
                print(f"❌ TTS em {lang_name} falhou: {tts_result}")
            
            time.sleep(4)  # Aguardar TTS
    
    def test_tts_timing(self):
        """Testa timing do TTS."""
        print("\n⏱️  TESTE DE TIMING")
        print("=" * 40)
        
        # Configurar volume alto
        self.audio_client.SetVolume(85)
        
        print("🗣️  TTS 1: 'Primeira mensagem'")
        start_time = time.time()
        result1 = self.audio_client.TtsMaker("Primeira mensagem", 0)
        tts1_time = time.time() - start_time
        print(f"⏱️  Tempo para iniciar TTS 1: {tts1_time:.2f}s")
        
        time.sleep(2)
        
        print("🗣️  TTS 2: 'Segunda mensagem'")
        start_time = time.time()
        result2 = self.audio_client.TtsMaker("Segunda mensagem", 0)
        tts2_time = time.time() - start_time
        print(f"⏱️  Tempo para iniciar TTS 2: {tts2_time:.2f}s")
        
        time.sleep(2)
        
        print("🗣️  TTS 3: 'Terceira mensagem'")
        start_time = time.time()
        result3 = self.audio_client.TtsMaker("Terceira mensagem", 0)
        tts3_time = time.time() - start_time
        print(f"⏱️  Tempo para iniciar TTS 3: {tts3_time:.2f}s")
        
        print(f"\n📊 Resultados:")
        print(f"  TTS 1: {result1} (tempo: {tts1_time:.2f}s)")
        print(f"  TTS 2: {result2} (tempo: {tts2_time:.2f}s)")
        print(f"  TTS 3: {result3} (tempo: {tts3_time:.2f}s)")
    
    def test_led_with_tts(self):
        """Testa LEDs com TTS."""
        print("\n💡 TESTE LED + TTS")
        print("=" * 40)
        
        # Configurar volume alto
        self.audio_client.SetVolume(85)
        
        print("🗣️  TTS: 'Testando LEDs com áudio'")
        tts_result = self.audio_client.TtsMaker("Testando LEDs com áudio", 0)
        
        if tts_result == 0:
            print("✅ TTS iniciado")
            
            # LEDs durante TTS
            print("💡 LED Vermelho")
            self.audio_client.LedControl(255, 0, 0)
            time.sleep(1)
            
            print("💡 LED Verde")
            self.audio_client.LedControl(0, 255, 0)
            time.sleep(1)
            
            print("💡 LED Azul")
            self.audio_client.LedControl(0, 0, 255)
            time.sleep(1)
            
            print("💡 LED Azul Claro (estado original)")
            self.audio_client.LedControl(173, 216, 230)
            
            print("✅ LEDs testados durante TTS")
        else:
            print(f"❌ TTS falhou: {tts_result}")
    
    def run_investigation(self):
        """Executa toda a investigação."""
        print("🔍 INVESTIGAÇÃO TTS G1")
        print("=" * 60)
        print("🎯 OBJETIVO: Entender TTS, idiomas, speaker_id e volume")
        
        if not self.initialize_sdk():
            return False
        
        # 1. Teste de volumes
        self.test_volume_levels()
        
        # 2. Teste de speaker_id
        self.test_speaker_ids()
        
        # 3. Teste de idiomas
        self.test_languages()
        
        # 4. Teste de timing
        self.test_tts_timing()
        
        # 5. Teste LED + TTS
        self.test_led_with_tts()
        
        print("\n🎉 INVESTIGAÇÃO CONCLUÍDA!")
        return True

def main():
    """Função principal."""
    print("🔍 G1 TTS INVESTIGATION")
    print("=" * 60)
    print("📋 TESTES:")
    print("  - Volumes: 30%, 50%, 70%, 85%, 100%")
    print("  - Speaker IDs: 0, 1, 2, 3, 10, 100")
    print("  - Idiomas: PT, EN, ES, FR, DE, ZH, JP, KR")
    print("  - Timing: Múltiplos TTS")
    print("  - LEDs: Durante TTS")
    
    response = input("\nDeseja continuar? (s/n): ").strip().lower()
    if response not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada")
        return
    
    investigator = G1TTSInvestigation()
    
    if investigator.run_investigation():
        print("\n🎉 INVESTIGAÇÃO CONCLUÍDA COM SUCESSO!")
    else:
        print("\n❌ INVESTIGAÇÃO FALHOU")

if __name__ == "__main__":
    main()
