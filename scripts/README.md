# 📁 **SCRIPTS AUXILIARES**

Esta pasta contém scripts auxiliares para configuração e manutenção do sistema.

## 🛠️ **Scripts Disponíveis:**

### **🔧 activate_venv.sh**
- **Função**: Ativar ambiente virtual Python
- **Uso**: `./scripts/activate_venv.sh`
- **Quando usar**: Setup manual do ambiente

### **🖥️ setup_terminal.sh**  
- **Função**: Configurar terminal (ZSH, venv, Cursor)
- **Uso**: `./scripts/setup_terminal.sh`
- **Quando usar**: Primeira configuração do ambiente

### **📦 install_g1_sdk.sh**
- **Função**: Instalar Unitree SDK manualmente
- **Uso**: `./scripts/install_g1_sdk.sh`  
- **Quando usar**: Problemas com SDK ou instalação manual

---

## 🎯 **USO RECOMENDADO**

**Em vez de usar estes scripts diretamente, use o script principal:**

```bash
# Script principal (na raiz)
./t031a5 setup    # Substitui activate_venv.sh
./t031a5 deploy   # Faz setup completo incluindo SDK
```

---

## 📋 **Scripts Legacy**

Estes scripts foram mantidos para:
- **Compatibilidade**: Casos específicos de setup
- **Debug**: Troubleshooting de instalação  
- **Customização**: Modificações avançadas

**Para uso normal, prefira sempre o script principal `./t031a5`**
