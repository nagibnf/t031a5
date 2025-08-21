# 🤖 Checklist Deploy Final Jetson G1 Tobias

**🫧 Desenvolvido por Bolha**

## 📋 Estratégia: Limpeza Completa + Deploy Limpo

### **FASE 1: AUDITORIA JETSON** 🔍

#### 1.1 Processos Ativos
```bash
# Verificar o que está rodando
ps aux | grep -E "(python|unitree|t031a5)" | grep -v grep
ps aux | grep -E "(ollama|llava)" | grep -v grep

# Verificar serviços do sistema  
systemctl list-units --type=service --state=running | grep -E "(unitree|python)"
```

#### 1.2 Conexões de Rede
```bash
# Verificar portas em uso
netstat -tulpn | grep LISTEN
netstat -tulpn | grep 8080  # WebSim
netstat -tulpn | grep 1234  # Ollama padrão

# Verificar interfaces
ifconfig
ip addr show eth0
```

#### 1.3 Espaço e Arquivos
```bash
# Espaço em disco
df -h
du -sh /home/unitree/*
du -sh /home/unitree/.* 2>/dev/null

# Logs e temporários
find /home/unitree -name "*.log" -size +10M
find /home/unitree -name "__pycache__" -type d
```

### **FASE 2: LIMPEZA RADICAL** 🧹

#### 2.1 Parar Tudo
```bash
# Parar processos t031a5
sudo pkill -f "python.*t031a5" || true
sudo pkill -f "t031a5" || true

# Parar processos relacionados  
sudo pkill -f "ollama" || true
sudo pkill -f "websim" || true

# Verificar se parou
ps aux | grep -E "(t031a5|ollama)" | grep -v grep
```

#### 2.2 Remover Instalações Antigas
```bash
# Backups e versões antigas
rm -rf /home/unitree/t031a5_old* || true
rm -rf /home/unitree/t031a5_backup* || true

# Logs antigos
rm -rf /home/unitree/logs/* || true
mkdir -p /home/unitree/logs

# Cache Python
rm -rf /home/unitree/.cache/pip/* || true
find /home/unitree -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
```

#### 2.3 Verificar Dependências
```bash
# Packages Python instalados
pip list | grep -E "(test|debug|temp|mock)"
pip list | grep -E "(unitree|torch|opencv)"

# Verificar ambiente virtual atual
which python3
pip list | wc -l
```

### **FASE 3: DEPLOY LIMPO** 🚀

#### 3.1 Preparar Ambiente
```bash
cd /home/unitree

# Backup config atual (se necessário)
cp -r t031a5/.env t031a5_env_backup 2>/dev/null || true

# Git sync código limpo
cd t031a5
git status
git pull origin main
```

#### 3.2 Ambiente Virtual Novo
```bash
# Remover venv antigo
rm -rf venv

# Criar venv novo
python3 -m venv venv
source venv/bin/activate

# Instalar dependências mínimas
pip install --upgrade pip
pip install -e .
```

#### 3.3 Configuração Produção
```bash
# Verificar arquivo .env
ls -la .env
cat .env | grep -E "(OPENAI|ANTHROPIC|ELEVENLABS)" | wc -l

# Configurar interface eth0 
grep -r "eth0" config/
grep -r "en11\|en0" config/ || echo "✅ Todas interfaces corretas"
```

#### 3.4 Testes Finais
```bash
# Teste básico
python3 -m t031a5.cli validate --config config/g1_real.json5

# Teste conexão G1
ping -c 3 192.168.123.161

# Teste SDK
python3 -c "
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
ChannelFactoryInitialize(0, 'eth0')
print('✅ SDK OK')
"
```

### **FASE 4: VERIFICAÇÃO SISTEMA** ✅

#### 4.1 Checklist Final
- [ ] Processos antigos parados
- [ ] Espaço em disco suficiente (>2GB)
- [ ] Código sincronizado (git)
- [ ] Virtual env novo
- [ ] Dependências instaladas
- [ ] Configuração eth0 correta
- [ ] .env com credenciais
- [ ] G1 conectado (ping OK)
- [ ] SDK funcionando
- [ ] Teste t031a5 OK

#### 4.2 Status Esperado
```bash
# Deve estar assim:
ps aux | grep python           # Só nossos processos
netstat -tulpn | grep 8080     # WebSim disponível
ifconfig eth0                  # Interface configurada  
ping 192.168.123.161           # G1 respondendo
```

---

## 🎯 **OBJETIVOS DO DEPLOY:**

1. **🧹 Jetson Limpa**: Sem processos fantasmas ou lixo
2. **🔗 Conectividade**: eth0 configurado, G1 respondendo  
3. **🐍 Python**: Ambiente isolado, dependências corretas
4. **⚙️ Configuração**: Arquivos corretos, credenciais OK
5. **✅ Funcional**: Sistema validado e operacional

---

## 📞 **SUPORTE:**

- **Documentação**: `docs/project/RESUMO_COMPLETO_SISTEMA_t031a5_ATUALIZADO.md`
- **Arquitetura**: `docs/project/DIAGRAMA_ARQUITETURA_t031a5.md`  
- **Lições**: Memórias persistentes no chat
- **Configs**: Tudo em `config/g1_real.json5`

**🎯 Meta: G1 Tobias 100% operacional em produção! 🤖✨**
