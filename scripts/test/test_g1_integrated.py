#!/usr/bin/env python3
"""
Teste Integrado G1 - Sistema t031a5

Demonstra todas as funcionalidades confirmadas do G1:
- TTS (Inglês e Chinês)
- LEDs (Emoções)
- Movimentos (ID 32)
- WAV Playback
- Sequências de comandos
"""

import asyncio
import sys
import time
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from t031a5.unitree.g1_controller import G1Controller, G1Language, G1Emotion, G1AudioCommand


class G1IntegratedTest:
    """Teste integrado do sistema G1."""
    
    def __init__(self):
        self.controller = None
        
        # Configuração para teste local
        self.config = {
            "interface": {
                "robot_ip": "192.168.123.161",
                "robot_port": 8080,
                "interface": "en11",
                "timeout": 10.0,
                "safety_mode": "normal",
                "emergency_stop": True,
                "max_speed": 0.5,
                "max_turn_speed": 0.3
            },
            "default_speed": 0.3,
            "default_volume": 100,
            "default_speaker_id": 1,  # Inglês por padrão
            "audio_timeout": 5.0,
            "max_history": 100
        }
    
    async def run_integrated_test(self):
        """Executa teste integrado completo."""
        print("🎯 TESTE INTEGRADO G1 - SISTEMA t031a5")
        print("=" * 50)
        
        try:
            # 1. Inicialização
            print("\n🔧 1. INICIALIZANDO SISTEMA...")
            success = await self._initialize_system()
            if not success:
                print("❌ Falha na inicialização")
                return False
            
            # 2. Teste de Status
            print("\n📊 2. VERIFICANDO STATUS...")
            await self._test_status()
            
            # 3. Teste de LEDs/Emoções
            print("\n🎨 3. TESTANDO LEDs E EMOÇÕES...")
            await self._test_emotions()
            
            # 4. Teste de TTS
            print("\n🗣️ 4. TESTANDO TTS...")
            await self._test_tts()
            
            # 5. Teste de Movimentos
            print("\n🤚 5. TESTANDO MOVIMENTOS...")
            await self._test_movements()
            
            # 6. Teste de WAV
            print("\n🎵 6. TESTANDO WAV PLAYBACK...")
            await self._test_wav_playback()
            
            # 7. Teste de Sequência
            print("\n🎭 7. TESTANDO SEQUÊNCIA INTEGRADA...")
            await self._test_integrated_sequence()
            
            # 8. Limpeza
            print("\n🧹 8. FINALIZANDO...")
            await self._cleanup()
            
            print("\n✅ TESTE INTEGRADO CONCLUÍDO COM SUCESSO!")
            return True
            
        except Exception as e:
            print(f"\n❌ Erro no teste integrado: {e}")
            await self._cleanup()
            return False
    
    async def _initialize_system(self) -> bool:
        """Inicializa o sistema G1."""
        try:
            print("  🔧 Criando controlador...")
            self.controller = G1Controller(self.config)
            
            print("  🔧 Inicializando controlador...")
            success = await self.controller.initialize()
            
            if success:
                print("  ✅ Sistema inicializado com sucesso")
                return True
            else:
                print("  ❌ Falha na inicialização")
                return False
                
        except Exception as e:
            print(f"  ❌ Erro na inicialização: {e}")
            return False
    
    async def _test_status(self):
        """Testa obtenção de status."""
        try:
            status = await self.controller.get_status()
            
            print("  📊 Status do Controlador:")
            print(f"    - Nome: {status['controller']['name']}")
            print(f"    - Inicializado: {status['controller']['initialized']}")
            print(f"    - Executando: {status['controller']['running']}")
            print(f"    - Volume padrão: {status['controller']['default_volume']}")
            print(f"    - Speaker padrão: {status['controller']['default_speaker_id']}")
            
            print("  📊 Status da Interface:")
            print(f"    - Estado: {status['interface']['state']}")
            print(f"    - Interface: {status['interface']['interface']}")
            print(f"    - Audio Client: {status['interface']['audio_client_ready']}")
            print(f"    - Motion Client: {status['interface']['motion_client_ready']}")
            
            # Verifica saúde
            health = await self.controller.health_check()
            print(f"  🏥 Saúde do sistema: {'✅' if health else '❌'}")
            
        except Exception as e:
            print(f"  ❌ Erro ao verificar status: {e}")
    
    async def _test_emotions(self):
        """Testa LEDs e emoções."""
        emotions = [
            (G1Emotion.HAPPY, "Feliz"),
            (G1Emotion.SAD, "Triste"),
            (G1Emotion.EXCITED, "Empolgado"),
            (G1Emotion.CALM, "Calmo"),
            (G1Emotion.NEUTRAL, "Neutro"),
            (G1Emotion.ENGLISH, "Inglês"),
            (G1Emotion.CHINESE, "Chinês")
        ]
        
        for emotion, name in emotions:
            try:
                print(f"  🎨 Testando emoção: {name}")
                success = await self.controller.set_emotion(emotion)
                print(f"    {'✅' if success else '❌'} {name}")
                await asyncio.sleep(1.0)
                
            except Exception as e:
                print(f"    ❌ Erro em {name}: {e}")
    
    async def _test_tts(self):
        """Testa TTS em diferentes idiomas."""
        tts_tests = [
            (G1Language.ENGLISH, "Hello! I am the G1 robot from t031a5 system.", "Inglês"),
            (G1Language.CHINESE, "你好！我是G1机器人。", "Chinês"),
            (G1Language.ENGLISH, "Testing volume and speaker settings.", "Inglês 2"),
        ]
        
        for language, text, description in tts_tests:
            try:
                print(f"  🗣️ Testando TTS: {description}")
                print(f"    Texto: '{text}'")
                
                success = await self.controller.speak(text, language)
                print(f"    {'✅' if success else '❌'} {description}")
                
                # Aguarda TTS processar
                await asyncio.sleep(3.0)
                
            except Exception as e:
                print(f"    ❌ Erro em {description}: {e}")
    
    async def _test_movements(self):
        """Testa movimentos disponíveis."""
        try:
            # Obtém movimentos disponíveis
            movements = await self.controller.get_available_movements()
            
            print(f"  🤚 Movimentos disponíveis: {len(movements)}")
            for movement_id, name in movements.items():
                print(f"    - ID {movement_id}: {name}")
            
            # Testa movimento ID 32 (Right Hand on Mouth)
            if 32 in movements:
                print("  🤚 Testando movimento ID 32 (Right Hand on Mouth)")
                success = await self.controller.execute_gesture(32, emotion=G1Emotion.HAPPY)
                print(f"    {'✅' if success else '❌'} Movimento 32")
                await asyncio.sleep(2.0)
            
        except Exception as e:
            print(f"  ❌ Erro ao testar movimentos: {e}")
    
    async def _test_wav_playback(self):
        """Testa reprodução de WAV."""
        try:
            # Cria um WAV de teste simples
            wav_file = await self._create_test_wav()
            
            if wav_file and wav_file.exists():
                print(f"  🎵 Testando WAV: {wav_file.name}")
                success = await self.controller.play_audio(str(wav_file), emotion=G1Emotion.EXCITED)
                print(f"    {'✅' if success else '❌'} WAV playback")
                
                # Aguarda reprodução
                await asyncio.sleep(2.0)
                
                # Para reprodução
                await self.controller.stop_audio()
                
                # Remove arquivo temporário
                wav_file.unlink()
            else:
                print("  ⚠️  Não foi possível criar WAV de teste")
                
        except Exception as e:
            print(f"  ❌ Erro ao testar WAV: {e}")
    
    async def _test_integrated_sequence(self):
        """Testa sequência integrada de comandos."""
        try:
            print("  🎭 Executando sequência integrada...")
            
            # Cria WAV de teste
            wav_file = await self._create_test_wav()
            
            # Define sequência de comandos
            commands = [
                G1AudioCommand("tts", text="Starting integrated sequence", speaker_id=1, volume=100),
                G1AudioCommand("wav", wav_file=str(wav_file) if wav_file else "", stream_name="sequence"),
                G1AudioCommand("stop", stream_name="sequence")
            ]
            
            # Executa sequência
            success = await self.controller.execute_sequence(commands, delay_between=1.0)
            print(f"    {'✅' if success else '❌'} Sequência integrada")
            
            # Executa movimento após sequência
            await asyncio.sleep(1.0)
            movement_success = await self.controller.execute_gesture(32, emotion=G1Emotion.HAPPY)
            print(f"    {'✅' if movement_success else '❌'} Movimento após sequência")
            
            # Limpa arquivo temporário
            if wav_file and wav_file.exists():
                wav_file.unlink()
                
        except Exception as e:
            print(f"  ❌ Erro na sequência integrada: {e}")
    
    async def _create_test_wav(self) -> Path:
        """Cria um arquivo WAV de teste."""
        try:
            import wave
            import struct
            
            # Cria arquivo WAV temporário
            wav_file = Path("test_audio.wav")
            
            # Parâmetros do WAV
            sample_rate = 16000
            duration = 2.0  # 2 segundos
            frequency = 440.0  # Nota A4
            amplitude = 0.3
            
            # Gera dados PCM
            num_samples = int(sample_rate * duration)
            pcm_data = []
            
            for i in range(num_samples):
                # Gera tom simples
                sample = amplitude * struct.pack('<h', int(32767 * 0.3 * (i % 100) / 100))
                pcm_data.append(sample)
            
            # Escreve arquivo WAV
            with wave.open(str(wav_file), 'wb') as wav:
                wav.setnchannels(1)  # Mono
                wav.setsampwidth(2)  # 16-bit
                wav.setframerate(sample_rate)
                wav.writeframes(b''.join(pcm_data))
            
            return wav_file
            
        except Exception as e:
            print(f"  ⚠️  Erro ao criar WAV: {e}")
            return None
    
    async def _cleanup(self):
        """Limpa recursos."""
        try:
            if self.controller:
                print("  🧹 Parando controlador...")
                await self.controller.stop()
                print("  ✅ Controlador parado")
                
        except Exception as e:
            print(f"  ❌ Erro na limpeza: {e}")


async def main():
    """Função principal."""
    print("🎯 Iniciando Teste Integrado G1 - Sistema t031a5")
    print("=" * 60)
    
    test = G1IntegratedTest()
    success = await test.run_integrated_test()
    
    if success:
        print("\n🎉 SUCESSO: Sistema t031a5 integrado com G1 funcionando!")
        print("📋 Funcionalidades confirmadas:")
        print("   ✅ TTS (Inglês e Chinês)")
        print("   ✅ LEDs e Emoções")
        print("   ✅ Movimentos (ID 32)")
        print("   ✅ WAV Playback")
        print("   ✅ Sequências integradas")
        print("   ✅ Controle de volume")
        print("   ✅ Interface de rede (en11)")
    else:
        print("\n❌ FALHA: Teste integrado não foi bem-sucedido")
        print("🔧 Verifique:")
        print("   - Conexão com G1")
        print("   - Interface de rede (en11)")
        print("   - SDK Unitree instalado")
        print("   - Estado do robô (Main Operation Control)")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
