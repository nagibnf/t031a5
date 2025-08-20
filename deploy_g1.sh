#!/bin/bash
# Deploy Script para Robô G1 - Sistema t031a5
# Este script prepara e instala o sistema no robô G1

set -e  # Para se houver erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🤖 t031a5 - Deploy para Robô G1${NC}"
echo -e "${BLUE}=================================${NC}"

# Verificar se está na pasta correta
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Execute este script na pasta raiz do projeto t031a5"
    exit 1
fi

# Verificar se o venv existe
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
echo "📦 Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
echo "📦 Instalando dependências do projeto..."
pip install -e .

# Instalar Unitree SDK (se não estiver instalado)
if ! python -c "import unitree_sdk2py" 2>/dev/null; then
    echo "🤖 Instalando Unitree SDK..."
    if [ -d "unitree_sdk2_python" ]; then
        cd unitree_sdk2_python
        pip install -e .
        cd ..
    else
        echo "⚠️  Pasta unitree_sdk2_python não encontrada"
        echo "   Download do SDK necessário de: https://github.com/unitreerobotics/unitree_sdk2"
    fi
fi

# Verificar variáveis de ambiente
echo "🔧 Verificando configuração..."
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY não configurada"
    echo "   Execute: export OPENAI_API_KEY='sua_key_aqui'"
fi

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p logs
mkdir -p data
mkdir -p temp

# Testar sistema
echo "🧪 Testando sistema..."
python -m t031a5.cli validate --config config/g1_production.json5

# Verificar conectividade com G1
echo "🔌 Verificando conectividade com G1..."
G1_IP=$(python -c "
import json5
with open('config/g1_production.json5', 'r') as f:
    config = json5.load(f)
print(config['g1_controller']['interface']['robot_ip'])
")

echo "📡 Testando ping para G1 em $G1_IP..."
if ping -c 1 -W 3 "$G1_IP" >/dev/null 2>&1; then
    echo "✅ G1 acessível em $G1_IP"
else
    echo "⚠️  G1 não encontrado em $G1_IP"
    echo "   Verifique se o robô está ligado e na mesma rede"
fi

# Executar testes
echo "🧪 Executando testes rápidos..."
python tests/run_test.py test_system.py --quick

echo ""
echo "🎉 DEPLOY CONCLUÍDO!"
echo ""
echo "📋 Próximos passos:"
echo "1. Verificar se o G1 está ligado e conectado na rede"
echo "2. Configurar IP correto em config/g1_production.json5"
echo "3. Executar: python -m t031a5.cli run --config config/g1_production.json5"
echo ""
echo "🌐 WebSim estará disponível em: http://localhost:8080"
echo "📊 Logs em: logs/g1_production.log"
echo ""
echo "🚀 Para iniciar: ./start_g1.sh"
