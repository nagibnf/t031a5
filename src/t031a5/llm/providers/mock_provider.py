"""
Provedor LLM Mock para o sistema t031a5.

Usado para testes e desenvolvimento quando provedores reais não estão disponíveis.
"""

import asyncio
import logging
from typing import Any, Dict, Optional
from datetime import datetime

from ..provider import BaseLLMProvider, LLMRequest, LLMResponse

logger = logging.getLogger(__name__)


class MockLLMProvider(BaseLLMProvider):
    """Provedor LLM Mock para testes e desenvolvimento."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o MockLLMProvider.
        
        Args:
            config: Configuração do provedor
        """
        super().__init__(config)
        
        # Configurações específicas do mock
        self.response_delay = config.get("response_delay", 0.1)
        self.response_template = config.get("response_template", "Olá! Sou o G1 e estou funcionando corretamente.")
        self.error_rate = config.get("error_rate", 0.0)  # 0.0 = sem erros
        
        logger.debug(f"MockLLMProvider configurado com delay: {self.response_delay}s")
    
    async def _initialize(self) -> bool:
        """
        Inicialização específica do MockLLMProvider.
        
        Returns:
            True se a inicialização foi bem-sucedida
        """
        try:
            logger.info("MockLLMProvider inicializado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro na inicialização do MockLLMProvider: {e}")
            return False
    
    async def _process(self, request: LLMRequest) -> Optional[LLMResponse]:
        """
        Processamento específico da requisição.
        
        Args:
            request: Requisição para o LLM
            
        Returns:
            Resposta do LLM ou None se falhar
        """
        try:
            # Simula delay de processamento
            await asyncio.sleep(self.response_delay)
            
            # Simula erro ocasional
            if self.error_rate > 0.0:
                import random
                if random.random() < self.error_rate:
                    logger.warning("MockLLMProvider simulando erro")
                    return None
            
            # Gera resposta baseada nos dados fundidos
            response_content = self._generate_response(request)
            
            # Cria resposta
            response = LLMResponse(
                content=response_content,
                model=self.model,
                timestamp=datetime.now(),
                tokens_used=len(response_content.split()),
                response_time=self.response_delay,
                finish_reason="stop",
                metadata={
                    "mock_provider": True,
                    "request_data": str(request.fused_data.data)[:100] + "..." if len(str(request.fused_data.data)) > 100 else str(request.fused_data.data)
                }
            )
            
            logger.debug(f"MockLLMProvider gerou resposta: {len(response_content)} caracteres")
            return response
            
        except Exception as e:
            logger.error(f"Erro no processamento do MockLLMProvider: {e}")
            return None
    
    def _generate_response(self, request: LLMRequest) -> str:
        """
        Gera uma resposta baseada nos dados fundidos.
        
        Args:
            request: Requisição para o LLM
            
        Returns:
            Resposta gerada
        """
        try:
            # Extrai informações dos dados fundidos
            fused_data = request.fused_data
            system_prompt = request.system_prompt
            
            # Analisa os dados para gerar resposta contextual
            response_parts = []
            
            # Adiciona saudação baseada no prompt do sistema
            if "assistente" in system_prompt.lower():
                response_parts.append("Olá! Sou seu assistente robótico G1.")
            elif "companheiro" in system_prompt.lower():
                response_parts.append("Oi! Que bom ver você! Sou seu companheiro G1.")
            else:
                response_parts.append("Olá! Sou o G1.")
            
            # Adiciona informações baseadas nos dados fundidos
            if fused_data.data:
                # Verifica se há dados de voz
                if "voice_data" in fused_data.data or "audio" in str(fused_data.data).lower():
                    response_parts.append("Entendi o que você disse!")
                
                # Verifica se há dados de sensores
                if "battery" in fused_data.data:
                    battery_level = fused_data.data.get("battery", 100)
                    response_parts.append(f"Minha bateria está em {battery_level}%.")
                
                if "temperature" in fused_data.data:
                    temp = fused_data.data.get("temperature", 25)
                    response_parts.append(f"Minha temperatura está em {temp}°C.")
                
                # Verifica se há dados de localização
                if "gps" in fused_data.data or "location" in fused_data.data:
                    response_parts.append("Estou ciente da minha localização.")
                
                # Verifica se há dados de estado
                if "posture" in fused_data.data or "movement" in fused_data.data:
                    response_parts.append("Estou monitorando meu movimento e postura.")
            
            # Adiciona resposta padrão se não houver dados específicos
            if len(response_parts) == 1:  # Apenas a saudação
                response_parts.append("Estou funcionando perfeitamente e pronto para ajudar!")
            
            # Adiciona emoção se configurado
            if "emotion" in str(fused_data.data).lower():
                response_parts.append("Estou sentindo muito bem hoje!")
            
            # Junta as partes da resposta
            response = " ".join(response_parts)
            
            # Adiciona informações de debug se em modo desenvolvimento
            if self.config_manager and self.config_manager.is_development_mode():
                response += f"\n\n[DEBUG] Dados fundidos: {len(fused_data.data)} campos, Confiança: {fused_data.confidence:.2f}"
            
            return response
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            return self.response_template
    
    async def _stop(self) -> bool:
        """
        Parada específica do MockLLMProvider.
        
        Returns:
            True se a parada foi bem-sucedida
        """
        try:
            logger.info("MockLLMProvider parado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao parar MockLLMProvider: {e}")
            return False
    
    async def _health_check(self) -> bool:
        """
        Verificação específica de saúde do MockLLMProvider.
        
        Returns:
            True se está saudável
        """
        try:
            # Mock sempre está saudável
            return True
            
        except Exception as e:
            logger.error(f"Erro na verificação de saúde do MockLLMProvider: {e}")
            return False
    
    def set_response_delay(self, delay: float):
        """
        Define o delay de resposta.
        
        Args:
            delay: Delay em segundos
        """
        self.response_delay = delay
        logger.info(f"Delay de resposta definido como {delay}s")
    
    def set_error_rate(self, error_rate: float):
        """
        Define a taxa de erro.
        
        Args:
            error_rate: Taxa de erro (0.0 a 1.0)
        """
        if 0.0 <= error_rate <= 1.0:
            self.error_rate = error_rate
            logger.info(f"Taxa de erro definida como {error_rate}")
        else:
            logger.error(f"Taxa de erro inválida: {error_rate}")
    
    def set_response_template(self, template: str):
        """
        Define o template de resposta.
        
        Args:
            template: Template de resposta
        """
        self.response_template = template
        logger.info(f"Template de resposta atualizado")
    
    async def get_detailed_status(self) -> Dict[str, Any]:
        """
        Retorna status detalhado do MockLLMProvider.
        
        Returns:
            Status detalhado
        """
        base_status = await self.get_status()
        
        return {
            **base_status,
            "response_delay": self.response_delay,
            "error_rate": self.error_rate,
            "response_template": self.response_template[:50] + "..." if len(self.response_template) > 50 else self.response_template,
            "mock_provider": True
        }
