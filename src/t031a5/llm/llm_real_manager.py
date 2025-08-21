#!/usr/bin/env python3
"""
🤖 LLM REAL MANAGER - Ollama Local + OpenAI Fallback
Sistema de Large Language Model com múltiplos providers para conversação
"""

import os
import json
import logging
import asyncio
import aiohttp
from typing import Optional, Dict, Any, List
from datetime import datetime

# Carregar variáveis do .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv é opcional

# OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

logger = logging.getLogger(__name__)

class LLMRealManager:
    """
    Gerenciador de LLM real com múltiplos providers.
    
    Ordem de prioridade:
    1. Ollama Local (rápido, privado, sem custo)
    2. OpenAI GPT (cloud, alta qualidade, fallback)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa LLM Manager.
        
        Args:
            config: Configurações customizadas
        """
        self.config = config or {}
        
        # Configurações Ollama
        self.ollama_url = self.config.get("ollama_url", "http://localhost:11434")
        self.ollama_model = self.config.get("ollama_model", "llama3.1:8b")
        self.ollama_timeout = self.config.get("ollama_timeout", 30)
        
        # Configurações OpenAI
        self.openai_model = self.config.get("openai_model", "gpt-4o-mini")
        self.openai_max_tokens = self.config.get("openai_max_tokens", 150)
        
        # Configurações de conversação
        self.max_context_length = self.config.get("max_context_length", 4000)
        self.temperature = self.config.get("temperature", 0.7)
        
        # Histórico de conversação
        self.conversation_history = []
        
        # Providers disponíveis
        self.providers_available = {
            "ollama": False,  # Será verificado
            "openai": OPENAI_AVAILABLE
        }
        
        # Inicializar providers
        self._init_ollama()
        self._init_openai()
        
        # Configurar personalidade do robô
        self._setup_robot_personality()
        
        logger.info("🤖 LLM Real Manager inicializado")
        self._log_providers_status()
    
    def _init_ollama(self):
        """Inicializa conexão com Ollama local."""
        try:
            # Verificar se Ollama está rodando (será testado no primeiro uso)
            self.ollama_available = True  # Assumir disponível até teste
            logger.info("🔧 Ollama configurado para teste")
            
        except Exception as e:
            logger.warning(f"⚠️ Problema na configuração Ollama: {e}")
            self.ollama_available = False
    
    def _init_openai(self):
        """Inicializa OpenAI client."""
        self.openai_client = None
        
        if not OPENAI_AVAILABLE:
            logger.warning("⚠️ OpenAI não disponível (openai não instalado)")
            return
        
        try:
            # Configurar API key
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("⚠️ OPENAI_API_KEY não encontrada no .env")
                return
            
            # Criar cliente
            self.openai_client = openai.OpenAI(api_key=api_key)
            logger.info("✅ OpenAI configurado")
            
        except Exception as e:
            logger.warning(f"⚠️ Falha na configuração OpenAI: {e}")
            self.openai_client = None
    
    def _setup_robot_personality(self):
        """Configura personalidade do robô G1 Tobias."""
        self.system_prompt = """Você é Tobias, um robô humanoide G1 da Unitree. 

PERSONALIDADE:
- Amigável, prestativo e curioso
- Fala português brasileiro naturalmente
- Inteligente mas humilde
- Gosta de aprender e ajudar

CAPACIDADES FÍSICAS:
- Pode mover braços e fazer gestos
- Tem LEDs que mostram emoções
- Pode se locomover e dançar
- Vê através de câmeras

LIMITAÇÕES:
- Respostas devem ser concisas (máximo 2-3 frases)
- Foque no essencial da conversa
- Seja natural e conversacional

CONTEXTO ATUAL:
- Está em uma sessão de conversação por voz
- Pode executar movimentos quando apropriado
- Responda de forma que faça sentido para uma conversa falada"""

        # Adicionar prompt de sistema ao histórico
        self.conversation_history = [{
            "role": "system",
            "content": self.system_prompt
        }]
    
    def _log_providers_status(self):
        """Log status dos providers."""
        logger.info("📊 STATUS PROVIDERS LLM:")
        logger.info(f"   ollama: {'🔧 Configurado' if self.ollama_available else '❌ Indisponível'}")
        logger.info(f"   openai: {'✅ Disponível' if self.openai_client else '❌ Indisponível'}")
    
    async def generate_response(self, user_message: str) -> Optional[Dict[str, Any]]:
        """
        Gera resposta do LLM para mensagem do usuário.
        
        Args:
            user_message: Mensagem do usuário
            
        Returns:
            dict: {
                "text": "resposta_texto",
                "movement": "movimento_sugerido",
                "emotion": "emocao_sugerida",
                "provider": "provider_usado"
            }
        """
        if not user_message or len(user_message.strip()) == 0:
            logger.warning("⚠️ Mensagem do usuário vazia")
            return None
        
        # Adicionar mensagem ao histórico
        self._add_to_history("user", user_message)
        
        # Tentar providers em ordem de prioridade
        providers = [
            ("ollama", self._generate_ollama),
            ("openai", self._generate_openai)
        ]
        
        for provider_name, generate_func in providers:
            try:
                logger.info(f"🤖 Tentando LLM via {provider_name}...")
                
                response = await generate_func(user_message)
                
                if response:
                    # Adicionar resposta ao histórico
                    self._add_to_history("assistant", response["text"])
                    
                    # Processar movimento e emoção
                    processed_response = self._process_response(response, provider_name)
                    
                    logger.info(f"✅ LLM sucesso via {provider_name}")
                    return processed_response
                else:
                    logger.warning(f"⚠️ {provider_name} retornou resposta vazia")
                    
            except Exception as e:
                logger.warning(f"⚠️ Falha LLM {provider_name}: {e}")
                continue
        
        logger.error("❌ Todos os providers LLM falharam")
        return self._generate_fallback_response(user_message)
    
    async def _generate_ollama(self, user_message: str) -> Optional[Dict[str, Any]]:
        """Gera resposta via Ollama local."""
        try:
            # Preparar contexto
            messages = self._prepare_context()
            
            # Payload para Ollama
            payload = {
                "model": self.ollama_model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": 100,  # Respostas concisas
                    "top_p": 0.9,
                    "repeat_penalty": 1.1
                }
            }
            
            # Fazer requisição
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_url}/api/chat",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.ollama_timeout)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if "message" in data and "content" in data["message"]:
                            return {
                                "text": data["message"]["content"].strip(),
                                "model": self.ollama_model
                            }
                    else:
                        logger.error(f"❌ Ollama erro HTTP: {response.status}")
                        
        except asyncio.TimeoutError:
            logger.warning("⚠️ Timeout Ollama")
            # Marcar como indisponível temporariamente
            self.providers_available["ollama"] = False
        except Exception as e:
            logger.warning(f"⚠️ Erro Ollama: {e}")
        
        return None
    
    async def _generate_openai(self, user_message: str) -> Optional[Dict[str, Any]]:
        """Gera resposta via OpenAI."""
        if not self.openai_client:
            raise Exception("OpenAI client não inicializado")
        
        # Preparar contexto
        messages = self._prepare_context()
        
        # Fazer requisição
        response = self.openai_client.chat.completions.create(
            model=self.openai_model,
            messages=messages,
            max_tokens=self.openai_max_tokens,
            temperature=self.temperature,
            top_p=0.9
        )
        
        if response.choices:
            content = response.choices[0].message.content
            if content:
                return {
                    "text": content.strip(),
                    "model": self.openai_model
                }
        
        return None
    
    def _prepare_context(self) -> List[Dict[str, str]]:
        """Prepara contexto da conversação."""
        # Manter histórico dentro do limite
        context = self.conversation_history.copy()
        
        # Calcular tamanho aproximado
        total_length = sum(len(msg["content"]) for msg in context)
        
        # Remover mensagens antigas se necessário (mantendo system prompt)
        while total_length > self.max_context_length and len(context) > 2:
            # Remover segunda mensagem (primeira é system prompt)
            context.pop(1)
            total_length = sum(len(msg["content"]) for msg in context)
        
        return context
    
    def _process_response(self, response: Dict[str, Any], provider: str) -> Dict[str, Any]:
        """Processa resposta do LLM para extrair movimento e emoção."""
        text = response["text"]
        
        # Análise simples para sugerir movimentos baseado no texto
        movement = self._suggest_movement(text)
        emotion = self._suggest_emotion(text)
        
        return {
            "text": text,
            "movement": movement,
            "emotion": emotion,
            "provider": provider,
            "model": response.get("model", "unknown")
        }
    
    def _suggest_movement(self, text: str) -> str:
        """Sugere movimento baseado no texto da resposta."""
        text_lower = text.lower()
        
        # Mapeamento texto → movimento
        movement_keywords = {
            "olá": "wave_hello",
            "oi": "wave_hello", 
            "cumprimento": "wave_hello",
            "tchau": "wave_goodbye",
            "obrigado": "hand_on_heart",
            "parabéns": "clap_hands",
            "legal": "thumbs_up",
            "coração": "hand_on_heart",
            "amor": "hand_on_heart",
            "sim": "nod_head",
            "não": "shake_head",
            "dança": "dance_move",
            "música": "dance_move"
        }
        
        for keyword, movement in movement_keywords.items():
            if keyword in text_lower:
                return movement
        
        return "neutral_pose"  # Posição neutra padrão
    
    def _suggest_emotion(self, text: str) -> str:
        """Sugere emoção baseada no texto da resposta."""
        text_lower = text.lower()
        
        # Mapeamento texto → emoção
        emotion_keywords = {
            "feliz": "happy",
            "alegre": "happy",
            "legal": "happy",
            "ótimo": "happy",
            "triste": "sad",
            "problema": "concerned",
            "erro": "concerned",
            "interessante": "curious",
            "curioso": "curious",
            "obrigado": "grateful",
            "desculpe": "sorry"
        }
        
        for keyword, emotion in emotion_keywords.items():
            if keyword in text_lower:
                return emotion
        
        return "neutral"  # Emoção neutra padrão
    
    def _add_to_history(self, role: str, content: str):
        """Adiciona mensagem ao histórico."""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def _generate_fallback_response(self, user_message: str) -> Dict[str, Any]:
        """Gera resposta de fallback quando todos os providers falham."""
        fallback_responses = [
            "Desculpe, estou com problemas técnicos no momento.",
            "Não consegui processar sua mensagem. Pode repetir?",
            "Meus sistemas estão sobrecarregados. Tente novamente em instantes.",
            "Hmm, algo deu errado aqui. Pode falar de novo?"
        ]
        
        import random
        response_text = random.choice(fallback_responses)
        
        return {
            "text": response_text,
            "movement": "shake_head",
            "emotion": "concerned",
            "provider": "fallback",
            "model": "internal"
        }
    
    def clear_history(self):
        """Limpa histórico de conversação (mantém system prompt)."""
        system_msg = self.conversation_history[0] if self.conversation_history else None
        self.conversation_history = [system_msg] if system_msg else []
        logger.info("🗑️ Histórico de conversação limpo")
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Obtém resumo da conversação atual."""
        total_messages = len(self.conversation_history) - 1  # Excluir system prompt
        user_messages = len([msg for msg in self.conversation_history if msg["role"] == "user"])
        assistant_messages = len([msg for msg in self.conversation_history if msg["role"] == "assistant"])
        
        return {
            "total_messages": total_messages,
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "context_length": sum(len(msg["content"]) for msg in self.conversation_history)
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Obtém status detalhado do LLM Manager."""
        return {
            "providers_available": self.providers_available.copy(),
            "ollama_url": self.ollama_url,
            "ollama_model": self.ollama_model,
            "openai_model": self.openai_model,
            "openai_ready": self.openai_client is not None,
            "conversation_summary": self.get_conversation_summary(),
            "temperature": self.temperature
        }

# Exemplo de uso
if __name__ == "__main__":
    import asyncio
    import logging
    
    logging.basicConfig(level=logging.INFO)
    
    async def test_llm():
        """Teste básico do LLM."""
        llm_manager = LLMRealManager()
        
        # Status
        status = llm_manager.get_status()
        print("📊 STATUS LLM:")
        for key, value in status.items():
            print(f"   {key}: {value}")
        
        # Teste de conversa
        response = await llm_manager.generate_response("Olá, como você está?")
        if response:
            print(f"🤖 Resposta: {response['text']}")
            print(f"   Movimento: {response['movement']}")
            print(f"   Emoção: {response['emotion']}")
        
        print("✅ LLM Manager testado")
    
    asyncio.run(test_llm())
