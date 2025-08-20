"""
ConfigManager para o sistema t031a5.

Responsável por carregar, validar e gerenciar configurações do sistema G1.
"""

import json5
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union
from pydantic import BaseModel, Field, validator
import logging

logger = logging.getLogger(__name__)


class G1Config(BaseModel):
    """Configuração base do sistema G1."""
    
    # Configurações básicas
    hertz: int = Field(default=10, ge=1, le=100, description="Frequência de execução do loop principal")
    name: str = Field(default="g1_assistant", description="Nome do assistente")
    unitree_ethernet: str = Field(default="en0", description="Interface de rede para comunicação com G1")
    
    # Prompt do sistema
    system_prompt_base: str = Field(
        default="Você é um assistente robótico humanóide G1 da Unitree...",
        description="Prompt base do sistema"
    )
    
    # Configurações de desenvolvimento
    development: Dict[str, Any] = Field(
        default_factory=lambda: {
            "websim_enabled": False,
            "debug_mode": False,
            "hot_reload": False
        },
        description="Configurações de desenvolvimento"
    )
    
    # Configurações específicas do G1
    g1_specific: Dict[str, Any] = Field(
        default_factory=lambda: {
            "safety_mode": "normal",
            "emergency_stop": True,
            "battery_conservation": True,
            "thermal_management": True,
            "network_timeout": 5.0
        },
        description="Configurações específicas do G1"
    )


class ConfigManager:
    """Gerenciador de configurações do sistema t031a5."""
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """
        Inicializa o ConfigManager.
        
        Args:
            config_path: Caminho para o arquivo de configuração JSON5
        """
        self.config_path = Path(config_path) if config_path else None
        self.config: Optional[G1Config] = None
        self._raw_config: Dict[str, Any] = {}
        
    def load_config(self, config_path: Optional[Union[str, Path]] = None) -> G1Config:
        """
        Carrega configuração de um arquivo JSON5.
        
        Args:
            config_path: Caminho para o arquivo de configuração
            
        Returns:
            Configuração carregada e validada
            
        Raises:
            FileNotFoundError: Se o arquivo não for encontrado
            ValueError: Se a configuração for inválida
        """
        if config_path:
            self.config_path = Path(config_path)
        
        if not self.config_path or not self.config_path.exists():
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {self.config_path}")
        
        try:
            # Carrega o arquivo JSON5
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._raw_config = json5.load(f)
            
            # Valida e cria a configuração
            self.config = G1Config(**self._raw_config)
            
            logger.info(f"Configuração carregada com sucesso: {self.config_path}")
            logger.debug(f"Configuração: {self.config.dict()}")
            
            return self.config
            
        except Exception as e:
            raise ValueError(f"Erro ao decodificar JSON5: {e}")
        except Exception as e:
            raise ValueError(f"Erro ao carregar configuração: {e}")
    
    def get_config(self) -> G1Config:
        """
        Retorna a configuração atual.
        
        Returns:
            Configuração atual
            
        Raises:
            ValueError: Se nenhuma configuração foi carregada
        """
        if self.config is None:
            raise ValueError("Nenhuma configuração foi carregada. Use load_config() primeiro.")
        return self.config
    
    def get_raw_config(self) -> Dict[str, Any]:
        """
        Retorna a configuração raw (sem validação Pydantic).
        
        Returns:
            Configuração raw
            
        Raises:
            ValueError: Se nenhuma configuração foi carregada
        """
        if not self._raw_config:
            raise ValueError("Nenhuma configuração foi carregada. Use load_config() primeiro.")
        return self._raw_config.copy()
    
    def get_inputs_config(self) -> list:
        """
        Retorna a configuração dos inputs.
        
        Returns:
            Lista de configurações de inputs
        """
        inputs_dict = self._raw_config.get("agent_inputs", {})
        inputs_list = []
        
        for input_name, input_config in inputs_dict.items():
            if isinstance(input_config, dict):
                input_config["type"] = input_name
                inputs_list.append(input_config)
        
        return inputs_list
    
    def get_actions_config(self) -> list:
        """
        Retorna a configuração das actions.
        
        Returns:
            Lista de configurações de actions
        """
        actions_dict = self._raw_config.get("agent_actions", {})
        actions_list = []
        
        for action_name, action_config in actions_dict.items():
            if isinstance(action_config, dict):
                action_config["name"] = action_name
                # Converter para formato esperado pelo orchestrator (ex: G1Speech -> g1_speech)
                connector_name = "g1_" + action_name[2:].lower() if action_name.startswith("G1") else action_name.lower()
                action_config["connector"] = connector_name
                action_config["type"] = action_name
                actions_list.append(action_config)
        
        return actions_list
    
    def get_llm_config(self) -> Dict[str, Any]:
        """
        Retorna a configuração do LLM.
        
        Returns:
            Configuração do LLM
        """
        return self._raw_config.get("llm", {})
    
    def get_fuser_config(self) -> Dict[str, Any]:
        """
        Retorna a configuração do fuser.
        
        Returns:
            Configuração do fuser
        """
        return self._raw_config.get("fuser", {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """
        Retorna a configuração de logging.
        
        Returns:
            Configuração de logging
        """
        return self._raw_config.get("logging", {})
    
    def is_development_mode(self) -> bool:
        """
        Verifica se está em modo de desenvolvimento.
        
        Returns:
            True se estiver em modo de desenvolvimento
        """
        if self.config is None:
            return False
        return self.config.development.get("debug_mode", False)
    
    def is_websim_enabled(self) -> bool:
        """
        Verifica se o WebSim está habilitado.
        
        Returns:
            True se o WebSim estiver habilitado
        """
        if self.config is None:
            return False
        return self.config.development.get("websim_enabled", False)
    
    def get_websim_config(self) -> Dict[str, Any]:
        """
        Retorna a configuração do WebSim.
        
        Returns:
            Configuração do WebSim
        """
        if not self.is_websim_enabled():
            return {}
        
        if self.config is None:
            return {}
        
        return {
            "port": self.config.development.get("websim_port", 8080),
            "host": self.config.development.get("websim_host", "0.0.0.0"),
        }
    
    def reload_config(self) -> G1Config:
        """
        Recarrega a configuração do arquivo.
        
        Returns:
            Nova configuração carregada
        """
        if self.config_path is None:
            raise ValueError("Nenhum caminho de configuração definido")
        
        return self.load_config(self.config_path)
    
    def validate_environment(self) -> bool:
        """
        Valida se o ambiente está configurado corretamente.
        
        Returns:
            True se o ambiente estiver válido
        """
        try:
            # Verifica se as variáveis de ambiente necessárias estão definidas
            llm_config = self.get_llm_config()
            api_key_env = llm_config.get("api_key_env")
            
            if api_key_env and not os.getenv(api_key_env):
                logger.warning(f"Variável de ambiente {api_key_env} não está definida")
                return False
            
            # Verifica se os diretórios necessários existem
            logging_config = self.get_logging_config()
            log_file = logging_config.get("file")
            
            if log_file:
                log_dir = Path(log_file).parent
                log_dir.mkdir(parents=True, exist_ok=True)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao validar ambiente: {e}")
            return False
