"""
Classe base para actions do sistema t031a5.

Define a interface comum para todos os plugins de action do G1.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ActionRequest:
    """Estrutura de dados para requisições de ação."""
    
    # Identificação da ação
    action_type: str
    action_name: str
    timestamp: datetime
    
    # Dados da ação
    data: Dict[str, Any]
    
    # Metadados
    priority: int = 1
    timeout: float = 30.0
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Inicialização pós-criação."""
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class ActionResult:
    """Estrutura de dados para resultados de ação."""
    
    # Identificação da ação
    action_type: str
    action_name: str
    timestamp: datetime
    
    # Resultado da ação
    success: bool
    data: Dict[str, Any]
    
    # Metadados
    execution_time: float = 0.0
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Inicialização pós-criação."""
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()


class BaseAction(ABC):
    """Classe base para todos os actions do sistema t031a5."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o action base.
        
        Args:
            config: Configuração do action
        """
        self.config = config
        self.name = self.__class__.__name__
        self.is_initialized = False
        self.is_running = False
        self.last_result: Optional[ActionResult] = None
        
        # Configurações padrão
        self.enabled = config.get("enabled", True)
        self.priority = config.get("priority", 1)
        self.timeout = config.get("timeout", 30.0)
        
        logger.debug(f"Inicializando {self.name} com configuração: {config}")
    
    async def initialize(self) -> bool:
        """
        Inicializa o action.
        
        Returns:
            True se a inicialização foi bem-sucedida
        """
        try:
            if not self.enabled:
                logger.info(f"{self.name} está desabilitado")
                return True
            
            logger.info(f"Inicializando {self.name}...")
            
            # Inicialização específica do action
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
        Inicialização específica do action.
        
        Returns:
            True se a inicialização foi bem-sucedida
        """
        pass
    
    async def start(self) -> bool:
        """
        Inicia o action.
        
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
            
            # Início específico do action
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
        Início específico do action.
        
        Returns:
            True se o início foi bem-sucedido
        """
        pass
    
    async def stop(self) -> bool:
        """
        Para o action.
        
        Returns:
            True se a parada foi bem-sucedida
        """
        try:
            if not self.is_running:
                logger.info(f"{self.name} não está rodando")
                return True
            
            logger.info(f"Parando {self.name}...")
            
            # Parada específica do action
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
        Parada específica do action.
        
        Returns:
            True se a parada foi bem-sucedida
        """
        pass
    
    async def execute(self, request: ActionRequest) -> ActionResult:
        """
        Executa uma ação.
        
        Args:
            request: Requisição de ação
            
        Returns:
            Resultado da execução
        """
        start_time = datetime.now()
        
        try:
            if not self.is_running:
                logger.error(f"{self.name} não está rodando")
                return ActionResult(
                    action_type=request.action_type,
                    action_name=request.action_name,
                    timestamp=datetime.now(),
                    success=False,
                    data={},
                    error_message=f"{self.name} não está rodando"
                )
            
            logger.debug(f"Executando {request.action_name} em {self.name}")
            
            # Execução específica da ação
            result = await self._execute(request)
            
            # Calcula tempo de execução
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time
            
            self.last_result = result
            logger.debug(f"Ação {request.action_name} executada em {execution_time:.3f}s")
            
            return result
            
        except asyncio.TimeoutError:
            logger.error(f"Timeout na execução de {request.action_name}")
            return ActionResult(
                action_type=request.action_type,
                action_name=request.action_name,
                timestamp=datetime.now(),
                success=False,
                data={},
                execution_time=(datetime.now() - start_time).total_seconds(),
                error_message="Timeout na execução"
            )
        except Exception as e:
            logger.error(f"Erro na execução de {request.action_name}: {e}")
            return ActionResult(
                action_type=request.action_type,
                action_name=request.action_name,
                timestamp=datetime.now(),
                success=False,
                data={},
                execution_time=(datetime.now() - start_time).total_seconds(),
                error_message=str(e)
            )
    
    @abstractmethod
    async def _execute(self, request: ActionRequest) -> ActionResult:
        """
        Execução específica da ação.
        
        Args:
            request: Requisição de ação
            
        Returns:
            Resultado da execução
        """
        pass
    
    async def emergency_stop(self) -> bool:
        """
        Para de emergência do action.
        
        Returns:
            True se a parada de emergência foi bem-sucedida
        """
        try:
            logger.warning(f"Parada de emergência de {self.name}")
            
            # Parada de emergência específica
            success = await self._emergency_stop()
            
            if success:
                self.is_running = False
                logger.warning(f"{self.name} parado de emergência com sucesso")
            else:
                logger.error(f"Falha na parada de emergência de {self.name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro na parada de emergência de {self.name}: {e}")
            return False
    
    async def _emergency_stop(self) -> bool:
        """
        Parada de emergência específica do action.
        
        Returns:
            True se a parada de emergência foi bem-sucedida
        """
        # Implementação padrão - chama a parada normal
        return await self._stop()
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Retorna o status atual do action.
        
        Returns:
            Dicionário com informações de status
        """
        return {
            "name": self.name,
            "enabled": self.enabled,
            "initialized": self.is_initialized,
            "running": self.is_running,
            "priority": self.priority,
            "timeout": self.timeout,
            "last_result": self.last_result is not None,
            "last_result_success": self.last_result.success if self.last_result else None,
            "last_result_timestamp": self.last_result.timestamp if self.last_result else None,
        }
    
    def get_config(self) -> Dict[str, Any]:
        """
        Retorna a configuração atual do action.
        
        Returns:
            Configuração do action
        """
        return self.config.copy()
    
    async def update_config(self, new_config: Dict[str, Any]) -> bool:
        """
        Atualiza a configuração do action.
        
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
        Verifica a saúde do action.
        
        Returns:
            True se o action está saudável
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
        Verificação específica de saúde do action.
        
        Returns:
            True se o action está saudável
        """
        # Implementação padrão - assume que está saudável se está rodando
        return self.is_running
