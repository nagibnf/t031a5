"""
Fuser de prioridade para o sistema t031a5.

Combina inputs baseado em prioridades, selecionando o input de maior prioridade
quando múltiplos inputs estão disponíveis simultaneamente.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base import BaseFuser, FusedData
from ..inputs.base import InputData

logger = logging.getLogger(__name__)


class PriorityFuser(BaseFuser):
    """Fuser que combina inputs baseado em prioridades."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o PriorityFuser.
        
        Args:
            config: Configuração do fuser
        """
        super().__init__(config)
        
        # Configurações específicas de prioridade
        self.priority_weights = config.get("priority_weights", {})
        self.fallback_input = config.get("fallback_input", None)
        self.min_confidence = config.get("min_confidence", 0.5)
        
        logger.debug(f"PriorityFuser configurado com pesos: {self.priority_weights}")
    
    async def _initialize(self) -> bool:
        """
        Inicialização específica do PriorityFuser.
        
        Returns:
            True se a inicialização foi bem-sucedida
        """
        try:
            # Validação de configuração
            if not self.priority_weights:
                logger.warning("PriorityFuser sem pesos de prioridade configurados")
            
            logger.info("PriorityFuser inicializado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro na inicialização do PriorityFuser: {e}")
            return False
    
    async def _fuse(self, inputs_data: List[InputData]) -> Optional[FusedData]:
        """
        Fusão baseada em prioridade.
        
        Args:
            inputs_data: Lista de dados de inputs
            
        Returns:
            Dados fundidos baseados em prioridade
        """
        try:
            if not inputs_data:
                return None
            
            # Filtra inputs por confiança mínima
            valid_inputs = [
                data for data in inputs_data 
                if data.confidence >= self.min_confidence
            ]
            
            if not valid_inputs:
                logger.debug("Nenhum input com confiança suficiente")
                return None
            
            # Seleciona input de maior prioridade
            selected_input = self._select_highest_priority(valid_inputs)
            
            if not selected_input:
                logger.debug("Nenhum input selecionado por prioridade")
                return None
            
            # Cria dados fundidos
            fused_data = FusedData(
                fusion_type="priority",
                timestamp=datetime.now(),
                data=selected_input.data,
                confidence=selected_input.confidence,
                source_inputs=[selected_input.input_type],
                fusion_metadata={
                    "selected_input": selected_input.input_type,
                    "priority_score": self._calculate_priority_score(selected_input),
                    "total_inputs": len(inputs_data),
                    "valid_inputs": len(valid_inputs)
                }
            )
            
            logger.debug(f"Input selecionado por prioridade: {selected_input.input_type}")
            return fused_data
            
        except Exception as e:
            logger.error(f"Erro na fusão por prioridade: {e}")
            return None
    
    def _select_highest_priority(self, inputs_data: List[InputData]) -> Optional[InputData]:
        """
        Seleciona o input de maior prioridade.
        
        Args:
            inputs_data: Lista de dados de inputs válidos
            
        Returns:
            Input de maior prioridade ou None
        """
        if not inputs_data:
            return None
        
        # Se há apenas um input, retorna ele
        if len(inputs_data) == 1:
            return inputs_data[0]
        
        # Calcula pontuação de prioridade para cada input
        scored_inputs = []
        for input_data in inputs_data:
            priority_score = self._calculate_priority_score(input_data)
            scored_inputs.append((priority_score, input_data))
        
        # Ordena por pontuação de prioridade (maior primeiro)
        scored_inputs.sort(key=lambda x: x[0], reverse=True)
        
        # Retorna o input de maior prioridade
        return scored_inputs[0][1]
    
    def _calculate_priority_score(self, input_data: InputData) -> float:
        """
        Calcula a pontuação de prioridade para um input.
        
        Args:
            input_data: Dados do input
            
        Returns:
            Pontuação de prioridade
        """
        # Pontuação base da prioridade do input
        base_priority = input_data.priority
        
        # Peso específico do tipo de input
        type_weight = self.priority_weights.get(input_data.input_type, 1.0)
        
        # Fator de confiança
        confidence_factor = input_data.confidence
        
        # Pontuação final
        priority_score = base_priority * type_weight * confidence_factor
        
        logger.debug(f"Prioridade calculada para {input_data.input_type}: {priority_score}")
        
        return priority_score
    
    def _get_supported_input_types(self) -> List[str]:
        """
        Retorna os tipos de input suportados.
        
        Returns:
            Lista de tipos de input suportados
        """
        # Suporta todos os tipos de input do G1
        return [
            "G1Voice",
            "G1Vision", 
            "G1Sensors",
            "G1GPS",
            "G1State"
        ]
    
    async def _health_check(self) -> bool:
        """
        Verificação específica de saúde do PriorityFuser.
        
        Returns:
            True se está saudável
        """
        try:
            # Verifica se a configuração está válida
            if not self.priority_weights:
                logger.warning("PriorityFuser sem pesos de prioridade")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na verificação de saúde do PriorityFuser: {e}")
            return False
    
    def get_priority_weights(self) -> Dict[str, float]:
        """
        Retorna os pesos de prioridade atuais.
        
        Returns:
            Dicionário com pesos de prioridade
        """
        return self.priority_weights.copy()
    
    def set_priority_weight(self, input_type: str, weight: float):
        """
        Define o peso de prioridade para um tipo de input.
        
        Args:
            input_type: Tipo do input
            weight: Peso de prioridade
        """
        self.priority_weights[input_type] = weight
        logger.info(f"Peso de prioridade para {input_type} definido como {weight}")
    
    def get_fallback_input(self) -> Optional[str]:
        """
        Retorna o input de fallback configurado.
        
        Returns:
            Tipo do input de fallback ou None
        """
        return self.fallback_input
    
    def set_fallback_input(self, input_type: str):
        """
        Define o input de fallback.
        
        Args:
            input_type: Tipo do input de fallback
        """
        self.fallback_input = input_type
        logger.info(f"Input de fallback definido como {input_type}")
    
    def get_min_confidence(self) -> float:
        """
        Retorna a confiança mínima configurada.
        
        Returns:
            Confiança mínima
        """
        return self.min_confidence
    
    def set_min_confidence(self, min_confidence: float):
        """
        Define a confiança mínima.
        
        Args:
            min_confidence: Confiança mínima (0.0 a 1.0)
        """
        if 0.0 <= min_confidence <= 1.0:
            self.min_confidence = min_confidence
            logger.info(f"Confiança mínima definida como {min_confidence}")
        else:
            logger.error(f"Confiança mínima inválida: {min_confidence}")
    
    async def get_detailed_status(self) -> Dict[str, Any]:
        """
        Retorna status detalhado do PriorityFuser.
        
        Returns:
            Status detalhado
        """
        base_status = await self.get_status()
        
        return {
            **base_status,
            "priority_weights": self.priority_weights,
            "fallback_input": self.fallback_input,
            "min_confidence": self.min_confidence,
            "supported_input_types": self._get_supported_input_types()
        }
