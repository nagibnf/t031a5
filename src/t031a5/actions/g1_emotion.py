"""Action G1EmotionAction mock para o sistema t031a5."""

import logging
from typing import Any, Dict, Optional
from datetime import datetime

from .base import BaseAction, ActionRequest, ActionResult

logger = logging.getLogger(__name__)


class G1EmotionAction(BaseAction):
    """Action de emoção do G1 (implementação mock)."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.led_brightness = config.get("led_brightness", 0.7)
        logger.debug(f"G1EmotionAction configurado")
    
    async def _initialize(self) -> bool:
        logger.info("G1EmotionAction inicializado com sucesso")
        return True
    
    async def _start(self) -> bool:
        logger.info("G1EmotionAction iniciado com sucesso")
        return True
    
    async def _stop(self) -> bool:
        logger.info("G1EmotionAction parado com sucesso")
        return True
    
    async def _execute(self, request: ActionRequest) -> ActionResult:
        try:
            emotion = request.data.get("emotion", "neutral")
            logger.info(f"G1 expressando emoção: {emotion}")
            
            return ActionResult(
                action_type="emotion",
                action_name=request.action_name,
                timestamp=datetime.now(),
                success=True,
                data={"emotion": emotion, "led_brightness": self.led_brightness},
                execution_time=0.2
            )
        except Exception as e:
            logger.error(f"Erro ao executar emoção: {e}")
            return ActionResult(
                action_type="emotion",
                action_name=request.action_name,
                timestamp=datetime.now(),
                success=False,
                data={},
                error_message=str(e)
            )
    
    async def _health_check(self) -> bool:
        return True
