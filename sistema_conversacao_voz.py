#!/usr/bin/env python3
"""
🗣️ SISTEMA DE CONVERSAÇÃO POR VOZ - t031a5 G1 Tobias
Fluxo completo: DJI Mic → STT PT → LLM → TTS PT → Bluetooth + Movimentos

Funcionalidades:
- STT: Google Speech API (português) + Whisper fallback
- LLM: Ollama local + OpenAI fallback  
- TTS: ElevenLabs (português) via Bluetooth Anker
- Movimentos: G1 gestos contextuais sincronizados
- Áudio: DJI Mic 2 entrada + Anker Soundcore saída
"""

import sys
import time
import asyncio
import logging
import json
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import wave
import numpy as np

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, "/home/unitree/t031a5/src")

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SistemaConversacaoVoz:
    """Sistema completo de conversação por voz em português."""
    
    def __init__(self):
        self.config = self.carregar_configuracao()
        self.audio_manager = None
        self.g1_client = None
        self.conversas_historico = []
        self.ativo = False
        
        # Componentes
        self.stt_engine = None
        self.llm_provider = None  
        self.tts_engine = None
        self.movimento_engine = None
        
        # Status dos componentes
        self.componentes_status = {
            "audio_hibrido": False,
            "g1_sdk": False,
            "stt": False,
            "llm": False,
            "tts": False,
            "bluetooth": False
        }
    
    def carregar_configuracao(self) -> Dict:
        """Carrega configurações do sistema."""
        return {
            "idioma": "pt-BR",
            "sample_rate": 16000,
            "duracao_escuta": 5.0,
            "threshold_silencio": 0.02,
            "max_tentativas": 3,
            "timeout_resposta": 30.0,
            
            # STT
            "stt_google_habilitado": True,
            "stt_whisper_fallback": True,
            
            # LLM  
            "llm_local_habilitado": True,
            "llm_openai_fallback": True,
            "max_tokens_resposta": 150,
            
            # TTS
            "tts_elevenlabs": True,
            "voz_elevenlabs": "Portuguese Female",
            "velocidade_fala": 1.0,
            
            # Movimentos
            "gestos_habilitados": True,
            "movimento_timeout": 10.0,
        }
    
    async def inicializar_componentes(self) -> bool:
        """Inicializa todos os componentes do sistema."""
        logger.info("🔧 INICIALIZANDO SISTEMA DE CONVERSAÇÃO...")
        logger.info("="*60)
        
        sucesso_total = True
        
        # 1. Sistema Híbrido de Áudio
        if await self.inicializar_audio():
            self.componentes_status["audio_hibrido"] = True
            logger.info("✅ Áudio Híbrido: OK")
        else:
            logger.error("❌ Áudio Híbrido: FALHA")
            sucesso_total = False
        
        # 2. G1 SDK
        if await self.inicializar_g1():
            self.componentes_status["g1_sdk"] = True
            logger.info("✅ G1 SDK: OK")
        else:
            logger.error("❌ G1 SDK: FALHA")
            sucesso_total = False
        
        # 3. STT (Speech-to-Text)
        if await self.inicializar_stt():
            self.componentes_status["stt"] = True
            logger.info("✅ STT: OK")
        else:
            logger.error("❌ STT: FALHA")
            sucesso_total = False
        
        # 4. LLM (Language Model)
        if await self.inicializar_llm():
            self.componentes_status["llm"] = True
            logger.info("✅ LLM: OK")
        else:
            logger.error("❌ LLM: FALHA")
            sucesso_total = False
        
        # 5. TTS (Text-to-Speech)
        if await self.inicializar_tts():
            self.componentes_status["tts"] = True
            logger.info("✅ TTS: OK")
        else:
            logger.error("❌ TTS: FALHA")
            sucesso_total = False
        
        # 6. Bluetooth
        if await self.verificar_bluetooth():
            self.componentes_status["bluetooth"] = True
            logger.info("✅ Bluetooth: OK")
        else:
            logger.warning("⚠️ Bluetooth: Limitado")
        
        logger.info("="*60)
        componentes_ok = sum(1 for status in self.componentes_status.values() if status)
        total_componentes = len(self.componentes_status)
        taxa_sucesso = (componentes_ok / total_componentes) * 100
        
        logger.info(f"🎯 INICIALIZAÇÃO: {componentes_ok}/{total_componentes} ({taxa_sucesso:.1f}%)")
        
        if taxa_sucesso >= 80:
            logger.info("🎉 Sistema pronto para conversação!")
            return True
        else:
            logger.warning("⚠️ Sistema com limitações")
            return sucesso_total
    
    async def inicializar_audio(self) -> bool:
        """Inicializa sistema híbrido de áudio."""
        try:
            from t031a5.audio.hybrid_microphone_manager import HybridMicrophoneManager
            
            self.audio_manager = HybridMicrophoneManager({
                "sample_rate": self.config["sample_rate"],
                "test_duration": 2,
                "auto_switch": True,
                "quality_threshold": 10
            })
            
            # Teste rápido
            results = self.audio_manager.run_full_diagnostics()
            current_mic = self.audio_manager.current_source.value if self.audio_manager.current_source else None
            
            if current_mic and current_mic != "none":
                logger.info(f"🎤 Microfone ativo: {current_mic}")
                return True
            else:
                logger.warning("⚠️ Nenhum microfone funcional detectado")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao inicializar áudio: {e}")
            return False
    
    async def inicializar_g1(self) -> bool:
        """Inicializa conexão com G1."""
        try:
            from unitree_sdk2py.core.channel import ChannelFactoryInitialize
            from unitree_sdk2py.g1.arm.g1_arm_action_client import G1ArmActionClient
            
            # Inicializar canal
            ChannelFactoryInitialize(0, "eth0")
            
            # Criar cliente
            self.g1_client = G1ArmActionClient()
            self.g1_client.SetTimeout(self.config["movimento_timeout"])
            self.g1_client.Init()
            
            # Teste movimento básico
            result = self.g1_client.ExecuteAction(99)  # relaxar
            
            if result == 0:
                logger.info("🤖 G1 respondendo a comandos")
                return True
            else:
                logger.warning(f"⚠️ G1 erro no teste: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao inicializar G1: {e}")
            return False
    
    async def inicializar_stt(self) -> bool:
        """Inicializa Speech-to-Text."""
        try:
            # Verificar Google Speech API
            if self.config["stt_google_habilitado"]:
                try:
                    import google.cloud.speech as speech
                    self.stt_engine = "google"
                    logger.info("🗣️ Google Speech API disponível")
                    return True
                except ImportError:
                    logger.warning("⚠️ Google Speech API não disponível")
            
            # Fallback para Whisper
            if self.config["stt_whisper_fallback"]:
                try:
                    import whisper
                    self.stt_engine = "whisper"
                    logger.info("🗣️ Whisper disponível como fallback")
                    return True
                except ImportError:
                    logger.warning("⚠️ Whisper não disponível")
            
            # Simulação como último recurso
            self.stt_engine = "simulado"
            logger.warning("⚠️ Usando STT simulado")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao inicializar STT: {e}")
            return False
    
    async def inicializar_llm(self) -> bool:
        """Inicializa Language Model."""
        try:
            # Tentar Ollama local primeiro
            if self.config["llm_local_habilitado"]:
                try:
                    import requests
                    response = requests.get("http://localhost:11434/api/tags", timeout=5)
                    if response.status_code == 200:
                        self.llm_provider = "ollama"
                        logger.info("🧠 Ollama local disponível")
                        return True
                except:
                    logger.warning("⚠️ Ollama local não disponível")
            
            # Fallback para OpenAI
            if self.config["llm_openai_fallback"]:
                import os
                if os.getenv("OPENAI_API_KEY"):
                    self.llm_provider = "openai"
                    logger.info("🧠 OpenAI API disponível")
                    return True
                else:
                    logger.warning("⚠️ OpenAI API key não encontrada")
            
            # Simulação como último recurso
            self.llm_provider = "simulado"
            logger.warning("⚠️ Usando LLM simulado")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao inicializar LLM: {e}")
            return False
    
    async def inicializar_tts(self) -> bool:
        """Inicializa Text-to-Speech."""
        try:
            # Verificar ElevenLabs
            if self.config["tts_elevenlabs"]:
                import os
                if os.getenv("ELEVENLABS_API_KEY"):
                    self.tts_engine = "elevenlabs"
                    logger.info("🗣️ ElevenLabs TTS disponível")
                    return True
                else:
                    logger.warning("⚠️ ElevenLabs API key não encontrada")
            
            # Fallback para TTS do sistema
            try:
                import pyttsx3
                self.tts_engine = "sistema"
                logger.info("🗣️ TTS do sistema disponível")
                return True
            except ImportError:
                logger.warning("⚠️ TTS do sistema não disponível")
            
            # Simulação como último recurso
            self.tts_engine = "simulado"
            logger.warning("⚠️ Usando TTS simulado")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao inicializar TTS: {e}")
            return False
    
    async def verificar_bluetooth(self) -> bool:
        """Verifica dispositivos Bluetooth."""
        try:
            # Verificar se Anker está conectado
            result = subprocess.run(
                ["pactl", "list", "sinks", "short"], 
                capture_output=True, text=True, timeout=5
            )
            
            if "anker" in result.stdout.lower() or "soundcore" in result.stdout.lower():
                logger.info("🔊 Anker Soundcore detectado")
                return True
            else:
                logger.info("🔊 Usando saída de áudio padrão")
                return True
                
        except Exception as e:
            logger.warning(f"Erro ao verificar Bluetooth: {e}")
            return True  # Não é crítico
    
    async def capturar_audio(self, duracao: float = None) -> Tuple[Optional[np.ndarray], str]:
        """Captura áudio do microfone."""
        if not self.audio_manager:
            return None, "Áudio não inicializado"
        
        duracao = duracao or self.config["duracao_escuta"]
        
        try:
            logger.info(f"🎤 Capturando áudio ({duracao}s)...")
            audio_data, source = self.audio_manager.capture_audio(duration=duracao)
            
            if audio_data is not None and len(audio_data) > 0:
                return audio_data, f"Capturado via {source.value}"
            else:
                return None, "Nenhum áudio capturado"
                
        except Exception as e:
            logger.error(f"Erro na captura: {e}")
            return None, f"Erro: {e}"
    
    async def processar_stt(self, audio_data: np.ndarray) -> Tuple[Optional[str], str]:
        """Converte áudio em texto (Speech-to-Text)."""
        if audio_data is None:
            return None, "Áudio inválido"
        
        try:
            if self.stt_engine == "google":
                return await self.stt_google(audio_data)
            elif self.stt_engine == "whisper":
                return await self.stt_whisper(audio_data)
            else:
                # STT simulado para testes
                frases_teste = [
                    "Olá Tobias, como você está?",
                    "Acenar com a mão para mim",
                    "Bater palmas",
                    "Colocar a mão no coração",
                    "Como está o tempo hoje?"
                ]
                import random
                frase = random.choice(frases_teste)
                logger.info(f"🗣️ STT Simulado: '{frase}'")
                await asyncio.sleep(1)  # Simular processamento
                return frase, "STT simulado"
                
        except Exception as e:
            logger.error(f"Erro no STT: {e}")
            return None, f"Erro STT: {e}"
    
    async def stt_google(self, audio_data: np.ndarray) -> Tuple[Optional[str], str]:
        """STT usando Google Speech API."""
        try:
            import google.cloud.speech as speech
            
            # Converter para formato WAV
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                # Normalizar áudio para int16
                audio_int16 = (audio_data * 32767).astype(np.int16)
                
                # Salvar como WAV
                with wave.open(temp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(self.config["sample_rate"])
                    wav_file.writeframes(audio_int16.tobytes())
                
                # Processar com Google
                client = speech.SpeechClient()
                
                with open(temp_file.name, 'rb') as audio_file:
                    content = audio_file.read()
                
                audio = speech.RecognitionAudio(content=content)
                config = speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=self.config["sample_rate"],
                    language_code=self.config["idioma"],
                )
                
                response = client.recognize(config=config, audio=audio)
                
                # Limpar arquivo temporário
                Path(temp_file.name).unlink()
                
                if response.results:
                    texto = response.results[0].alternatives[0].transcript
                    confianca = response.results[0].alternatives[0].confidence
                    logger.info(f"🗣️ Google STT: '{texto}' (confiança: {confianca:.2f})")
                    return texto, f"Google STT (conf: {confianca:.2f})"
                else:
                    return None, "Google STT: sem resultado"
                    
        except Exception as e:
            logger.error(f"Erro Google STT: {e}")
            return None, f"Erro Google: {e}"
    
    async def stt_whisper(self, audio_data: np.ndarray) -> Tuple[Optional[str], str]:
        """STT usando Whisper local."""
        try:
            import whisper
            
            # Carregar modelo Whisper
            model = whisper.load_model("base")
            
            # Converter para formato que Whisper aceita
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                audio_int16 = (audio_data * 32767).astype(np.int16)
                
                with wave.open(temp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(self.config["sample_rate"])
                    wav_file.writeframes(audio_int16.tobytes())
                
                # Processar com Whisper
                result = model.transcribe(temp_file.name, language="pt")
                
                # Limpar arquivo temporário
                Path(temp_file.name).unlink()
                
                if result["text"].strip():
                    texto = result["text"].strip()
                    logger.info(f"🗣️ Whisper STT: '{texto}'")
                    return texto, "Whisper STT"
                else:
                    return None, "Whisper: sem resultado"
                    
        except Exception as e:
            logger.error(f"Erro Whisper STT: {e}")
            return None, f"Erro Whisper: {e}"
    
    async def processar_llm(self, texto_entrada: str) -> Tuple[Optional[str], Optional[str], str]:
        """Processa texto com LLM e extrai resposta + movimento."""
        if not texto_entrada:
            return None, None, "Texto vazio"
        
        try:
            # Prompt em português
            prompt = f"""Você é Tobias, um robô humanóide social amigável. Responda de forma natural e amigável em português brasileiro.

Entrada do usuário: "{texto_entrada}"

Instruções:
1. Responda de forma natural e conversacional
2. Se o usuário pedir um movimento específico (acenar, aplaudir, etc), inclua [MOVIMENTO:nome_movimento] na resposta
3. Mantenha respostas concisas (máximo 2 frases)
4. Seja amigável e empático

Movimentos disponíveis: acenar, aplaudir, coracao, cumprimentar, abracar, recusar

Resposta:"""
            
            if self.llm_provider == "ollama":
                resposta, movimento = await self.llm_ollama(prompt)
            elif self.llm_provider == "openai":
                resposta, movimento = await self.llm_openai(prompt)
            else:
                # LLM simulado
                respostas_teste = {
                    "acenar": ("Claro! Vou acenar para você agora. [MOVIMENTO:acenar]", "acenar"),
                    "palmas": ("Que alegria! Vou bater palmas. [MOVIMENTO:aplaudir]", "aplaudir"),
                    "coração": ("Isso me toca o coração! [MOVIMENTO:coracao]", "coracao"),
                    "olá": ("Olá! É um prazer falar com você! [MOVIMENTO:cumprimentar]", "cumprimentar"),
                    "como": ("Estou muito bem, obrigado por perguntar!", None),
                    "tempo": ("Desculpe, não tenho acesso a informações meteorológicas no momento.", None)
                }
                
                for palavra_chave, (resp, mov) in respostas_teste.items():
                    if palavra_chave in texto_entrada.lower():
                        resposta, movimento = resp, mov
                        break
                else:
                    resposta, movimento = "Entendi! Como posso ajudá-lo?", None
                
                await asyncio.sleep(1)  # Simular processamento
            
            logger.info(f"🧠 LLM: '{resposta}'")
            if movimento:
                logger.info(f"🎭 Movimento sugerido: {movimento}")
            
            return resposta, movimento, f"Processado via {self.llm_provider}"
            
        except Exception as e:
            logger.error(f"Erro no LLM: {e}")
            return None, None, f"Erro LLM: {e}"
    
    async def llm_ollama(self, prompt: str) -> Tuple[str, Optional[str]]:
        """Processa com Ollama local."""
        try:
            import requests
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.1:8b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": self.config["max_tokens_resposta"]
                    }
                },
                timeout=self.config["timeout_resposta"]
            )
            
            if response.status_code == 200:
                resultado = response.json()
                resposta = resultado.get("response", "").strip()
                
                # Extrair movimento
                movimento = self.extrair_movimento(resposta)
                
                return resposta, movimento
            else:
                raise Exception(f"Ollama erro {response.status_code}")
                
        except Exception as e:
            raise Exception(f"Ollama falhou: {e}")
    
    async def llm_openai(self, prompt: str) -> Tuple[str, Optional[str]]:
        """Processa com OpenAI API."""
        try:
            import openai
            import os
            
            openai.api_key = os.getenv("OPENAI_API_KEY")
            
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.config["max_tokens_resposta"],
                temperature=0.7,
                timeout=self.config["timeout_resposta"]
            )
            
            resposta = response.choices[0].message.content.strip()
            movimento = self.extrair_movimento(resposta)
            
            return resposta, movimento
            
        except Exception as e:
            raise Exception(f"OpenAI falhou: {e}")
    
    def extrair_movimento(self, resposta: str) -> Optional[str]:
        """Extrai comando de movimento da resposta do LLM."""
        import re
        
        # Procurar padrão [MOVIMENTO:nome]
        match = re.search(r'\[MOVIMENTO:(\w+)\]', resposta)
        if match:
            movimento = match.group(1).lower()
            
            # Mapear para IDs do G1
            mapeamento_movimentos = {
                "acenar": 26,      # wave_above_head
                "aplaudir": 17,    # clamp
                "coracao": 33,     # right_hand_on_heart
                "cumprimentar": 27, # shake_hand
                "abracar": 19,     # hug
                "recusar": 22,     # refuse
                "relaxar": 99      # release_arm
            }
            
            if movimento in mapeamento_movimentos:
                return movimento
        
        return None
    
    async def processar_tts_e_movimento(self, resposta: str, movimento: Optional[str]) -> Tuple[bool, str]:
        """Processa TTS e executa movimento simultaneamente."""
        try:
            # Remover marcadores de movimento da resposta
            import re
            resposta_limpa = re.sub(r'\[MOVIMENTO:\w+\]', '', resposta).strip()
            
            # Executar TTS e movimento em paralelo
            tasks = []
            
            # TTS
            if resposta_limpa:
                tasks.append(self.executar_tts(resposta_limpa))
            
            # Movimento
            if movimento and self.config["gestos_habilitados"]:
                tasks.append(self.executar_movimento(movimento))
            
            if tasks:
                resultados = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Verificar resultados
                sucesso_tts = True
                sucesso_movimento = True
                detalhes = []
                
                for i, resultado in enumerate(resultados):
                    if isinstance(resultado, Exception):
                        if i == 0:  # TTS
                            sucesso_tts = False
                            detalhes.append(f"TTS erro: {resultado}")
                        else:  # Movimento
                            sucesso_movimento = False
                            detalhes.append(f"Movimento erro: {resultado}")
                    else:
                        if i == 0:  # TTS
                            detalhes.append("TTS OK")
                        else:  # Movimento
                            detalhes.append("Movimento OK")
                
                sucesso_geral = sucesso_tts or sucesso_movimento
                return sucesso_geral, "; ".join(detalhes)
            else:
                return True, "Nada para executar"
                
        except Exception as e:
            logger.error(f"Erro no TTS/Movimento: {e}")
            return False, f"Erro: {e}"
    
    async def executar_tts(self, texto: str) -> bool:
        """Executa Text-to-Speech."""
        try:
            if self.tts_engine == "elevenlabs":
                return await self.tts_elevenlabs(texto)
            elif self.tts_engine == "sistema":
                return await self.tts_sistema(texto)
            else:
                # TTS simulado
                logger.info(f"🗣️ TTS Simulado: '{texto}'")
                # Simular duração da fala
                duracao = len(texto) * 0.1  # ~100ms por caractere
                await asyncio.sleep(min(duracao, 5.0))
                return True
                
        except Exception as e:
            logger.error(f"Erro no TTS: {e}")
            return False
    
    async def tts_elevenlabs(self, texto: str) -> bool:
        """TTS usando ElevenLabs."""
        try:
            import requests
            import os
            
            url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"  # Voz feminina
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": os.getenv("ELEVENLABS_API_KEY")
            }
            
            data = {
                "text": texto,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5,
                    "speed": self.config["velocidade_fala"]
                }
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                # Salvar áudio temporário
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                    temp_file.write(response.content)
                    
                    # Reproduzir via PulseAudio (Bluetooth)
                    subprocess.run([
                        "paplay", temp_file.name
                    ], check=True, timeout=30)
                    
                    # Limpar arquivo
                    Path(temp_file.name).unlink()
                
                logger.info("🗣️ ElevenLabs TTS executado")
                return True
            else:
                raise Exception(f"ElevenLabs erro {response.status_code}")
                
        except Exception as e:
            logger.error(f"Erro ElevenLabs: {e}")
            return False
    
    async def tts_sistema(self, texto: str) -> bool:
        """TTS usando sistema local."""
        try:
            import pyttsx3
            
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)  # Velocidade
            engine.setProperty('volume', 0.8)  # Volume
            
            # Definir voz em português se disponível
            voices = engine.getProperty('voices')
            for voice in voices:
                if 'portuguese' in voice.name.lower() or 'brazil' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
            
            engine.say(texto)
            engine.runAndWait()
            
            logger.info("🗣️ TTS sistema executado")
            return True
            
        except Exception as e:
            logger.error(f"Erro TTS sistema: {e}")
            return False
    
    async def executar_movimento(self, movimento: str) -> bool:
        """Executa movimento no G1."""
        if not self.g1_client:
            logger.warning("G1 não disponível para movimento")
            return False
        
        try:
            # Mapear movimento para ID
            mapeamento = {
                "acenar": 26,      # wave_above_head
                "aplaudir": 17,    # clamp
                "coracao": 33,     # right_hand_on_heart
                "cumprimentar": 27, # shake_hand
                "abracar": 19,     # hug
                "recusar": 22,     # refuse
                "relaxar": 99      # release_arm
            }
            
            if movimento not in mapeamento:
                logger.warning(f"Movimento desconhecido: {movimento}")
                return False
            
            movimento_id = mapeamento[movimento]
            
            logger.info(f"🎭 Executando: {movimento} (ID: {movimento_id})")
            
            # Executar movimento
            result = self.g1_client.ExecuteAction(movimento_id)
            
            if result == 0:
                logger.info(f"✅ Movimento {movimento} executado")
                
                # Aguardar conclusão
                if movimento == "acenar":
                    await asyncio.sleep(8)
                elif movimento == "aplaudir":
                    await asyncio.sleep(4.5)
                else:
                    await asyncio.sleep(3)
                
                # Relaxar braços após movimento
                self.g1_client.ExecuteAction(99)
                
                return True
            else:
                logger.error(f"❌ Movimento {movimento} falhou: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Erro no movimento {movimento}: {e}")
            return False
    
    def salvar_conversa(self, entrada: str, resposta: str, movimento: Optional[str], detalhes: Dict):
        """Salva conversa no histórico."""
        conversa = {
            "timestamp": datetime.now().isoformat(),
            "entrada": entrada,
            "resposta": resposta,
            "movimento": movimento,
            "detalhes": detalhes
        }
        
        self.conversas_historico.append(conversa)
        
        # Limitar histórico
        if len(self.conversas_historico) > 50:
            self.conversas_historico = self.conversas_historico[-50:]
    
    async def ciclo_conversacao(self) -> bool:
        """Executa um ciclo completo de conversação."""
        logger.info("\n" + "="*60)
        logger.info("🎙️ INICIANDO CICLO DE CONVERSAÇÃO")
        logger.info("="*60)
        
        detalhes = {
            "inicio": datetime.now().isoformat(),
            "etapas": {}
        }
        
        try:
            # 1. Capturar áudio
            logger.info("1️⃣ Capturando áudio...")
            audio_data, status_audio = await self.capturar_audio()
            detalhes["etapas"]["captura_audio"] = status_audio
            
            if audio_data is None:
                logger.warning(f"⚠️ Falha na captura: {status_audio}")
                return False
            
            # 2. STT
            logger.info("2️⃣ Processando STT...")
            texto_entrada, status_stt = await self.processar_stt(audio_data)
            detalhes["etapas"]["stt"] = status_stt
            
            if not texto_entrada:
                logger.warning(f"⚠️ STT falhou: {status_stt}")
                return False
            
            logger.info(f"👤 Usuário disse: '{texto_entrada}'")
            
            # 3. LLM
            logger.info("3️⃣ Processando LLM...")
            resposta, movimento, status_llm = await self.processar_llm(texto_entrada)
            detalhes["etapas"]["llm"] = status_llm
            
            if not resposta:
                logger.warning(f"⚠️ LLM falhou: {status_llm}")
                return False
            
            logger.info(f"🤖 Tobias responde: '{resposta}'")
            
            # 4. TTS + Movimento
            logger.info("4️⃣ Executando resposta...")
            sucesso_saida, status_saida = await self.processar_tts_e_movimento(resposta, movimento)
            detalhes["etapas"]["saida"] = status_saida
            
            # 5. Salvar no histórico
            self.salvar_conversa(texto_entrada, resposta, movimento, detalhes)
            
            logger.info("="*60)
            logger.info("✅ CICLO DE CONVERSAÇÃO COMPLETO")
            logger.info("="*60)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no ciclo de conversação: {e}")
            detalhes["erro"] = str(e)
            return False
    
    async def executar_sistema_conversacao(self):
        """Executa o sistema de conversação principal."""
        logger.info("🗣️ SISTEMA DE CONVERSAÇÃO POR VOZ - t031a5 G1 TOBIAS")
        logger.info("="*70)
        logger.info(f"Idioma: {self.config['idioma']}")
        logger.info(f"Duração escuta: {self.config['duracao_escuta']}s")
        logger.info("="*70)
        
        # Inicializar componentes
        if not await self.inicializar_componentes():
            logger.error("❌ Falha na inicialização - sistema não pode continuar")
            return
        
        self.ativo = True
        ciclo = 0
        
        try:
            logger.info("\n🎙️ SISTEMA PRONTO! Diga 'parar' para encerrar.")
            logger.info("Aguardando interação...")
            
            while self.ativo:
                ciclo += 1
                logger.info(f"\n🔄 CICLO #{ciclo}")
                
                sucesso = await self.ciclo_conversacao()
                
                if not sucesso:
                    logger.warning("⚠️ Ciclo falhou - tentando novamente em 2s...")
                    await asyncio.sleep(2)
                else:
                    # Pausa entre ciclos
                    await asyncio.sleep(1)
                
                # Verificar se deve parar (implementar lógica de parada)
                if ciclo >= 10:  # Limite para demonstração
                    logger.info("🛑 Limite de ciclos atingido")
                    break
                    
        except KeyboardInterrupt:
            logger.info("\n⏹️ Sistema interrompido pelo usuário")
        except Exception as e:
            logger.error(f"❌ Erro crítico: {e}")
        finally:
            self.ativo = False
            logger.info("🛑 Sistema de conversação encerrado")

async def main():
    """Função principal."""
    sistema = SistemaConversacaoVoz()
    await sistema.executar_sistema_conversacao()

if __name__ == "__main__":
    asyncio.run(main())
