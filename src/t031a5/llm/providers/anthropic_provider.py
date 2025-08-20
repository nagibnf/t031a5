"""
Provedor Anthropic para o sistema t031a5.

Integração com Claude via Anthropic API.
"""

import asyncio
import logging
import json
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..provider import LLMRequest, LLMResponse, BaseLLMProvider
from ...fuser.base import FusedData

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseLLMProvider):
    """Provedor Anthropic para Claude."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o provedor Anthropic.
        
        Args:
            config: Configuração do provedor
        """
        super().__init__(config)
        
        # Configurações específicas do Anthropic
        self.api_key = config.get("api_key")
        self.model = config.get("model", "claude-3-5-sonnet-20241022")
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 1000)
        self.timeout = config.get("timeout", 30.0)
        
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
        
        # Cliente Anthropic (será inicializado se disponível)
        self.client = None
        
        # Métricas
        self.metrics = {
            "requests": 0,
            "errors": 0,
            "last_request": None
        }
        
        logger.debug(f"AnthropicProvider configurado: {self.model}, temp={self.temperature}")
    
    async def initialize(self) -> bool:
        """
        Inicializa o provedor Anthropic.
        
        Returns:
            True se a inicialização foi bem-sucedida
        """
        try:
            logger.info("Inicializando AnthropicProvider...")
            
            # Verifica se a API key está configurada
            if not self.api_key:
                logger.error("API key do Anthropic não configurada")
                return False
            
            # Tenta importar o cliente Anthropic
            try:
                import anthropic
                self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
                logger.info("Cliente Anthropic inicializado com sucesso")
            except ImportError:
                logger.error("Biblioteca anthropic não instalada. Execute: pip install anthropic")
                return False
            
            # Testa a conexão
            success = await self._test_connection()
            if not success:
                logger.error("Falha no teste de conexão com Anthropic")
                return False
            
            self.is_initialized = True
            logger.info("AnthropicProvider inicializado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro na inicialização do AnthropicProvider: {e}")
            return False
    
    async def _test_connection(self) -> bool:
        """
        Testa a conexão com a API Anthropic.
        
        Returns:
            True se a conexão está funcionando
        """
        try:
            # Teste simples com uma requisição pequena
            test_fused_data = FusedData(
                content="Teste de conexão",
                confidence=1.0,
                source="test",
                timestamp=1234567890.0,
                metadata={"test": True}
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
            logger.error(f"Erro no processamento Anthropic: {e}")
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
        Faz uma requisição para a API Anthropic.
        
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
                "max_tokens": self.max_tokens,
                "timeout": self.timeout
            }
            
            # Faz a requisição
            logger.debug(f"Fazendo requisição para Anthropic: {self.model}")
            
            response = await asyncio.wait_for(
                self.client.messages.create(**params),
                timeout=self.timeout
            )
            
            # Processa a resposta
            content = response.content[0].text
            usage = response.usage
            
            # Cria a resposta
            llm_response = LLMResponse(
                content=content,
                model=self.model,
                timestamp=datetime.now(),
                tokens_used=usage.input_tokens + usage.output_tokens if usage else 0,
                metadata={
                    "anthropic_response_id": response.id,
                    "stop_reason": response.stop_reason,
                    "model": self.model,
                    "input_tokens": usage.input_tokens if usage else 0,
                    "output_tokens": usage.output_tokens if usage else 0,
                    "provider": "anthropic"
                }
            )
            
            logger.debug(f"Resposta Anthropic recebida: {len(content)} chars")
            return llm_response
            
        except asyncio.TimeoutError:
            logger.error("Timeout na requisição Anthropic")
            return None
        except Exception as e:
            logger.error(f"Erro na requisição Anthropic: {e}")
            return None
    
    def _prepare_messages(self, request: LLMRequest) -> List[Dict[str, Any]]:
        """
        Prepara as mensagens para a API Anthropic.
        
        Args:
            request: Requisição LLM
            
        Returns:
            Lista de mensagens formatadas
        """
        messages = []
        
        # Conteúdo principal
        content = request.fused_data.content
        
        # Adiciona contexto se disponível
        if request.fused_data.metadata:
            context_parts = []
            
            # Informações de sensores
            if self.include_sensors and "sensors" in request.fused_data.metadata:
                sensors = request.fused_data.metadata["sensors"]
                if sensors:
                    context_parts.append(f"Sensores: {json.dumps(sensors, ensure_ascii=False)}")
            
            # Informações de localização
            if self.include_location and "gps" in request.fused_data.metadata:
                gps = request.fused_data.metadata["gps"]
                if gps:
                    context_parts.append(f"Localização: {json.dumps(gps, ensure_ascii=False)}")
            
            # Estado do robô
            if self.include_robot_state and "robot_state" in request.fused_data.metadata:
                state = request.fused_data.metadata["robot_state"]
                if state:
                    context_parts.append(f"Estado do robô: {json.dumps(state, ensure_ascii=False)}")
            
            # Adiciona contexto se houver
            if context_parts:
                context = "\n".join(context_parts)
                content = f"Contexto:\n{context}\n\nPergunta:\n{content}"
        
        # Adiciona system prompt se disponível
        if request.system_prompt:
            content = f"System: {request.system_prompt}\n\nUser: {content}"
        
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
        Para o provedor Anthropic.
        
        Returns:
            True se a parada foi bem-sucedida
        """
        try:
            logger.info("Parando AnthropicProvider...")
            
            # Fecha o cliente se necessário
            if self.client:
                await self.client.close()
            
            logger.info("AnthropicProvider parado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao parar AnthropicProvider: {e}")
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Retorna o status do provedor.
        
        Returns:
            Dicionário com informações de status
        """
        return {
            "provider": "anthropic",
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
            logger.error(f"Erro na verificação de saúde do AnthropicProvider: {e}")
            return False
    
    async def _initialize(self) -> bool:
        """
        Inicialização específica do provedor Anthropic.
        
        Returns:
            True se a inicialização foi bem-sucedida
        """
        try:
            # Verifica se a API key está configurada
            if not self.api_key:
                logger.error("API key do Anthropic não configurada")
                return False
            
            # Tenta importar o cliente Anthropic
            try:
                import anthropic
                self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
                logger.info("Cliente Anthropic inicializado com sucesso")
            except ImportError:
                logger.error("Biblioteca anthropic não instalada. Execute: pip install anthropic")
                return False
            
            # Testa a conexão
            success = await self._test_connection()
            if not success:
                logger.error("Falha no teste de conexão com Anthropic")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na inicialização do AnthropicProvider: {e}")
            return False
    
    async def _health_check(self) -> bool:
        """
        Verificação específica de saúde do provedor Anthropic.
        
        Returns:
            True se o provedor está saudável
        """
        try:
            if not self.is_initialized:
                return False
            
            # Testa conexão
            return await self._test_connection()
            
        except Exception as e:
            logger.error(f"Erro na verificação de saúde do AnthropicProvider: {e}")
            return False
    
    async def _stop(self) -> bool:
        """
        Parada específica do provedor Anthropic.
        
        Returns:
            True se a parada foi bem-sucedida
        """
        try:
            # Fecha o cliente se necessário
            if self.client:
                await self.client.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao parar AnthropicProvider: {e}")
            return False
