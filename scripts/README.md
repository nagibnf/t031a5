# 📁 Scripts - Sistema t031a5

Esta pasta contém todos os scripts utilitários do sistema t031a5, organizados por categoria.

## 📂 Estrutura

### 🧪 `test/` - Scripts de Teste
Scripts para testar funcionalidades específicas do sistema.

- **`test_t031a5_integrated.py`** - Teste integrado completo do sistema
- **`test_g1_confirmed_features.py`** - Teste das funcionalidades confirmadas
- **`test_g1_integrated.py`** - Teste integrado do G1
- **`test_g1_locomotion_rotation.py`** - Teste de locomoção e rotação
- **`test_g1_state_verification_example.py`** - Verificação de estado do G1
- **`test_camera.py`** - Teste da câmera USB

### 📊 `monitor/` - Scripts de Monitoramento
Scripts para monitorar o estado do sistema e hardware.

- **`wait_for_g1.py`** - Monitoramento de conexão com G1

### 🚀 `deploy/` - Scripts de Deploy
Scripts para deploy e configuração do sistema.

- **`deploy_g1.sh`** - Script de deploy para G1

### 🔧 `create_config.py` - Criador de Configurações
Script para criar novas configurações baseadas na configuração base.

## 🎯 Como Usar

### Executar Testes
```bash
# Teste integrado
python scripts/test/test_t031a5_integrated.py

# Teste funcionalidades confirmadas
python scripts/test/test_g1_confirmed_features.py

# Teste câmera
python scripts/test/test_camera.py
```

### Monitorar G1
```bash
# Aguardar G1 ligar
python scripts/monitor/wait_for_g1.py
```

### Deploy
```bash
# Deploy do sistema
./scripts/deploy/deploy_g1.sh
```

### Criar Configurações
```bash
# Criar configuração de teste
python scripts/create_config.py g1_meu_teste --test

# Criar configuração mock
python scripts/create_config.py g1_meu_mock --mock

# Criar configuração de produção
python scripts/create_config.py g1_meu_prod --production
```

## 📋 Requisitos

- Python 3.9+
- Ambiente virtual ativado
- SDK Unitree instalado
- Configurações válidas em `config/`

---

**🎯 Scripts organizados e prontos para uso!**
