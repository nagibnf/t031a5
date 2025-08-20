#!/bin/bash
# Script para ativar o ambiente virtual do t031a5

echo "🔧 Ativando ambiente virtual t031a5..."

# Verificar se o venv existe
if [ ! -d "venv" ]; then
    echo "❌ Ambiente virtual não encontrado. Criando..."
    python3 -m venv venv
fi

# Ativar o ambiente virtual
source venv/bin/activate

# Verificar se está ativo
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Ambiente virtual ativado: $VIRTUAL_ENV"
    echo "🐍 Python: $(which python)"
    echo "📦 Pip: $(which pip)"
    echo ""
    echo "🚀 Para usar o sistema t031a5:"
    echo "   python -m t031a5.cli run --config config/g1_conversation.json5"
    echo ""
    echo "🔍 Para verificar status:"
    echo "   python -m t031a5.cli status"
    echo ""
    echo "🧪 Para executar testes:"
    echo "   python tests/run_test.py test_conversation_system.py"
    echo ""
    echo "❌ Para desativar: deactivate"
else
    echo "❌ Falha ao ativar ambiente virtual"
    exit 1
fi
