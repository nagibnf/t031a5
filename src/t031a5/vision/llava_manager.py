#!/usr/bin/env python3
"""
Gerenciador LLaVA - Sistema t031a5

Usa LLaVA local via Ollama para análise de imagem
"""

import asyncio
import logging
import os
import base64
import json
import requests
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class LLaVAManager:
    """Gerenciador LLaVA para análise de imagem local."""
    
    def __init__(self, config_path: str = "config/g1_llava.json5"):
        self.config_path = Path(config_path)
        self.config = self.load_config() if self.config_path.exists() else self.default_config()
        self.ollama_host = self.config.get("llava", {}).get("host", "localhost")
        self.ollama_port = self.config.get("llava", {}).get("port", 11434)
        self.model = self.config.get("llava", {}).get("model", "llava")
        self.is_initialized = False
        
    def default_config(self) -> Dict[str, Any]:
        """Configuração padrão se arquivo não existir."""
        return {
            "llava": {
                "model": "llava",
                "host": "localhost", 
                "port": 11434,
                "temperature": 0.3,
                "max_tokens": 200,
                "context_length": 2048
            }
        }
        
    def load_config(self) -> Dict[str, Any]:
        """Carrega configuração do LLaVA."""
        try:
            import json5
            with open(self.config_path, 'r') as f:
                return json5.load(f)
        except ImportError:
            import json
            with open(self.config_path, 'r') as f:
                return json.load(f)
    
    async def initialize(self) -> bool:
        """Inicializa o LLaVA Manager."""
        try:
            logger.info("👁️ Inicializando LLaVA Manager...")
            
            # Testa conexão com Ollama
            if await self._test_ollama_connection():
                logger.info("✅ Ollama conectado")
                
                # Verifica se o modelo LLaVA está disponível
                if await self._check_llava_model():
                    logger.info("✅ Modelo LLaVA disponível")
                    self.is_initialized = True
                    return True
                else:
                    logger.error("❌ Modelo LLaVA não encontrado")
                    return False
            else:
                logger.error("❌ Falha na conexão com Ollama")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar LLaVA Manager: {e}")
            return False
    
    async def _test_ollama_connection(self) -> bool:
        """Testa conexão com Ollama."""
        try:
            url = f"http://{self.ollama_host}:{self.ollama_port}/api/tags"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ Erro ao conectar Ollama: {e}")
            return False
    
    async def _check_llava_model(self) -> bool:
        """Verifica se o modelo LLaVA está disponível."""
        try:
            url = f"http://{self.ollama_host}:{self.ollama_port}/api/tags"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                models = response.json().get("models", [])
                llava_models = [m for m in models if "llava" in m.get("name", "")]
                
                if llava_models:
                    logger.info(f"✅ Modelos LLaVA encontrados: {len(llava_models)}")
                    return True
                else:
                    logger.warning("⚠️ Nenhum modelo LLaVA encontrado")
                    return False
            else:
                logger.error(f"❌ Erro ao listar modelos: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao verificar modelo LLaVA: {e}")
            return False
    
    def get_prompt(self, prompt_type: str = "quick") -> str:
        """Retorna prompt pré-definido do tipo especificado."""
        prompts = self.config.get("prompts", {})
        return prompts.get(prompt_type, prompts.get("quick", "Descreva em 2-3 frases o que você vê."))
    
    async def analyze_image(self, image_path: str, prompt: str = None) -> Optional[str]:
        """Analisa imagem usando LLaVA local."""
        if not self.is_initialized:
            logger.error("LLaVA Manager não inicializado")
            return None
        
        try:
            logger.info(f"👁️ Analisando imagem: {image_path}")
            
            # Verifica se o arquivo existe
            if not Path(image_path).exists():
                logger.error(f"❌ Arquivo não encontrado: {image_path}")
                return None
            
            # Codifica imagem em base64
            image_b64 = self._encode_image_to_base64(image_path)
            if not image_b64:
                return None
            
            # Faz request para Ollama com prompt melhorado
            url = f"http://{self.ollama_host}:{self.ollama_port}/api/generate"
            
            # Usa prompt fornecido ou padrão rápido
            if prompt is None:
                prompt = self.get_prompt("quick")
            
            enhanced_prompt = prompt
            
            payload = {
                "model": self.model,
                "prompt": enhanced_prompt,
                "images": [image_b64],
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Mais determinístico
                    "num_predict": 200,   # Equilibrio: conciso mas funcional
                    "top_p": 0.9,
                    "repeat_penalty": 1.1
                }
            }
            
            logger.info(f"🔄 Enviando request para LLaVA...")
            response = requests.post(url, json=payload, timeout=45)
            
            if response.status_code == 200:
                result = response.json()
                analysis = result.get("response", "").strip()
                
                if analysis and len(analysis) > 20:  # Resposta deve ter conteúdo
                    logger.info(f"✅ LLaVA análise: '{analysis[:100]}...'")
                    return analysis
                else:
                    logger.warning(f"⚠️ LLaVA retornou resposta inadequada: '{analysis}'")
                    return None
            else:
                logger.error(f"❌ Erro na análise LLaVA: {response.status_code}")
                logger.error(f"   📝 Resposta: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro na análise de imagem: {e}")
            return None
    
    def _encode_image_to_base64(self, image_path: str) -> Optional[str]:
        """Codifica imagem para base64."""
        try:
            image_path = Path(image_path)
            if not image_path.exists():
                logger.error(f"❌ Imagem não encontrada: {image_path}")
                return None
            
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
                image_b64 = base64.b64encode(image_data).decode('utf-8')
                
            logger.info(f"✅ Imagem codificada: {len(image_b64)} caracteres")
            return image_b64
            
        except Exception as e:
            logger.error(f"❌ Erro ao codificar imagem: {e}")
            return None
    
    async def analyze_image_from_bytes(self, image_data: bytes, prompt: str = "Descreva esta imagem em português.") -> Optional[str]:
        """Analisa imagem diretamente dos bytes."""
        if not self.is_initialized:
            logger.error("LLaVA Manager não inicializado")
            return None
        
        try:
            logger.info("👁️ Analisando imagem (bytes)...")
            
            # Codifica bytes para base64
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            
            # Faz request para Ollama
            url = f"http://{self.ollama_host}:{self.ollama_port}/api/generate"
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "images": [image_b64],
                "stream": False,
                "options": {
                    "temperature": self.config.get("llava", {}).get("temperature", 0.3),
                    "num_predict": self.config.get("llava", {}).get("max_tokens", 200)
                }
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                analysis = result.get("response", "").strip()
                
                if analysis:
                    logger.info(f"✅ LLaVA análise: '{analysis[:100]}...'")
                    return analysis
                else:
                    logger.warning("⚠️ LLaVA retornou resposta vazia")
                    return None
            else:
                logger.error(f"❌ Erro na análise LLaVA: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro na análise de imagem (bytes): {e}")
            return None
    
    async def cleanup(self) -> None:
        """Limpa recursos do LLaVA Manager."""
        try:
            logger.info("🧹 Limpando LLaVA Manager...")
            self.is_initialized = False
            logger.info("✅ LLaVA Manager limpo")
        except Exception as e:
            logger.error(f"❌ Erro ao limpar LLaVA Manager: {e}")


# Exemplo de uso
async def main() -> None:
    """Exemplo de uso do LLaVA Manager."""
    llava_manager = LLaVAManager()
    
    if await llava_manager.initialize():
        print("✅ LLaVA Manager inicializado")
        
        # Exemplo de análise (seria com imagem real)
        # analysis = await llava_manager.analyze_image("test_image.jpg")
        # print(f"Análise: {analysis}")
        
        await llava_manager.cleanup()
    else:
        print("❌ Falha ao inicializar LLaVA Manager")


if __name__ == "__main__":
    asyncio.run(main())
