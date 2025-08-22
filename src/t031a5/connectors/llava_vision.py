# -*- coding: utf-8 -*-
"""
LLaVA Vision Analysis Connector
Método validado: RealSense + LLaVA análise inteligente
TESTE 7: ✅ SUCESSO (21/08/2025)
"""

import asyncio
import logging
import base64
import requests
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class LLaVAVisionRequest:
    """Request para análise LLaVA"""
    def __init__(self, image_path: str, prompt: str = None):
        self.image_path = image_path
        self.prompt = prompt or "Descreva o que você vê nesta imagem de forma objetiva e detalhada."

class LLaVAVisionResponse:
    """Response da análise LLaVA"""
    def __init__(self, success: bool, description: str = "", error: str = ""):
        self.success = success
        self.description = description
        self.error = error

class LLaVAVisionConnector:
    """
    Connector para análise inteligente de imagens com LLaVA
    
    MÉTODO VALIDADO NO TESTE 7:
    - Modelo: llava:latest (via Ollama)
    - Endpoint: http://localhost:11434/api/generate
    - Input: Base64 encoded image
    - Output: Descrição textual inteligente
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.enabled = config.get("enabled", True)
        self.model = config.get("model", "llava:latest")
        self.endpoint = config.get("endpoint", "http://localhost:11434/api/generate")
        self.timeout = config.get("timeout", 60)
        self.default_prompt = config.get("default_prompt", 
            "Descreva o que você vê nesta imagem de forma objetiva e detalhada.")
        
        logger.info(f"LLaVAVisionConnector inicializado: enabled={self.enabled}, model={self.model}")
    
    async def analyze_image(self, request: LLaVAVisionRequest) -> LLaVAVisionResponse:
        """
        Analisa imagem com LLaVA - MÉTODO VALIDADO
        
        Args:
            request: LLaVAVisionRequest com imagem e prompt
            
        Returns:
            LLaVAVisionResponse com descrição ou erro
        """
        if not self.enabled:
            return LLaVAVisionResponse(
                success=False,
                error="LLaVA connector desabilitado"
            )
        
        try:
            # Validar arquivo de imagem
            image_path = Path(request.image_path)
            if not image_path.exists():
                return LLaVAVisionResponse(
                    success=False,
                    error=f"Arquivo de imagem não encontrado: {request.image_path}"
                )
            
            logger.info(f"Analisando imagem: {request.image_path}")
            
            # Converter imagem para base64 - MÉTODO TESTADO
            with open(request.image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Preparar requisição LLaVA - FORMATO VALIDADO
            llava_request = {
                'model': self.model,
                'prompt': request.prompt or self.default_prompt,
                'images': [image_data],
                'stream': False
            }
            
            # Executar análise - ENDPOINT TESTADO
            response = requests.post(
                self.endpoint,
                json=llava_request,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                description = result.get('response', 'Sem resposta')
                
                logger.info(f"LLaVA análise concluída: {len(description)} caracteres")
                
                return LLaVAVisionResponse(
                    success=True,
                    description=description
                )
            else:
                error_msg = f"LLaVA HTTP {response.status_code}"
                logger.error(error_msg)
                return LLaVAVisionResponse(
                    success=False,
                    error=error_msg
                )
                
        except requests.exceptions.ConnectionError:
            error_msg = "Ollama/LLaVA não está rodando (porta 11434)"
            logger.error(error_msg)
            return LLaVAVisionResponse(
                success=False,
                error=error_msg
            )
        except Exception as e:
            error_msg = f"Erro LLaVA: {str(e)}"
            logger.error(error_msg)
            return LLaVAVisionResponse(
                success=False,
                error=error_msg
            )
    
    async def quick_analyze(self, image_path: str, prompt: str = None) -> str:
        """
        Análise rápida de imagem - helper method
        
        Returns:
            Descrição da imagem ou mensagem de erro
        """
        request = LLaVAVisionRequest(image_path, prompt)
        response = await self.analyze_image(request)
        
        if response.success:
            return response.description
        else:
            return f"ERRO: {response.error}"
    
    def is_available(self) -> bool:
        """Verifica se LLaVA está disponível"""
        try:
            response = requests.get(f"{self.endpoint.replace('/api/generate', '/api/tags')}", timeout=5)
            return response.status_code == 200
        except:
            return False
