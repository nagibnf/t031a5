"""
Provedor OpenAI para o sistema t031a5.

Integração com GPT-4o e GPT-4o-mini via OpenAI API.
"""

import asyncio
import logging
import json
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..provider import LLMRequest, LLMResponse, BaseLLMProvider
from ...fuser.base import FusedData

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """Provedor OpenAI para GPT-4o e GPT-4o-mini."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o provedor OpenAI.
        
        Args:
            config: Configuração do provedor
        """
        super().__init__(config)
        
        # Configurações específicas do OpenAI
        import os
        
        # Carrega .env se disponível
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass  # dotenv não disponível
        
        api_key_env = config.get("api_key_env", "OPENAI_API_KEY")
        self.api_key = config.get("api_key") or os.getenv(api_key_env)
        self.model = config.get("model", "gpt-4o-mini")
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 150)
        self.timeout = config.get("timeout", 10.0)
        
        # Configurações de contexto
        self.include_vision = config.get("include_vision", False)
        self.include_sensors = config.get("include_sensors", True)
        self.include_location = config.get("include_location", True)
        self.include_robot_state = config.get("include_robot_state", True)
        
        # Controle de rate limiting
        self.requests_per_minute = config.get("requests_per_minute", 60)
        self.last_request_time = None
        self.request_count = 0
        self.reset_time = datetime.now()
        
        # Cliente OpenAI (será inicializado se disponível)
        self.client = None
        
        # Métricas
        self.metrics = {
            "requests": 0,
            "errors": 0,
            "last_request": None
        }
        
        logger.debug(f"OpenAIProvider configurado: {self.model}, temp={self.temperature}")
    
    async def initialize(self) -> bool:
        """
        Inicializa o provedor OpenAI.
        
        Returns:
            True se a inicialização foi bem-sucedida
        """
        try:
            logger.info("Inicializando OpenAIProvider...")
            
            # Verifica se a API key está configurada
            if not self.api_key:
                logger.error("API key do OpenAI não configurada")
                return False
            
            # Tenta importar o cliente OpenAI
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=self.api_key)
                logger.info("Cliente OpenAI inicializado com sucesso")
            except ImportError:
                logger.error("Biblioteca openai não instalada. Execute: pip install openai")
                return False
            
            # Testa a conexão
            success = await self._test_connection()
            if not success:
                logger.error("Falha no teste de conexão com OpenAI")
                return False
            
            self.is_initialized = True
            logger.info("OpenAIProvider inicializado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro na inicialização do OpenAIProvider: {e}")
            return False
    
    async def _test_connection(self) -> bool:
        """
        Testa a conexão com a API OpenAI.
        
        Returns:
            True se a conexão está funcionando
        """
        try:
            # Teste simples com uma requisição pequena
            from ...fuser.base import FusedData
            
            test_fused_data = FusedData(
                fusion_type="test",
                timestamp=datetime.now(),
                data={"content": "Teste de conexão"},
                confidence=1.0,
                source_inputs=["test"],
                fusion_metadata={"test": True}
            )
            
            test_request = LLMRequest(
                fused_data=test_fused_data,
                system_prompt="Você é um assistente de teste. Responda apenas 'OK'.",
                model=self.model,
                temperature=0.1,
                max_tokens=10
            )
            
            response = await self._make_request(test_request)
            return response is not None and "OK" in response.content
            
        except Exception as e:
            logger.error(f"Erro no teste de conexão: {e}")
            return False
    
    async def _process(self, request: LLMRequest) -> Optional[LLMResponse]:
        """
        Processa uma requisição LLM.
        
        Args:
            request: Requisição LLM
            
        Returns:
            Resposta LLM ou None se falhar
        """
        try:
            # Controle de rate limiting
            if not await self._check_rate_limit():
                logger.warning("Rate limit atingido, aguardando...")
                await asyncio.sleep(60)  # Aguarda 1 minuto
            
            # Faz a requisição
            response = await self._make_request(request)
            
            # Atualiza métricas
            self._update_metrics()
            
            return response
            
        except Exception as e:
            logger.error(f"Erro no processamento OpenAI: {e}")
            self.metrics["errors"] += 1
            return None
    
    async def process(self, fused_data: FusedData, system_prompt: str) -> Optional[LLMResponse]:
        """
        Processa dados fundidos com o LLM.
        
        Args:
            fused_data: Dados fundidos dos inputs
            system_prompt: Prompt do sistema
            
        Returns:
            Resposta do LLM ou None se falhar
        """
        try:
            if not self.is_initialized:
                logger.error(f"{self.name} não foi inicializado")
                return None
            
            if not self.enabled:
                logger.debug(f"{self.name} está desabilitado")
                return None
            
            # Cria requisição
            request = LLMRequest(
                fused_data=fused_data,
                system_prompt=system_prompt,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout
            )
            
            logger.debug(f"Processando dados com {self.name}")
            
            # Processamento específico
            response = await self._process(request)
            
            if response:
                logger.debug(f"Resposta obtida de {self.name}: {len(response.content)} caracteres")
            
            return response
            
        except asyncio.TimeoutError:
            logger.error(f"Timeout no processamento com {self.name}")
            return None
        except Exception as e:
            logger.error(f"Erro no processamento com {self.name}: {e}")
            return None
    
    async def _make_request(self, request: LLMRequest) -> Optional[LLMResponse]:
        """
        Faz uma requisição para a API OpenAI.
        
        Args:
            request: Requisição LLM
            
        Returns:
            Resposta LLM ou None se falhar
        """
        try:
            # Prepara as mensagens
            messages = self._prepare_messages(request)
            
            # Parâmetros da requisição
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            # Faz a requisição
            logger.debug(f"Fazendo requisição para OpenAI: {self.model}")
            
            response = await asyncio.wait_for(
                self.client.chat.completions.create(**params),
                timeout=self.timeout
            )
            
            # Processa a resposta
            content = response.choices[0].message.content
            usage = response.usage
            
            # Cria a resposta
            llm_response = LLMResponse(
                content=content,
                model=self.model,
                timestamp=datetime.now(),
                tokens_used=usage.total_tokens if usage else 0,
                metadata={
                    "openai_response_id": response.id,
                    "finish_reason": response.choices[0].finish_reason,
                    "model": self.model,
                    "provider": "openai"
                }
            )
            
            logger.debug(f"Resposta OpenAI recebida: {len(content)} chars")
            return llm_response
            
        except asyncio.TimeoutError:
            logger.error("Timeout na requisição OpenAI")
            return None
        except Exception as e:
            logger.error(f"Erro na requisição OpenAI: {e}")
            return None
    
    def _prepare_messages(self, request: LLMRequest) -> List[Dict[str, Any]]:
        """
        Prepara as mensagens para a API OpenAI.
        
        Args:
            request: Requisição LLM
            
        Returns:
            Lista de mensagens formatadas
        """
        messages = []
        
        # Mensagem do sistema
        if request.system_prompt:
            messages.append({
                "role": "system",
                "content": request.system_prompt
            })
        
        # Conteúdo principal baseado nos dados fundidos
        fused_data = request.fused_data.data
        content = str(fused_data) if fused_data else "Nenhum dado disponível"
        
        # Adiciona contexto dos dados fundidos
        if request.fused_data.data:
            context_parts = []
            
            # Adiciona todos os dados fundidos como contexto
            for key, value in request.fused_data.data.items():
                if isinstance(value, (dict, list)):
                    context_parts.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
                else:
                    context_parts.append(f"{key}: {value}")
            
            # Informações de metadata se disponível
            if request.fused_data.fusion_metadata:
                meta_str = json.dumps(request.fused_data.fusion_metadata, ensure_ascii=False)
                context_parts.append(f"Metadados: {meta_str}")
            
            # Adiciona contexto se houver
            if context_parts:
                context = "\n".join(context_parts)
                content = f"Contexto atual:\n{context}\n\nUse essas informações para responder de forma natural e conversacional."
        
        # Mensagem do usuário
        messages.append({
            "role": "user",
            "content": content
        })
        
        return messages
    
    async def _check_rate_limit(self) -> bool:
        """
        Verifica se não excedeu o rate limit.
        
        Returns:
            True se pode fazer requisição
        """
        now = datetime.now()
        
        # Reseta contador a cada minuto
        if (now - self.reset_time).seconds >= 60:
            self.request_count = 0
            self.reset_time = now
        
        # Verifica se pode fazer requisição
        if self.request_count >= self.requests_per_minute:
            return False
        
        self.request_count += 1
        return True
    
    def _update_metrics(self):
        """Atualiza métricas do provedor."""
        self.metrics["requests"] += 1
        self.metrics["last_request"] = datetime.now().isoformat()
    
    async def stop(self) -> bool:
        """
        Para o provedor OpenAI.
        
        Returns:
            True se a parada foi bem-sucedida
        """
        try:
            logger.info("Parando OpenAIProvider...")
            
            # Fecha o cliente se necessário
            if self.client:
                await self.client.close()
            
            logger.info("OpenAIProvider parado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao parar OpenAIProvider: {e}")
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Retorna o status do provedor.
        
        Returns:
            Dicionário com informações de status
        """
        return {
            "provider": "openai",
            "model": self.model,
            "initialized": self.is_initialized,
            "api_key_configured": bool(self.api_key),
            "client_available": self.client is not None,
            "rate_limit": {
                "requests_per_minute": self.requests_per_minute,
                "current_requests": self.request_count,
                "reset_time": self.reset_time.isoformat()
            },
            "metrics": self.metrics.copy()
        }
    
    async def health_check(self) -> bool:
        """
        Verifica a saúde do provedor.
        
        Returns:
            True se o provedor está saudável
        """
        try:
            if not self.is_initialized:
                return False
            
            # Testa conexão
            return await self._test_connection()
            
        except Exception as e:
            logger.error(f"Erro na verificação de saúde do OpenAIProvider: {e}")
            return False
    
    async def _initialize(self) -> bool:
        """
        Inicialização específica do provedor OpenAI.
        
        Returns:
            True se a inicialização foi bem-sucedida
        """
        try:
            # Verifica se a API key está configurada
            if not self.api_key:
                logger.error("API key do OpenAI não configurada")
                return False
            
            # Tenta importar o cliente OpenAI
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=self.api_key)
                logger.info("Cliente OpenAI inicializado com sucesso")
            except ImportError:
                logger.error("Biblioteca openai não instalada. Execute: pip install openai")
                return False
            
            # Testa a conexão
            success = await self._test_connection()
            if not success:
                logger.error("Falha no teste de conexão com OpenAI")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na inicialização do OpenAIProvider: {e}")
            return False
    
    async def _health_check(self) -> bool:
        """
        Verificação específica de saúde do provedor OpenAI.
        
        Returns:
            True se o provedor está saudável
        """
        try:
            if not self.is_initialized:
                return False
            
            # Testa conexão
            return await self._test_connection()
            
        except Exception as e:
            logger.error(f"Erro na verificação de saúde do OpenAIProvider: {e}")
            return False
    
    async def _stop(self) -> bool:
        """
        Parada específica do provedor OpenAI.
        
        Returns:
            True se a parada foi bem-sucedida
        """
        try:
            # Fecha o cliente se necessário
            if self.client:
                await self.client.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao parar OpenAIProvider: {e}")
            return False
