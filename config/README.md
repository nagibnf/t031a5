# 📋 **CONFIGURAÇÕES DO SISTEMA t031a5**

## 🎯 **PERFIS DISPONÍVEIS**

### **🚀 g1_production.json5** (RECOMENDADO)
```bash
# Para uso em produção com G1 real
python -m t031a5.cli run --config config/g1_production.json5
```
- ✅ **G1 Real**: Hardware conectado (RealSense/LiDAR)
- ✅ **Performance otimizada**: 10 Hz
- ✅ **WebSim ativo**: Monitoramento
- ✅ **Logging completo**: Produção
- ⚠️ **Requer**: G1 na rede + API Keys

### **📷 g1_logitech.json5** (CÂMERA USB)
```bash
# Para testes com câmera Logitech USB
python -m t031a5.cli run --config config/g1_logitech.json5
```
- 📷 **Câmera Logitech**: USB conectada
- 🔧 **G1 Real**: Hardware básico (sem LiDAR)
- ⚡ **Performance**: 8 Hz otimizado para USB
- 🛡️ **Segurança**: Configurações conservadoras
- ⚠️ **Requer**: G1 + câmera USB + API Keys

### **🧪 g1_mock.json5** (DESENVOLVIMENTO)
```bash
# Para testes sem hardware real
python -m t031a5.cli run --config config/g1_mock.json5
```
- 🔧 **Mock Mode**: Simula tudo
- 🔧 **Desenvolvimento**: Debug ativo
- 🔧 **Sem dependências**: Não precisa de G1
- 🔧 **Logs simples**: Desenvolvimento

### **💬 g1_conversation.json5** (CONVERSAÇÃO)
```bash
# Para conversação multimodal avançada
python -m t031a5.cli run --config config/g1_conversation.json5
```
- 🗣️ **ConversationEngine**: Ativo
- 👁️ **Visão + Voz**: Sincronizados
- 🎭 **Gestos + Emoções**: Integrados
- 🤖 **Hardware real**: Se disponível

### **🤖 g1_real.json5** (HARDWARE BÁSICO)
```bash
# Para teste de hardware básico
python -m t031a5.cli run --config config/g1_real.json5
```
- 🔧 **Hardware real**: Sem conversação
- 🔧 **Básico**: Inputs/Actions principais
- 🔧 **Performance**: Padrão
- 🔧 **Debug**: Ativo

---

## 🔧 **PERSONALIZAÇÃO**

### **IP do G1:**
```json5
"g1_controller": {
    "interface": {
        "robot_ip": "192.168.1.120",  // Seu IP aqui
        "robot_port": 8080
    }
}
```

### **API Keys:**
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### **Performance:**
```json5
"hertz": 10,  // Frequência do loop (1-20 Hz)
```

---

## 🎯 **QUAL USAR?**

| Situação | Configuração | Comando |
|----------|--------------|---------|
| **Produção G1** | `g1_production.json5` | `./t031a5 prod` |
| **Câmera Logitech** | `g1_logitech.json5` | `./t031a5 logitech` |
| **Desenvolvimento** | `g1_mock.json5` | `./t031a5 mock` |
| **Demo/Conversação** | `g1_conversation.json5` | `./t031a5 talk` |
| **Teste hardware** | `g1_real.json5` | `./t031a5 start` → Opção 4 |
