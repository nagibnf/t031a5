#!/usr/bin/env python3
"""
Script de setup para Ollama no sistema t031a5
Configura Ollama para uso com o robô Tobias (G1)
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    print("🚀 SETUP OLLAMA - Sistema t031a5")
    print("=" * 50)
    print("Configurando Ollama para Tobias (G1)")
    print()

def check_system():
    """Verifica o sistema operacional"""
    system = platform.system()
    arch = platform.machine()
    
    print(f"🖥️ Sistema: {system}")
    print(f"🏗️ Arquitetura: {arch}")
    
    if system == "Linux" and "aarch64" in arch:
        print("✅ Jetson detectado!")
        return "jetson"
    elif system == "Darwin":
        print("✅ macOS detectado!")
        return "macos"
    else:
        print("⚠️ Sistema não identificado")
        return "unknown"

def install_ollama(system_type):
    """Instala Ollama baseado no sistema"""
    print("\n📥 Instalando Ollama...")
    
    if system_type == "jetson":
        # Jetson Orin NX - ARM64
        install_cmd = "curl -fsSL https://ollama.ai/install.sh | sh"
    elif system_type == "macos":
        # macOS
        install_cmd = "curl -fsSL https://ollama.ai/install.sh | sh"
    else:
        print("❌ Sistema não suportado")
        return False
    
    try:
        print(f"🔧 Executando: {install_cmd}")
        result = subprocess.run(install_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Ollama instalado com sucesso!")
            return True
        else:
            print(f"❌ Erro na instalação: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def start_ollama_service():
    """Inicia o serviço Ollama"""
    print("\n🔧 Iniciando serviço Ollama...")
    
    try:
        # Tenta iniciar o serviço
        result = subprocess.run(["ollama", "serve"], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        
        if result.returncode == 0:
            print("✅ Serviço Ollama iniciado!")
            return True
        else:
            print("⚠️ Serviço já pode estar rodando")
            return True
            
    except subprocess.TimeoutExpired:
        print("✅ Serviço Ollama iniciado em background")
        return True
    except Exception as e:
        print(f"❌ Erro ao iniciar serviço: {e}")
        return False

def download_models():
    """Baixa modelos principais"""
    print("\n📥 Baixando modelos principais...")
    
    models = [
        "llama3.1:8b",      # Modelo principal
        "mistral:7b",       # Alternativa rápida
    ]
    
    for model in models:
        print(f"📥 Baixando {model}...")
        try:
            result = subprocess.run(["ollama", "pull", model], 
                                  capture_output=True, 
                                  text=True)
            
            if result.returncode == 0:
                print(f"✅ {model} baixado com sucesso!")
            else:
                print(f"❌ Erro ao baixar {model}: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")

def create_config_files():
    """Cria arquivos de configuração"""
    print("\n⚙️ Criando configurações...")
    
    # Verifica se os arquivos já existem
    config_files = [
        "config/g1_ollama_llm.json5",
        "src/t031a5/llm/ollama_manager.py"
    ]
    
    for config_file in config_files:
        if Path(config_file).exists():
            print(f"✅ {config_file} já existe")
        else:
            print(f"❌ {config_file} não encontrado")

def create_test_script():
    """Cria script de teste"""
    test_script = """#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from t031a5.llm.ollama_manager import OllamaManager

async def test_ollama():
    manager = OllamaManager()
    if await manager.initialize():
        print("✅ Ollama inicializado")
        
        print("\\n📊 Testando performance...")
        results = await manager.test_performance()
        
        print("\\n📋 RESULTADOS")
        if results["ollama"]["success"]:
            print(f"🖥️ Ollama: {results['ollama']['time']:.2f}s")
            print(f"   Resposta: {results['ollama']['response']}")
        else:
            print("❌ Ollama: Falhou")
            
        if results["openai"]["success"]:
            print(f"☁️ OpenAI: {results['openai']['time']:.2f}s")
            print(f"   Resposta: {results['openai']['response']}")
        else:
            print("❌ OpenAI: Falhou")
            
        await manager.cleanup()
    else:
        print("❌ Falha na inicialização")
    print("\\n🎉 Teste concluído!")

if __name__ == "__main__":
    asyncio.run(test_ollama())
"""
    
    test_path = Path("scripts/test/test_ollama.py")
    test_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(test_path, 'w') as f:
        f.write(test_script)
    
    # Torna executável
    test_path.chmod(0o755)
    print(f"✅ Script de teste criado: {test_path}")

def print_usage_instructions():
    """Imprime instruções de uso"""
    print("\n" + "=" * 50)
    print("🎉 SETUP OLLAMA CONCLUÍDO!")
    print("=" * 50)
    
    print("\n📋 COMANDOS ÚTEIS:")
    print("ollama serve                    # Iniciar serviço")
    print("ollama list                     # Listar modelos")
    print("ollama pull llama3.1:8b         # Baixar modelo")
    print("ollama run llama3.1:8b          # Executar modelo")
    
    print("\n🧪 TESTES:")
    print("python scripts/test/test_ollama.py")
    print("python examples/basic_usage.py --config config/g1_ollama_llm.json5")
    
    print("\n🔄 TROCAR MODELOS:")
    print("ollama pull mistral:7b          # Baixar modelo alternativo")
    print("ollama pull llama3.1:70b        # Modelo avançado (40GB)")
    
    print("\n📊 MONITORAMENTO:")
    print("ollama ps                       # Status dos modelos")
    print("ollama logs                     # Logs do serviço")
    
    print("\n🚀 PRÓXIMO PASSO:")
    print("Conectar DJI Mic 2 e Anker Soundcore 300 via Bluetooth")
    print("Executar: python scripts/test/test_ollama.py")

def main():
    print_header()
    
    # Verifica sistema
    system_type = check_system()
    
    # Instala Ollama
    if not install_ollama(system_type):
        print("❌ Falha na instalação do Ollama")
        return
    
    # Inicia serviço
    if not start_ollama_service():
        print("❌ Falha ao iniciar serviço")
        return
    
    # Baixa modelos
    download_models()
    
    # Cria arquivos de configuração
    create_config_files()
    
    # Cria script de teste
    create_test_script()
    
    # Instruções finais
    print_usage_instructions()

if __name__ == "__main__":
    main()
