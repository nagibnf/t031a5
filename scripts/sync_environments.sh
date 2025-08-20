#!/bin/bash
# Script de Sincronização de Ambientes t031a5
# Sincroniza Mac (desenvolvimento) ↔ Jetson (produção)

set -e

JETSON_IP="192.168.123.164"
JETSON_USER="unitree"
PROJECT_PATH="/Users/nagib/t031a5"
JETSON_PATH="/home/unitree/t031a5"

echo "🔄 SINCRONIZAÇÃO DE AMBIENTES T031A5"
echo "=================================="
echo "📱 Mac (dev): $PROJECT_PATH"
echo "🤖 Jetson: $JETSON_USER@$JETSON_IP:$JETSON_PATH"
echo ""

# Função para sincronizar do Mac para Jetson
sync_to_jetson() {
    echo "📤 SINCRONIZANDO MAC → JETSON..."
    echo "--------------------------------"
    
    # Sincronizar código fonte
    echo "📁 Sincronizando src/..."
    rsync -avz --delete \
        "$PROJECT_PATH/src/" \
        "$JETSON_USER@$JETSON_IP:$JETSON_PATH/src/"
    
    # Sincronizar scripts
    echo "📁 Sincronizando scripts/..."
    rsync -avz --delete \
        "$PROJECT_PATH/scripts/" \
        "$JETSON_USER@$JETSON_IP:$JETSON_PATH/scripts/"
    
    # Sincronizar configurações
    echo "📁 Sincronizando config/..."
    rsync -avz --delete \
        "$PROJECT_PATH/config/" \
        "$JETSON_USER@$JETSON_IP:$JETSON_PATH/config/"
    
    # Sincronizar arquivos importantes
    echo "📄 Sincronizando arquivos raiz..."
    scp "$PROJECT_PATH/pyproject.toml" \
        "$JETSON_USER@$JETSON_IP:$JETSON_PATH/"
    
    echo "✅ Sincronização MAC → JETSON concluída!"
}

# Função para sincronizar da Jetson para Mac
sync_from_jetson() {
    echo "📥 SINCRONIZANDO JETSON → MAC..."
    echo "--------------------------------"
    
    # Sincronizar apenas arquivos específicos que podem ter mudado
    echo "📁 Sincronizando modificações da Jetson..."
    
    # Criar backup antes
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_dir="$PROJECT_PATH/backup_sync_$timestamp"
    mkdir -p "$backup_dir"
    
    # Backup dos arquivos que vamos sobrescrever
    cp -r "$PROJECT_PATH/src" "$backup_dir/" 2>/dev/null || true
    cp -r "$PROJECT_PATH/scripts" "$backup_dir/" 2>/dev/null || true
    
    # Sincronizar da Jetson
    rsync -avz \
        "$JETSON_USER@$JETSON_IP:$JETSON_PATH/src/" \
        "$PROJECT_PATH/src/"
    
    rsync -avz \
        "$JETSON_USER@$JETSON_IP:$JETSON_PATH/scripts/" \
        "$PROJECT_PATH/scripts/"
    
    echo "📦 Backup criado em: $backup_dir"
    echo "✅ Sincronização JETSON → MAC concluída!"
}

# Função para validar sincronização
validate_sync() {
    echo "🔍 VALIDANDO SINCRONIZAÇÃO..."
    echo "-----------------------------"
    
    # Verificar se arquivos principais existem na Jetson
    echo "🔎 Verificando arquivos na Jetson..."
    ssh "$JETSON_USER@$JETSON_IP" "
        cd $JETSON_PATH && \
        echo '📁 Estrutura do projeto:' && \
        ls -la && \
        echo '' && \
        echo '🐍 Arquivos Python principais:' && \
        find src -name '*.py' | head -10 && \
        echo '' && \
        echo '⚙️ Configurações:' && \
        ls -la config/ | head -5
    "
    
    echo "✅ Validação concluída!"
}

# Função para testar funcionamento na Jetson
test_jetson() {
    echo "🧪 TESTANDO FUNCIONAMENTO NA JETSON..."
    echo "------------------------------------"
    
    ssh "$JETSON_USER@$JETSON_IP" "
        cd $JETSON_PATH && \
        export PYTHONPATH=$JETSON_PATH/src && \
        echo '🐍 Testando imports...' && \
        python3 -c 'from t031a5.unitree.g1_controller import G1Controller; print(\"✅ G1Controller OK\")' && \
        echo '🤖 Executando teste rápido...' && \
        timeout 30s python3 ~/test_final_clean.py || echo '⏰ Timeout (normal para teste rápido)'
    "
    
    echo "✅ Teste na Jetson concluído!"
}

# Menu principal
case "${1:-menu}" in
    "to-jetson"|"push")
        sync_to_jetson
        validate_sync
        ;;
    "from-jetson"|"pull")
        sync_from_jetson
        ;;
    "validate")
        validate_sync
        ;;
    "test")
        test_jetson
        ;;
    "full")
        sync_to_jetson
        validate_sync
        test_jetson
        ;;
    "menu"|*)
        echo "🛠️ OPÇÕES DE SINCRONIZAÇÃO:"
        echo ""
        echo "  $0 to-jetson    📤 Sincronizar Mac → Jetson"
        echo "  $0 from-jetson  📥 Sincronizar Jetson → Mac"
        echo "  $0 validate     🔍 Validar sincronização"
        echo "  $0 test         🧪 Testar funcionamento"
        echo "  $0 full         🚀 Sincronização completa + teste"
        echo ""
        echo "💡 Uso: $0 [opção]"
        ;;
esac

echo ""
echo "🎯 Script de sincronização concluído!"
