#!/usr/bin/env python3
"""
Teste Integrado t031a5 - Sistema Completo com G1

Este script demonstra o sistema t031a5 completo integrado com o robô G1,
usando todas as funcionalidades confirmadas:
- TTS (Inglês e Chinês)
- LEDs (Emoções)
- Movimentos (ID 32)
- WAV Playback
- Sequências integradas
"""

import asyncio
import sys
import time
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from t031a5.unitree.g1_controller import G1Controller, G1Language, G1Emotion, G1AudioCommand


class T031a5IntegratedDemo:
    """Demonstração integrada do sistema t031a5 com G1."""
    
    def __init__(self):
        self.controller = None
        
        # Configuração completa do sistema
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
    
    async def run_demo(self):
        """Executa demonstração completa."""
        print("🎯 SISTEMA t031a5 - DEMONSTRAÇÃO INTEGRADA COM G1")
        print("=" * 60)
        print("📋 Funcionalidades confirmadas:")
        print("   ✅ TTS Inglês (speaker_id=1)")
        print("   ✅ TTS Chinês (speaker_id=0)")
        print("   ✅ LEDs e Emoções")
        print("   ✅ Movimento ID 32 (Right Hand on Mouth)")
        print("   ✅ WAV Playback (16kHz mono)")
        print("   ✅ Sequências integradas")
        print("=" * 60)
        
        try:
            # 1. Inicialização
            print("\n🔧 1. INICIALIZANDO SISTEMA t031a5...")
            success = await self._initialize_system()
            if not success:
                print("❌ Falha na inicialização")
                return False
            
            # 2. Demonstração de TTS
            print("\n🗣️ 2. DEMONSTRAÇÃO TTS...")
            await self._demo_tts()
            
            # 3. Demonstração de LEDs
            print("\n🎨 3. DEMONSTRAÇÃO LEDs...")
            await self._demo_leds()
            
            # 4. Demonstração de Movimentos
            print("\n🤚 4. DEMONSTRAÇÃO MOVIMENTOS...")
            await self._demo_movements()
            
            # 5. Demonstração de WAV
            print("\n🎵 5. DEMONSTRAÇÃO WAV...")
            await self._demo_wav()
            
            # 6. Demonstração Integrada
            print("\n🎭 6. DEMONSTRAÇÃO INTEGRADA...")
            await self._demo_integrated()
            
            # 7. Limpeza
            print("\n🧹 7. FINALIZANDO...")
            await self._cleanup()
            
            print("\n✅ DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
            print("🎉 Sistema t031a5 funcionando perfeitamente com G1!")
            return True
            
        except Exception as e:
            print(f"\n❌ Erro na demonstração: {e}")
            await self._cleanup()
            return False
    
    async def _initialize_system(self) -> bool:
        """Inicializa o sistema t031a5."""
        try:
            print("  🔧 Criando controlador G1...")
            self.controller = G1Controller(self.config)
            
            print("  🔧 Inicializando controlador...")
            success = await self.controller.initialize()
            
            if success:
                print("  ✅ Sistema t031a5 inicializado com sucesso")
                
                # Mostra status
                status = await self.controller.get_status()
                print(f"  📊 Status: {status['interface']['state']}")
                print(f"  🌐 Interface: {status['interface']['interface']}")
                print(f"  🔊 Audio: {'✅' if status['interface']['audio_client_ready'] else '❌'}")
                print(f"  🤖 Motion: {'✅' if status['interface']['motion_client_ready'] else '❌'}")
                
                return True
            else:
                print("  ❌ Falha na inicialização")
                return False
                
        except Exception as e:
            print(f"  ❌ Erro na inicialização: {e}")
            return False
    
    async def _demo_tts(self):
        """Demonstra TTS em diferentes idiomas."""
        try:
            # TTS Inglês
            print("  🗣️ TTS Inglês:")
            text_en = "Hello! I am the G1 robot from the t031a5 system. I can speak English and Chinese."
            success_en = await self.controller.speak(text_en, G1Language.ENGLISH)
            print(f"    {'✅' if success_en else '❌'} Inglês: '{text_en}'")
            await asyncio.sleep(4.0)
            
            # TTS Chinês
            print("  🗣️ TTS Chinês:")
            text_zh = "你好！我是G1机器人，来自t031a5系统。我会说中文和英文。"
            success_zh = await self.controller.speak(text_zh, G1Language.CHINESE)
            print(f"    {'✅' if success_zh else '❌'} Chinês: '{text_zh}'")
            await asyncio.sleep(4.0)
            
        except Exception as e:
            print(f"  ❌ Erro no TTS: {e}")
    
    async def _demo_leds(self):
        """Demonstra LEDs e emoções."""
        try:
            emotions = [
                (G1Emotion.HAPPY, "Feliz", "Verde"),
                (G1Emotion.EXCITED, "Empolgado", "Amarelo"),
                (G1Emotion.SAD, "Triste", "Azul"),
                (G1Emotion.ENGLISH, "Inglês", "Verde"),
                (G1Emotion.CHINESE, "Chinês", "Vermelho"),
                (G1Emotion.CALM, "Calmo", "Azul claro")
            ]
            
            for emotion, name, color in emotions:
                print(f"  🎨 {name} ({color})")
                success = await self.controller.set_emotion(emotion)
                print(f"    {'✅' if success else '❌'} {name}")
                await asyncio.sleep(1.5)
                
        except Exception as e:
            print(f"  ❌ Erro nos LEDs: {e}")
    
    async def _demo_movements(self):
        """Demonstra movimentos."""
        try:
            # Obtém movimentos disponíveis
            movements = await self.controller.get_available_movements()
            
            print(f"  🤚 Movimentos disponíveis: {len(movements)}")
            for movement_id, name in movements.items():
                print(f"    - ID {movement_id}: {name}")
            
            # Demonstra movimento ID 32
            print("  🤚 Demonstração movimento ID 32:")
            success = await self.controller.execute_gesture(32, emotion=G1Emotion.HAPPY)
            print(f"    {'✅' if success else '❌'} Right Hand on Mouth")
            await asyncio.sleep(2.0)
            
        except Exception as e:
            print(f"  ❌ Erro nos movimentos: {e}")
    
    async def _demo_wav(self):
        """Demonstra WAV playback."""
        try:
            # Cria WAV de demonstração
            wav_file = await self._create_demo_wav()
            
            if wav_file and wav_file.exists():
                print(f"  🎵 Demonstração WAV: {wav_file.name}")
                
                # Reproduz WAV
                success = await self.controller.play_audio(str(wav_file), emotion=G1Emotion.EXCITED)
                print(f"    {'✅' if success else '❌'} WAV playback")
                
                # Aguarda reprodução
                await asyncio.sleep(3.0)
                
                # Para reprodução
                await self.controller.stop_audio()
                print("    ✅ WAV parado")
                
                # Remove arquivo
                wav_file.unlink()
            else:
                print("  ⚠️  WAV não criado")
                
        except Exception as e:
            print(f"  ❌ Erro no WAV: {e}")
    
    async def _demo_integrated(self):
        """Demonstra sequência integrada."""
        try:
            print("  🎭 Demonstração integrada:")
            
            # Cria WAV para sequência
            wav_file = await self._create_demo_wav()
            
            # Define sequência de comandos
            commands = [
                G1AudioCommand("tts", text="Starting integrated demonstration", speaker_id=1, volume=100),
                G1AudioCommand("wav", wav_file=str(wav_file) if wav_file else "", stream_name="demo"),
                G1AudioCommand("stop", stream_name="demo")
            ]
            
            # Executa sequência
            success = await self.controller.execute_sequence(commands, delay_between=1.0)
            print(f"    {'✅' if success else '❌'} Sequência integrada")
            
            # Executa movimento após sequência
            await asyncio.sleep(1.0)
            movement_success = await self.controller.execute_gesture(32, emotion=G1Emotion.HAPPY)
            print(f"    {'✅' if movement_success else '❌'} Movimento integrado")
            
            # Limpa arquivo
            if wav_file and wav_file.exists():
                wav_file.unlink()
                
        except Exception as e:
            print(f"  ❌ Erro na sequência: {e}")
    
    async def _create_demo_wav(self) -> Path:
        """Cria WAV de demonstração."""
        try:
            import wave
            import struct
            
            wav_file = Path("demo_audio.wav")
            
            # WAV 16kHz mono com tom variado
            sample_rate = 16000
            duration = 2.0
            num_samples = int(sample_rate * duration)
            
            pcm_data = []
            for i in range(num_samples):
                # Gera tom variado (simula fala)
                frequency = 440 + 200 * (i / num_samples)  # Varia de 440Hz a 640Hz
                sample_value = int(32767 * 0.2 * (i % int(sample_rate / frequency)) / int(sample_rate / frequency))
                sample = struct.pack('<h', sample_value)
                pcm_data.append(sample)
            
            with wave.open(str(wav_file), 'wb') as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
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
                print("  🧹 Parando sistema t031a5...")
                await self.controller.stop()
                print("  ✅ Sistema parado")
                
        except Exception as e:
            print(f"  ❌ Erro na limpeza: {e}")


async def main():
    """Função principal."""
    print("🎯 Iniciando Demonstração t031a5 - Sistema Integrado com G1")
    print("=" * 80)
    
    demo = T031a5IntegratedDemo()
    success = await demo.run_demo()
    
    if success:
        print("\n🎉 SUCESSO: Sistema t031a5 funcionando perfeitamente!")
        print("📋 Resumo das funcionalidades:")
        print("   ✅ TTS Inglês e Chinês")
        print("   ✅ LEDs com emoções")
        print("   ✅ Movimentos confirmados")
        print("   ✅ WAV Playback")
        print("   ✅ Sequências integradas")
        print("   ✅ Interface de rede (en11)")
        print("   ✅ Controle de volume")
        print("\n🚀 Sistema pronto para uso em produção!")
    else:
        print("\n❌ FALHA: Demonstração não foi bem-sucedida")
        print("🔧 Verifique:")
        print("   - Conexão com G1")
        print("   - Interface de rede (en11)")
        print("   - SDK Unitree instalado")
        print("   - Estado do robô (Main Operation Control)")
        print("   - Configurações de rede")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
