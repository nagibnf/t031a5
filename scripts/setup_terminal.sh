#!/bin/bash
# Script para configurar terminal e ambiente virtual do t031a5

echo "🔧 Configurando ambiente t031a5..."

# Verificar se estamos no zsh
if [[ "$SHELL" == *"zsh"* ]]; then
    echo "✅ Usando ZSH - Perfeito!"
else
    echo "⚠️  Recomendado: Configure o Cursor para usar ZSH"
    echo "   Vá em: Cmd + , → Terminal › Integrated › Default Profile: Osx → zsh"
fi

# Verificar se o venv existe
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Verificar se está ativo
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Ambiente virtual ativado: $VIRTUAL_ENV"
    echo "🐍 Python: $(which python)"
    echo "📦 Pip: $(which pip)"
    
    # Verificar se o projeto está instalado
    if python -c "import t031a5" 2>/dev/null; then
        echo "✅ Projeto t031a5 instalado"
    else
        echo "📦 Instalando projeto t031a5..."
        pip install -e .
    fi
    
    echo ""
    echo "🚀 AMBIENTE CONFIGURADO COM SUCESSO!"
    echo ""
    echo "📋 Comandos úteis:"
    echo "   python -m t031a5.cli run --config config/g1_conversation.json5"
    echo "   python -m t031a5.cli status"
    echo "   python tests/run_test.py test_conversation_system.py"
    echo ""
    echo "🔍 Para verificar se está tudo funcionando:"
    echo "   python -m t031a5.cli --help"
    echo ""
    echo "❌ Para desativar: deactivate"
    
else
    echo "❌ Falha ao ativar ambiente virtual"
    exit 1
fi
