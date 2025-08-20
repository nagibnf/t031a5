# 🤖 **GUIA DE PRODUÇÃO - t031a5 Sistema G1**

## 🎯 **DEPLOY RÁPIDO**

### **1. Preparação (Uma vez)**
```bash
# Clone e configure
git clone <repo> && cd t031a5

# Deploy completo
./deploy_g1.sh

# Configure variáveis de ambiente
export OPENAI_API_KEY="sua_key_aqui"
```

### **2. Uso Diário**
```bash
# Iniciar sistema
./start_g1.sh

# Escolher modo:
# 1) Produção completa (G1 real)
# 2) Teste seguro (Mock)  
# 3) Apenas WebSim
```

### **3. Monitoramento**
- **WebSim**: http://localhost:8080
- **Logs**: `tail -f logs/g1_production.log`
- **Status**: `python -m t031a5.cli status`

---

## ⚙️ **CONFIGURAÇÕES**

### **🎛️ Perfis Disponíveis:**
- `g1_production.json5` → **Produção otimizada**
- `g1_mock.json5` → **Desenvolvimento/teste**
- `g1_conversation.json5` → **Conversação avançada**
- `g1_real.json5` → **Hardware real básico**

### **🔧 IP do Robô G1:**
Edite `config/g1_production.json5`:
```json5
"g1_controller": {
    "interface": {
        "robot_ip": "192.168.1.120",  // IP do seu G1
        "robot_port": 8080
    }
}
```

### **🔑 API Keys:**
```bash
# OpenAI (recomendado)
export OPENAI_API_KEY="sk-..."

# Anthropic (alternativo)
export ANTHROPIC_API_KEY="sk-ant-..."
```

---

## 🚨 **SEGURANÇA**

### **🛡️ Modo Segurança (Sempre Ativo):**
- Parada de emergência automática
- Limites de workspace definidos
- Detecção de obstáculos
- Monitoramento de força nos braços

### **⚠️ Troubleshooting:**

**G1 não conecta:**
```bash
# Verificar rede
ping 192.168.1.120

# Verificar portas
nmap -p 8080 192.168.1.120

# Logs de depuração
python -m t031a5.cli run --config config/g1_production.json5 --debug
```

**Performance baixa:**
```bash
# Verificar recursos
python -m t031a5.cli status

# Ajustar frequência
# Editar "hertz": 5 em config/g1_production.json5
```

**LLM não responde:**
```bash
# Verificar API key
echo $OPENAI_API_KEY

# Testar conexão
python -m t031a5.cli validate --config config/g1_production.json5
```

---

## 📊 **MONITORAMENTO**

### **🔍 Logs Importantes:**
```bash
# Sistema principal
tail -f logs/g1_production.log

# Métricas
cat logs/g1_production_metrics.json | jq .

# Erros específicos
grep ERROR logs/g1_production.log
```

### **📈 Métricas Key:**
- **Response Time**: < 2.0s
- **Error Rate**: < 5%
- **Loop Frequency**: ~10 Hz
- **Memory Usage**: Monitorado automaticamente

---

## 🎮 **COMANDOS ÚTEIS**

### **CLI Completo:**
```bash
# Status completo
python -m t031a5.cli status

# Validar configuração
python -m t031a5.cli validate --config config/g1_production.json5

# Executar testes
python -m t031a5.cli test

# Versão
python -m t031a5.cli version
```

### **WebSim (Interface Web):**
- **URL**: http://localhost:8080
- **Controles**: Movimento, fala, gestos
- **Monitoramento**: Status em tempo real
- **API**: REST endpoints para integração

---

## 🔄 **WORKFLOW RECOMENDADO**

### **🌅 Início do Dia:**
1. `./start_g1.sh` → Escolher modo produção
2. Verificar WebSim funcionando
3. Testar comando básico (ex: "G1, acenar")

### **🌙 Fim do Dia:**
1. `Ctrl+C` para parar sistema
2. Verificar logs: `tail logs/g1_production.log`
3. Backup se necessário

### **🔧 Manutenção:**
1. Semanal: `./deploy_g1.sh` (atualizar)
2. Mensal: Limpar logs antigos
3. Sempre: Monitorar métricas de performance

---

## 📞 **SUPORTE**

### **🐛 Problemas Comuns:**
- **"G1 não conecta"** → Verificar IP e rede
- **"Comandos não executam"** → Verificar mock_mode: false
- **"LLM muito lento"** → Verificar API key ou usar mock
- **"WebSim erro 500"** → Verificar logs e reiniciar

### **📝 Reportar Bug:**
1. Logs relevantes
2. Configuração usada
3. Passos para reproduzir
4. Comportamento esperado vs atual

**Sistema preparado para produção! 🚀**
