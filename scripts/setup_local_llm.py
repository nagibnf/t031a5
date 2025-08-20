#!/usr/bin/env python3
"""
Configuração de LLM Local - Sistema t031a5

Configura e testa:
- Llama-3.1-8B-Instruct (LLM local)
- Otimizado para Jetson Orin NX 16GB
- Fallback para OpenAI GPT-4o
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional


class LocalLLMConfig:
    """Configurador de LLM local para t031a5."""
    
    def __init__(self):
        self.config_path = Path("config/g1_local_llm.json5")
        self.models_dir = Path("models")
        self.llama_model = "llama-3.1-8b-instruct-q4_k_m.gguf"
        self.model_url = "https://huggingface.co/TheBloke/Llama-3.1-8B-Instruct-GGUF/resolve/main/llama-3.1-8b-instruct-q4_k_m.gguf"
        
    def create_llm_config(self) -> Dict[str, Any]:
        """Cria configuração de LLM local."""
        config = {
            "name": "G1 Local LLM Configuration",
            "description": "Configuração de LLM local para Tobias (G1) - Jetson Orin NX 16GB",
            "version": "1.0",
            "llm": {
                "primary": {
                    "provider": "llama_cpp",
                    "model": "llama-3.1-8b-instruct-q4_k_m.gguf",
                    "model_path": "models/llama-3.1-8b-instruct-q4_k_m.gguf",
                    "context_length": 4096,
                    "temperature": 0.7,
                    "max_tokens": 512,
                    "top_p": 0.9,
                    "frequency_penalty": 0.0,
                    "presence_penalty": 0.0,
                    "threads": 8,
                    "gpu_layers": 32,
                    "batch_size": 512,
                    "use_mmap": True,
                    "use_mlock": False,
                    "n_ctx": 4096,
                    "n_batch": 512,
                    "n_gpu_layers": 32,
                    "rope_scaling": {
                        "type": "linear",
                        "factor": 1.0
                    }
                },
                "fallback": {
                    "provider": "openai",
                    "model": "gpt-4o-mini",
                    "api_key": "${OPENAI_API_KEY}",
                    "temperature": 0.7,
                    "max_tokens": 512
                },
                "routing": {
                    "online": "openai",
                    "offline": "llama_cpp",
                    "fallback": "llama_cpp",
                    "auto_switch": True
                }
            },
            "performance": {
                "jetson": {
                    "model": "orin_nx_16gb",
                    "ram": "16GB",
                    "gpu": "1024-core_ampere",
                    "tensor_cores": 32,
                    "optimization": "max"
                },
                "expected": {
                    "response_time": "2-5 seconds",
                    "memory_usage": "4-6GB",
                    "gpu_usage": "2-4GB",
                    "throughput": "10-20 tokens/second"
                }
            }
        }
        
        return config
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Salva configuração em arquivo JSON5."""
        try:
            # Converte para JSON5 (com comentários)
            json5_content = f"""// Configuração de LLM Local - Sistema t031a5
// Para Tobias (G1) - Jetson Orin NX 16GB
// Llama-3.1-8B-Instruct + OpenAI GPT-4o fallback

{json.dumps(config, indent=2, ensure_ascii=False)}
"""
            
            self.config_path.write_text(json5_content, encoding='utf-8')
            print(f"✅ Configuração salva: {self.config_path}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar configuração: {e}")
            return False
    
    def create_llm_manager(self) -> str:
        """Cria gerenciador de LLM local."""
        llm_manager_code = '''#!/usr/bin/env python3
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
        
        print("\\n📊 RESULTADOS DOS TESTES")
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
'''
        
        manager_path = Path("src/t031a5/llm/local_manager.py")
        manager_path.parent.mkdir(parents=True, exist_ok=True)
        manager_path.write_text(llm_manager_code, encoding='utf-8')
        
        return str(manager_path)
    
    def create_download_script(self) -> str:
        """Cria script para download do modelo."""
        download_script = '''#!/usr/bin/env python3
"""
Download do Modelo LLM - Sistema t031a5

Download do Llama-3.1-8B-Instruct para Jetson Orin NX 16GB
"""

import requests
import sys
from pathlib import Path
from tqdm import tqdm


def download_model():
    """Download do modelo Llama-3.1-8B-Instruct."""
    model_url = "https://huggingface.co/TheBloke/Llama-3.1-8B-Instruct-GGUF/resolve/main/llama-3.1-8b-instruct-q4_k_m.gguf"
    model_path = Path("models/llama-3.1-8b-instruct-q4_k_m.gguf")
    
    # Cria diretório se não existir
    model_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Verifica se já existe
    if model_path.exists():
        print(f"✅ Modelo já existe: {model_path}")
        return True
    
    print(f"📥 Download do modelo: {model_url}")
    print(f"💾 Salvar em: {model_path}")
    print(f"📦 Tamanho: ~4.5GB")
    
    try:
        # Download com barra de progresso
        response = requests.get(model_url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(model_path, 'wb') as f:
            with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    pbar.update(len(chunk))
        
        print(f"✅ Download concluído: {model_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erro no download: {e}")
        return False


if __name__ == "__main__":
    success = download_model()
    sys.exit(0 if success else 1)
'''
        
        download_path = Path("scripts/download_llama_model.py")
        download_path.write_text(download_script, encoding='utf-8')
        
        return str(download_path)
    
    def create_test_script(self) -> str:
        """Cria script de teste para LLM local."""
        test_script = '''#!/usr/bin/env python3
"""
Teste de LLM Local - Sistema t031a5

Testa Llama-3.1-8B-Instruct no Jetson Orin NX 16GB
"""

import asyncio
import sys
from pathlib import Path

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from t031a5.llm.local_manager import LocalLLMManager


async def test_local_llm():
    """Testa sistema de LLM local."""
    print("🧠 TESTE DE LLM LOCAL - SISTEMA t031a5")
    print("=" * 50)
    
    manager = LocalLLMManager()
    
    print("🔧 Inicializando...")
    if await manager.initialize():
        print("✅ Sistema inicializado")
        
        # Teste de performance
        print("\\n📊 Testando performance...")
        results = await manager.test_performance()
        
        print("\\n📋 RESULTADOS")
        print("=" * 20)
        
        if results["local"]["success"]:
            print(f"🖥️ LLM Local: {results['local']['time']:.2f}s")
            print(f"   Resposta: {results['local']['response']}")
        else:
            print("❌ LLM Local: Falha")
        
        if results["openai"]["success"]:
            print(f"☁️ OpenAI: {results['openai']['time']:.2f}s")
            print(f"   Resposta: {results['openai']['response']}")
        else:
            print("❌ OpenAI: Falha")
        
        await manager.cleanup()
    else:
        print("❌ Falha ao inicializar sistema")
    
    print("\\n🎉 Teste concluído!")


if __name__ == "__main__":
    asyncio.run(test_local_llm())
'''
        
        test_path = Path("scripts/test/test_local_llm.py")
        test_path.parent.mkdir(parents=True, exist_ok=True)
        test_path.write_text(test_script, encoding='utf-8')
        
        return str(test_path)
    
    def setup_complete(self) -> bool:
        """Configuração completa do sistema de LLM local."""
        print("🧠 CONFIGURAÇÃO DE LLM LOCAL - SISTEMA t031a5")
        print("=" * 60)
        
        # Cria configuração
        config = self.create_llm_config()
        if not self.save_config(config):
            return False
        
        # Cria gerenciador
        manager_path = self.create_llm_manager()
        print(f"✅ Gerenciador criado: {manager_path}")
        
        # Cria script de download
        download_path = self.create_download_script()
        print(f"✅ Script de download criado: {download_path}")
        
        # Cria script de teste
        test_path = self.create_test_script()
        print(f"✅ Script de teste criado: {test_path}")
        
        print("\\n📋 RESUMO DA CONFIGURAÇÃO")
        print("=" * 30)
        print("🧠 LLM Local: Llama-3.1-8B-Instruct")
        print("💾 Tamanho: ~4.5GB")
        print("⚡ Performance: 2-5 segundos/resposta")
        print("🔄 Fallback: OpenAI GPT-4o-mini")
        print("🎯 Otimizado: Jetson Orin NX 16GB")
        
        print("\\n💡 PRÓXIMOS PASSOS")
        print("=" * 20)
        print("1. Instale: pip install llama-cpp-python")
        print("2. Download: python scripts/download_llama_model.py")
        print("3. Teste: python scripts/test/test_local_llm.py")
        print("4. Configure OPENAI_API_KEY (opcional)")
        
        return True


def main():
    """Função principal."""
    try:
        configurator = LocalLLMConfig()
        success = configurator.setup_complete()
        
        if success:
            print("\\n🎉 Configuração de LLM local concluída!")
            print("🚀 Sistema t031a5 pronto para LLM local")
        else:
            print("\\n❌ Falha na configuração")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
