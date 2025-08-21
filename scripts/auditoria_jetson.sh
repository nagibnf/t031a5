#!/bin/bash

# 🤖 Script de Auditoria Completa Jetson G1 Tobias
# Baseado no CHECKLIST_DEPLOY_JETSON.md

echo "🔍 INICIANDO AUDITORIA JETSON..."
echo "=================================="

echo ""
echo "📋 FASE 1.1: Processos Ativos"
echo "--------------------------------"
echo "Processos Python/Unitree/t031a5:"
ssh unitree@192.168.123.164 "ps aux | grep -E '(python|unitree|t031a5)' | grep -v grep" 2>/dev/null || echo "❌ Erro SSH"

echo ""
echo "Processos Ollama/LLaVA:"
ssh unitree@192.168.123.164 "ps aux | grep -E '(ollama|llava)' | grep -v grep" 2>/dev/null || echo "ℹ️  Nenhum processo Ollama/LLaVA ativo"

echo ""
echo "Serviços do sistema:"
ssh unitree@192.168.123.164 "systemctl list-units --type=service --state=running | grep -E '(unitree|python)'" 2>/dev/null || echo "ℹ️  Nenhum serviço específico encontrado"

echo ""
echo "📋 FASE 1.2: Conexões de Rede"
echo "--------------------------------"
echo "Portas em uso:"
ssh unitree@192.168.123.164 "netstat -tulpn | grep LISTEN | head -10" 2>/dev/null || echo "❌ Erro verificando portas"

echo ""
echo "Porta 8080 (WebSim):"
ssh unitree@192.168.123.164 "netstat -tulpn | grep 8080" 2>/dev/null || echo "ℹ️  Porta 8080 livre"

echo ""
echo "Interface eth0:"
ssh unitree@192.168.123.164 "ip addr show eth0" 2>/dev/null || echo "❌ Interface eth0 não encontrada"

echo ""
echo "📋 FASE 1.3: Espaço e Arquivos"
echo "--------------------------------"
echo "Espaço em disco:"
ssh unitree@192.168.123.164 "df -h | head -5" 2>/dev/null || echo "❌ Erro verificando espaço"

echo ""
echo "Tamanho diretórios usuário:"
ssh unitree@192.168.123.164 "du -sh /home/unitree/* 2>/dev/null | head -10" || echo "ℹ️  Verificando diretórios..."

echo ""
echo "Logs grandes (>10MB):"
ssh unitree@192.168.123.164 "find /home/unitree -name '*.log' -size +10M 2>/dev/null" || echo "ℹ️  Nenhum log grande encontrado"

echo ""
echo "Diretórios __pycache__:"
ssh unitree@192.168.123.164 "find /home/unitree -name '__pycache__' -type d 2>/dev/null | wc -l" || echo "0"

echo ""
echo "✅ AUDITORIA COMPLETA!"
echo "=================================="
