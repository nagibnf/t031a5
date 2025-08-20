#!/bin/bash

# Script de instalação do SDK G1 para t031a5
# Este script instala e configura o SDK2 Python da Unitree

set -e  # Para em caso de erro

echo "🚀 Instalando SDK G1 para t031a5..."
echo "=================================="

# Verificar Python
echo "🔍 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instale Python 3.9+ primeiro."
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python $PYTHON_VERSION encontrado"

# Verificar pip
echo "🔍 Verificando pip..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado. Instale pip primeiro."
    exit 1
fi

echo "✅ pip3 encontrado"

# Instalar SDK2 Python
echo "📦 Instalando SDK2 Python da Unitree..."
if pip3 install unitree-sdk2py; then
    echo "✅ SDK2 Python instalado com sucesso"
else
    echo "❌ Falha na instalação do SDK2 Python"
    echo "💡 Tente instalar manualmente: pip3 install unitree-sdk2py"
    exit 1
fi

# Verificar instalação
echo "🔍 Verificando instalação..."
if python3 -c "import unitree_sdk2py; print('✅ SDK importado com sucesso')"; then
    echo "✅ SDK2 Python funcionando corretamente"
else
    echo "❌ Erro ao importar SDK2 Python"
    exit 1
fi

# Verificar versão
echo "🔍 Verificando versão do SDK..."
python3 -c "
try:
    import unitree_sdk2py
    version = getattr(unitree_sdk2py, '__version__', 'Não disponível')
    print(f'📋 Versão do SDK: {version}')
except Exception as e:
    print(f'⚠️  Não foi possível obter versão: {e}')
"

# Configurar rede (opcional)
echo ""
echo "🌐 Configuração de rede (opcional)..."
echo "Para conectar com G1, configure a rede:"
echo ""
echo "Opção A - Conexão direta (recomendado):"
echo "  1. Conecte cabo Ethernet entre G1 e computador"
echo "  2. Execute: sudo ifconfig en0 192.168.123.100 netmask 255.255.255.0"
echo ""
echo "Opção B - Rede WiFi:"
echo "  1. Conecte G1 e computador à mesma rede WiFi"
echo "  2. Descubra IP do G1: ifconfig (no G1)"
echo ""

# Testar conectividade
echo "🔍 Testando conectividade com G1..."
if ping -c 1 192.168.123.161 &> /dev/null; then
    echo "✅ G1 encontrado na rede (192.168.123.161)"
else
    echo "⚠️  G1 não encontrado na rede padrão"
    echo "💡 Verifique se G1 está ligado e conectado"
fi

# Verificar configuração
echo "🔍 Verificando configuração do t031a5..."
if [ -f "config/g1_real.json5" ]; then
    echo "✅ Configuração g1_real.json5 encontrada"
else
    echo "⚠️  Configuração g1_real.json5 não encontrada"
    echo "💡 Execute: python3 test_real_g1_integration.py"
fi

# Instruções finais
echo ""
echo "🎉 Instalação concluída!"
echo "========================"
echo ""
echo "📋 Próximos passos:"
echo "1. Configure a rede para conectar com G1"
echo "2. Teste a conectividade: python3 test_real_g1_integration.py"
echo "3. Execute o sistema: python3 -m t031a5.cli run --config config/g1_real.json5"
echo "4. Acesse a interface web: http://localhost:8080"
echo ""
echo "📚 Documentação: docs/g1_integration_guide.md"
echo "🧪 Testes: test_real_g1_integration.py"
echo ""
echo "🚀 Boa sorte com seu G1!"
