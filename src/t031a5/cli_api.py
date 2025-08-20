"""
CLI para Gerenciamento Seguro de APIs.
Interface de linha de comando para configurar APIs de forma segura.
"""

import typer
from typing import Optional
from pathlib import Path

from .security import SimpleAPIManager

app = typer.Typer(help="Gerenciamento Simples de APIs")





@app.command()
def list():
    """Lista todas as APIs configuradas (sem mostrar chaves)."""
    api_manager = SimpleAPIManager()
    api_manager.initialize()
    
    apis = api_manager.list_apis()
    
    if not apis:
        typer.echo("📋 Nenhuma API configurada")
        return
    
    typer.echo("📋 APIs Configuradas:")
    typer.echo("=" * 50)
    
    for name, config in apis.items():
        status = "✅" if config["enabled"] else "❌"
        typer.echo(f"{status} {name}")
        typer.echo(f"   Provedor: {config['provider']}")
        typer.echo(f"   Rate Limit: {config.get('rate_limit', 'N/A')}")
        typer.echo(f"   Timeout: {config.get('timeout', 'N/A')}s")
        typer.echo()





@app.command()
def validate():
    """Valida todas as APIs configuradas."""
    api_manager = SimpleAPIManager()
    api_manager.initialize()
    
    results = api_manager.validate_apis()
    
    typer.echo("🔍 Validação das APIs:")
    typer.echo("=" * 30)
    
    all_valid = True
    for name, is_valid in results.items():
        status = "✅" if is_valid else "❌"
        typer.echo(f"{status} {name}")
        if not is_valid:
            all_valid = False
    
    if all_valid:
        typer.echo("\n🎉 Todas as APIs são válidas!")
    else:
        typer.echo("\n⚠️ Algumas APIs têm problemas")
        raise typer.Exit(1)


@app.command()
def init():
    """Inicializa arquivo .env para configuração de APIs."""
    env_example_path = Path("env.example")
    env_path = Path(".env")
    
    if env_path.exists():
        typer.echo(f"⚠️  Arquivo .env já existe")
        overwrite = typer.confirm("Deseja sobrescrever?")
        if not overwrite:
            typer.echo("Operação cancelada")
            return
    
    if env_example_path.exists():
        # Copiar exemplo para .env
        with open(env_example_path, 'r') as f:
            content = f.read()
        
        with open(env_path, 'w') as f:
            f.write(content)
        
        typer.echo(f"✅ Arquivo .env criado com sucesso!")
        typer.echo(f"📝 Edite o arquivo .env e adicione suas chaves de API")
        typer.echo(f"🔧 Depois execute: './t031a5 api load' para carregar as chaves")
    else:
        # Criar arquivo .env básico
        content = """# Configuração de APIs para t031a5
# Adicione suas chaves reais abaixo

# OpenAI API (GPT-4o, GPT-4o-mini)
OPENAI_API_KEY=sk-proj-sua_chave_aqui

# Anthropic API (Claude)
ANTHROPIC_API_KEY=sk-ant-sua_chave_aqui

# ElevenLabs API (TTS Avançado)
ELEVENLABS_API_KEY=sua_chave_aqui

# Google API (Speech-to-Text, etc.)
GOOGLE_API_KEY=sua_chave_aqui

# Google ASR (arquivo JSON de credenciais)
# O arquivo deve estar em: credentials/google_asr.json
GOOGLE_ASR_CREDENTIALS_FILE=credentials/google_asr.json
"""
        
        with open(env_path, 'w') as f:
            f.write(content)
        
        typer.echo(f"✅ Arquivo .env criado com sucesso!")
        typer.echo(f"📝 Edite o arquivo .env e adicione suas chaves de API")
        typer.echo(f"🔧 Depois execute: './t031a5 api load' para carregar as chaves")


@app.command()
def setup_google_asr():
    """Configura Google ASR com arquivo JSON."""
    typer.echo(f"🔧 Google ASR - Configuração")
    typer.echo(f"")
    typer.echo(f"📁 Coloque seu arquivo JSON em: credentials/google_asr.json")
    typer.echo(f"")
    typer.echo(f"🔗 Obtenha o arquivo em: https://console.cloud.google.com/apis/credentials")
    typer.echo(f"")
    typer.echo(f"✅ Depois execute: './t031a5 api load' para carregar")


@app.command()
def init():
    """Inicializa arquivo .env para configuração de APIs."""
    env_example_path = Path("env.example")
    env_path = Path(".env")
    
    if env_path.exists():
        typer.echo(f"⚠️  Arquivo .env já existe")
        overwrite = typer.confirm("Deseja sobrescrever?")
        if not overwrite:
            typer.echo("Operação cancelada")
            return
    
    if env_example_path.exists():
        # Copiar exemplo para .env
        with open(env_example_path, 'r') as f:
            content = f.read()
        
        with open(env_path, 'w') as f:
            f.write(content)
        
        typer.echo(f"✅ Arquivo .env criado com sucesso!")
        typer.echo(f"📝 Edite o arquivo .env e adicione suas chaves de API")
        typer.echo(f"🔧 Depois execute: './t031a5 api load' para carregar as chaves")
    else:
        # Criar arquivo .env básico
        content = """# Configuração de APIs para t031a5
# Adicione suas chaves reais abaixo

# OpenAI API (GPT-4o, GPT-4o-mini)
OPENAI_API_KEY=sk-proj-sua_chave_aqui

# Anthropic API (Claude)
ANTHROPIC_API_KEY=sk-ant-sua_chave_aqui

# ElevenLabs API (TTS Avançado)
ELEVENLABS_API_KEY=sua_chave_aqui

# Google API (Speech-to-Text, etc.)
GOOGLE_API_KEY=sua_chave_aqui
"""
        
        with open(env_path, 'w') as f:
            f.write(content)
        
        typer.echo(f"✅ Arquivo .env criado com sucesso!")
        typer.echo(f"📝 Edite o arquivo .env e adicione suas chaves de API")
        typer.echo(f"🔧 Depois execute: './t031a5 api load' para carregar as chaves")


@app.command()
def load():
    """Carrega APIs do arquivo .env."""
    from .security import SimpleAPIManager
    
    env_path = Path(".env")
    if not env_path.exists():
        typer.echo("❌ Arquivo .env não encontrado")
        typer.echo("Execute './t031a5 api init' para criar o arquivo")
        raise typer.Exit(1)
    
    api_manager = SimpleAPIManager()
    api_manager.initialize()
    
    # Contar APIs carregadas
    apis = api_manager.list_apis()
    count = len([api for api in apis.values() if api["enabled"]])
    
    if count > 0:
        typer.echo(f"✅ {count} APIs carregadas do arquivo .env")
        typer.echo("Use './t031a5 api list' para ver as APIs configuradas")
    else:
        typer.echo("⚠️  Nenhuma API encontrada no arquivo .env")
        typer.echo("Verifique se as chaves estão configuradas corretamente")





@app.command()
def test():
    """Testa conectividade das APIs configuradas."""
    api_manager = SimpleAPIManager()
    api_manager.initialize()
    
    typer.echo("🧪 Testando conectividade das APIs:")
    typer.echo("=" * 40)
    
    apis = api_manager.list_apis()
    
    if not apis:
        typer.echo("❌ Nenhuma API configurada para testar")
        return
    
    for name, config in apis.items():
        if not config["enabled"]:
            typer.echo(f"⏸️ {name}: Desabilitada")
            continue
        
        api_key = api_manager.get_api_key(name)
        if not api_key:
            typer.echo(f"❌ {name}: Chave não encontrada")
            continue
        
        # Teste básico de conectividade
        try:
            if name == "openai":
                import openai
                client = openai.OpenAI(api_key=api_key)
                response = client.models.list()
                typer.echo(f"✅ {name}: Conectividade OK")
            elif name == "anthropic":
                import anthropic
                client = anthropic.Anthropic(api_key=api_key)
                response = client.models.list()
                typer.echo(f"✅ {name}: Conectividade OK")
            elif name == "elevenlabs":
                import requests
                headers = {"xi-api-key": api_key}
                response = requests.get("https://api.elevenlabs.io/v1/voices", headers=headers)
                if response.status_code == 200:
                    typer.echo(f"✅ {name}: Conectividade OK")
                else:
                    typer.echo(f"❌ {name}: Erro de conectividade - {response.status_code}")
            else:
                typer.echo(f"✅ {name}: Configurada (teste manual necessário)")
        except Exception as e:
            typer.echo(f"❌ {name}: Erro de conectividade - {str(e)}")


if __name__ == "__main__":
    app()
