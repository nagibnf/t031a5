"""Action G1SpeechAction mock para o sistema t031a5."""

import logging
from typing import Any, Dict, Optional
from datetime import datetime

from .base import BaseAction, ActionRequest, ActionResult

logger = logging.getLogger(__name__)


class G1SpeechAction(BaseAction):
    """Action de fala do G1 (implementação mock)."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.tts_provider = config.get("tts_provider", "g1_native")
        self.voice_id = config.get("voice_id", "g1_default")
        logger.debug(f"G1SpeechAction configurado: {self.tts_provider}")
    
    async def _initialize(self) -> bool:
        logger.info("G1SpeechAction inicializado com sucesso")
        return True
    
    async def _start(self) -> bool:
        logger.info("G1SpeechAction iniciado com sucesso")
        return True
    
    async def _stop(self) -> bool:
        logger.info("G1SpeechAction parado com sucesso")
        return True
    
    async def _execute(self, request: ActionRequest) -> ActionResult:
        try:
            text = request.data.get("text", "Olá! Sou o G1.")
            logger.info(f"G1 falando: {text}")
            
            return ActionResult(
                action_type="speech",
                action_name=request.action_name,
                timestamp=datetime.now(),
                success=True,
                data={"text": text, "tts_provider": self.tts_provider},
                execution_time=0.5
            )
        except Exception as e:
            logger.error(f"Erro ao executar fala: {e}")
            return ActionResult(
                action_type="speech",
                action_name=request.action_name,
                timestamp=datetime.now(),
                success=False,
                data={},
                error_message=str(e)
            )
    
    async def _health_check(self) -> bool:
        return True
