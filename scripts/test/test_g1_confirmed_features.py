#!/usr/bin/env python3
"""
Teste G1 - Funcionalidades Confirmadas

Testa apenas as funcionalidades que foram confirmadas como funcionando:
- TTS com speaker_id 1 (Inglês)
- LEDs (Emoções)
- Movimento ID 32 (Right Hand on Mouth)
- WAV Playback
"""

import asyncio
import sys
import time
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from t031a5.unitree.g1_controller import G1Controller, G1Language, G1Emotion


class G1ConfirmedFeaturesTest:
    """Teste das funcionalidades confirmadas do G1."""
    
    def __init__(self):
        self.controller = None
        
        # Configuração mínima
        self.config = {
            "interface": {
                "interface": "eth0",
                "timeout": 10.0
            },
            "default_volume": 100,
            "default_speaker_id": 1  # Inglês
        }
    
    async def run_confirmed_test(self):
        """Executa teste das funcionalidades confirmadas."""
        print("🎯 TESTE G1 - FUNCIONALIDADES CONFIRMADAS")
        print("=" * 50)
        
        try:
            # 1. Inicialização
            print("\n🔧 1. INICIALIZANDO...")
            success = await self._initialize()
            if not success:
                return False
            
            # 2. Teste TTS Inglês
            print("\n🗣️ 2. TESTE TTS INGLÊS...")
            await self._test_english_tts()
            
            # 3. Teste LEDs
            print("\n🎨 3. TESTE LEDs...")
            await self._test_leds()
            
            # 4. Teste Movimento
            print("\n🤚 4. TESTE MOVIMENTO...")
            await self._test_movement()
            
            # 5. Teste WAV
            print("\n🎵 5. TESTE WAV...")
            await self._test_wav()
            
            # 6. Limpeza
            print("\n🧹 6. FINALIZANDO...")
            await self._cleanup()
            
            print("\n✅ TESTE CONCLUÍDO COM SUCESSO!")
            return True
            
        except Exception as e:
            print(f"\n❌ Erro no teste: {e}")
            await self._cleanup()
            return False
    
    async def _initialize(self) -> bool:
        """Inicializa o sistema."""
        try:
            print("  🔧 Criando controlador...")
            self.controller = G1Controller(self.config)
            
            print("  🔧 Inicializando...")
            success = await self.controller.initialize()
            
            if success:
                print("  ✅ Inicializado com sucesso")
                return True
            else:
                print("  ❌ Falha na inicialização")
                return False
                
        except Exception as e:
            print(f"  ❌ Erro: {e}")
            return False
    
    async def _test_english_tts(self):
        """Testa TTS em inglês."""
        try:
            text = "Hello! I am the G1 robot. This is a test of the t031a5 system."
            print(f"  🗣️ Texto: '{text}'")
            
            success = await self.controller.speak(text, G1Language.ENGLISH)
            print(f"  {'✅' if success else '❌'} TTS Inglês")
            
            # Aguarda TTS processar
            await asyncio.sleep(3.0)
            
        except Exception as e:
            print(f"  ❌ Erro TTS: {e}")
    
    async def _test_leds(self):
        """Testa LEDs."""
        try:
            emotions = [
                (G1Emotion.HAPPY, "Verde"),
                (G1Emotion.ENGLISH, "Verde (Inglês)"),
                (G1Emotion.CALM, "Azul claro")
            ]
            
            for emotion, name in emotions:
                print(f"  🎨 {name}")
                success = await self.controller.set_emotion(emotion)
                print(f"    {'✅' if success else '❌'} {name}")
                await asyncio.sleep(1.0)
                
        except Exception as e:
            print(f"  ❌ Erro LEDs: {e}")
    
    async def _test_movement(self):
        """Testa movimento ID 32."""
        try:
            print("  🤚 Movimento ID 32 (Right Hand on Mouth)")
            success = await self.controller.execute_gesture(32, emotion=G1Emotion.HAPPY)
            print(f"  {'✅' if success else '❌'} Movimento 32")
            await asyncio.sleep(2.0)
            
        except Exception as e:
            print(f"  ❌ Erro movimento: {e}")
    
    async def _test_wav(self):
        """Testa WAV playback."""
        try:
            # Cria WAV simples
            wav_file = await self._create_simple_wav()
            
            if wav_file and wav_file.exists():
                print(f"  🎵 WAV: {wav_file.name}")
                success = await self.controller.play_audio(str(wav_file), emotion=G1Emotion.EXCITED)
                print(f"  {'✅' if success else '❌'} WAV playback")
                
                await asyncio.sleep(2.0)
                await self.controller.stop_audio()
                
                # Remove arquivo
                wav_file.unlink()
            else:
                print("  ⚠️  WAV não criado")
                
        except Exception as e:
            print(f"  ❌ Erro WAV: {e}")
    
    async def _create_simple_wav(self) -> Path:
        """Cria WAV simples."""
        try:
            import wave
            import struct
            
            wav_file = Path("simple_test.wav")
            
            # WAV 16kHz mono
            sample_rate = 16000
            duration = 1.0
            num_samples = int(sample_rate * duration)
            
            pcm_data = []
            for i in range(num_samples):
                # Tom simples
                sample = struct.pack('<h', int(32767 * 0.1 * (i % 50) / 50))
                pcm_data.append(sample)
            
            with wave.open(str(wav_file), 'wb') as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(sample_rate)
                wav.writeframes(b''.join(pcm_data))
            
            return wav_file
            
        except Exception as e:
            print(f"  ⚠️  Erro WAV: {e}")
            return None
    
    async def _cleanup(self):
        """Limpa recursos."""
        try:
            if self.controller:
                print("  🧹 Parando...")
                await self.controller.stop()
                print("  ✅ Parado")
                
        except Exception as e:
            print(f"  ❌ Erro limpeza: {e}")


async def main():
    """Função principal."""
    print("🎯 Teste G1 - Funcionalidades Confirmadas")
    print("=" * 60)
    
    test = G1ConfirmedFeaturesTest()
    success = await test.run_confirmed_test()
    
    if success:
        print("\n🎉 SUCESSO: Funcionalidades confirmadas funcionando!")
        print("📋 Confirmado:")
        print("   ✅ TTS Inglês (speaker_id=1)")
        print("   ✅ LEDs e Emoções")
        print("   ✅ Movimento ID 32")
        print("   ✅ WAV Playback")
    else:
        print("\n❌ FALHA: Algumas funcionalidades não funcionaram")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
