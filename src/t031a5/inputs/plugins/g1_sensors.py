"""Plugin G1SensorsInput mock para o sistema t031a5."""

import logging
from typing import Any, Dict, Optional
from datetime import datetime

from ..base import BaseInput, InputData

logger = logging.getLogger(__name__)


class G1SensorsInput(BaseInput):
    """Input de sensores do G1 (implementação mock)."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.update_interval = config.get("update_interval", 1.0)
        logger.debug(f"G1SensorsInput configurado")
    
    async def _initialize(self) -> bool:
        logger.info("G1SensorsInput inicializado com sucesso")
        return True
    
    async def _start(self) -> bool:
        logger.info("G1SensorsInput iniciado com sucesso")
        return True
    
    async def _stop(self) -> bool:
        logger.info("G1SensorsInput parado com sucesso")
        return True
    
    async def _get_data(self) -> Optional[InputData]:
        try:
            sensors_data = {
                "battery": 85,
                "temperature": 32.5,
                "imu": {"roll": 0.1, "pitch": 0.2, "yaw": 0.3},
                "timestamp": datetime.now().isoformat()
            }
            
            return InputData(
                input_type="G1Sensors",
                source="g1_sensors",
                timestamp=datetime.now(),
                data=sensors_data,
                confidence=0.9
            )
        except Exception as e:
            logger.error(f"Erro ao capturar dados de sensores: {e}")
            return None
    
    async def _health_check(self) -> bool:
        return True
