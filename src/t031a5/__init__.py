"""
t031a5 - Sistema OM1 Focado no G1

Sistema de IA multimodal baseado na arquitetura OM1, otimizado especificamente 
para o robô humanóide G1 da Unitree.
"""

__version__ = "0.1.0"
__author__ = "t031a5 Team"
__email__ = "dev@t031a5.org"

from .runtime.cortex import CortexRuntime
from .runtime.config import ConfigManager

__all__ = [
    "CortexRuntime",
    "ConfigManager",
    "__version__",
    "__author__",
    "__email__",
]
