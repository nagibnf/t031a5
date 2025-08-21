"""
Provedor LLM Ollama para o sistema t031a5.

Integração com servidor Ollama local para modelos LLM.
"""

import asyncio
import logging
import httpx
from typing import Any, Dict, Optional
from datetime import datetime

from ..provider import BaseLLMProvider, LLMRequest, LLMResponse

logger = logging.getLogger(__name__)


class OllamaProvider(BaseLLMProvider):
    """Provedor LLM Ollama para processamento local."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o OllamaProvider.
        
        Args:
            config: Configuração do provedor
        """
        super().__init__(config)
        
        # Configurações específicas do Ollama para fallback
        self.base_url = config.get("base_url", "http://localhost:11434")
        self.model = config.get("model", "llama3.1:8b")
        self.stream = config.get("stream", False)
        self.timeout = config.get("timeout", 30.0)
        
        # Cliente HTTP
        self.client: Optional[httpx.AsyncClient] = None
        
        logger.debug(f"OllamaProvider configurado para {self.base_url} com modelo {self.model}")
    
    async def _initialize(self) -> bool:
        """
        Inicialização específica do OllamaProvider.
        
        Returns:
            True se a inicialização foi bem-sucedida
        """
        try:
            # Cria cliente HTTP
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(self.timeout)
            )
            
            # Testa conectividade
            response = await self.client.get("/api/tags")
            
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model.get("name") for model in models]
                
                if self.model in model_names:
                    logger.info(f"OllamaProvider inicializado com modelo {self.model}")
                    return True
                else:
                    logger.warning(f"Modelo {self.model} não encontrado. Modelos disponíveis: {model_names}")
                    return False
            else:
                logger.error(f"Falha ao conectar com Ollama: HTTP {response.status_code}")
                return False
                
        except httpx.ConnectError:
            logger.error("Ollama não está rodando ou não acessível")
            return False
        except Exception as e:
            logger.error(f"Erro na inicialização do OllamaProvider: {e}")
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
            if not self.client:
                logger.error("OllamaProvider não foi inicializado")
                return None
            
            # Prepara o prompt
            prompt = self._prepare_prompt(request)
            
            # Prepara payload
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": self.stream,
                "options": {
                    "temperature": request.temperature,
                    "num_predict": request.max_tokens
                }
            }
            
            start_time = datetime.now()
            
            # Faz requisição para Ollama
            response = await self.client.post("/api/generate", json=payload)
            
            if response.status_code == 200:
                response_data = response.json()
                content = response_data.get("response", "")
                
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds()
                
                # Cria resposta
                llm_response = LLMResponse(
                    content=content.strip(),
                    model=self.model,
                    timestamp=end_time,
                    tokens_used=len(content.split()),
                    response_time=response_time,
                    finish_reason="stop",
                    metadata={
                        "ollama_provider": True,
                        "model": self.model,
                        "temperature": request.temperature,
                        "max_tokens": request.max_tokens
                    }
                )
                
                logger.debug(f"OllamaProvider gerou resposta: {len(content)} caracteres em {response_time:.2f}s")
                return llm_response
            else:
                logger.error(f"Erro na requisição Ollama: HTTP {response.status_code}")
                return None
                
        except asyncio.TimeoutError:
            logger.error("Timeout na requisição para Ollama")
            return None
        except Exception as e:
            logger.error(f"Erro no processamento do OllamaProvider: {e}")
            return None
    
    def _prepare_prompt(self, request: LLMRequest) -> str:
        """
        Prepara o prompt para o Ollama.
        
        Args:
            request: Requisição para o LLM
            
        Returns:
            Prompt formatado
        """
        try:
            # Extrai informações dos dados fundidos
            fused_data = request.fused_data
            system_prompt = request.system_prompt
            
            # Constrói contexto dos dados
            context_parts = []
            
            if fused_data.data:
                for key, value in fused_data.data.items():
                    if isinstance(value, (str, int, float, bool)):
                        context_parts.append(f"{key}: {value}")
                    elif isinstance(value, dict):
                        context_parts.append(f"{key}: {str(value)[:100]}...")
                    else:
                        context_parts.append(f"{key}: {type(value).__name__}")
            
            # Monta prompt completo
            prompt_parts = [
                f"SISTEMA: {system_prompt}",
                "",
                "CONTEXTO ATUAL:",
            ]
            
            if context_parts:
                prompt_parts.extend(context_parts)
            else:
                prompt_parts.append("Nenhum dado específico disponível.")
            
            prompt_parts.extend([
                "",
                "INSTRUÇÕES:",
                "- Responda de forma natural e conversacional",
                "- Use o contexto fornecido para personalizar sua resposta",
                "- Mantenha as respostas concisas (máximo 2-3 frases)",
                "- Expresse emoções apropriadas",
                "",
                "RESPOSTA:"
            ])
            
            return "\n".join(prompt_parts)
            
        except Exception as e:
            logger.error(f"Erro ao preparar prompt: {e}")
            return f"{request.system_prompt}\n\nResponda de forma natural e amigável."
    
    async def _stop(self) -> bool:
        """
        Parada específica do OllamaProvider.
        
        Returns:
            True se a parada foi bem-sucedida
        """
        try:
            if self.client:
                await self.client.aclose()
                self.client = None
            
            logger.info("OllamaProvider parado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao parar OllamaProvider: {e}")
            return False
    
    async def _health_check(self) -> bool:
        """
        Verificação específica de saúde do OllamaProvider.
        
        Returns:
            True se está saudável
        """
        try:
            if not self.client:
                return False
            
            # Testa conectividade
            response = await self.client.get("/api/tags")
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Erro na verificação de saúde do OllamaProvider: {e}")
            return False
    
    async def get_available_models(self) -> list:
        """
        Retorna lista de modelos disponíveis.
        
        Returns:
            Lista de modelos disponíveis
        """
        try:
            if not self.client:
                return []
            
            response = await self.client.get("/api/tags")
            
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model.get("name") for model in models]
            else:
                return []
                
        except Exception as e:
            logger.error(f"Erro ao obter modelos disponíveis: {e}")
            return []
    
    async def get_detailed_status(self) -> Dict[str, Any]:
        """
        Retorna status detalhado do OllamaProvider.
        
        Returns:
            Status detalhado
        """
        base_status = await self.get_status()
        available_models = await self.get_available_models()
        
        return {
            **base_status,
            "base_url": self.base_url,
            "stream": self.stream,
            "available_models": available_models,
            "client_initialized": self.client is not None,
            "ollama_provider": True
        }
