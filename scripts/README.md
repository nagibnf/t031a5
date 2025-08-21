# 🔧 Scripts - Sistema t031a5

Scripts utilitários essenciais para operação e manutenção do sistema.

## 📁 **Scripts Principais**

### **🔍 Verificação:**
- **`verificar_estado_g1.py`** - Verifica estado do G1 (usado no README)
- **`verificar_sistema.py`** - Verifica componentes do sistema (usado no README)

### **🚀 Operação:**
- **`tobias_startup_complete.sh`** - Script de startup completo do Tobias
- **`activate_venv.sh`** - Ativa ambiente virtual Python

### **🔧 Manutenção:**
- **`auditoria_jetson.sh`** - Auditoria do sistema Jetson

### **📁 Subpastas:**
- **`deploy/`** - Scripts de deploy
  - `deploy_g1.sh` - Deploy para G1
- **`monitor/`** - Scripts de monitoramento  
  - `wait_for_g1.py` - Aguarda conexão G1

## 🚀 **Uso Básico**

### **Verificação do Sistema:**
```bash
# Verificar G1
python scripts/verificar_estado_g1.py

# Verificar sistema completo
python scripts/verificar_sistema.py
```

### **Startup:**
```bash
# Ativar ambiente
source scripts/activate_venv.sh

# Startup completo
./scripts/tobias_startup_complete.sh
```

### **Deploy:**
```bash
# Deploy para G1
./scripts/deploy/deploy_g1.sh
```

---

**Scripts mantidos apenas os essenciais após limpeza do sistema!** ✅
