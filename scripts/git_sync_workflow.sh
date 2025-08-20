#!/bin/bash
# Workflow de Sincronização via Git
# Permite sincronização bidirecional usando Git como fonte única da verdade

set -e

JETSON_IP="192.168.123.164"
JETSON_USER="unitree"
PROJECT_PATH="/Users/nagib/t031a5"
JETSON_PATH="/home/unitree/t031a5"

echo "🔄 SINCRONIZAÇÃO VIA GIT"
echo "======================="

# Função para push do Mac
push_from_mac() {
    echo "📤 PUSH: MAC → GIT → JETSON"
    echo "----------------------------"
    
    echo "📝 Commitando mudanças no Mac..."
    cd "$PROJECT_PATH"
    
    # Adicionar mudanças
    git add .
    
    # Verificar se há mudanças para commit
    if git diff --staged --quiet; then
        echo "⚠️ Nenhuma mudança para commitar"
    else
        # Criar commit com timestamp
        timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        commit_msg="Sync from Mac - $timestamp"
        git commit -m "$commit_msg" || true
        
        echo "🚀 Fazendo push para repositório..."
        git push origin main || echo "⚠️ Push falhou - verifique conectividade"
    fi
    
    echo "📥 Fazendo pull na Jetson..."
    ssh "$JETSON_USER@$JETSON_IP" "
        cd $JETSON_PATH && \
        echo '🔄 Fazendo pull das mudanças...' && \
        git pull origin main && \
        echo '✅ Jetson atualizada!'
    "
    
    echo "✅ Push Mac → Jetson concluído!"
}

# Função para pull da Jetson
pull_from_jetson() {
    echo "📥 PULL: JETSON → GIT → MAC"
    echo "----------------------------"
    
    echo "📝 Commitando mudanças na Jetson..."
    ssh "$JETSON_USER@$JETSON_IP" "
        cd $JETSON_PATH && \
        git add . && \
        if ! git diff --staged --quiet; then
            timestamp=\$(date '+%Y-%m-%d %H:%M:%S')
            git commit -m 'Sync from Jetson - \$timestamp' || true
            echo '🚀 Fazendo push para repositório...'
            git push origin main || echo '⚠️ Push falhou - verifique conectividade'
        else
            echo '⚠️ Nenhuma mudança para commitar na Jetson'
        fi
    "
    
    echo "📥 Fazendo pull no Mac..."
    cd "$PROJECT_PATH"
    git pull origin main
    
    echo "✅ Pull Jetson → Mac concluído!"
}

# Função para status dos repositórios
check_status() {
    echo "📊 STATUS DOS REPOSITÓRIOS"
    echo "--------------------------"
    
    echo "📱 Mac:"
    cd "$PROJECT_PATH"
    echo "   Branch: $(git branch --show-current)"
    echo "   Último commit: $(git log -1 --pretty=format:'%h - %s (%cr)')"
    
    if ! git diff --quiet; then
        echo "   ⚠️ Mudanças não commitadas no Mac"
        git status --porcelain | head -5
    else
        echo "   ✅ Mac limpo"
    fi
    
    echo ""
    echo "🤖 Jetson:"
    ssh "$JETSON_USER@$JETSON_IP" "
        cd $JETSON_PATH && \
        echo '   Branch: '\$(git branch --show-current) && \
        echo '   Último commit: '\$(git log -1 --pretty=format:'%h - %s (%cr)') && \
        if ! git diff --quiet; then
            echo '   ⚠️ Mudanças não commitadas na Jetson'
            git status --porcelain | head -5
        else
            echo '   ✅ Jetson limpa'
        fi
    "
}

# Função para sincronização bidirecional
bidirectional_sync() {
    echo "🔄 SINCRONIZAÇÃO BIDIRECIONAL"
    echo "-----------------------------"
    
    echo "1️⃣ Verificando status..."
    check_status
    
    echo ""
    echo "2️⃣ Sincronizando Mac → Git..."
    cd "$PROJECT_PATH"
    git add .
    if ! git diff --staged --quiet; then
        timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        git commit -m "Bidirectional sync from Mac - $timestamp" || true
        git push origin main || echo "⚠️ Push do Mac falhou"
    fi
    
    echo ""
    echo "3️⃣ Sincronizando Jetson → Git..."
    ssh "$JETSON_USER@$JETSON_IP" "
        cd $JETSON_PATH && \
        git add . && \
        if ! git diff --staged --quiet; then
            timestamp=\$(date '+%Y-%m-%d %H:%M:%S')
            git commit -m 'Bidirectional sync from Jetson - \$timestamp' || true
            git push origin main || echo '⚠️ Push da Jetson falhou'
        fi
    "
    
    echo ""
    echo "4️⃣ Atualizando ambos os ambientes..."
    git pull origin main
    ssh "$JETSON_USER@$JETSON_IP" "cd $JETSON_PATH && git pull origin main"
    
    echo "✅ Sincronização bidirecional concluída!"
}

# Menu
case "${1:-menu}" in
    "push")
        push_from_mac
        ;;
    "pull")
        pull_from_jetson
        ;;
    "status")
        check_status
        ;;
    "sync"|"bidirectional")
        bidirectional_sync
        ;;
    "menu"|*)
        echo "🛠️ OPÇÕES DE SINCRONIZAÇÃO VIA GIT:"
        echo ""
        echo "  $0 push           📤 Mac → Git → Jetson"
        echo "  $0 pull           📥 Jetson → Git → Mac"
        echo "  $0 status         📊 Status dos repositórios"
        echo "  $0 sync           🔄 Sincronização bidirecional"
        echo ""
        echo "💡 Uso: $0 [opção]"
        ;;
esac

echo ""
echo "🎯 Git sync concluído!"
