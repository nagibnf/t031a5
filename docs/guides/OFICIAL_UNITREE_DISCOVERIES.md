# Descobertas Críticas - Manual Oficial Unitree G1

## 📚 Fonte: "1_Unitree G1 Rapid Intro and Dev.pdf" (39 páginas)

---

## 🚨 MUDANÇAS CRÍTICAS REQUERIDAS

### **1. 🔧 MUDANÇA DE SERVIÇO (FIRMWARE >=8.2.0.0)**
```cpp
// ANTES (Firmware < 8.2.0.0):
LOCO_SERVICE_NAME = "loco"

// AGORA (Firmware >= 8.2.0.0):
LOCO_SERVICE_NAME = "sport"
```

**⚠️ AÇÃO NECESSÁRIA:** Verificar versão firmware e atualizar código!

### **2. 🎵 SISTEMA DE ÁUDIO NATIVO CONFIRMADO**
```cpp
// G1 suporta NATIVAMENTE:
- .wav files via PlayStream()
- .mp3 files via PlayStream()
- Microfone via thread_mic()
- ASR via AUDIO_SUBSCRIBE_TOPIC
```

**✅ TTS INGLÊS OFICIALMENTE CONFIRMADO** - Funciona nativamente!

---

## 📊 ESPECIFICAÇÕES TÉCNICAS OFICIAIS

### **🤖 GRAUS DE LIBERDADE:**
- **Total:** 23-43 DOF
- **Por Perna:** 7 DOF
- **Por Braço:** 5 DOF (Dex3-1) + 2 punho = 7 DOF
- **Por Mão:** 1 DOF (Dex3-1)
- **Cintura:** 1-2 DOF (opcional)

### **🌐 REDE E CONECTIVIDADE:**
```
G1 (OCCU):     192.168.123.161  # Operation Control Computing Unit
Jetson (DCU):  192.168.123.164  # Development Computing Unit
PC/Dev:        192.168.123.99   # Recomendado para desenvolvimento
```

### **👁️ SENSORES CONFIRMADOS:**
- **LiDAR:** Livox MID-360 (360° SLAM)
- **Câmera Depth:** Intel D435i + IMU
- **Fusão:** MID360 + D435i com FOV combinado

---

## 🎛️ CONTROLE E MODOS

### **🎮 SEQUÊNCIA DE INICIALIZAÇÃO CORRETA:**
```
1. L2 + B  →  Damping Mode
2. L2 + A  →  Main Operation Control
3. Para retornar: L2 + A → Squat, depois L2 + B → Damping, depois L2 + A → Main Control
```

### **🔍 MODO DEBUG (BAIXO NÍVEL):**
```
1. Suspender robô
2. L1 + A (antigo) / L2 + B (novo) → Damping
3. L2 + R2 → Debug Mode
4. L2 + A → Verificar

⚠️ CRÍTICO: Modo Debug DESABILITA motion control service!
⚠️ Requer reboot para reativar motion control!
```

### **🗣️ SISTEMA DE VOZ NATIVO:**
```
Modo Wake-up: "Hello Robot" + conversa natural
Modo Push-to-Talk: L2 + Select (melhor para ambientes ruidosos)
Timeout: 15 segundos sem som
```

---

## 🔒 SEGURANÇA E LIMITAÇÕES

### **❌ PATHS PROTEGIDOS - NUNCA MODIFICAR:**
```
/unitree/                  # Sistema principal
/lib/                      # Bibliotecas (não editar existentes)
~/cyclonedx/              # DDS middleware
~/cyclonedx_ws/           # Workspace DDS
~/nomachine.sh            # Não deletar!
```

### **✅ PATHS SEGUROS PARA EDIÇÃO:**
```
~/unitree_SDK2/           # Pode atualizar
Containers/Docker         # Seguro usar
```

### **🚨 COMANDOS PROIBIDOS:**
```bash
sudo apt upgrade          # NUNCA USAR - QUEBRA SISTEMA!
```

---

## 🔧 DESENVOLVIMENTO E DEPLOYMENT

### **🐳 CONTAINERS/DOCKER:**
- **✅ Seguro usar** - Não afeta DDS/Unitree components
- **✅ Recomendado** para LLM services offline
- **✅ Usar modelos quantizados** para performance

### **🧠 LLM E IA:**
- **LLM Interno:** Requer Wi-Fi, usa cloud GPT service
- **LLM Custom:** Usar ASR service + próprio LLM
- **Simulação RL:** Usar low-level scripts (high-level requer PC1)
- **Sim2Real:** Cuidado extremo - verificar segurança

### **🎯 DESENVOLVIMENTO SIMULTÂNEO:**
- **✅ Possível:** Desenvolver braços + manter locomoção
- **✅ High Level API:** Funciona mas sem assistência de equilíbrio
- **⚠️ Cuidado:** Evitar perturbações externas durante demo

---

## 📸 CAMERA INTEL D435i

### **🔌 CONEXÕES POSSÍVEIS:**

**G1 EDU:**
- Conectada ao PC1 (inacessível via SSH)
- Solução: Desmontar cabeça (4 parafusos) + conectar ao DCU/PC2

**G1 EDU+:**
- Fio direto do pescoço do G1
- Conectar diretamente ao DCU/PC2

---

## 🎵 SISTEMA DE ÁUDIO AVANÇADO

### **📻 FUNCIONALIDADES NATIVAS:**
```cpp
// TTS (Text-to-Speech)
TTS_Client::PlayText("Hello World");  // Inglês nativo

// Audio Files
AudioClient::PlayStream("file.wav");   // WAV nativo  
AudioClient::PlayStream("file.mp3");   // MP3 nativo

// ASR (Automatic Speech Recognition)
thread_mic();                          // Gravação
AUDIO_SUBSCRIBE_TOPIC                  // Reconhecimento

// Controles
GetVolume() / SetVolume()              // Volume
PlayState / Stop                       // Controle playback
```

---

## 🔄 FIRMWARE E VERSIONING

### **📋 VERSÕES CRÍTICAS:**
```
Motion Control >= 8.2.0.0  →  Service = "sport"
Motion Control < 8.2.0.0   →  Service = "loco"

Firmware >= 1.3.3          →  Suporte GPT
Firmware >= 1.3.0          →  Voice Assistant
```

### **🔍 VERIFICAÇÃO DE VERSÃO:**
```bash
# TODO: Implementar verificação automática
# Verificar via DDS status ou firmware query
```

---

## 📝 EXEMPLOS OFICIAIS DISPONÍVEIS

### **🎯 LOCOMOTION:**
```bash
./g1_loco_client --network_interface eth0 --set_velocity "0.5 0 0 1"

# Parâmetros disponíveis:
set_swing_height    # Altura levantamento perna (m)
set_stand_height    # Altura em pé (m)  
set_velocity        # Velocidade [vx vy omega duration]
high_stand          # Postura alta
low_stand           # Postura baixa
move               # Mover com velocidade [vx vy omega]
```

### **🤚 CONTROLE DE BRAÇOS:**
```bash
./g1_arm7_sdk_dds_example ethernet_interface  # 7 DOF
./g1_arm5_sdk_dds_example ethernet_interface  # 5 DOF
```

### **🔊 SISTEMA VUI (Voice User Interface):**
```bash
./g1_vui_example ethernet_interface
# Funções: TTS, Volume, Play Stream, Play Stop, LED Control, ASR
```

---

## 🎯 AÇÕES REQUERIDAS PARA NOSSO SISTEMA

### **1. 🔧 VERIFICAÇÕES IMEDIATAS:**
- [ ] Verificar versão firmware atual
- [ ] Ajustar nome serviço "loco"→"sport" se necessário  
- [ ] Confirmar conectividade IPs (161/164)

### **2. 🎵 MELHORIAS DE ÁUDIO:**
- [ ] Implementar PlayStream nativo para áudio
- [ ] Configurar ASR via AUDIO_SUBSCRIBE_TOPIC
- [ ] Otimizar TTS inglês nativo

### **3. 📸 SISTEMA DE VISÃO:**
- [ ] Verificar localização D435i (PC1 vs fio pescoço)
- [ ] Configurar acesso se necessário

### **4. 🔒 SEGURANÇA:**
- [ ] Auditar paths acessados pelo sistema
- [ ] Confirmar uso seguro de containers
- [ ] Documentar comandos proibidos

### **5. 📚 DOCUMENTAÇÃO:**
- [ ] Atualizar guides com descobertas
- [ ] Revisar configurações de rede
- [ ] Corrigir procedimentos de inicialização

---

## 💡 OPORTUNIDADES DE MELHORIA

### **🚀 PERFORMANCE:**
- Usar ASR nativo em vez de external services
- Otimizar áudio via PlayStream direto
- Container LLM quantizado para offline

### **🎭 FUNCIONALIDADES:**
- Voice wake-up integration ("Hello Robot")
- Multi-modal: LiDAR + D435i fusion
- Sim2real training pipeline

### **🔧 DESENVOLVIMENTO:**
- Verificação automática de firmware
- Health check de services (loco vs sport)
- Debugging tools with safety checks

---

**📅 Atualizado:** 21 Agosto 2025  
**📚 Fonte:** Manual Oficial Unitree G1 (39 páginas)  
**🎯 Status:** Descobertas integradas ao sistema t031a5
