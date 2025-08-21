#!/usr/bin/env python3
"""
🤖 SISTEMA CONVERSAÇÃO REAL COMPLETO
Integração completa: DJI Mic → STT → LLM → TTS → Anker + G1 Movimentos

FLUXO COMPLETO:
1. 🎤 AudioManagerDefinitivo: Captura DJI Mic 2 (formato nativo s24le)
2. 🗣️ STTRealManager: Google Speech API → OpenAI Whisper → Whisper Local
3. 🤖 LLMRealManager: Ollama Local → OpenAI GPT (personalidade Tobias)  
4. 🔊 TTSRealManager: ElevenLabs → gTTS → Pyttsx3
5. 📢 AudioManagerDefinitivo: Reprodução Anker Bluetooth
6. 🦾 G1MovementLibrary: Movimentos físicos sincronizados
"""

import sys
import logging
import asyncio
import time
from pathlib import Path
from typing import Optional, Dict, Any

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, "/home/unitree/t031a5/src")

# Importar componentes do sistema
from t031a5.audio.audio_manager_definitivo import AudioManagerDefinitivo
from t031a5.speech.stt_real_manager import STTRealManager
from t031a5.llm.llm_real_manager import LLMRealManager
from t031a5.speech.tts_real_manager import TTSRealManager
from t031a5.actions.g1_movement_mapping import G1MovementLibrary

# Importar G1 SDK para movimentos
try:
    from unitree_sdk2py.core.channel import ChannelFactoryInitialize
    from unitree_sdk2py.g1.arm.g1_arm_action_client import G1ArmActionClient as ArmActionClient
    G1_SDK_AVAILABLE = True
except ImportError:
    G1_SDK_AVAILABLE = False
    logger.warning("⚠️ G1 SDK não disponível")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SistemaConversacaoRealCompleto:
    """
    Sistema completo de conversação em tempo real para robô G1 Tobias.
    
    Integra todos os componentes de IA validados:
    - Captura de áudio DJI Mic 2 (formato nativo)
    - STT multi-provider (Google/OpenAI/Whisper)
    - LLM conversacional (Ollama/OpenAI)
    - TTS natural (ElevenLabs/gTTS/Pyttsx3)
    - Reprodução Bluetooth Anker
    - Movimentos G1 sincronizados
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa sistema completo.
        
        Args:
            config: Configurações customizadas
        """
        self.config = config or {}
        
        # Configurações de conversação
        self.capture_duration = self.config.get("capture_duration", 5.0)
        self.conversation_timeout = self.config.get("conversation_timeout", 300)  # 5 min
        self.movement_enabled = self.config.get("movement_enabled", True)
        
        # Estados do sistema
        self.system_ready = False
        self.conversation_active = False
        self.stats = {
            "conversations": 0,
            "messages_processed": 0,
            "errors": 0,
            "start_time": None
        }
        
        # Inicializar componentes
        logger.info("🚀 INICIALIZANDO SISTEMA CONVERSAÇÃO REAL COMPLETO")
        logger.info("="*70)
        
        self._init_components()
        
    def _init_components(self):
        """Inicializa todos os componentes do sistema."""
        try:
            # 1. Audio Manager (DJI + Anker)
            logger.info("🎧 Inicializando Audio Manager...")
            self.audio_manager = AudioManagerDefinitivo(auto_connect_anker=True)
            logger.info("✅ Audio Manager inicializado")
            
            # 2. STT Manager (Google + Whisper)
            logger.info("🎤 Inicializando STT Manager...")
            self.stt_manager = STTRealManager(self.config.get("stt", {}))
            logger.info("✅ STT Manager inicializado")
            
            # 3. LLM Manager (Ollama + OpenAI)
            logger.info("🤖 Inicializando LLM Manager...")
            self.llm_manager = LLMRealManager(self.config.get("llm", {}))
            logger.info("✅ LLM Manager inicializado")
            
            # 4. TTS Manager (ElevenLabs + fallbacks)
            logger.info("🔊 Inicializando TTS Manager...")
            self.tts_manager = TTSRealManager(self.config.get("tts", {}))
            logger.info("✅ TTS Manager inicializado")
            
            # 5. G1 Movement (opcional)
            if self.movement_enabled and G1_SDK_AVAILABLE:
                logger.info("🦾 Inicializando G1 Movement...")
                self._init_g1_movement()
                logger.info("✅ G1 Movement inicializado")
            else:
                logger.info("⚠️ G1 Movement desabilitado ou SDK indisponível")
                self.g1_client = None
                self.movement_library = None
            
            self.system_ready = True
            logger.info("🎉 SISTEMA COMPLETO INICIALIZADO COM SUCESSO!")
            
        except Exception as e:
            logger.error(f"❌ Falha na inicialização: {e}")
            self.system_ready = False
            raise
    
    def _init_g1_movement(self):
        """Inicializa sistema de movimentos G1."""
        try:
            # Inicializar canal DDS
            ChannelFactoryInitialize(0, "eth0")
            
            # Criar cliente de braços
            self.g1_client = ArmActionClient()
            self.g1_client.SetTimeout(10.0)
            self.g1_client.Init()
            
            # Biblioteca de movimentos
            self.movement_library = G1MovementLibrary()
            
            logger.info("✅ G1 SDK conectado")
            
        except Exception as e:
            logger.warning(f"⚠️ Falha G1 SDK: {e}")
            self.g1_client = None
            self.movement_library = None
    
    async def iniciar_conversacao(self):
        """Inicia loop principal de conversação."""
        if not self.system_ready:
            logger.error("❌ Sistema não está pronto")
            return False
        
        logger.info("🎬 INICIANDO CONVERSAÇÃO INTERATIVA")
        logger.info("="*70)
        
        self.conversation_active = True
        self.stats["start_time"] = time.time()
        
        # Mensagem de boas-vindas
        await self._falar_boas_vindas()
        
        try:
            while self.conversation_active:
                # Ciclo de conversação
                sucesso = await self._ciclo_conversacao()
                
                if not sucesso:
                    logger.warning("⚠️ Falha no ciclo - tentando continuar...")
                    await asyncio.sleep(2)
                
                # Verificar timeout
                if self._verificar_timeout():
                    logger.info("⏰ Timeout de conversação atingido")
                    break
                    
        except KeyboardInterrupt:
            logger.info("🛑 Conversação interrompida pelo usuário")
        except Exception as e:
            logger.error(f"❌ Erro na conversação: {e}")
            self.stats["errors"] += 1
        finally:
            await self._finalizar_conversacao()
    
    async def _falar_boas_vindas(self):
        """Fala mensagem de boas-vindas."""
        mensagem = "Olá! Eu sou o Tobias, seu assistente robótico. Como posso ajudá-lo hoje?"
        
        logger.info("👋 Falando boas-vindas...")
        
        # Sintetizar e reproduzir
        audio_boas_vindas = await self.tts_manager.synthesize_speech(mensagem)
        if audio_boas_vindas is not None:
            self.audio_manager.reproduzir_audio_anker(audio_boas_vindas)
            
            # Movimento de cumprimento
            await self._executar_movimento("wave_hello", 3.0)
        else:
            logger.warning("⚠️ Falha na síntese de boas-vindas")
    
    async def _ciclo_conversacao(self) -> bool:
        """
        Executa um ciclo completo de conversação.
        
        Returns:
            bool: True se ciclo bem-sucedido
        """
        try:
            logger.info("\n" + "="*50)
            logger.info("🗣️ AGUARDANDO FALA DO USUÁRIO")
            logger.info("💡 Diga algo ou 'tchau' para encerrar...")
            
            # 1. CAPTURAR ÁUDIO
            logger.info(f"🎤 Capturando áudio ({self.capture_duration}s)...")
            
            for i in range(3, 0, -1):
                logger.info(f"⏰ {i}...")
                await asyncio.sleep(1)
            
            logger.info("🔴 GRAVANDO...")
            audio_data = self.audio_manager.capturar_audio_dji(self.capture_duration)
            
            if audio_data is None:
                logger.error("❌ Falha na captura de áudio")
                return False
            
            # Validar qualidade do áudio
            metricas = self.audio_manager.obter_metricas_audio(audio_data)
            if not metricas.get("quality_ok", False):
                logger.warning("⚠️ Qualidade de áudio baixa - pode afetar reconhecimento")
                # Continuar mesmo assim
            
            # 2. SPEECH-TO-TEXT
            logger.info("🗣️ Processando STT...")
            texto_usuario = await self.stt_manager.transcribe_audio(audio_data)
            
            if not texto_usuario:
                await self._responder_nao_entendeu()
                return False
            
            logger.info(f"📝 Usuário disse: '{texto_usuario}'")
            
            # Verificar comando de saída
            if self._verificar_comando_saida(texto_usuario):
                await self._despedir()
                self.conversation_active = False
                return True
            
            # 3. LARGE LANGUAGE MODEL
            logger.info("🤖 Processando LLM...")
            resposta_llm = await self.llm_manager.generate_response(texto_usuario)
            
            if not resposta_llm:
                await self._responder_erro_llm()
                return False
            
            logger.info(f"🤖 Tobias responde: '{resposta_llm['text']}'")
            logger.info(f"   Movimento: {resposta_llm['movement']}")
            logger.info(f"   Emoção: {resposta_llm['emotion']}")
            
            # 4. TEXT-TO-SPEECH
            logger.info("🔊 Processando TTS...")
            audio_resposta = await self.tts_manager.synthesize_speech(resposta_llm["text"])
            
            if not audio_resposta:
                logger.error("❌ Falha na síntese de voz")
                return False
            
            # 5. REPRODUÇÃO + MOVIMENTO SINCRONIZADO
            logger.info("🎭 Executando resposta + movimento...")
            
            # Iniciar reprodução
            task_audio = asyncio.create_task(
                self._reproduzir_audio_async(audio_resposta)
            )
            
            # Executar movimento simultaneamente
            task_movimento = asyncio.create_task(
                self._executar_movimento(resposta_llm["movement"], len(audio_resposta) / 16000)
            )
            
            # Aguardar ambos
            await asyncio.gather(task_audio, task_movimento)
            
            # Atualizar estatísticas
            self.stats["messages_processed"] += 1
            
            logger.info("✅ Ciclo conversacional concluído com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no ciclo conversacional: {e}")
            self.stats["errors"] += 1
            return False
    
    async def _reproduzir_audio_async(self, audio_data):
        """Reproduz áudio de forma assíncrona."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None, 
            self.audio_manager.reproduzir_audio_anker,
            audio_data
        )
    
    async def _executar_movimento(self, movimento: str, duracao: float):
        """Executa movimento G1 se disponível."""
        if not self.g1_client or not self.movement_library:
            # Simular movimento
            logger.info(f"🎭 [SIMULADO] Movimento: {movimento} ({duracao:.1f}s)")
            await asyncio.sleep(min(duracao, 3.0))
            return
        
        try:
            # Obter ID da ação
            action_id = self.movement_library.get_action_id(movimento)
            
            if action_id is not None:
                logger.info(f"🦾 Executando movimento real: {movimento}")
                
                # Executar movimento
                self.g1_client.ExecuteAction(action_id)
                
                # Aguardar duração do movimento
                movimento_duracao = self.movement_library.get_duration(movimento)
                await asyncio.sleep(movimento_duracao)
                
                # Retornar à posição neutra
                release_id = self.movement_library.get_action_id("release_arm")
                if release_id:
                    self.g1_client.ExecuteAction(release_id)
                    
            else:
                logger.warning(f"⚠️ Movimento '{movimento}' não encontrado")
                
        except Exception as e:
            logger.warning(f"⚠️ Erro no movimento: {e}")
    
    async def _responder_nao_entendeu(self):
        """Responde quando não entende o usuário."""
        mensagens = [
            "Desculpe, não consegui entender. Pode repetir?",
            "Não escutei direito. Pode falar novamente?",
            "Hmm, pode repetir mais claramente?",
            "Não entendi. Tente falar mais devagar."
        ]
        
        import random
        mensagem = random.choice(mensagens)
        
        audio_resposta = await self.tts_manager.synthesize_speech(mensagem)
        if audio_resposta:
            self.audio_manager.reproduzir_audio_anker(audio_resposta)
            await self._executar_movimento("shake_head", 2.0)
    
    async def _responder_erro_llm(self):
        """Responde quando há erro no LLM."""
        mensagem = "Desculpe, estou com problemas técnicos. Tente novamente."
        
        audio_resposta = await self.tts_manager.synthesize_speech(mensagem)
        if audio_resposta:
            self.audio_manager.reproduzir_audio_anker(audio_resposta)
            await self._executar_movimento("shake_head", 2.0)
    
    def _verificar_comando_saida(self, texto: str) -> bool:
        """Verifica se usuário quer sair."""
        comandos_saida = ["tchau", "sair", "parar", "fim", "encerrar", "bye", "goodbye"]
        texto_lower = texto.lower()
        
        return any(cmd in texto_lower for cmd in comandos_saida)
    
    async def _despedir(self):
        """Executa despedida."""
        mensagem = "Foi um prazer conversar com você! Até a próxima!"
        
        logger.info("👋 Executando despedida...")
        
        audio_despedida = await self.tts_manager.synthesize_speech(mensagem)
        if audio_despedida:
            self.audio_manager.reproduzir_audio_anker(audio_despedida)
            await self._executar_movimento("wave_goodbye", 3.0)
    
    def _verificar_timeout(self) -> bool:
        """Verifica se atingiu timeout de conversação."""
        if self.stats["start_time"]:
            elapsed = time.time() - self.stats["start_time"]
            return elapsed > self.conversation_timeout
        return False
    
    async def _finalizar_conversacao(self):
        """Finaliza conversação e mostra estatísticas."""
        self.conversation_active = False
        
        if self.stats["start_time"]:
            duracao = time.time() - self.stats["start_time"]
        else:
            duracao = 0
        
        logger.info("📊 ESTATÍSTICAS DA CONVERSAÇÃO:")
        logger.info(f"   Duração: {duracao:.1f}s")
        logger.info(f"   Mensagens processadas: {self.stats['messages_processed']}")
        logger.info(f"   Erros: {self.stats['errors']}")
        logger.info(f"   Taxa de sucesso: {(1 - self.stats['errors']/max(1, self.stats['messages_processed']))*100:.1f}%")
        
        logger.info("👋 Conversação finalizada!")
    
    def obter_status_sistema(self) -> Dict[str, Any]:
        """Obtém status completo do sistema."""
        return {
            "system_ready": self.system_ready,
            "conversation_active": self.conversation_active,
            "stats": self.stats.copy(),
            "components": {
                "audio": self.audio_manager.get_status() if hasattr(self, 'audio_manager') else None,
                "stt": self.stt_manager.get_status() if hasattr(self, 'stt_manager') else None,
                "llm": self.llm_manager.get_status() if hasattr(self, 'llm_manager') else None,
                "tts": self.tts_manager.get_status() if hasattr(self, 'tts_manager') else None,
                "g1_available": self.g1_client is not None
            }
        }

async def main():
    """Função principal."""
    logger.info("🤖 SISTEMA CONVERSAÇÃO REAL COMPLETO - G1 TOBIAS")
    logger.info("="*70)
    
    try:
        # Configurações do sistema
        config = {
            "capture_duration": 5.0,  # Segundos de captura
            "movement_enabled": True,  # Habilitar movimentos G1
            "conversation_timeout": 600,  # 10 minutos
            "stt": {
                "min_confidence": 0.7
            },
            "llm": {
                "temperature": 0.7
            },
            "tts": {
                "language": "pt",
                "sample_rate": 16000
            }
        }
        
        # Criar sistema
        sistema = SistemaConversacaoRealCompleto(config)
        
        # Mostrar status
        status = sistema.obter_status_sistema()
        logger.info("📊 STATUS DO SISTEMA:")
        logger.info(f"   Sistema pronto: {status['system_ready']}")
        
        if status["system_ready"]:
            # Iniciar conversação
            await sistema.iniciar_conversacao()
        else:
            logger.error("❌ Sistema não está pronto - verifique componentes")
            
    except KeyboardInterrupt:
        logger.info("🛑 Sistema interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}")

if __name__ == "__main__":
    asyncio.run(main())
