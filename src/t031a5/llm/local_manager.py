#!/usr/bin/env python3
"""
Gerenciador de LLM Local - Sistema t031a5

Gerencia LLM local (Llama-3.1-8B) + fallback OpenAI:
- Llama-3.1-8B-Instruct (local)
- OpenAI GPT-4o-mini (fallback)
"""

import asyncio
import logging
import os
from typing import Optional, Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)


class LocalLLMManager:
    """Gerenciador de LLM local para t031a5."""
    
    def __init__(self, config_path: str = "config/g1_local_llm.json5"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.llama_model = None
        self.openai_client = None
        self.is_initialized = False
        
    def load_config(self) -> Dict[str, Any]:
        """Carrega configuração de LLM."""
        try:
            import json5
            with open(self.config_path, 'r') as f:
                return json5.load(f)
        except ImportError:
            # Fallback para JSON se json5 não estiver disponível
            with open(self.config_path, 'r') as f:
                return json.load(f)
    
    async def initialize(self) -> bool:
        """Inicializa gerenciador de LLM."""
        try:
            logger.info("Inicializando LocalLLMManager...")
            
            # Inicializa Llama.cpp
            await self._init_llama_cpp()
            
            # Inicializa OpenAI (se API key disponível)
            await self._init_openai()
            
            self.is_initialized = True
            logger.info("LocalLLMManager inicializado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao inicializar LocalLLMManager: {e}")
            return False
    
    async def _init_llama_cpp(self) -> bool:
        """Inicializa Llama.cpp."""
        try:
            from llama_cpp import Llama
            
            model_path = self.config["llm"]["primary"]["model_path"]
            if not Path(model_path).exists():
                logger.error(f"Modelo não encontrado: {model_path}")
                return False
            
            # Configuração para Jetson Orin NX
            llama_config = self.config["llm"]["primary"]
            
            self.llama_model = Llama(
                model_path=model_path,
                n_ctx=llama_config["n_ctx"],
                n_batch=llama_config["n_batch"],
                n_gpu_layers=llama_config["n_gpu_layers"],
                use_mmap=llama_config["use_mmap"],
                use_mlock=llama_config["use_mlock"],
                threads=llama_config["threads"],
                rope_scaling=llama_config["rope_scaling"]
            )
            
            logger.info("Llama.cpp inicializado com sucesso")
            return True
            
        except ImportError:
            logger.warning("llama-cpp-python não instalado")
            return False
        except Exception as e:
            logger.error(f"Erro ao inicializar Llama.cpp: {e}")
            return False
    
    async def _init_openai(self) -> bool:
        """Inicializa cliente OpenAI."""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("OPENAI_API_KEY não configurada")
                return False
            
            from openai import AsyncOpenAI
            
            self.openai_client = AsyncOpenAI(api_key=api_key)
            logger.info("OpenAI client inicializado")
            return True
            
        except ImportError:
            logger.warning("openai não instalado")
            return False
        except Exception as e:
            logger.error(f"Erro ao inicializar OpenAI: {e}")
            return False
    
    async def generate_response(self, prompt: str, context: str = "", 
                              use_local: bool = True) -> Optional[str]:
        """Gera resposta usando LLM local ou OpenAI."""
        try:
            if use_local and self.llama_model:
                return await self._generate_local(prompt, context)
            elif self.openai_client:
                return await self._generate_openai(prompt, context)
            else:
                logger.error("Nenhum LLM disponível")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            return None
    
    async def _generate_local(self, prompt: str, context: str = "") -> Optional[str]:
        """Gera resposta usando Llama.cpp local."""
        try:
            # Formata prompt para Llama-3.1-Instruct
            formatted_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

Você é Tobias, um robô G1 inteligente e amigável. Responda de forma natural e útil.

<|eot_id|><|start_header_id|>user<|end_header_id|>

{context}
{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
            
            # Configuração
            config = self.config["llm"]["primary"]
            
            # Gera resposta
            response = self.llama_model(
                formatted_prompt,
                max_tokens=config["max_tokens"],
                temperature=config["temperature"],
                top_p=config["top_p"],
                frequency_penalty=config["frequency_penalty"],
                presence_penalty=config["presence_penalty"],
                stop=["<|eot_id|>", "<|end_of_text|>"]
            )
            
            return response["choices"][0]["text"].strip()
            
        except Exception as e:
            logger.error(f"Erro no LLM local: {e}")
            return None
    
    async def _generate_openai(self, prompt: str, context: str = "") -> Optional[str]:
        """Gera resposta usando OpenAI."""
        try:
            # Formata mensagens
            messages = []
            if context:
                messages.append({"role": "system", "content": context})
            messages.append({"role": "user", "content": prompt})
            
            # Configuração
            config = self.config["llm"]["fallback"]
            
            # Gera resposta
            response = await self.openai_client.chat.completions.create(
                model=config["model"],
                messages=messages,
                max_tokens=config["max_tokens"],
                temperature=config["temperature"]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Erro no OpenAI: {e}")
            return None
    
    async def test_performance(self) -> Dict[str, Any]:
        """Testa performance do LLM."""
        test_prompt = "Olá! Como você está hoje?"
        
        results = {
            "local": {"success": False, "time": 0, "response": ""},
            "openai": {"success": False, "time": 0, "response": ""}
        }
        
        # Teste local
        if self.llama_model:
            start_time = asyncio.get_event_loop().time()
            response = await self._generate_local(test_prompt)
            end_time = asyncio.get_event_loop().time()
            
            results["local"] = {
                "success": response is not None,
                "time": end_time - start_time,
                "response": response or ""
            }
        
        # Teste OpenAI
        if self.openai_client:
            start_time = asyncio.get_event_loop().time()
            response = await self._generate_openai(test_prompt)
            end_time = asyncio.get_event_loop().time()
            
            results["openai"] = {
                "success": response is not None,
                "time": end_time - start_time,
                "response": response or ""
            }
        
        return results
    
    async def cleanup(self):
        """Limpa recursos do LLM."""
        try:
            if self.llama_model:
                del self.llama_model
                self.llama_model = None
            
            if self.openai_client:
                self.openai_client = None
            
            self.is_initialized = False
            logger.info("LocalLLMManager limpo")
            
        except Exception as e:
            logger.error(f"Erro ao limpar LocalLLMManager: {e}")


# Exemplo de uso
async def main():
    """Exemplo de uso do LocalLLMManager."""
    manager = LocalLLMManager()
    
    if await manager.initialize():
        print("✅ LLM Local inicializado")
        
        # Teste de performance
        results = await manager.test_performance()
        
        print("\n📊 RESULTADOS DOS TESTES")
        print("=" * 30)
        
        if results["local"]["success"]:
            print(f"🖥️ Local: {results['local']['time']:.2f}s")
            print(f"   Resposta: {results['local']['response'][:100]}...")
        else:
            print("❌ Local: Falha")
        
        if results["openai"]["success"]:
            print(f"☁️ OpenAI: {results['openai']['time']:.2f}s")
            print(f"   Resposta: {results['openai']['response'][:100]}...")
        else:
            print("❌ OpenAI: Falha")
        
        await manager.cleanup()
    else:
        print("❌ Falha ao inicializar LLM Local")


if __name__ == "__main__":
    asyncio.run(main())
