# 🤖 Sistema t031a5 - Robô G1 Tobias

**Sistema conversacional contínuo baseado na arquitetura OM1 - ULTRA-OTIMIZADO**

---

## 🚀 **EXECUÇÃO RÁPIDA**

```bash
# 1. Verificar sistema G1 
python scripts/verificar_estado_g1.py

# 2. Executar sistema principal (modo contínuo)
python3 t031a5_main.py

# 3. Acessar interface debug (opcional)
http://localhost:8080
```

---

## 🎯 **ARQUITETURA**

### **Sistema "VIVO" - Loop Contínuo:**
```
🎤 Inputs → 🔗 Fuser → 🧠 LLM → 🎭 Actions → [LOOP INFINITO]
```

### **🎤 INPUTS (Auto-contidos):**
- **G1Voice**: DJI Mic 2 + STT integrado
- **G1Vision**: Intel RealSense D435i + AI integrado  
- **G1State**: Estado robô via DDS

### **🔗 FUSER:**
- **MultimodalFuser**: Fusão weighted de modalidades
- **Weights**: Audio(1.0), Vision(0.9), State(0.4)

### **🧠 LLM (Hierarquia):**
- **🥇 Principal**: GPT-4o-mini (OpenAI) - API key do .env
- **🥈 Fallback**: Llama3.1:8b (Ollama local)
- **🛡️ Backup**: MockProvider (desenvolvimento)

### **🎭 ACTIONS (Auto-contidos):**
- **G1Speech**: TTS + Anker Bluetooth integrado
- **G1Arms**: 20 gestos mapeados + library
- **G1Emotion**: LEDs RGB pulsantes  
- **G1Movement**: Locomoção + FSM states
- **G1Audio**: Efeitos sonoros via PyAudio

---

## 📁 **ESTRUTURA CONSOLIDADA**

```
t031a5/
├── 🚀 t031a5_main.py              # Sistema principal
├── 🔧 run_t031a5.py               # Wrapper execução
├── 📖 README.md                   # Esta documentação
│
├── ⚙️ config/
│   └── g1_production.json5        # Configuração única
│
├── 🌐 websim/                     # Interface debug
│   ├── static/ (CSS + JS)
│   └── templates/ (HTML)
│
├── 🧠 src/t031a5/                 # Código core
│   ├── inputs/plugins/            # 3 inputs auto-contidos
│   ├── actions/                   # 5 actions auto-contidos
│   ├── fuser/                     # Fusão multimodal
│   ├── llm/providers/             # 3 LLM providers
│   ├── runtime/                   # Core loop (cortex)
│   └── connectors/                # Auxiliares reais
│
├── 🔧 scripts/                    # Utilitários
└── 📚 docs/                       # Documentação técnica
```

---

## 📋 **PRÉ-REQUISITOS**

### **🤖 Hardware G1:**
- ✅ G1 Tobias ligado e em modo CONTROL (192.168.123.161)
- ✅ Interface eth0 configurada na Jetson  
- ✅ Comando: R1+X (modo CONTROL após L2+↑)

### **🎤 Áudio:**
- ✅ DJI Mic 2 conectado via Bluetooth
- ✅ Anker Soundcore para saída de áudio
- ✅ Configuração automática no boot

### **🖥️ Jetson Orin:**
- ✅ IP: 192.168.123.164  
- ✅ Python 3.8+ com dependências
- ✅ Arquivo .env com chaves API configurado

### **👁️ Visão:**
- ✅ Intel RealSense D435i conectada
- ✅ Resolução 848x480 @ 15fps
- ✅ Depth sensing habilitado

---

## ⚙️ **CONFIGURAÇÃO**

### **Arquivo Único**: `config/g1_production.json5`
- **Sistema**: 10Hz loop contínuo
- **LLM**: OpenAI primary + Ollama fallback
- **Inputs**: DJI + D435i + G1State  
- **Actions**: Speech + Arms + Emotion + Movement + Audio
- **WebSim**: localhost:8080 (debug)

### **Ambiente**: `.env`
```bash
OPENAI_API_KEY=sk-...           # Chave OpenAI GPT-4
# Outras chaves já configuradas
```

### **Credenciais**: `credentials/`
```bash
# Google Speech-to-Text para G1VoiceInput
credentials/google_asr.json     # Arquivo JSON do Google Cloud
```

---

## 🛠️ **DESENVOLVIMENTO**

### **Local (Mac):**
```bash
# Verificar core
python3 scripts/verificar_sistema.py

# Testar sistema  
python3 t031a5_main.py
```

### **Deploy Jetson:**
```bash
# SSH para Jetson
ssh unitree@192.168.123.164

# Ambiente
cd /home/unitree/t031a5
source venv/bin/activate

# Executar
python3 t031a5_main.py
```

---

## 📊 **STATUS ATUAL**

### **✅ 100% FUNCIONAL:**
- **Core sistema**: Inputs → Fuser → LLM → Actions
- **Audio híbrido**: DJI Mic 2 + Anker funcionando  
- **Visão avançada**: D435i RGB-D integrada
- **LLM inteligente**: GPT-4 + fallback local
- **Movimentos**: 20 gestos G1 mapeados
- **Interface**: WebSim mobile-first
- **Arquitetura**: Ultra-otimizada (15 auxiliares órfãos removidos)

### **🎯 OTIMIZAÇÕES REALIZADAS:**
- **-15 arquivos órfãos** removidos (speech/, vision/, audio/)
- **-5 pastas soltas** consolidadas (websim/)
- **~4000 linhas** código não usado eliminadas
- **Zero redundância** restante
- **Componentes 100% auto-contidos**

---

## 🎉 **RESULTADO FINAL**

### **🤖 Robô Conversacional que:**
- 🎤 **Escuta continuamente** via DJI Mic 2
- 👁️ **Analiza ambiente** via D435i RGB-D + AI
- 🧠 **Processa inteligente** com GPT-4 + Ollama
- 🗣️ **Responde natural** via Anker Bluetooth  
- 🤲 **Gesticula expressivo** com 20 movimentos G1
- 💡 **Expressa emoções** via LEDs RGB pulsantes
- 📊 **Monitora status** via WebSim tempo real

### **⚡ OPERAÇÃO:**
```
SISTEMA VIVO - Loop infinito autônomo
Sem intervenção manual - Como OM1 original
Conversação fluida e natural 24/7
```

---

## 🏆 **TECNOLOGIAS**

**Core**: Python 3.8+ | AsyncIO | Pydantic | FastAPI  
**IA**: OpenAI GPT-4o-mini | Ollama Llama3.1 | Intel RealSense  
**Audio**: DJI Mic 2 | Anker Soundcore | PyAudio  
**Robótica**: Unitree G1 SDK | DDS | Ethernet  
**Interface**: WebSim HTML5 | Mobile-first | WebSocket  

---

**🚀 Sistema t031a5 - Conversação Robótica do Futuro! 🤖✨**