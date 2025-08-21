# 🏗️ **DIAGRAMA DE ARQUITETURA - SISTEMA t031a5**

*Sistema de IA Multimodal para Robô Humanóide G1 Tobias*

**🫧 Desenvolvido por Bolha**

---

## **📊 ARQUITETURA VISUAL**

```mermaid
graph TB
    %% INPUTS - Sensores e Captura
    subgraph INPUTS["🎤 INPUTS - Sensores"]
        Camera["📷 RealSense D455<br/>+ Motor 2DOF<br/>(Cabeça)"]
        TempCam["📹 Logitech C920<br/>(Temporária)"]
        Mic["🎙️ DJI Mic 2<br/>Bluetooth"]
        GPS["🗺️ GPS Arduino<br/>Localização"]
        Sensors["🌡️ Sensores Arduino<br/>Temp/Humidade"]
        G1State["🤖 G1 State Monitor<br/>DDS eth0"]
    end

    %% PROCESSAMENTO IA
    subgraph AI["🧠 PROCESSAMENTO IA"]
        LLaVA["👁️ LLaVA-1.5-7B<br/>Visão Local"]
        ASR["🗣️ Google ASR<br/>+ Whisper STT"]
        NLDB["🔗 NLDB<br/>Fusão Multimodal"]
        LLM["🤖 Ollama Llama-3.1-8B<br/>+ OpenAI Fallback"]
        ContextEngine["🎯 Context Engine<br/>Escuta Conversacional"]
    end

    %% OUTPUTS - Ações
    subgraph OUTPUTS["🎭 OUTPUTS - Ações"]
        G1TTS["📢 G1 TTS<br/>Alertas Sistema<br/>(Inglês)"]
        BluetoothAudio["🔊 Bluetooth Anker<br/>Conversas + Música<br/>+ Efeitos"]
        LEDs["💡 LEDs Emocionais<br/>10 Estados<br/>Pulsação Sincronizada"]
        Arms["🤚 G1 Arms<br/>16 Movimentos<br/>G1ArmActionClient"]
        Locomotion["🚶 G1 Locomotion<br/>Giros + Posturas"]
    end

    %% CONTROLE E SEGURANÇA
    subgraph CONTROL["🛡️ CONTROLE & SEGURANÇA"]
        WebSim["📱 WebSim Mobile<br/>Streaming Câmera<br/>Interface Operador"]
        Safety["⚠️ Sistema Segurança<br/>Botão STOP<br/>Regras Proteção"]
        Setup["🔧 Setup Automatizado<br/>Configuração Robot<br/>Personalidade"]
    end

    %% AMBIENTE DE EXECUÇÃO
    subgraph ENVIRONMENT["💾 AMBIENTE EXECUÇÃO"]
        Jetson["🖥️ Jetson Orin<br/>Ubuntu + ROS2<br/>192.168.123.164"]
        G1Robot["🤖 G1 Tobias<br/>Unitree SDK2<br/>192.168.123.161"]
        MacDev["💻 Mac Development<br/>Offline Sync<br/>GitHub"]
    end

    %% FLUXO DE DADOS PRINCIPAL
    Camera --> LLaVA
    TempCam --> LLaVA
    Mic --> ASR
    GPS --> ContextEngine
    Sensors --> ContextEngine
    G1State --> NLDB

    LLaVA --> NLDB
    ASR --> NLDB
    NLDB --> LLM
    LLM --> ContextEngine

    %% SAÍDAS COORDENADAS
    ContextEngine --> G1TTS
    ContextEngine --> BluetoothAudio
    ContextEngine --> LEDs
    ContextEngine --> Arms
    ContextEngine --> Locomotion

    %% CONTROLE
    WebSim --> Safety
    Safety --> ContextEngine
    Setup --> ContextEngine

    %% AMBIENTE
    Jetson --> AI
    G1Robot --> OUTPUTS
    MacDev --> Jetson

    %% EFEITOS CONTEXTUAIS
    ContextEngine -.-> EffectsMatrix["🎵 Matriz Efeitos<br/>Carl Whisper<br/>Terminator<br/>Surpresa, etc."]
    EffectsMatrix --> BluetoothAudio

    %% VERIFICAÇÃO BLUETOOTH
    BluetoothAudio -.-> BluetoothCheck["🔄 Verificação Auto<br/>Reconexão Anker"]

    %% MOVIMENTOS DETALHADOS
    Arms -.-> MovementDetails["📋 16 Movimentos:<br/>release_arm(99)<br/>clap(17), shake_hand(27)<br/>high_five(18), hug(19)<br/>heart(20), reject(22)<br/>etc."]

    %% SEGURANÇA DETALHADA
    Safety -.-> SafetyRules["⚠️ Regras:<br/>STOP < 2s<br/>Proximidade<br/>Timeout 30s<br/>Logs Segurança"]

    style INPUTS fill:#e1f5fe
    style AI fill:#f3e5f5
    style OUTPUTS fill:#e8f5e8
    style CONTROL fill:#fff3e0
    style ENVIRONMENT fill:#fce4ec
```

---

## **🔍 EXPLICAÇÃO DOS COMPONENTES**

### **🎤 INPUTS - Camada de Sensores:**
- **RealSense D455** - Câmera principal RGB-D com motor 2DOF para tracking
- **Logitech C920** - Câmera temporária até RealSense chegar
- **DJI Mic 2** - Captura de áudio Bluetooth para conversas
- **GPS Arduino** - Localização precisa para mapeamento
- **Sensores Arduino** - Temperatura, humidade, qualidade ar
- **G1 State Monitor** - Monitoramento contínuo estado robô via DDS

### **🧠 PROCESSAMENTO IA - Pipeline Inteligente:**
- **LLaVA-1.5-7B** - Visão computacional local para análise de imagens
- **Google ASR + Whisper** - Speech-to-Text para processamento de voz
- **NLDB** - Natural Language Data Bus para fusão multimodal
- **Ollama + OpenAI** - LLM local com fallback cloud para decisões
- **Context Engine** - Motor de contexto conversacional contínuo

### **🎭 OUTPUTS - Ações Coordenadas:**
- **G1 TTS** - Apenas alertas sistema em inglês
- **Bluetooth Anker** - Áudio principal para conversas e efeitos
- **LEDs Emocionais** - 10 estados com pulsação sincronizada
- **G1 Arms** - 16 movimentos via G1ArmActionClient
- **G1 Locomotion** - Locomoção com giros usando os pés

### **🛡️ CONTROLE & SEGURANÇA:**
- **WebSim Mobile** - Interface mobile-first com streaming câmera
- **Sistema Segurança** - Botão STOP, regras proteção, monitoramento
- **Setup Automatizado** - Configuração personalidade e parâmetros

### **💾 AMBIENTE EXECUÇÃO:**
- **Jetson Orin** - Processamento principal Ubuntu + ROS2
- **G1 Tobias** - Robô físico com Unitree SDK2
- **Mac Development** - Desenvolvimento offline sincronizado

---

## **🔄 FLUXO DE DADOS**

### **📥 ENTRADA (Input → Processing):**
1. **Sensores** capturam dados multimodais
2. **IA especializada** processa cada modalidade
3. **NLDB** funde todas as informações
4. **LLM** gera resposta contextual

### **📤 SAÍDA (Processing → Output):**
1. **Context Engine** coordena resposta
2. **Ações simultâneas** executadas:
   - Fala via Bluetooth
   - LEDs pulsantes sincronizados
   - Movimentos corporais
   - Efeitos sonoros contextuais

### **🎵 EFEITOS CONTEXTUAIS:**
- **Mulher bonita** → Carl Whisper (10s)
- **Despedidas** → "Hasta la vista baby"
- **Surpresa** → Efeito sonoro
- **Aprovação** → Som complimento
- **E muitos outros...**

---

## **⚡ CARACTERÍSTICAS TÉCNICAS**

### **🔗 Conectividade:**
- **Rede:** eth0 (OBRIGATÓRIO)
- **G1 Tobias:** 192.168.123.161
- **Jetson:** 192.168.123.164
- **WebSim:** Porta 8080 (Mobile-first)

### **⏱️ Performance:**
- **Análise imagem:** 3-5s
- **Resposta completa:** 5-10s
- **Movimento G1:** 2-4s
- **Efeitos audio:** < 0.5s
- **STOP emergência:** < 2s

### **🛡️ Segurança:**
- **Botão STOP** prioritário no WebSim
- **Timeout** máximo 30s para operações
- **Monitoramento** contínuo estado G1
- **Logs** completos de segurança
- **Reconexão** automática Bluetooth

---

## **🎯 DIFERENCIAIS DA ARQUITETURA**

1. **🔄 Processamento Contínuo** - Escuta e analisa ambiente constantemente
2. **🎭 Expressão Coordenada** - Fala + LEDs + movimentos sincronizados  
3. **🎵 Efeitos Contextuais** - Áudios apropriados por situação
4. **📱 Controle Mobile** - Interface operador em tempo real
5. **🛡️ Segurança Integrada** - STOP e proteções em todos os níveis
6. **🔧 Setup Automatizado** - Configuração completa personalidade
7. **💾 Ambiente Híbrido** - Local + Cloud com fallbacks

---

*Diagrama criado em: 20 de Agosto de 2025*  
*Sistema: t031a5 - Robô G1 Tobias*  
*Status: Preparação Fase 1 de Produção*
