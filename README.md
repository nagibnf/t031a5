# 🤖 Sistema t031a5 - Robô G1 Tobias

**Sistema conversacional contínuo baseado na arquitetura OM1**

## 🚀 Execução Rápida

```bash
# 1. Verificar sistema
python scripts/verificar_sistema.py

# 2. Executar sistema principal (modo contínuo)
python t031a5_main.py

# 3. Acessar interface (opcional)
http://192.168.123.164:8080
```

## 🎯 Arquitetura

Sistema "vivo" que funciona continuamente:

```
🎤 Inputs → 🔗 Fuser → 🧠 LLM → 🎭 Actions → [LOOP INFINITO]
```

### Componentes Core:

- **Inputs**: DJI Mic 2 + Câmera + Sensores G1
- **Fuser**: NLDB multimodal (weighted fusion)  
- **LLM**: Ollama local + OpenAI fallback
- **Actions**: Fala + Gestos + LEDs + Movimentos

## 📋 Pré-requisitos

✅ G1 Tobias em modo CONTROL (192.168.123.161)  
✅ DJI Mic 2 conectado via Bluetooth  
✅ Anker Soundcore para áudio de saída  
✅ Jetson Orin (192.168.123.164) com deps instaladas  
✅ Interface eth0 configurada  

## 🔧 Configuração

Arquivo único: `config/g1_production.json5`

**Não há step-by-step** - sistema roda continuamente como OM1.

## 🛠️ Desenvolvimento

```bash
# SSH para Jetson
ssh unitree@192.168.123.164

# Ativar ambiente
cd /home/unitree/t031a5
source venv/bin/activate

# Verificar status
python scripts/verificar_sistema.py

# Executar
python t031a5_main.py
```

## 📊 Status

- ✅ Sistema híbrido de áudio 100% funcional
- ✅ G1 SDK integrado com 50 movimentos
- ✅ WebSim interface mobile-first 
- ✅ Documentação completa em docs/project/
- ✅ **PRONTO PARA PRODUÇÃO**

## 🎉 Resultado

Robô conversacional que:
- 🎤 Escuta continuamente via DJI Mic
- 👁️ Analisa ambiente via câmera  
- 🧠 Processa com IA local/cloud
- 🗣️ Responde via Anker Bluetooth
- 🤖 Gesticula com movimentos G1
- 💡 Expressa emoções via LEDs

**Sistema VIVO - sem intervenção manual!**