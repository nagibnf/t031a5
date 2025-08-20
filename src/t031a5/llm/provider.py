"""
LLM Provider base para o sistema t031a5.

Gerencia diferentes provedores de LLM e fornece interface unificada.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from ..fuser.base import FusedData

logger = logging.getLogger(__name__)


@dataclass
class LLMRequest:
    """Estrutura de dados para requisições ao LLM."""
    
    # Dados de entrada
    fused_data: FusedData
    system_prompt: str
    
    # Configurações da requisição
    model: str
    temperature: float = 0.7
    max_tokens: int = 500
    timeout: float = 30.0
    
    # Metadados
    timestamp: datetime = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Inicialização pós-criação."""
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class LLMResponse:
    """Estrutura de dados para respostas do LLM."""
    
    # Conteúdo da resposta
    content: str
    model: str
    
    # Metadados da resposta
    timestamp: datetime
    tokens_used: int = 0
    response_time: float = 0.0
    
    # Metadados adicionais
    finish_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Inicialização pós-criação."""
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()


class BaseLLMProvider(ABC):
    """Classe base para provedores de LLM."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o provedor base.
        
        Args:
            config: Configuração do provedor
        """
        self.config = config
        self.name = self.__class__.__name__
        self.is_initialized = False
        
        # Configurações padrão
        self.enabled = config.get("enabled", True)
        self.model = config.get("model", "gpt-4o-mini")
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 500)
        self.timeout = config.get("timeout", 30.0)
        
        logger.debug(f"Inicializando {self.name} com configuração: {config}")
    
    async def initialize(self) -> bool:
        """
        Inicializa o provedor.
        
        Returns:
            True se a inicialização foi bem-sucedida
        """
        try:
            if not self.enabled:
                logger.info(f"{self.name} está desabilitado")
                return True
            
            logger.info(f"Inicializando {self.name}...")
            
            # Inicialização específica do provedor
            success = await self._initialize()
            
            if success:
                self.is_initialized = True
                logger.info(f"{self.name} inicializado com sucesso")
            else:
                logger.error(f"Falha na inicialização de {self.name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro na inicialização de {self.name}: {e}")
            return False
    
    @abstractmethod
    async def _initialize(self) -> bool:
        """
        Inicialização específica do provedor.
        
        Returns:
            True se a inicialização foi bem-sucedida
        """
        pass
    
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
    
    @abstractmethod
    async def _process(self, request: LLMRequest) -> Optional[LLMResponse]:
        """
        Processamento específico da requisição.
        
        Args:
            request: Requisição para o LLM
            
        Returns:
            Resposta do LLM ou None se falhar
        """
        pass
    
    async def stop(self) -> bool:
        """
        Para o provedor.
        
        Returns:
            True se a parada foi bem-sucedida
        """
        try:
            logger.info(f"Parando {self.name}...")
            
            # Parada específica do provedor
            success = await self._stop()
            
            if success:
                logger.info(f"{self.name} parado com sucesso")
            else:
                logger.error(f"Falha ao parar {self.name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao parar {self.name}: {e}")
            return False
    
    @abstractmethod
    async def _stop(self) -> bool:
        """
        Parada específica do provedor.
        
        Returns:
            True se a parada foi bem-sucedida
        """
        pass
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Retorna o status atual do provedor.
        
        Returns:
            Dicionário com informações de status
        """
        return {
            "name": self.name,
            "enabled": self.enabled,
            "initialized": self.is_initialized,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
        }
    
    def get_config(self) -> Dict[str, Any]:
        """
        Retorna a configuração atual do provedor.
        
        Returns:
            Configuração do provedor
        """
        return self.config.copy()
    
    async def health_check(self) -> bool:
        """
        Verifica a saúde do provedor.
        
        Returns:
            True se o provedor está saudável
        """
        try:
            if not self.enabled:
                return True
            
            # Verificação específica de saúde
            healthy = await self._health_check()
            
            if not healthy:
                logger.warning(f"{self.name} não está saudável")
            
            return healthy
            
        except Exception as e:
            logger.error(f"Erro na verificação de saúde de {self.name}: {e}")
            return False
    
    @abstractmethod
    async def _health_check(self) -> bool:
        """
        Verificação específica de saúde do provedor.
        
        Returns:
            True se o provedor está saudável
        """
        pass


class LLMProvider:
    """Gerenciador principal de LLM do sistema t031a5."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o LLM Provider.
        
        Args:
            config: Configuração do LLM
        """
        self.config = config
        self.provider: Optional[BaseLLMProvider] = None
        
        # Configurações
        self.provider_type = config.get("provider", "openai")
        self.fallback_provider = config.get("fallback_provider", None)
        
        logger.debug(f"LLMProvider configurado com provedor: {self.provider_type}")
    
    async def initialize(self) -> bool:
        """
        Inicializa o provedor de LLM.
        
        Returns:
            True se a inicialização foi bem-sucedida
        """
        try:
            logger.info("Inicializando LLM Provider...")
            
            # Cria o provedor apropriado
            self.provider = await self._create_provider()
            
            if not self.provider:
                logger.error("Falha ao criar provedor de LLM")
                return False
            
            # Inicializa o provedor
            success = await self.provider.initialize()
            
            if success:
                logger.info("LLM Provider inicializado com sucesso")
            else:
                logger.error("Falha na inicialização do LLM Provider")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro na inicialização do LLM Provider: {e}")
            return False
    
    async def _create_provider(self) -> Optional[BaseLLMProvider]:
        """
        Cria o provedor de LLM apropriado.
        
        Returns:
            Provedor de LLM ou None se falhar
        """
        try:
            if self.provider_type == "openai":
                try:
                    from .providers.openai_provider import OpenAIProvider
                    return OpenAIProvider(self.config)
                except ImportError:
                    logger.warning("OpenAI provider não disponível, usando mock")
                    from .providers.mock_provider import MockLLMProvider
                    return MockLLMProvider(self.config)
            elif self.provider_type == "anthropic":
                try:
                    from .providers.anthropic_provider import AnthropicProvider
                    return AnthropicProvider(self.config)
                except ImportError:
                    logger.warning("Anthropic provider não disponível, usando mock")
                    from .providers.mock_provider import MockLLMProvider
                    return MockLLMProvider(self.config)
            elif self.provider_type == "mock":
                from .providers.mock_provider import MockLLMProvider
                return MockLLMProvider(self.config)
            else:
                logger.warning(f"Provedor de LLM não suportado: {self.provider_type}, usando mock")
                from .providers.mock_provider import MockLLMProvider
                return MockLLMProvider(self.config)
                
        except Exception as e:
            logger.error(f"Erro ao criar provedor {self.provider_type}: {e}")
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
            if not self.provider:
                logger.error("LLM Provider não foi inicializado")
                return None
            
            # Tenta com o provedor principal
            response = await self.provider.process(fused_data, system_prompt)
            
            if response:
                return response
            
            # Tenta com o provedor de fallback se disponível
            if self.fallback_provider and self.fallback_provider != self.provider_type:
                logger.info(f"Tentando provedor de fallback: {self.fallback_provider}")
                
                # Cria provedor de fallback
                fallback_config = self.config.copy()
                fallback_config["provider"] = self.fallback_provider
                
                fallback_provider = await self._create_provider()
                if fallback_provider:
                    await fallback_provider.initialize()
                    response = await fallback_provider.process(fused_data, system_prompt)
                    await fallback_provider.stop()
                    
                    if response:
                        logger.info("Resposta obtida do provedor de fallback")
                        return response
            
            logger.warning("Nenhum provedor de LLM respondeu")
            return None
            
        except Exception as e:
            logger.error(f"Erro no processamento LLM: {e}")
            return None
    
    async def stop(self) -> bool:
        """
        Para o LLM Provider.
        
        Returns:
            True se a parada foi bem-sucedida
        """
        try:
            if self.provider:
                return await self.provider.stop()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao parar LLM Provider: {e}")
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Retorna o status atual do LLM Provider.
        
        Returns:
            Dicionário com informações de status
        """
        provider_status = {}
        if self.provider:
            provider_status = await self.provider.get_status()
        
        return {
            "provider_type": self.provider_type,
            "fallback_provider": self.fallback_provider,
            "provider_initialized": self.provider is not None,
            "provider_status": provider_status
        }
    
    async def health_check(self) -> bool:
        """
        Verifica a saúde do LLM Provider.
        
        Returns:
            True se está saudável
        """
        try:
            if not self.provider:
                return False
            
            return await self.provider.health_check()
            
        except Exception as e:
            logger.error(f"Erro na verificação de saúde do LLM Provider: {e}")
            return False
