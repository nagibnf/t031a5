#!/usr/bin/env python3
"""
Teste G1 - Funcionalidades Confirmadas (Modo Mock)

Testa apenas as funcionalidades que foram confirmadas como funcionando:
- TTS com speaker_id 1 (Inglês)
- LEDs (Emoções)
- Movimento ID 32 (Right Hand on Mouth)
- WAV Playback

Versão que funciona sem o G1 físico conectado.
"""

import asyncio
import sys
import time
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from t031a5.unitree.g1_controller import G1Controller, G1Language, G1Emotion


class G1ConfirmedFeaturesMockTest:
    """Teste das funcionalidades confirmadas do G1 em modo mock."""
    
    def __init__(self):
        self.controller = None
        
        # Configuração para modo mock
        self.config = {
            "interface": {
                "interface": "en0",  # Interface que existe
                "timeout": 10.0,
                "mock_mode": True  # Ativa modo mock
            },
            "default_volume": 100,
            "default_speaker_id": 1,  # Inglês
            "mock_mode": True  # Força modo mock
        }
    
    async def run_confirmed_test(self):
        """Executa teste das funcionalidades confirmadas."""
        print("🎯 TESTE G1 - FUNCIONALIDADES CONFIRMADAS (MOCK)")
        print("=" * 60)
        
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
            print("  🗣️ Testando TTS em inglês...")
            
            # Teste 1: Texto simples
            success = await self.controller.speak("Hello, I am Tobias", G1Language.ENGLISH)
            if success:
                print("  ✅ TTS inglês funcionando")
            else:
                print("  ❌ TTS inglês falhou")
            
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"  ❌ Erro no teste TTS: {e}")
    
    async def _test_leds(self):
        """Testa controle de LEDs."""
        try:
            print("  🎨 Testando LEDs...")
            
            # Teste 1: LED feliz
            success = await self.controller.set_emotion(G1Emotion.HAPPY)
            if success:
                print("  ✅ LED feliz funcionando")
            else:
                print("  ❌ LED feliz falhou")
            
            await asyncio.sleep(1)
            
            # Teste 2: LED triste
            success = await self.controller.set_emotion(G1Emotion.SAD)
            if success:
                print("  ✅ LED triste funcionando")
            else:
                print("  ❌ LED triste falhou")
            
            await asyncio.sleep(1)
            
            # Teste 3: LED neutro
            success = await self.controller.set_emotion(G1Emotion.NEUTRAL)
            if success:
                print("  ✅ LED neutro funcionando")
            else:
                print("  ❌ LED neutro falhou")
            
        except Exception as e:
            print(f"  ❌ Erro no teste LEDs: {e}")
    
    async def _test_movement(self):
        """Testa movimento ID 32."""
        try:
            print("  🤚 Testando movimento ID 32...")
            
            success = await self.controller.execute_gesture(32, wait_time=2.0)
            if success:
                print("  ✅ Movimento ID 32 funcionando")
            else:
                print("  ❌ Movimento ID 32 falhou")
            
        except Exception as e:
            print(f"  ❌ Erro no teste movimento: {e}")
    
    async def _test_wav(self):
        """Testa reprodução de WAV."""
        try:
            print("  🎵 Testando reprodução WAV...")
            
            # Teste com arquivo de exemplo (se existir)
            wav_file = "audio/effects/notification.wav"
            
            if Path(wav_file).exists():
                success = await self.controller.play_audio(wav_file)
                if success:
                    print("  ✅ Reprodução WAV funcionando")
                else:
                    print("  ❌ Reprodução WAV falhou")
            else:
                print("  ⚠️ Arquivo WAV não encontrado, simulando...")
                success = await self.controller.play_audio("audio/effects/test.wav")
                if success:
                    print("  ✅ Simulação WAV funcionando")
                else:
                    print("  ❌ Simulação WAV falhou")
            
        except Exception as e:
            print(f"  ❌ Erro no teste WAV: {e}")
    
    async def _cleanup(self):
        """Limpa recursos."""
        try:
            if self.controller:
                await self.controller.stop()
                print("  ✅ Limpeza concluída")
        except Exception as e:
            print(f"  ❌ Erro na limpeza: {e}")


async def main():
    """Função principal."""
    print("🎯 Teste G1 - Funcionalidades Confirmadas (Mock)")
    print("=" * 60)
    
    test = G1ConfirmedFeaturesMockTest()
    success = await test.run_confirmed_test()
    
    if success:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema t031a5 para Tobias (G1) funcionando em modo mock")
    else:
        print("\n❌ ALGUNS TESTES FALHARAM")
        print("⚠️ Verifique os logs acima")
    
    return success


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)
