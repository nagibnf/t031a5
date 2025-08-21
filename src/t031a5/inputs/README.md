# 🎤 Sistema de Inputs - t031a5

Sistema de inputs multimodais para captura contínua de dados do robô G1 Tobias.

## 📁 **Estrutura Atual**

```
src/t031a5/inputs/
├── __init__.py              # Exportações principais
├── base.py                  # Classe BaseInput
└── plugins/                 # 3 inputs essenciais
    ├── __init__.py
    ├── g1_voice.py          # 🗣️ DJI Mic 2 + STT
    ├── g1_vision_d435i.py   # 👁️ Intel RealSense D435i + AI
    └── g1_state.py          # 🤖 Estado G1 via DDS
```

## 🎯 **Inputs Funcionais**

### **🗣️ G1VoiceInput** (`g1_voice.py`)
**Entrada de áudio via DJI Mic 2**
- **Hardware**: DJI Mic 2 Bluetooth
- **STT**: Google ASR (configurado via credentials/)
- **Idioma**: Português brasileiro (pt-BR)
- **Modo**: Captura contínua conversacional

### **👁️ G1VisionInput** (`g1_vision_d435i.py`)  
**Visão RGB-D avançada**
- **Hardware**: Intel RealSense D435i
- **Resolução**: 848x480 @ 15fps
- **Recursos**: RGB + Depth + AI analysis
- **Detecção**: Faces, objetos, contexto visual

### **🤖 G1StateInput** (`g1_state.py`)
**Monitoramento estado robô**
- **Protocolo**: DDS via Unitree SDK
- **Dados**: Posição, orientação, bateria, sensores
- **Frequência**: Tempo real via eth0

## ⚙️ **Configuração**

### **Arquivo**: `config/g1_production.json5`
```json5
"agent_inputs": [
  {
    "type": "G1Voice",
    "config": {
      "device": "dji_mic_2",
      "language": "pt-BR",
      "asr_provider": "google"
    }
  },
  {
    "type": "G1Vision", 
    "config": {
      "camera_device": "realsense",
      "resolution": [848, 480],
      "fps": 15,
      "enable_depth": true
    }
  },
  {
    "type": "G1State",
    "config": {
      "interface": "eth0",
      "robot_ip": "192.168.123.161"
    }
  }
]
```

## 🔗 **Fusão de Dados**

### **MultimodalFuser**
```json5
"modality_weights": {
  "audio": 1.0,    // Voz prioritária
  "visual": 0.9,   // Visão importante  
  "state": 0.4     // Estado como apoio
}
```

### **Fluxo de Dados**
```
🎤 G1Voice → Transcrição texto
👁️ G1Vision → Contexto visual + depth
🤖 G1State → Status robô
       ↓
🔗 MultimodalFuser → Contexto unificado
       ↓  
🧠 LLM → Resposta inteligente
```

## 🎯 **Características**

### **✅ Auto-contidos**
- Cada input integra suas próprias dependências
- STT, AI, DDS embutidos nos plugins
- Sem managers auxiliares órfãos

### **⚡ Tempo Real**
- Captura contínua simultânea
- Loop 10Hz coordenado
- Baixa latência para conversação

### **🔧 Configuráveis**
- JSON5 único de configuração
- Parâmetros ajustáveis por input
- Enable/disable individual

---

**Sistema de inputs ultra-otimizado para conversação robótica fluida!** 🚀
