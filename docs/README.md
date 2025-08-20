# 📚 **DOCUMENTAÇÃO t031a5**

## 🎯 **DOCUMENTOS PRINCIPAIS**

### **🚀 [PRODUCTION_GUIDE.md](../PRODUCTION_GUIDE.md)**
- Guia completo para deploy em produção
- Configuração do G1 real
- Troubleshooting e monitoramento

### **📋 [config/README.md](../config/README.md)**
- Explicação de todas as configurações
- Perfis disponíveis (produção, mock, conversação)
- Personalização de parâmetros

### **🧪 [tests/README.md](../tests/README.md)**
- Suite completa de testes
- Como executar testes específicos
- Validação do sistema

---

## 🔄 **WORKFLOWS COMUNS**

### **🌅 Setup Inicial:**
1. `./deploy_g1.sh` - Deploy completo
2. `./quick_start.sh` - Início rápido
3. Acessar WebSim: http://localhost:8080

### **🎮 Uso Diário:**
1. `./start_g1.sh` - Iniciar sistema
2. Escolher modo (produção/mock/websim)
3. Monitorar via WebSim

### **🔧 Manutenção:**
1. `python -m t031a5.cli status` - Status
2. `tail -f logs/g1_production.log` - Logs
3. `python -m t031a5.cli validate` - Validar

---

## 📁 **ESTRUTURA DE ARQUIVOS**

```
docs/
├── README.md              # Este arquivo
├── archive/               # Docs antigos
│   ├── installation.md
│   ├── g1_integration_guide.md
│   └── PROJECT_SUMMARY.md
```

---

## 🔗 **LINKS ÚTEIS**

- **Unitree G1 SDK**: https://github.com/unitreerobotics/unitree_sdk2
- **OpenAI API**: https://platform.openai.com/docs
- **Anthropic API**: https://docs.anthropic.com/

---

## 🆘 **SUPORTE**

### **Problemas Comuns:**
1. **G1 não conecta** → Verificar IP em config/
2. **LLM não responde** → Verificar API keys
3. **Performance baixa** → Ajustar "hertz" em config
4. **WebSim erro** → Verificar logs/

### **Debug:**
```bash
# Logs detalhados
python -m t031a5.cli run --config config/g1_production.json5 --debug

# Status completo
python -m t031a5.cli status

# Validar config
python -m t031a5.cli validate --config config/g1_production.json5
```
