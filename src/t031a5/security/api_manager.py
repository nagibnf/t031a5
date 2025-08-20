"""
Gerenciador Simples de APIs.
Gerencia chaves de API usando arquivo .env.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class APIConfig:
    """Configuração de uma API."""
    name: str
    key: str
    provider: str
    enabled: bool = True
    timeout: float = 30.0


class SimpleAPIManager:
    """Gerenciador simples de APIs usando .env."""
    
    def __init__(self):
        self.apis: Dict[str, APIConfig] = {}
        self.logger = logging.getLogger(__name__)
        self.logger.info("SimpleAPIManager inicializado")
    
    def _load_env_file(self, env_path: Path = None) -> None:
        """Carrega variáveis de ambiente do arquivo .env"""
        if env_path is None:
            env_path = Path(".env")
        
        if not env_path.exists():
            return
        
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key and value and not value.startswith('sk-') and not value.startswith('sua_chave'):
                            os.environ[key] = value
        except Exception as e:
            self.logger.warning(f"Erro ao carregar .env: {e}")
    
    def _load_credential_files(self) -> None:
        """Carrega arquivos de credenciais."""
        credentials_dir = Path("credentials")
        if not credentials_dir.exists():
            return
        
        # Google ASR - arquivo JSON
        google_asr_file = credentials_dir / "google_asr.json"
        if google_asr_file.exists():
            os.environ["GOOGLE_ASR_CREDENTIALS_FILE"] = str(google_asr_file.absolute())
            self.logger.info(f"Google ASR: arquivo carregado")
        else:
            self.logger.info(f"Google ASR: arquivo não encontrado (opcional)")
    
    def load_from_env(self) -> None:
        """Carrega APIs de variáveis de ambiente."""
        self._load_env_file()
        self._load_credential_files()
        
        env_apis = {
            "OPENAI_API_KEY": ("openai", "openai"),
            "ANTHROPIC_API_KEY": ("anthropic", "anthropic"),
            "GOOGLE_API_KEY": ("google", "google"),
            "AZURE_OPENAI_API_KEY": ("azure_openai", "azure"),
            "COHERE_API_KEY": ("cohere", "cohere"),
            "ELEVENLABS_API_KEY": ("elevenlabs", "elevenlabs"),
            "GOOGLE_ASR_CREDENTIALS_FILE": ("google_asr", "google_asr")
        }
        
        for env_var, (name, provider) in env_apis.items():
            api_key = os.getenv(env_var)
            if api_key:
                # Verificar se não é placeholder
                if not api_key.startswith('sk-') and not api_key.startswith('sua_chave') and not api_key.startswith('credentials/'):
                    self.apis[name] = APIConfig(
                        name=name,
                        key=api_key,
                        provider=provider
                    )
                    self.logger.info(f"API '{name}' carregada de variável de ambiente")
    
    def get_api(self, name: str) -> Optional[APIConfig]:
        """Obtém configuração de uma API."""
        return self.apis.get(name)
    
    def get_api_key(self, name: str) -> Optional[str]:
        """Obtém chave de uma API."""
        api = self.get_api(name)
        return api.key if api else None
    
    def is_api_enabled(self, name: str) -> bool:
        """Verifica se uma API está habilitada."""
        api = self.get_api(name)
        return api.enabled if api else False
    
    def list_apis(self) -> Dict[str, Dict[str, Any]]:
        """Lista todas as APIs (sem mostrar chaves)."""
        return {
            name: {
                "provider": api.provider,
                "enabled": api.enabled,
                "timeout": api.timeout
            }
            for name, api in self.apis.items()
        }
    
    def validate_apis(self) -> Dict[str, bool]:
        """Valida todas as APIs configuradas."""
        results = {}
        
        for name, api in self.apis.items():
            if api.enabled:
                # Validação básica (chave não vazia e não é placeholder)
                results[name] = bool(api.key and len(api.key) > 10 and not api.key.startswith('sk-'))
            else:
                results[name] = True  # Desabilitada = válida
        
        return results
    
    def get_secure_config(self) -> Dict[str, Any]:
        """Obtém configuração segura para o sistema."""
        return {
            "openai": {
                "api_key": self.get_api_key("openai"),
                "enabled": self.is_api_enabled("openai")
            },
            "anthropic": {
                "api_key": self.get_api_key("anthropic"),
                "enabled": self.is_api_enabled("anthropic")
            },
            "google": {
                "api_key": self.get_api_key("google"),
                "enabled": self.is_api_enabled("google")
            },
            "elevenlabs": {
                "api_key": self.get_api_key("elevenlabs"),
                "enabled": self.is_api_enabled("elevenlabs")
            }
        }
    
    def initialize(self) -> None:
        """Inicializa o gerenciador."""
        # Carrega de variáveis de ambiente
        self.load_from_env()
        
        self.logger.info(f"Gerenciador inicializado com {len(self.apis)} APIs")
