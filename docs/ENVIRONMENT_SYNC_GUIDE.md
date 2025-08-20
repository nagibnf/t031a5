# Guia de Sincronização de Ambientes t031a5

## 🎯 Visão Geral

Este documento descreve como manter os ambientes **Mac (desenvolvimento)** e **Jetson (produção)** sincronizados com as versões funcionais do sistema t031a5.

## 🏗️ Arquitetura de Sincronização

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Mac (Dev)     │────▶│   Git Repo      │────▶│ Jetson (Prod)   │
│                 │     │  (Fonte da      │     │                 │
│ - Desenvolvimento│     │   Verdade)      │     │ - Robô Tobias   │
│ - Testes        │◀────│                 │◀────│ - Produção      │
│ - Debugging     │     │                 │     │ - Deploy        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## 🛠️ Ferramentas de Sincronização

### 1. Script de Sincronização Direta (`sync_environments.sh`)

**Uso rápido para desenvolvimento:**

```bash
# Sincronizar Mac → Jetson
./scripts/sync_environments.sh to-jetson

# Sincronizar Jetson → Mac  
./scripts/sync_environments.sh from-jetson

# Sincronização completa + teste
./scripts/sync_environments.sh full

# Ver todas as opções
./scripts/sync_environments.sh menu
```

**Vantagens:**
- ✅ Rápido e direto
- ✅ Não requer commits
- ✅ Ideal para desenvolvimento ativo

**Desvantagens:**
- ⚠️ Não mantém histórico
- ⚠️ Pode sobrescrever mudanças

### 2. Workflow Git (`git_sync_workflow.sh`)

**Uso para controle de versão:**

```bash
# Push: Mac → Git → Jetson
./scripts/git_sync_workflow.sh push

# Pull: Jetson → Git → Mac
./scripts/git_sync_workflow.sh pull

# Sincronização bidirecional
./scripts/git_sync_workflow.sh sync

# Verificar status dos repositórios
./scripts/git_sync_workflow.sh status
```

**Vantagens:**
- ✅ Mantém histórico completo
- ✅ Controle de versão
- ✅ Seguro contra perda de dados

**Desvantagens:**
- ⚠️ Mais lento
- ⚠️ Requer commits

## 📋 Fluxos de Trabalho Recomendados

### Desenvolvimento Ativo (Iterações Rápidas)

```bash
# 1. Fazer mudanças no Mac
# 2. Sincronizar rapidamente
./scripts/sync_environments.sh to-jetson

# 3. Testar na Jetson
./scripts/sync_environments.sh test

# 4. Se funcionou, repetir ciclo
```

### Release/Deploy (Versão Estável)

```bash
# 1. Finalizar mudanças no Mac
# 2. Commitar e fazer push via Git
./scripts/git_sync_workflow.sh push

# 3. Validar sincronização
./scripts/git_sync_workflow.sh status

# 4. Testar versão final
./scripts/sync_environments.sh test
```

### Correção de Bug na Jetson

```bash
# 1. Fazer correção diretamente na Jetson
# 2. Sincronizar de volta via Git
./scripts/git_sync_workflow.sh pull

# 3. Validar no Mac
# 4. Continuar desenvolvimento
```

## 🔧 Estrutura dos Arquivos Sincronizados

### Diretórios Principais
```
t031a5/
├── src/                    # Código fonte principal
│   └── t031a5/            # Pacote Python
├── scripts/               # Scripts de teste e deploy
│   └── test/             # Scripts de teste
├── config/               # Configurações JSON5
├── pyproject.toml        # Configuração do projeto
└── README.md            # Documentação
```

### Arquivos Importantes para Sincronização
- **Código fonte**: `src/t031a5/**/*.py`
- **Scripts de teste**: `scripts/test/*.py`
- **Configurações**: `config/*.json5`
- **Projeto**: `pyproject.toml`

### Arquivos Ignorados
- `.env` (credenciais específicas do ambiente)
- `logs/` (logs específicos do ambiente)
- `venv/` (ambiente virtual)
- `.git/` (metadados do Git)

## ⚡ Comandos Úteis

### Verificação Rápida de Funcionamento

```bash
# Testar imports no Mac
python3 -c "from src.t031a5.unitree.g1_controller import G1Controller; print('✅ OK')"

# Testar na Jetson via SSH
ssh unitree@192.168.123.164 "cd ~/t031a5 && export PYTHONPATH=/home/unitree/t031a5/src && python3 -c 'from t031a5.unitree.g1_controller import G1Controller; print(\"✅ Jetson OK\")'"
```

### Backup Antes de Sincronizar

```bash
# Backup automático (feito pelo script)
./scripts/sync_environments.sh from-jetson
# Cria backup em: backup_sync_YYYYMMDD_HHMMSS/

# Backup manual
cp -r src/ backup_src_$(date +%Y%m%d_%H%M%S)/
```

### Verificação de Diferenças

```bash
# Ver diferenças locais
git status
git diff

# Ver diferenças entre ambientes
rsync -avz --dry-run src/ unitree@192.168.123.164:~/t031a5/src/
```

## 🚨 Resolução de Problemas

### Conflitos de Sincronização

```bash
# 1. Verificar status
./scripts/git_sync_workflow.sh status

# 2. Fazer backup
cp -r src/ backup_before_fix/

# 3. Resolver manualmente ou escolher versão
git checkout --theirs src/arquivo_conflito.py  # Usar versão remota
git checkout --ours src/arquivo_conflito.py    # Usar versão local
```

### Erro de Conectividade

```bash
# Testar conectividade SSH
ssh unitree@192.168.123.164 "echo 'Conectividade OK'"

# Verificar se Jetson está ligada
ping 192.168.123.164
```

### Permissões de Arquivo

```bash
# Corrigir permissões na Jetson
ssh unitree@192.168.123.164 "cd ~/t031a5 && chmod -R 755 scripts/ && chmod +x scripts/*.sh"
```

## 📊 Status Atual da Sincronização

### ✅ Funcionalidades Validadas (Ambos os Ambientes)

- **TTS**: Fala em inglês funcionando
- **LEDs**: Emoções HAPPY/CALM funcionando  
- **Movimento**: Clap (ID 32) funcionando
- **Inicialização**: Sistema inicializa corretamente
- **Sistema Interativo**: Tratamento de EOF/KeyboardInterrupt

### 🔧 Configurações Sincronizadas

- **Interface de rede**: `eth0`
- **IPs**: G1 (192.168.123.161), Jetson (192.168.123.164)
- **Timeout**: 10.0s
- **Volume padrão**: 100
- **Speaker ID**: 1

## 📝 Changelog de Sincronização

### Versão Atual (Pós-Correções)
- ✅ Erro de emoção LEDs corrigido (string → enum)
- ✅ Sistema interativo robusto com tratamento EOF
- ✅ Movimento de braços funcionando (action_map correto)
- ✅ Logging limpo e configurável
- ✅ Scripts de sincronização criados

### Próximas Melhorias
- 🔄 Sincronização automática via Git hooks
- 📊 Dashboard de status dos ambientes
- 🔍 Validação automática pós-sincronização
- 📦 Empacotamento de releases

---

**💡 Dica**: Para uso diário, prefira `sync_environments.sh` para velocidade. Para releases importantes, use `git_sync_workflow.sh` para controle de versão completo.
