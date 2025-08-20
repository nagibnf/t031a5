import asyncio
import logging
import os
import requests
import json
from typing import Optional, Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)

class OllamaManager:
    def __init__(self, config_path: str = "config/g1_ollama_llm.json5"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.base_url = f"http://{self.config['llm']['primary']['host']}:{self.config['llm']['primary']['port']}"
        self.current_model = self.config['llm']['primary']['model']
        self.is_initialized = False
        
    def load_config(self) -> Dict[str, Any]:
        """Carrega configuração JSON5"""
        try:
            import json5
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json5.load(f)
        except ImportError:
            # Fallback para JSON simples
            with open(self.config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Remove comentários simples
                lines = content.split('\n')
                cleaned_lines = []
                for line in lines:
                    if not line.strip().startswith('//'):
                        cleaned_lines.append(line)
                return json.loads('\n'.join(cleaned_lines))
    
    async def initialize(self) -> bool:
        """Inicializa o Ollama Manager"""
        try:
            logger.info("🔧 Inicializando Ollama Manager...")
            
            # Verifica se o Ollama está rodando
            if not await self._check_ollama_status():
                logger.error("❌ Ollama não está rodando")
                return False
            
            # Verifica se o modelo principal está disponível
            if not await self._check_model_availability(self.current_model):
                logger.warning(f"⚠️ Modelo {self.current_model} não encontrado")
                logger.info("📥 Baixando modelo principal...")
                if not await self._download_model(self.current_model):
                    logger.error("❌ Falha ao baixar modelo")
                    return False
            
            self.is_initialized = True
            logger.info(f"✅ Ollama Manager inicializado com modelo: {self.current_model}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na inicialização: {e}")
            return False
    
    async def _check_ollama_status(self) -> bool:
        """Verifica se o Ollama está rodando"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    async def _check_model_availability(self, model_name: str) -> bool:
        """Verifica se um modelo está disponível"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                return any(model['name'] == model_name for model in models)
            return False
        except:
            return False
    
    async def _download_model(self, model_name: str) -> bool:
        """Baixa um modelo via Ollama"""
        try:
            logger.info(f"📥 Baixando modelo: {model_name}")
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                stream=True
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        if 'status' in data:
                            logger.info(f"📥 {data['status']}")
                        if data.get('done', False):
                            logger.info(f"✅ Modelo {model_name} baixado com sucesso")
                            return True
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao baixar modelo: {e}")
            return False
    
    async def generate_response(self, prompt: str, context: str = "", use_local: bool = True) -> Optional[str]:
        """Gera resposta usando Ollama"""
        if not self.is_initialized:
            logger.error("❌ Ollama Manager não inicializado")
            return None
        
        try:
            if use_local:
                return await self._generate_ollama(prompt, context)
            else:
                return await self._generate_openai(prompt, context)
        except Exception as e:
            logger.error(f"❌ Erro na geração: {e}")
            return None
    
    async def _generate_ollama(self, prompt: str, context: str = "") -> Optional[str]:
        """Gera resposta usando Ollama"""
        try:
            # Obtém configurações
            config = self.config['llm']['primary']
            response_style = config.get("response_style", "normal")
            
            # Ajusta prompt baseado no estilo de resposta
            if response_style == "concise":
                style_instruction = "Resposta curta e direta, máximo 2-3 frases."
            else:
                style_instruction = ""
            
            full_prompt = f"{context}\n\n{style_instruction}\n\n{prompt}" if context else f"{style_instruction}\n\n{prompt}"
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.current_model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": config["temperature"],
                        "top_p": config["top_p"],
                        "num_predict": config["max_tokens"]
                    }
                },
                timeout=config["timeout"]
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '').strip()
                
                # Limita resposta se necessário
                max_tokens = config["max_tokens"]
                if len(response_text.split()) > max_tokens // 4:  # Aproximadamente max_tokens/4 palavras
                    words = response_text.split()[:max_tokens // 4]
                    response_text = " ".join(words) + "..."
                
                return response_text
            else:
                error_msg = response.text
                if response.status_code == 404:
                    logger.error("❌ OLLAMA: Modelo não encontrado!")
                    logger.error(f"   🤖 Modelo: {self.current_model}")
                    logger.error("   📥 Execute: ollama pull llama3.1:8b")
                elif response.status_code == 500:
                    logger.error("❌ OLLAMA: Erro interno do servidor!")
                    logger.error("   🔄 Reinicie o Ollama: brew services restart ollama")
                elif "timeout" in error_msg.lower():
                    logger.error("❌ OLLAMA: Timeout na resposta!")
                    logger.error("   ⏰ Aumente o timeout ou use um modelo menor")
                else:
                    logger.error(f"❌ OLLAMA: Erro {response.status_code}")
                    logger.error(f"   📝 Detalhes: {error_msg}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro na geração Ollama: {e}")
            return None
    
    async def _generate_openai(self, prompt: str, context: str = "") -> Optional[str]:
        """Gera resposta usando OpenAI (fallback)"""
        try:
            import openai
            
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                logger.error("❌ OpenAI API key não configurada")
                return None
            
            # Usa a nova API do OpenAI
            client = openai.OpenAI(api_key=api_key)
            
            # Adiciona instrução para resposta curta
            concise_instruction = "Resposta curta e direta, máximo 2-3 frases."
            full_prompt = f"{context}\n\n{concise_instruction}\n\n{prompt}" if context else f"{concise_instruction}\n\n{prompt}"
            
            response = await client.chat.completions.acreate(
                model=self.config['llm']['fallback']['model'],
                messages=[{"role": "user", "content": full_prompt}],
                temperature=self.config['llm']['fallback']['temperature'],
                max_tokens=self.config['llm']['fallback']['max_tokens']
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            error_msg = str(e)
            if "quota_exceeded" in error_msg or "billing" in error_msg:
                logger.error("❌ OPENAI: Cota excedida!")
                logger.error("   💳 Adicione créditos em: https://platform.openai.com/billing")
                logger.error("   📊 Verifique seu uso em: https://platform.openai.com/usage")
            elif "invalid_api_key" in error_msg or "authentication" in error_msg:
                logger.error("❌ OPENAI: API Key inválida!")
                logger.error("   🔑 Verifique OPENAI_API_KEY no arquivo .env")
                logger.error("   🔗 Obtenha uma nova key em: https://platform.openai.com/api-keys")
            elif "rate_limit" in error_msg:
                logger.error("❌ OPENAI: Limite de requisições excedido!")
                logger.error("   ⏰ Aguarde um momento e tente novamente")
            else:
                logger.error(f"❌ OPENAI: Erro na geração - {error_msg}")
            return None
    
    async def switch_model(self, model_name: str) -> bool:
        """Troca para outro modelo"""
        try:
            logger.info(f"🔄 Trocando para modelo: {model_name}")
            
            # Verifica se o modelo existe
            if not await self._check_model_availability(model_name):
                logger.info(f"📥 Baixando modelo: {model_name}")
                if not await self._download_model(model_name):
                    return False
            
            self.current_model = model_name
            logger.info(f"✅ Modelo trocado para: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao trocar modelo: {e}")
            return False
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """Lista modelos disponíveis"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                return response.json().get('models', [])
            return []
        except:
            return []
    
    async def test_performance(self) -> Dict[str, Any]:
        """Testa performance dos modelos"""
        test_prompt = "Olá, como você está? Responda em português."
        
        results = {
            "ollama": {"success": False, "time": 0, "response": ""},
            "openai": {"success": False, "time": 0, "response": ""}
        }
        
        # Teste Ollama
        try:
            start_time = asyncio.get_event_loop().time()
            response = await self._generate_ollama(test_prompt)
            end_time = asyncio.get_event_loop().time()
            
            results["ollama"] = {
                "success": response is not None,
                "time": end_time - start_time,
                "response": response or ""
            }
        except Exception as e:
            logger.error(f"❌ Erro no teste Ollama: {e}")
        
        # Teste OpenAI
        try:
            start_time = asyncio.get_event_loop().time()
            response = await self._generate_openai(test_prompt)
            end_time = asyncio.get_event_loop().time()
            
            results["openai"] = {
                "success": response is not None,
                "time": end_time - start_time,
                "response": response or ""
            }
        except Exception as e:
            logger.error(f"❌ Erro no teste OpenAI: {e}")
        
        return results
    
    async def cleanup(self):
        """Limpa recursos"""
        logger.info("🧹 Limpando Ollama Manager...")
        self.is_initialized = False
        logger.info("✅ Ollama Manager limpo")
