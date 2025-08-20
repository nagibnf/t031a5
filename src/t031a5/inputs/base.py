"""
Classe base para inputs do sistema t031a5.

Define a interface comum para todos os plugins de input do G1.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class InputData:
    """Estrutura de dados para inputs do sistema."""
    
    # Identificação do input
    input_type: str
    source: str
    timestamp: datetime
    
    # Dados do input
    data: Dict[str, Any]
    
    # Metadados
    confidence: float = 1.0
    priority: int = 1
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Inicialização pós-criação."""
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()


class BaseInput(ABC):
    """Classe base para todos os inputs do sistema t031a5."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o input base.
        
        Args:
            config: Configuração do input
        """
        self.config = config
        self.name = self.__class__.__name__
        self.is_initialized = False
        self.is_running = False
        self.last_data: Optional[InputData] = None
        
        # Configurações padrão
        self.enabled = config.get("enabled", True)
        self.priority = config.get("priority", 1)
        self.update_interval = config.get("update_interval", 1.0)
        
        logger.debug(f"Inicializando {self.name} com configuração: {config}")
    
    async def initialize(self) -> bool:
        """
        Inicializa o input.
        
        Returns:
            True se a inicialização foi bem-sucedida
        """
        try:
            if not self.enabled:
                logger.info(f"{self.name} está desabilitado")
                return True
            
            logger.info(f"Inicializando {self.name}...")
            
            # Inicialização específica do input
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
        Inicialização específica do input.
        
        Returns:
            True se a inicialização foi bem-sucedida
        """
        pass
    
    async def start(self) -> bool:
        """
        Inicia a captura de dados.
        
        Returns:
            True se o início foi bem-sucedido
        """
        try:
            if not self.is_initialized:
                logger.error(f"{self.name} não foi inicializado")
                return False
            
            if not self.enabled:
                logger.info(f"{self.name} está desabilitado")
                return True
            
            logger.info(f"Iniciando {self.name}...")
            
            # Início específico do input
            success = await self._start()
            
            if success:
                self.is_running = True
                logger.info(f"{self.name} iniciado com sucesso")
            else:
                logger.error(f"Falha ao iniciar {self.name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao iniciar {self.name}: {e}")
            return False
    
    @abstractmethod
    async def _start(self) -> bool:
        """
        Início específico do input.
        
        Returns:
            True se o início foi bem-sucedido
        """
        pass
    
    async def stop(self) -> bool:
        """
        Para a captura de dados.
        
        Returns:
            True se a parada foi bem-sucedida
        """
        try:
            if not self.is_running:
                logger.info(f"{self.name} não está rodando")
                return True
            
            logger.info(f"Parando {self.name}...")
            
            # Parada específica do input
            success = await self._stop()
            
            if success:
                self.is_running = False
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
        Parada específica do input.
        
        Returns:
            True se a parada foi bem-sucedida
        """
        pass
    
    async def get_data(self) -> Optional[InputData]:
        """
        Obtém os dados mais recentes do input.
        
        Returns:
            Dados do input ou None se não disponível
        """
        try:
            if not self.is_running:
                logger.debug(f"{self.name} não está rodando")
                return None
            
            # Captura específica de dados
            data = await self._get_data()
            
            if data is not None:
                self.last_data = data
                logger.debug(f"Dados obtidos de {self.name}: {data.input_type}")
            
            return data
            
        except Exception as e:
            logger.error(f"Erro ao obter dados de {self.name}: {e}")
            return None
    
    @abstractmethod
    async def _get_data(self) -> Optional[InputData]:
        """
        Captura específica de dados do input.
        
        Returns:
            Dados do input ou None se não disponível
        """
        pass
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Retorna o status atual do input.
        
        Returns:
            Dicionário com informações de status
        """
        return {
            "name": self.name,
            "enabled": self.enabled,
            "initialized": self.is_initialized,
            "running": self.is_running,
            "priority": self.priority,
            "update_interval": self.update_interval,
            "last_data": self.last_data is not None,
            "last_data_timestamp": self.last_data.timestamp if self.last_data else None,
        }
    
    def get_config(self) -> Dict[str, Any]:
        """
        Retorna a configuração atual do input.
        
        Returns:
            Configuração do input
        """
        return self.config.copy()
    
    async def update_config(self, new_config: Dict[str, Any]) -> bool:
        """
        Atualiza a configuração do input.
        
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
        Verifica a saúde do input.
        
        Returns:
            True se o input está saudável
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
        Verificação específica de saúde do input.
        
        Returns:
            True se o input está saudável
        """
        # Implementação padrão - assume que está saudável se está rodando
        return self.is_running
