"""
Classe base para fusão de inputs do sistema t031a5.

Define a interface comum para todos os fusores de inputs do G1.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from ..inputs.base import InputData

logger = logging.getLogger(__name__)


@dataclass
class FusedData:
    """Estrutura de dados para dados fundidos."""
    
    # Identificação dos dados fundidos
    fusion_type: str
    timestamp: datetime
    
    # Dados fundidos
    data: Dict[str, Any]
    
    # Metadados
    confidence: float = 1.0
    source_inputs: List[str] = None
    fusion_metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Inicialização pós-criação."""
        if self.source_inputs is None:
            self.source_inputs = []
        if self.fusion_metadata is None:
            self.fusion_metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()


class BaseFuser(ABC):
    """Classe base para todos os fusores do sistema t031a5."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o fuser base.
        
        Args:
            config: Configuração do fuser
        """
        self.config = config
        self.name = self.__class__.__name__
        self.is_initialized = False
        self.last_fused_data: Optional[FusedData] = None
        
        # Configurações padrão
        self.enabled = config.get("enabled", True)
        self.fusion_timeout = config.get("fusion_timeout", 5.0)
        self.context_window = config.get("context_window", 10)
        
        # Histórico de dados
        self.input_history: List[InputData] = []
        
        logger.debug(f"Inicializando {self.name} com configuração: {config}")
    
    async def initialize(self) -> bool:
        """
        Inicializa o fuser.
        
        Returns:
            True se a inicialização foi bem-sucedida
        """
        try:
            if not self.enabled:
                logger.info(f"{self.name} está desabilitado")
                return True
            
            logger.info(f"Inicializando {self.name}...")
            
            # Inicialização específica do fuser
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
        Inicialização específica do fuser.
        
        Returns:
            True se a inicialização foi bem-sucedida
        """
        pass
    
    async def fuse(self, inputs_data: List[InputData]) -> Optional[FusedData]:
        """
        Funde múltiplos inputs em um único conjunto de dados.
        
        Args:
            inputs_data: Lista de dados de inputs
            
        Returns:
            Dados fundidos ou None se não for possível fundir
        """
        try:
            if not self.is_initialized:
                logger.error(f"{self.name} não foi inicializado")
                return None
            
            if not self.enabled:
                logger.debug(f"{self.name} está desabilitado")
                return None
            
            if not inputs_data:
                logger.debug("Nenhum dado de input para fundir")
                return None
            
            # Adiciona dados ao histórico
            self._update_history(inputs_data)
            
            logger.debug(f"Fundindo {len(inputs_data)} inputs com {self.name}")
            
            # Fusão específica
            fused_data = await self._fuse(inputs_data)
            
            if fused_data is not None:
                self.last_fused_data = fused_data
                logger.debug(f"Dados fundidos com sucesso: {fused_data.fusion_type}")
            
            return fused_data
            
        except asyncio.TimeoutError:
            logger.error(f"Timeout na fusão de dados com {self.name}")
            return None
        except Exception as e:
            logger.error(f"Erro na fusão de dados com {self.name}: {e}")
            return None
    
    @abstractmethod
    async def _fuse(self, inputs_data: List[InputData]) -> Optional[FusedData]:
        """
        Fusão específica de dados.
        
        Args:
            inputs_data: Lista de dados de inputs
            
        Returns:
            Dados fundidos ou None se não for possível fundir
        """
        pass
    
    def _update_history(self, inputs_data: List[InputData]):
        """
        Atualiza o histórico de inputs.
        
        Args:
            inputs_data: Novos dados de inputs
        """
        # Adiciona novos dados ao histórico
        self.input_history.extend(inputs_data)
        
        # Mantém apenas os dados mais recentes
        if len(self.input_history) > self.context_window:
            self.input_history = self.input_history[-self.context_window:]
    
    def get_history(self) -> List[InputData]:
        """
        Retorna o histórico de inputs.
        
        Returns:
            Lista de dados históricos
        """
        return self.input_history.copy()
    
    def clear_history(self):
        """Limpa o histórico de inputs."""
        self.input_history.clear()
        logger.debug("Histórico de inputs limpo")
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Retorna o status atual do fuser.
        
        Returns:
            Dicionário com informações de status
        """
        return {
            "name": self.name,
            "enabled": self.enabled,
            "initialized": self.is_initialized,
            "fusion_timeout": self.fusion_timeout,
            "context_window": self.context_window,
            "history_size": len(self.input_history),
            "last_fused_data": self.last_fused_data is not None,
            "last_fused_data_timestamp": self.last_fused_data.timestamp if self.last_fused_data else None,
        }
    
    def get_config(self) -> Dict[str, Any]:
        """
        Retorna a configuração atual do fuser.
        
        Returns:
            Configuração do fuser
        """
        return self.config.copy()
    
    async def update_config(self, new_config: Dict[str, Any]) -> bool:
        """
        Atualiza a configuração do fuser.
        
        Args:
            new_config: Nova configuração
            
        Returns:
            True se a atualização foi bem-sucedida
        """
        try:
            logger.info(f"Atualizando configuração de {self.name}")
            
            # Atualização específica da configuração
            success = await self._update_config(new_config)
            
            if success:
                self.config.update(new_config)
                
                # Atualiza configurações locais
                self.fusion_timeout = new_config.get("fusion_timeout", self.fusion_timeout)
                self.context_window = new_config.get("context_window", self.context_window)
                
                logger.info(f"Configuração de {self.name} atualizada com sucesso")
            else:
                logger.error(f"Falha ao atualizar configuração de {self.name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao atualizar configuração de {self.name}: {e}")
            return False
    
    async def _update_config(self, new_config: Dict[str, Any]) -> bool:
        """
        Atualização específica da configuração.
        
        Args:
            new_config: Nova configuração
            
        Returns:
            True se a atualização foi bem-sucedida
        """
        # Implementação padrão - aceita qualquer configuração
        return True
    
    async def health_check(self) -> bool:
        """
        Verifica a saúde do fuser.
        
        Returns:
            True se o fuser está saudável
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
    
    async def _health_check(self) -> bool:
        """
        Verificação específica de saúde do fuser.
        
        Returns:
            True se o fuser está saudável
        """
        # Implementação padrão - assume que está saudável se está inicializado
        return self.is_initialized
    
    async def stop(self) -> bool:
        """
        Para o fuser.
        
        Returns:
            True se a parada foi bem-sucedida
        """
        try:
            logger.info(f"Parando {self.name}...")
            
            # Parada específica do fuser
            success = await self._stop()
            
            if success:
                logger.info(f"{self.name} parado com sucesso")
            else:
                logger.error(f"Falha ao parar {self.name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao parar {self.name}: {e}")
            return False
    
    async def _stop(self) -> bool:
        """
        Parada específica do fuser.
        
        Returns:
            True se a parada foi bem-sucedida
        """
        # Implementação padrão - limpa histórico
        self.clear_history()
        return True
    
    def get_input_types(self) -> List[str]:
        """
        Retorna os tipos de input suportados pelo fuser.
        
        Returns:
            Lista de tipos de input suportados
        """
        return self._get_supported_input_types()
    
    @abstractmethod
    def _get_supported_input_types(self) -> List[str]:
        """
        Retorna os tipos de input suportados.
        
        Returns:
            Lista de tipos de input suportados
        """
        pass
    
    def can_fuse(self, inputs_data: List[InputData]) -> bool:
        """
        Verifica se o fuser pode fundir os dados fornecidos.
        
        Args:
            inputs_data: Lista de dados de inputs
            
        Returns:
            True se pode fundir os dados
        """
        if not inputs_data:
            return False
        
        # Verifica se todos os tipos são suportados
        supported_types = self._get_supported_input_types()
        input_types = [data.input_type for data in inputs_data]
        
        return all(input_type in supported_types for input_type in input_types)
