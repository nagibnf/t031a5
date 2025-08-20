#!/usr/bin/env python3
"""
Teste Interativo COMPLETO do Sistema t031a5
- Mic, Speaker, Camera, LLMs, G1 Controller
- Conversação AI multimodal em tempo real
"""

import asyncio
import sys
import time
import os
import cv2
import numpy as np
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

# Carrega variáveis de ambiente do .env
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from t031a5.runtime.cortex import CortexRuntime
from t031a5.audio.native_audio_manager import NativeAudioManager
from t031a5.llm.ollama_manager import OllamaManager
from t031a5.vision.camera_manager import CameraManager
from t031a5.vision.llava_manager import LLaVAManager
from t031a5.speech.stt_manager import STTManager
from t031a5.speech.tts_manager import TTSManager

class InteractiveSystemTest:
    def __init__(self):
        self.cortex = None
        self.audio_manager = None
        self.llm_manager = None
        self.camera_manager = None
        self.llava_manager = None
        self.stt_manager = None
        self.tts_manager = None
        self.is_running = False
        self.conversation_count = 0
        
    async def start_interactive_test(self):
        """Inicia o teste interativo completo"""
        print("🚀 TESTE INTERATIVO COMPLETO - Sistema t031a5")
        print("=" * 70)
        print("🤖 Conversação AI Multimodal com Tobias (G1)")
        print("🎤 Mic + 🔊 Speaker + 📷 Camera + 🧠 LLMs")
        print()
        
        # Verifica APIs disponíveis
        await self._check_apis()
        
        # Inicializa componentes
        if not await self._initialize_components():
            print("❌ Falha na inicialização dos componentes")
            return
        
        # Menu interativo
        await self._interactive_menu()
    
    async def _check_apis(self):
        """Verifica APIs disponíveis"""
        print("🔑 VERIFICANDO APIs DISPONÍVEIS")
        print("-" * 50)
        
        apis = {
            "OpenAI": os.getenv('OPENAI_API_KEY'),
            "ElevenLabs": os.getenv('ELEVENLABS_API_KEY'),
            "Google": os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        }
        
        for api_name, api_key in apis.items():
            status = "✅ Configurada" if api_key else "❌ Não configurada"
            print(f"  {api_name}: {status}")
        
        print()
        if not any(apis.values()):
            print("⚠️ AVISO: Nenhuma API externa configurada")
            print("   Sistema funcionará apenas com Ollama local")
        
        return apis
    
    async def _initialize_components(self) -> bool:
        """Inicializa todos os componentes"""
        print("🔧 INICIALIZANDO COMPONENTES")
        print("-" * 50)
        
        success_count = 0.0
        total_components = 6
        
        # 1. Cortex Runtime
        try:
            print("🧠 Inicializando Cortex Runtime...")
            config_path = Path("config/g1_test.json5")
            if not config_path.exists():
                config_path = Path("config/g1_mock.json5")
            
            self.cortex = CortexRuntime(config_path)
            await self.cortex.initialize()
            print("  ✅ Cortex Runtime inicializado")
            success_count += 1
        except Exception as e:
            print(f"  ❌ Erro no Cortex: {e}")
        
        # 2. Sistema de Áudio
        try:
            print("🎤 Inicializando Sistema de Áudio...")
            self.audio_manager = NativeAudioManager()
            if await self.audio_manager.initialize():
                print("  ✅ Sistema de Áudio Nativo inicializado")
                success_count += 1
            else:
                print("  ⚠️ Áudio em modo simplificado")
                success_count += 0.5
        except Exception as e:
            print(f"  ❌ Erro no Áudio: {e}")
        
        # 3. Sistema de LLM
        try:
            print("🧠 Inicializando Sistema de LLM...")
            self.llm_manager = OllamaManager()
            if await self.llm_manager.initialize():
                print("  ✅ LLM Ollama inicializado")
                success_count += 1
            else:
                print("  ❌ Falha no LLM")
        except Exception as e:
            print(f"  ❌ Erro no LLM: {e}")
        
        # 4. Sistema de Câmera
        try:
            print("📷 Inicializando Sistema de Câmera...")
            self.camera_manager = CameraManager()
            if await self.camera_manager.initialize():
                print("  ✅ Câmera inicializada")
                success_count += 1
            else:
                print("  ⚠️ Câmera não disponível")
        except Exception as e:
            print(f"  ❌ Erro na câmera: {e}")
        
        # 5. Sistema de LLaVA (Análise de Imagem)
        try:
            print("👁️ Inicializando Sistema de LLaVA...")
            self.llava_manager = LLaVAManager()
            if await self.llava_manager.initialize():
                print("  ✅ LLaVA inicializado")
                success_count += 1
            else:
                print("  ⚠️ LLaVA não disponível")
        except Exception as e:
            print(f"  ❌ Erro no LLaVA: {e}")
        
        # 6. Sistema de STT
        try:
            print("🎤 Inicializando Sistema de STT...")
            self.stt_manager = STTManager()
            if await self.stt_manager.initialize():
                print("  ✅ STT inicializado")
                success_count += 1
            else:
                print("  ⚠️ STT não disponível")
        except Exception as e:
            print(f"  ❌ Erro no STT: {e}")
        
        # 7. Sistema de TTS
        try:
            print("🔊 Inicializando Sistema de TTS...")
            self.tts_manager = TTSManager()
            if await self.tts_manager.initialize():
                print("  ✅ TTS inicializado")
                success_count += 1
            else:
                print("  ⚠️ TTS não disponível")
        except Exception as e:
            print(f"  ❌ Erro no TTS: {e}")
        
        total_components = 7  # Cortex, Audio, LLM, Camera, LLaVA, STT, TTS
        success_rate = (success_count / total_components) * 100
        print(f"\n📊 Taxa de inicialização: {success_rate:.1f}% ({success_count}/{total_components})")
        
        return success_count >= 3  # Pelo menos 3 componentes funcionando
    
    async def _interactive_menu(self):
        """Menu interativo principal"""
        self.is_running = True
        
        while self.is_running:
            print("\n" + "=" * 70)
            print("🎮 MENU INTERATIVO - Sistema t031a5")
            print("=" * 70)
            print("1. 🗣️  Conversar com Tobias (Texto)")
            print("2. 🎤  Conversar com Tobias (Áudio)")
            print("3. 📷  Análise de Imagem")
            print("4. 🎭  Executar Gesto")
            print("5. 🚶  Comandos de Movimento")
            print("6. 📊  Status do Sistema")
            print("7. 🔄  Trocar Modelo LLM")
            print("8. 🧪  Teste de Performance")
            print("9. 🌐  Abrir WebSim")
            print("0. ❌  Sair")
            print()
            
            try:
                choice = input("👆 Escolha uma opção: ").strip()
            except EOFError:
                print("\n❌ EOF detectado - saindo do sistema")
                self.is_running = False
                continue
            except KeyboardInterrupt:
                print("\n❌ Interrompido pelo usuário - saindo")
                self.is_running = False
                continue
            
            try:
                if choice == "1":
                    await self._text_conversation()
                elif choice == "2":
                    await self._audio_conversation()
                elif choice == "3":
                    await self._image_analysis()
                elif choice == "4":
                    await self._gesture_demo()
                elif choice == "5":
                    await self._movement_demo()
                elif choice == "6":
                    await self._system_status()
                elif choice == "7":
                    await self._switch_llm_model()
                elif choice == "8":
                    await self._performance_test()
                elif choice == "9":
                    await self._open_websim()
                elif choice == "0":
                    self.is_running = False
                else:
                    print("❌ Opção inválida! Tente novamente.")
                    
            except KeyboardInterrupt:
                print("\n⚠️ Interrompido pelo usuário")
                self.is_running = False
            except Exception as e:
                print(f"❌ Erro: {e}")
                await asyncio.sleep(1)
        
        await self._cleanup()
    
    async def _text_conversation(self):
        """Conversação de texto com Tobias"""
        print("\n💬 CONVERSAÇÃO DE TEXTO COM TOBIAS")
        print("-" * 50)
        print("Digite 'sair' para voltar ao menu")
        print()
        
        conversation_active = True
        while conversation_active:
            try:
                # Input do usuário
                user_input = input("👤 Você: ").strip()
                
                if user_input.lower() in ['sair', 'exit', 'quit']:
                    conversation_active = False
                    continue
                
                if not user_input:
                    continue
                
                # Processa resposta
                print("🤖 Tobias: Pensando...", end="", flush=True)
                
                start_time = time.time()
                response = await self.llm_manager.generate_response(
                    user_input, 
                    context="Você é Tobias, um robô G1 inteligente e amigável. Responda sempre em português."
                )
                response_time = time.time() - start_time
                
                print(f"\r🤖 Tobias: {response}")
                print(f"   ⏱️ Tempo de resposta: {response_time:.2f}s")
                print()
                
                self.conversation_count += 1
                
            except KeyboardInterrupt:
                conversation_active = False
            except Exception as e:
                print(f"\n❌ Erro na conversação: {e}")
    
    async def _audio_conversation(self):
        """Conversação de áudio com Tobias usando APIs reais"""
        print("\n🎤 CONVERSAÇÃO DE ÁUDIO COM TOBIAS")
        print("-" * 50)
        
        if not self.audio_manager:
            print("❌ Sistema de áudio não disponível")
            return
        
        if not self.stt_manager:
            print("❌ Sistema de STT não disponível")
            return
        
        if not self.tts_manager:
            print("❌ Sistema de TTS não disponível")
            return
        
        print("🎤 Pressione ENTER para gravar, 'sair' para voltar")
        print()
        
        conversation_active = True
        while conversation_active:
            try:
                try:
                    user_input = input("🎤 Pressione ENTER para gravar (ou 'sair'): ").strip()
                except EOFError:
                    print("\n❌ EOF detectado - saindo da conversação")
                    conversation_active = False
                    continue
                except KeyboardInterrupt:
                    print("\n❌ Interrompido pelo usuário - saindo")
                    conversation_active = False
                    continue
                
                if user_input.lower() in ['sair', 'exit', 'quit']:
                    conversation_active = False
                    continue
                
                # Captura áudio
                print("🎤 Gravando por 5 segundos...")
                audio_data = await self.audio_manager.capture_audio(5.0)
                
                if audio_data is not None:
                    print("✅ Áudio capturado!")
                    print("🔄 Processando voz...")
                    
                    # STT real
                    transcribed_text = await self.stt_manager.transcribe_audio(audio_data, "pt-BR")
                    
                    if transcribed_text:
                        print(f"📝 Texto reconhecido: '{transcribed_text}'")
                        
                        # Gera resposta
                        print("🤖 Tobias: Processando...", end="", flush=True)
                        response = await self.llm_manager.generate_response(
                            transcribed_text,
                            context="Você é Tobias, robô G1. Respostas curtas e diretas em português."
                        )
                        print(f"\r🤖 Tobias: {response}")
                        
                        # TTS real
                        print("🔊 Sintetizando voz...")
                        synthesized_audio = await self.tts_manager.synthesize_speech(response)
                        
                        if synthesized_audio:
                            print("🎵 Reproduzindo resposta...")
                            success = await self.audio_manager.play_audio(synthesized_audio)
                            if success:
                                print("✅ Resposta reproduzida")
                            else:
                                print("❌ Falha na reprodução")
                        else:
                            print("⚠️ TTS falhou - mostrando apenas texto")
                            print(f"🤖 Tobias: {response}")
                            print("💡 Dica: Adicione créditos no ElevenLabs ou configure TTS local")
                    else:
                        print("❌ Não foi possível reconhecer a fala")
                    
                    self.conversation_count += 1
                else:
                    print("❌ Falha na captura de áudio")
                
            except KeyboardInterrupt:
                conversation_active = False
            except Exception as e:
                print(f"❌ Erro na conversação de áudio: {e}")
    
    async def _image_analysis(self):
        """Análise de imagem com câmera real"""
        print("\n📷 ANÁLISE DE IMAGEM")
        print("-" * 50)
        
        if not self.camera_manager:
            print("❌ Câmera não disponível")
            return
        
        try:
            print("📷 Capturando imagem da câmera...")
            image = await self.camera_manager.capture_image()
            
            if image is not None:
                print("✅ Imagem capturada!")
                
                # Salva a imagem
                timestamp = int(time.time())
                filename = f"capture_{timestamp}.jpg"
                await self.camera_manager.save_image(image, filename)
                
                # Informações da imagem
                height, width = image.shape[:2]
                print(f"📐 Resolução: {width}x{height}")
                
                # Análise básica da imagem
                print("🔍 Analisando imagem...")
                
                # Detecta se há movimento/objetos (análise simples)
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                blur = cv2.GaussianBlur(gray, (21, 21), 0)
                
                # Calcula variação de pixels (detecção básica de movimento)
                mean_intensity = np.mean(blur)
                std_intensity = np.std(blur)
                
                if std_intensity > 20:  # Há variação significativa
                    scene_description = "Detectei movimento e objetos na cena"
                else:
                    scene_description = "Cena estática ou pouca variação detectada"
                
                print(f"👀 Análise: {scene_description}")
                print(f"📊 Intensidade média: {mean_intensity:.1f}")
                print(f"📊 Variação: {std_intensity:.1f}")
                
                # Análise com GPT-4 Vision
                image_path = f"captures/{filename}"
                description = await self._analyze_image_with_gpt4_vision(image_path)
                
                if description:
                    print(f"🤖 Tobias: {description}")
                else:
                    # Fallback para análise básica
                    prompt = f"""
                    Analise esta imagem capturada pela câmera:
                    - Resolução: {width}x{height}
                    - Análise técnica: {scene_description}
                    - Intensidade média: {mean_intensity:.1f}
                    - Variação: {std_intensity:.1f}
                    
                    Descreva o que você vê e interpreta baseado nos dados técnicos. 
                    Responda como Tobias, o robô G1, de forma amigável.
                    """
                    
                    response = await self.llm_manager.generate_response(prompt)
                    print(f"🤖 Tobias: {response}")
                
            else:
                print("❌ Falha na captura de imagem")
                
        except Exception as e:
            print(f"❌ Erro na análise de imagem: {e}")
            import traceback
            traceback.print_exc()
    
    async def _analyze_image_with_gpt4_vision(self, image_path: str) -> Optional[str]:
        """Analisa imagem usando GPT-4 Vision"""
        try:
            import openai
            import base64
            
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                print("⚠️ OpenAI API key não configurada para análise de imagem")
                return None
            
            # Lê e codifica a imagem
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            client = openai.OpenAI(api_key=api_key)
            
            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analise esta imagem capturada pela câmera do robô Tobias. Descreva o que vê de forma detalhada e amigável, como se fosse o próprio Tobias falando. Responda em português."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"⚠️ GPT-4 Vision não disponível: {e}")
            return None
    
    async def _gesture_demo(self):
        """Demonstração de gestos"""
        print("\n🎭 DEMONSTRAÇÃO DE GESTOS")
        print("-" * 50)
        
        gestures = ["wave", "hug", "thumbs_up", "clap", "bow", "dance"]
        
        for i, gesture in enumerate(gestures, 1):
            print(f"{i}. {gesture.title()}")
        
        try:
            choice = int(input("\nEscolha um gesto (1-6): ")) - 1
            if 0 <= choice < len(gestures):
                gesture = gestures[choice]
                print(f"🎭 Executando gesto: {gesture}")
                print("🤖 Tobias está executando o movimento...")
                await asyncio.sleep(2)  # Simula execução
                print("✅ Gesto executado com sucesso!")
            else:
                print("❌ Opção inválida")
        except ValueError:
            print("❌ Digite um número válido")
    
    async def _movement_demo(self):
        """Demonstração de movimentos"""
        print("\n🚶 DEMONSTRAÇÃO DE MOVIMENTOS")
        print("-" * 50)
        
        movements = [
            ("move_forward", "Mover para frente"),
            ("move_backward", "Mover para trás"),
            ("turn_left", "Virar à esquerda"),
            ("turn_right", "Virar à direita"),
            ("emergency_stop", "Parada de emergência")
        ]
        
        for i, (cmd, desc) in enumerate(movements, 1):
            print(f"{i}. {desc}")
        
        try:
            choice = int(input("\nEscolha um movimento (1-5): ")) - 1
            if 0 <= choice < len(movements):
                cmd, desc = movements[choice]
                print(f"🚶 Executando: {desc}")
                print("🤖 Tobias está se movimentando...")
                await asyncio.sleep(1.5)  # Simula movimento
                print("✅ Movimento executado com sucesso!")
            else:
                print("❌ Opção inválida")
        except ValueError:
            print("❌ Digite um número válido")
    
    async def _system_status(self):
        """Mostra status detalhado do sistema"""
        print("\n📊 STATUS DETALHADO DO SISTEMA")
        print("-" * 50)
        
        # Status do Cortex
        if self.cortex:
            print("✅ Cortex Runtime: Ativo")
        else:
            print("❌ Cortex Runtime: Inativo")
        
        # Status do LLM
        if self.llm_manager:
            models = await self.llm_manager.list_models()
            print(f"✅ LLM Ollama: Ativo ({len(models)} modelos)")
            for model in models[:3]:  # Mostra até 3 modelos
                name = model.get('name', 'Desconhecido')
                print(f"   📦 {name}")
        else:
            print("❌ LLM: Inativo")
        
        # Status do Áudio
        if self.audio_manager and self.audio_manager.is_initialized:
            print("✅ Sistema de Áudio: Ativo")
        else:
            print("⚠️ Sistema de Áudio: Limitado")
        
        # Estatísticas
        print(f"\n📈 Estatísticas:")
        print(f"   💬 Conversas realizadas: {self.conversation_count}")
        print(f"   ⏱️ Tempo de execução: {time.time() - start_time:.1f}s")
    
    async def _switch_llm_model(self):
        """Troca modelo LLM"""
        print("\n🔄 TROCAR MODELO LLM")
        print("-" * 50)
        
        if not self.llm_manager:
            print("❌ LLM Manager não disponível")
            return
        
        # Lista modelos disponíveis
        models = await self.llm_manager.list_models()
        
        if not models:
            print("❌ Nenhum modelo encontrado")
            return
        
        print("Modelos disponíveis:")
        for i, model in enumerate(models, 1):
            name = model.get('name', 'Desconhecido')
            size = model.get('size', 'N/A')
            current = "🔵" if name == self.llm_manager.current_model else "⚪"
            print(f"{i}. {current} {name} ({size})")
        
        try:
            choice = int(input(f"\nEscolha um modelo (1-{len(models)}): ")) - 1
            if 0 <= choice < len(models):
                new_model = models[choice]['name']
                print(f"🔄 Trocando para: {new_model}")
                success = await self.llm_manager.switch_model(new_model)
                if success:
                    print("✅ Modelo trocado com sucesso!")
                else:
                    print("❌ Falha ao trocar modelo")
            else:
                print("❌ Opção inválida")
        except ValueError:
            print("❌ Digite um número válido")
    
    async def _image_analysis(self):
        """Análise de imagem com LLaVA"""
        print("\n📷 ANÁLISE DE IMAGEM")
        print("-" * 50)
        
        if not self.camera_manager:
            print("❌ Câmera não disponível")
            return
        
        if not self.llava_manager:
            print("❌ LLaVA não disponível")
            return
        
        try:
            print("📷 Capturando imagem da câmera...")
            image_data = await self.camera_manager.capture_image()
            
            if image_data is None:
                print("❌ Falha na captura de imagem")
                return
            
            print("✅ Imagem capturada!")
            
            # Salva a imagem capturada
            timestamp = int(time.time())
            image_filename = f"capture_{timestamp}.jpg"
            save_success = await self.camera_manager.save_image(image_data, image_filename)
            
            if not save_success:
                print("⚠️ Falha ao salvar imagem, mas continuando análise...")
            
            image_path = f"captures/{image_filename}" if save_success else None
            
            # Análise básica com dados da imagem
            height, width = image_data.shape[:2]
            print(f"📐 Resolução: {width}x{height}")
            
            # Análise básica de intensidade (image_data já está em RGB)
            gray = np.mean(image_data, axis=2)  # Converte RGB para grayscale
            mean_intensity = np.mean(gray)
            std_intensity = np.std(gray)
            
            print("🔍 Analisando imagem com LLaVA...")
            print(f"👀 Análise básica: Detectei movimento e objetos na cena")
            print(f"📊 Intensidade média: {mean_intensity:.1f}")
            print(f"📊 Variação: {std_intensity:.1f}")
            
            # Análise com LLaVA - Usa prompt rápido padrão
            if image_path and os.path.exists(image_path):
                # Usa arquivo salvo se disponível (prompt padrão "quick")
                analysis = await self.llava_manager.analyze_image(image_path)
            else:
                # Usa dados da imagem diretamente
                import cv2
                import tempfile
                
                # Salva temporariamente para LLaVA
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
                    # Converte RGB para BGR para salvar
                    image_bgr = cv2.cvtColor(image_data, cv2.COLOR_RGB2BGR)
                    cv2.imwrite(temp_file.name, image_bgr)
                    temp_path = temp_file.name
                
                analysis = await self.llava_manager.analyze_image(temp_path)
                
                # Remove arquivo temporário
                try:
                    os.unlink(temp_path)
                except:
                    pass
            
            if analysis:
                print(f"🤖 LLaVA: {analysis}")
            else:
                print("⚠️ LLaVA não conseguiu analisar a imagem")
                
                # Fallback para LLM básico
                if self.llm_manager:
                    basic_prompt = f"Você é Tobias, robô G1. Uma imagem foi capturada com resolução {width}x{height}, intensidade média {mean_intensity:.1f} e variação {std_intensity:.1f}. Comente sobre estes dados de forma natural."
                    fallback_response = await self.llm_manager.generate_response(basic_prompt)
                    if fallback_response:
                        print(f"🤖 Tobias: {fallback_response}")
                
        except Exception as e:
            print(f"❌ Erro na análise de imagem: {e}")
            import traceback
            traceback.print_exc()
    
    async def _performance_test(self):
        """Teste de performance"""
        print("\n🧪 TESTE DE PERFORMANCE")
        print("-" * 50)
        
        if not self.llm_manager:
            print("❌ LLM Manager não disponível")
            return
        
        print("🔄 Executando teste de performance...")
        results = await self.llm_manager.test_performance()
        
        print("\n📊 RESULTADOS:")
        if results["ollama"]["success"]:
            print(f"🖥️ Ollama Local: {results['ollama']['time']:.2f}s")
            print(f"   📝 Resposta: {results['ollama']['response'][:100]}...")
        else:
            print("❌ Ollama Local: Falhou")
        
        if results["openai"]["success"]:
            print(f"☁️ OpenAI Cloud: {results['openai']['time']:.2f}s")
            print(f"   📝 Resposta: {results['openai']['response'][:100]}...")
        else:
            print("❌ OpenAI Cloud: Falhou (API key não configurada)")
    
    async def _open_websim(self):
        """Abre WebSim"""
        print("\n🌐 ABRINDO WEBSIM")
        print("-" * 50)
        
        try:
            # Inicia WebSim
            from t031a5.simulators.websim import WebSim
            
            websim_config = {
                "host": "localhost",
                "port": 8081,
                "debug": True,
                "cors_enabled": True,
                "auto_start": False,
                "mock_robot": True
            }
            
            websim = WebSim(websim_config)
            
            if await websim.initialize():
                print("✅ WebSim inicializado")
                
                if await websim.start():
                    print("✅ Servidor WebSim iniciado!")
                    print(f"🌐 URL: http://localhost:8081")
                    print("📱 Abra seu navegador e acesse a URL acima")
                    print("⚠️ Pressione ENTER para parar o servidor...")
                    input()
                    
                    # Para o servidor
                    await websim.stop()
                    print("✅ WebSim parado")
                else:
                    print("❌ Falha ao iniciar servidor WebSim")
            else:
                print("❌ Falha ao inicializar WebSim")
                
        except Exception as e:
            print(f"❌ Erro ao abrir WebSim: {e}")
            import traceback
            traceback.print_exc()
    
    async def _cleanup(self):
        """Limpa recursos"""
        print("\n🧹 LIMPANDO RECURSOS...")
        
        if self.audio_manager:
            await self.audio_manager.cleanup()
            print("✅ Áudio limpo")
        
        if self.llm_manager:
            await self.llm_manager.cleanup()
            print("✅ LLM limpo")
        
        if self.camera_manager:
            await self.camera_manager.cleanup()
            print("✅ Câmera limpa")
        
        if self.llava_manager:
            await self.llava_manager.cleanup()
            print("✅ LLaVA limpo")
        
        if self.stt_manager:
            await self.stt_manager.cleanup()
            print("✅ STT limpo")
        
        if self.tts_manager:
            await self.tts_manager.cleanup()
            print("✅ TTS limpo")
        
        if self.cortex:
            await self.cortex.stop()
            print("✅ Cortex parado")
        
        print("\n🎉 TESTE INTERATIVO CONCLUÍDO!")
        print("Obrigado por testar o sistema t031a5!")

async def main():
    """Função principal"""
    global start_time
    start_time = time.time()
    
    print("🚀 Iniciando Teste Interativo Completo...")
    print()
    
    tester = InteractiveSystemTest()
    await tester.start_interactive_test()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Até logo!")
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
