"""
Runtime core do sistema t031a5.

Contém as classes principais para execução do sistema:
- CortexRuntime: Loop principal do sistema
- ConfigManager: Gerenciamento de configurações
- InputOrchestrator: Coordenação de inputs
- ActionOrchestrator: Execução de ações
"""

from .cortex import CortexRuntime
from .config import ConfigManager
from .orchestrators import InputOrchestrator, ActionOrchestrator

__all__ = [
    "CortexRuntime",
    "ConfigManager", 
    "InputOrchestrator",
    "ActionOrchestrator",
]
