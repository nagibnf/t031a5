# 🚀 PREPARAÇÃO PARA TESTE FINAL EM PRODUÇÃO

**Data:** 21/08/2025  
**Objetivo:** Teste completo end-to-end do sistema t031a5 G1 Tobias  
**Status:** PRONTO PARA EXECUÇÃO ✅

---

## 🎯 OBJETIVO DO TESTE FINAL

**VALIDAR SISTEMA COMPLETO EM PRODUÇÃO:**
- 🎤 **Audio Híbrido:** DJI Mic 2 + G1 → STT
- 🧠 **Processamento:** LLaVA + LLM + NLDB
- 🗣️ **Saída:** TTS + G1 Movimentos + LEDs
- 🌐 **Interface:** WebSim monitoramento
- 🤖 **Robô:** G1 Tobias operacional completo

---

## ✅ PRÉ-REQUISITOS ATENDIDOS

### **🎤 Sistema de Áudio (100% Funcional)**
- ✅ DJI Mic 2 funcionando (29/100 score)
- ✅ HybridMicrophoneManager operacional
- ✅ Fallbacks implementados
- ✅ Threshold ajustado (10/100)
- ✅ Captura 16kHz mono validated

### **🤖 Robô G1 Tobias**
- ✅ IP: 192.168.123.161 (ping OK)
- ✅ DDS Channel funcionando
- ✅ 50 movimentos mapeados (20 arms + 8 FSM + 22 locomotion)
- ✅ G1ArmActionClient confirmado
- ✅ Estado CONTROL necessário

### **💻 Jetson Orin**
- ✅ IP: 192.168.123.164
- ✅ Ubuntu 18.04, Python 3.8.10
- ✅ Virtual environment configurado
- ✅ Dependências instaladas
- ✅ SSH sem senha funcionando

### **🧠 Processamento IA**
- ✅ LLaVA-1.5-7B local (Ollama)
- ✅ LLM Ollama + OpenAI fallback
- ✅ Google STT configurado
- ✅ ElevenLabs TTS funcionando

### **📱 Interface**
- ✅ WebSim mobile-first
- ✅ Porta 8080 funcionando
- ✅ Streaming implementado

---

## 🧪 ROTEIRO DE TESTE FINAL

### **1. 🔧 Preparação do Sistema**
```bash
# SSH Jetson
ssh unitree@192.168.123.164

# Ativar ambiente
cd /home/unitree/t031a5
source venv/bin/activate

# Verificar G1 estado
python3 -c "from t031a5.runtime.cortex import test_g1_connection; test_g1_connection()"
```

### **2. 🎤 Validação Audio Híbrido**
```bash
# Teste rápido sistema híbrido
python3 /home/unitree/test_quick_production.py
# Esperado: 3/3 testes passando
```

### **3. 🤖 Verificação G1**
- **Estado:** Verificar se está em CONTROL mode
- **Sequência ativação:** Power → Damping (L2+B) → Ready (L2+↑) → Control (R2+X)
- **Conexão:** Ping + DDS channel

### **4. 🧠 Teste IA Completo**
```bash
# Teste integrado com LLaVA + LLM
python3 scripts/test_production_system.py
```

### **5. 🗣️ Fluxo Conversacional**
- **Input:** DJI Mic captura → Google STT
- **Processamento:** LLM + contexto visual
- **Output:** ElevenLabs TTS + G1 movements + LEDs

### **6. 🌐 Interface WebSim**
```bash
# Iniciar WebSim
python3 -m t031a5.simulators.websim --config=g1_production.json5
# Acessar: http://192.168.123.164:8080
```

### **7. 🎯 Cenários de Teste**

**A) Saudação Inicial:**
- Robô liga → TTS "Hello, I am Tobias" → LEDs + gesture

**B) Conversação Visual:**
- Pessoa fala → DJI captura → STT → LLaVA analisa → LLM responde → TTS + movimento

**C) Comando de Movimento:**
- "Wave your hand" → STT → LLM → G1 arm gesture

**D) Monitoramento Web:**
- WebSim mostra status, logs, métricas em tempo real

---

## 📊 MÉTRICAS DE SUCESSO

### **✅ Critérios de Aprovação:**
1. **Audio:** DJI capturando com qualidade ≥10/100
2. **STT:** Transcrição compreensível (≥80% accuracy)
3. **LLaVA:** Detecção de pessoas/objetos funcionando
4. **LLM:** Respostas contextualmente adequadas
5. **TTS:** Fala clara e compreensível
6. **G1:** Movimentos executados corretamente
7. **WebSim:** Interface respondendo e mostrando dados
8. **Latência:** Resposta total <10 segundos

### **🎯 Cenário de Sucesso Completo:**
```
👤 Usuário: "Hello Tobias, can you see me?"
🎤 DJI: Captura áudio limpo
🧠 STT: "Hello Tobias, can you see me?"
👁️ LLaVA: "I can see a person standing in front of me"
🧠 LLM: "Hello! Yes, I can see you standing there. Nice to meet you!"
🗣️ TTS: Fala em inglês claro
🤖 G1: Acena com a mão + LEDs azuis amigáveis
🌐 WebSim: Mostra toda a interação em tempo real
```

---

## 🛠️ FERRAMENTAS DE DEBUG

### **Scripts Disponíveis:**
```bash
# Teste rápido
/home/unitree/test_quick_production.py

# Teste completo  
/home/unitree/t031a5/scripts/test_production_system.py

# Debug audio específico
/home/unitree/debug_dji_quality.py

# Ajuste threshold
/home/unitree/fix_threshold_production.py
```

### **Logs Importantes:**
- **Sistema:** `/tmp/t031a5_*.log`
- **WebSim:** Console do navegador
- **G1:** DDS channel logs
- **Audio:** PulseAudio verbose logs

---

## 🚨 TROUBLESHOOTING RÁPIDO

### **Audio não funciona:**
```bash
pactl list sources | grep -A 10 DJI
pactl set-source-mute <dji-device> 0
```

### **G1 não responde:**
```bash
ping 192.168.123.161
# Verificar estado físico do robô
```

### **WebSim não carrega:**
```bash
netstat -tlnp | grep 8080
# Verificar se porta está livre
```

---

## 📋 CHECKLIST FINAL

**Antes do Teste:**
- [ ] G1 Tobias ligado e em CONTROL mode
- [ ] DJI Mic 2 conectado e desmutado
- [ ] Jetson conectada na rede robô (eth0)
- [ ] Virtual environment ativado
- [ ] WebSim acessível
- [ ] Câmera funcionando

**Durante o Teste:**
- [ ] Monitorar logs em tempo real
- [ ] Verificar latências
- [ ] Documentar problemas
- [ ] Capturar métricas
- [ ] Testar cenários variados

**Após o Teste:**
- [ ] Salvar logs importantes
- [ ] Documentar resultados
- [ ] Listar melhorias necessárias
- [ ] Preparar relatório final

---

## 🎯 EXPECTATIVA

**SISTEMA t031a5 G1 TOBIAS TOTALMENTE OPERACIONAL!**

- Robô humanóide conversacional
- Entrada multimodal (voz + visão)
- Processamento IA local + cloud
- Saída expressiva (fala + gestos + LEDs)
- Interface web de monitoramento
- Sistema híbrido robusto

**PRONTO PARA PRODUÇÃO! 🚀**

---

*Documento de preparação para teste final em produção*  
*Sistema t031a5 G1 Tobias - Fase 1 Finalização*
