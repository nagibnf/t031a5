"""
Fuser multimodal para o sistema t031a5.

Combina múltiplos inputs de diferentes modalidades (voz, visão, sensores)
em um contexto multimodal unificado.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base import BaseFuser, FusedData
from ..inputs.base import InputData

logger = logging.getLogger(__name__)


class MultimodalFuser(BaseFuser):
    """Fuser que combina múltiplas modalidades de input."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o MultimodalFuser.
        
        Args:
            config: Configuração do fuser
        """
        super().__init__(config)
        
        # Configurações específicas multimodais
        self.modality_weights = config.get("modality_weights", {})
        self.fusion_strategy = config.get("fusion_strategy", "weighted")
        self.min_modalities = config.get("min_modalities", 1)
        self.max_modalities = config.get("max_modalities", 5)
        
        logger.debug(f"MultimodalFuser configurado com estratégia: {self.fusion_strategy}")
    
    async def _initialize(self) -> bool:
        """
        Inicialização específica do MultimodalFuser.
        
        Returns:
            True se a inicialização foi bem-sucedida
        """
        try:
            # Validação de configuração
            if not self.modality_weights:
                logger.warning("MultimodalFuser sem pesos de modalidade configurados")
            
            if self.fusion_strategy not in ["weighted", "concatenate", "attention"]:
                logger.warning(f"Estratégia de fusão desconhecida: {self.fusion_strategy}")
            
            logger.info("MultimodalFuser inicializado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro na inicialização do MultimodalFuser: {e}")
            return False
    
    async def _fuse(self, inputs_data: List[InputData]) -> Optional[FusedData]:
        """
        Fusão multimodal.
        
        Args:
            inputs_data: Lista de dados de inputs
            
        Returns:
            Dados fundidos multimodalmente
        """
        try:
            if not inputs_data:
                return None
            
            # Agrupa inputs por modalidade
            modality_groups = self._group_by_modality(inputs_data)
            
            if len(modality_groups) < self.min_modalities:
                logger.debug(f"Modalidades insuficientes: {len(modality_groups)} < {self.min_modalities}")
                return None
            
            # Aplica estratégia de fusão
            if self.fusion_strategy == "weighted":
                fused_data = self._weighted_fusion(modality_groups)
            elif self.fusion_strategy == "concatenate":
                fused_data = self._concatenate_fusion(modality_groups)
            elif self.fusion_strategy == "attention":
                fused_data = self._attention_fusion(modality_groups)
            else:
                logger.warning(f"Estratégia desconhecida, usando weighted: {self.fusion_strategy}")
                fused_data = self._weighted_fusion(modality_groups)
            
            if fused_data:
                logger.debug(f"Fusão multimodal bem-sucedida com {len(modality_groups)} modalidades")
            
            return fused_data
            
        except Exception as e:
            logger.error(f"Erro na fusão multimodal: {e}")
            return None
    
    def _group_by_modality(self, inputs_data: List[InputData]) -> Dict[str, List[InputData]]:
        """
        Agrupa inputs por modalidade.
        
        Args:
            inputs_data: Lista de dados de inputs
            
        Returns:
            Dicionário agrupado por modalidade
        """
        modality_groups = {}
        
        for input_data in inputs_data:
            modality = self._get_modality_type(input_data.input_type)
            if modality not in modality_groups:
                modality_groups[modality] = []
            modality_groups[modality].append(input_data)
        
        return modality_groups
    
    def _get_modality_type(self, input_type: str) -> str:
        """
        Determina o tipo de modalidade de um input.
        
        Args:
            input_type: Tipo do input
            
        Returns:
            Tipo de modalidade
        """
        modality_mapping = {
            "G1Voice": "audio",
            "G1Vision": "visual",
            "G1Sensors": "sensor",
            "G1GPS": "location",
            "G1State": "state"
        }
        
        return modality_mapping.get(input_type, "unknown")
    
    def _weighted_fusion(self, modality_groups: Dict[str, List[InputData]]) -> Optional[FusedData]:
        """
        Fusão ponderada por modalidade.
        
        Args:
            modality_groups: Grupos de inputs por modalidade
            
        Returns:
            Dados fundidos
        """
        try:
            fused_data = {}
            total_confidence = 0.0
            total_weight = 0.0
            source_inputs = []
            
            for modality, inputs in modality_groups.items():
                # Seleciona o input de maior confiança da modalidade
                best_input = max(inputs, key=lambda x: x.confidence)
                
                # Peso da modalidade
                modality_weight = self.modality_weights.get(modality, 1.0)
                
                # Adiciona dados ponderados
                for key, value in best_input.data.items():
                    if key not in fused_data:
                        fused_data[key] = 0.0
                    
                    if isinstance(value, (int, float)):
                        fused_data[key] += value * modality_weight * best_input.confidence
                    else:
                        # Para dados não numéricos, usa o mais recente
                        fused_data[key] = value
                
                total_confidence += best_input.confidence * modality_weight
                total_weight += modality_weight
                source_inputs.append(best_input.input_type)
            
            # Normaliza confiança
            avg_confidence = total_confidence / total_weight if total_weight > 0 else 0.0
            
            return FusedData(
                fusion_type="multimodal_weighted",
                timestamp=datetime.now(),
                data=fused_data,
                confidence=avg_confidence,
                source_inputs=source_inputs,
                fusion_metadata={
                    "fusion_strategy": "weighted",
                    "modalities": list(modality_groups.keys()),
                    "total_modalities": len(modality_groups),
                    "modality_weights": self.modality_weights
                }
            )
            
        except Exception as e:
            logger.error(f"Erro na fusão ponderada: {e}")
            return None
    
    def _concatenate_fusion(self, modality_groups: Dict[str, List[InputData]]) -> Optional[FusedData]:
        """
        Fusão por concatenação.
        
        Args:
            modality_groups: Grupos de inputs por modalidade
            
        Returns:
            Dados fundidos
        """
        try:
            fused_data = {}
            source_inputs = []
            total_confidence = 0.0
            input_count = 0
            
            for modality, inputs in modality_groups.items():
                # Seleciona o input de maior confiança da modalidade
                best_input = max(inputs, key=lambda x: x.confidence)
                
                # Adiciona dados com prefixo da modalidade
                for key, value in best_input.data.items():
                    prefixed_key = f"{modality}_{key}"
                    fused_data[prefixed_key] = value
                
                source_inputs.append(best_input.input_type)
                total_confidence += best_input.confidence
                input_count += 1
            
            # Média da confiança
            avg_confidence = total_confidence / input_count if input_count > 0 else 0.0
            
            return FusedData(
                fusion_type="multimodal_concatenate",
                timestamp=datetime.now(),
                data=fused_data,
                confidence=avg_confidence,
                source_inputs=source_inputs,
                fusion_metadata={
                    "fusion_strategy": "concatenate",
                    "modalities": list(modality_groups.keys()),
                    "total_modalities": len(modality_groups)
                }
            )
            
        except Exception as e:
            logger.error(f"Erro na fusão por concatenação: {e}")
            return None
    
    def _attention_fusion(self, modality_groups: Dict[str, List[InputData]]) -> Optional[FusedData]:
        """
        Fusão por atenção (simplificada).
        
        Args:
            modality_groups: Grupos de inputs por modalidade
            
        Returns:
            Dados fundidos
        """
        try:
            # Implementação simplificada de atenção
            # Em uma implementação real, usaria um modelo de atenção
            
            fused_data = {}
            source_inputs = []
            attention_weights = {}
            total_attention = 0.0
            
            # Calcula pesos de atenção baseados na confiança e tipo
            for modality, inputs in modality_groups.items():
                best_input = max(inputs, key=lambda x: x.confidence)
                
                # Peso de atenção baseado na confiança e peso da modalidade
                modality_weight = self.modality_weights.get(modality, 1.0)
                attention_weight = best_input.confidence * modality_weight
                
                attention_weights[modality] = attention_weight
                total_attention += attention_weight
                source_inputs.append(best_input.input_type)
            
            # Normaliza pesos de atenção
            if total_attention > 0:
                for modality in attention_weights:
                    attention_weights[modality] /= total_attention
            
            # Aplica pesos de atenção aos dados
            for modality, inputs in modality_groups.items():
                best_input = max(inputs, key=lambda x: x.confidence)
                attention_weight = attention_weights[modality]
                
                for key, value in best_input.data.items():
                    if key not in fused_data:
                        fused_data[key] = 0.0
                    
                    if isinstance(value, (int, float)):
                        fused_data[key] += value * attention_weight
                    else:
                        # Para dados não numéricos, usa o de maior atenção
                        if key not in fused_data or attention_weight > attention_weights.get(
                            self._get_modality_type(next(
                                (i.input_type for i in inputs_data if key in i.data), "unknown"
                            )), 0.0
                        ):
                            fused_data[key] = value
            
            return FusedData(
                fusion_type="multimodal_attention",
                timestamp=datetime.now(),
                data=fused_data,
                confidence=sum(attention_weights.values()) / len(attention_weights),
                source_inputs=source_inputs,
                fusion_metadata={
                    "fusion_strategy": "attention",
                    "modalities": list(modality_groups.keys()),
                    "total_modalities": len(modality_groups),
                    "attention_weights": attention_weights
                }
            )
            
        except Exception as e:
            logger.error(f"Erro na fusão por atenção: {e}")
            return None
    
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
        Verificação específica de saúde do MultimodalFuser.
        
        Returns:
            True se está saudável
        """
        try:
            # Verifica se a configuração está válida
            if not self.modality_weights:
                logger.warning("MultimodalFuser sem pesos de modalidade")
            
            if self.fusion_strategy not in ["weighted", "concatenate", "attention"]:
                logger.warning(f"Estratégia de fusão inválida: {self.fusion_strategy}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na verificação de saúde do MultimodalFuser: {e}")
            return False
    
    def get_modality_weights(self) -> Dict[str, float]:
        """
        Retorna os pesos de modalidade atuais.
        
        Returns:
            Dicionário com pesos de modalidade
        """
        return self.modality_weights.copy()
    
    def set_modality_weight(self, modality: str, weight: float):
        """
        Define o peso de uma modalidade.
        
        Args:
            modality: Tipo da modalidade
            weight: Peso da modalidade
        """
        self.modality_weights[modality] = weight
        logger.info(f"Peso da modalidade {modality} definido como {weight}")
    
    def get_fusion_strategy(self) -> str:
        """
        Retorna a estratégia de fusão atual.
        
        Returns:
            Estratégia de fusão
        """
        return self.fusion_strategy
    
    def set_fusion_strategy(self, strategy: str):
        """
        Define a estratégia de fusão.
        
        Args:
            strategy: Nova estratégia de fusão
        """
        if strategy in ["weighted", "concatenate", "attention"]:
            self.fusion_strategy = strategy
            logger.info(f"Estratégia de fusão definida como {strategy}")
        else:
            logger.error(f"Estratégia de fusão inválida: {strategy}")
    
    async def get_detailed_status(self) -> Dict[str, Any]:
        """
        Retorna status detalhado do MultimodalFuser.
        
        Returns:
            Status detalhado
        """
        base_status = await self.get_status()
        
        return {
            **base_status,
            "modality_weights": self.modality_weights,
            "fusion_strategy": self.fusion_strategy,
            "min_modalities": self.min_modalities,
            "max_modalities": self.max_modalities,
            "supported_input_types": self._get_supported_input_types()
        }
