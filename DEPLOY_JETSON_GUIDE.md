# 🚀 GUIA COMPLETO DE DEPLOY - Sistema t031a5 na Jetson

## 📊 **STATUS PRÉ-DEPLOY**

### ✅ **COMPONENTES VALIDADOS (Mac)**
- 🧠 **LLM Ollama**: Llama-3.1-8B funcionando (2-3s respostas)
- 👁️ **LLaVA Local**: Análise de imagem consistente (3-5s)
- 🎤 **STT**: Google ASR + OpenAI Whisper fallback
- 🔊 **TTS**: ElevenLabs português natural
- 📷 **Câmera**: RGB 640x480 estável
- 🎵 **Áudio**: Sistema nativo Mac funcional
- 🤖 **G1 Controller**: Mock mode operacional
- 🧠 **Cortex Runtime**: 100% inicialização

### ⚠️ **COMPONENTE OPCIONAL**
- 🌐 **WebSim**: Interface web (bug nos handlers, não crítico)

---

## 🎯 **HARDWARE ALVO - Jetson Orin NX 16GB**

```
🖥️ Processador: 8-core ARM Cortex-A78AE
🧠 GPU: 1024-core Ampere + 32 Tensor cores  
💾 RAM: 16GB LPDDR5
💿 SSD: 256GB (expansível para 1TB)
🎤 Áudio: DJI Mic 2 Bluetooth
🔊 Speaker: Anker Soundcore 300 Bluetooth
```

---

## 📦 **ETAPAS DE DEPLOY**

### **1. 📥 PREPARAÇÃO DA JETSON**

```bash
# Conectar SSH na Jetson
ssh usuario@ip_jetson

# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências básicas
sudo apt install -y python3 python3-pip python3-venv git curl wget
sudo apt install -y build-essential cmake pkg-config
sudo apt install -y libjpeg-dev libpng-dev libtiff-dev
sudo apt install -y libavcodec-dev libavformat-dev libswscale-dev
sudo apt install -y libgtk-3-dev libcanberra-gtk-module
sudo apt install -y libxvidcore-dev libx264-dev
sudo apt install -y python3-dev python3-numpy
sudo apt install -y libblas-dev liblapack-dev libatlas-base-dev gfortran
sudo apt install -y ffmpeg sox mpv pulseaudio alsa-utils
```

### **2. 🔄 TRANSFERÊNCIA DO PROJETO**

```bash
# Opção 1: Git Clone (recomendado)
git clone <repo_url> t031a5
cd t031a5

# Opção 2: SCP do Mac
# No Mac: scp -r /Users/nagib/t031a5 usuario@ip_jetson:~/
```

### **3. 🐍 AMBIENTE PYTHON**

```bash
cd t031a5

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências core
pip install --upgrade pip setuptools wheel
pip install opencv-python
pip install numpy
pip install requests
pip install aiohttp
pip install asyncio
pip install python-dotenv
pip install pathlib
pip install typing
pip install json5

# Instalar Ollama para Jetson ARM64
curl -fsSL https://ollama.com/install.sh | sh
```

### **4. 🤖 CONFIGURAÇÃO DO G1**

```bash
# Instalar Unitree SDK2 Python
cd unitree_sdk2_python
pip install -e .
cd ..

# Configurar interface de rede do G1
# Verificar interface disponível
ip addr show

# Atualizar config para interface correta (ex: eth0, wlan0)
# Editar config/g1_real.json5 com interface da Jetson
```

### **5. 🧠 CONFIGURAÇÃO DE MODELOS AI**

```bash
# Iniciar Ollama
sudo systemctl enable ollama
sudo systemctl start ollama

# Baixar modelo LLM principal
ollama pull llama3.1:8b

# Baixar modelo LLaVA
ollama pull llava

# Verificar modelos instalados
ollama list
```

### **6. 🔧 CONFIGURAÇÃO DE ÁUDIO BLUETOOTH**

```bash
# Configurar Bluetooth
sudo systemctl enable bluetooth
sudo systemctl start bluetooth

# Pareamento DJI Mic 2
bluetoothctl
> scan on
> pair <MAC_DJI_MIC>
> connect <MAC_DJI_MIC>
> trust <MAC_DJI_MIC>

# Pareamento Anker Speaker
> pair <MAC_ANKER_SPEAKER>
> connect <MAC_ANKER_SPEAKER>
> trust <MAC_ANKER_SPEAKER>
> exit

# Configurar áudio
pactl list short sources  # Encontrar DJI Mic
pactl list short sinks    # Encontrar Anker Speaker
```

### **7. 🔑 CONFIGURAÇÃO DE CREDENCIAIS**

```bash
# Criar arquivo .env
cp .env.example .env

# Editar com suas credenciais
nano .env
```

```env
# APIs Cloud
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=...

# Google ASR
GOOGLE_ASR_CREDENTIALS_FILE=credentials/google_asr.json

# G1 Network
G1_INTERFACE=eth0  # ou wlan0, conforme sua configuração
G1_IP=192.168.123.15
```

### **8. ✅ TESTE COMPLETO**

```bash
# Ativar ambiente
source venv/bin/activate

# Teste básico do sistema
python scripts/test/test_interactive_complete.py

# Teste específico do G1 (com robô conectado)
python tests/test_g1_integrated.py

# Teste performance
python scripts/test/test_ollama.py
```

---

## 🔍 **VERIFICAÇÕES PRÉ-OPERAÇÃO**

### **✅ Checklist Obrigatório**

- [ ] Jetson conectada à rede
- [ ] G1 ligado e conectado via Ethernet
- [ ] DJI Mic 2 pareado e conectado
- [ ] Anker Speaker pareado e conectado
- [ ] Ollama rodando com llama3.1:8b e llava
- [ ] APIs configuradas no .env
- [ ] Câmera USB funcionando
- [ ] Teste interativo completo passou

### **🎯 Comandos de Verificação**

```bash
# Sistema
nvidia-smi                    # GPU funcionando
ollama list                   # Modelos instalados
pactl list                    # Áudio funcionando
v4l2-ctl --list-devices      # Câmera disponível

# Rede G1
ping 192.168.123.15          # G1 acessível
ip route | grep 192.168.123  # Rota configurada

# Bluetooth
bluetoothctl devices         # Dispositivos pareados
pactl list short sources     # Mic detectado
pactl list short sinks       # Speaker detectado
```

---

## 🚀 **INICIALIZAÇÃO DO SISTEMA**

### **Modo Desenvolvimento**
```bash
source venv/bin/activate
python scripts/test/test_interactive_complete.py
```

### **Modo Produção**
```bash
source venv/bin/activate
python examples/basic_usage.py --config config/g1_production.json5
```

### **Serviço Automático (Opcional)**
```bash
# Criar serviço systemd
sudo nano /etc/systemd/system/t031a5.service

[Unit]
Description=T031A5 G1 Robot System
After=network.target ollama.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/t031a5
Environment=PATH=/home/ubuntu/t031a5/venv/bin
ExecStart=/home/ubuntu/t031a5/venv/bin/python examples/basic_usage.py --config config/g1_production.json5
Restart=always

[Install]
WantedBy=multi-user.target

# Ativar serviço
sudo systemctl enable t031a5
sudo systemctl start t031a5
```

---

## 🔧 **TROUBLESHOOTING COMUM**

### **Problema: G1 não conecta**
```bash
# Verificar interface
ip addr show
ping 192.168.123.15

# Reconfigurar interface
sudo dhclient eth0
# ou configurar IP estático
```

### **Problema: Áudio Bluetooth**
```bash
# Reconectar dispositivos
bluetoothctl connect <MAC>
pulseaudio --kill
pulseaudio --start
```

### **Problema: Ollama lento**
```bash
# Verificar GPU
nvidia-smi
# Configurar Ollama para GPU
export OLLAMA_HOST=0.0.0.0:11434
```

### **Problema: Câmera não funciona**
```bash
# Verificar dispositivos
v4l2-ctl --list-devices
ls /dev/video*
# Testar câmera
ffplay /dev/video0
```

---

## 📊 **PERFORMANCE ESPERADA (Jetson Orin NX 16GB)**

| Componente | Latência | Recursos |
|------------|----------|----------|
| 🧠 LLM Local | 2-4s | 6GB RAM, 40% GPU |
| 👁️ LLaVA | 3-6s | 4GB RAM, 60% GPU |
| 🎤 STT Google | 1-2s | 100MB RAM, 5% CPU |
| 🔊 TTS ElevenLabs | 2-3s | 200MB RAM, 10% CPU |
| 📷 Câmera | 50ms | 500MB RAM, 20% CPU |
| 🤖 G1 Control | 100ms | 200MB RAM, 10% CPU |

### **🎯 Performance Total**
- **Conversação Completa**: 5-8 segundos
- **Análise Visual**: 6-10 segundos  
- **RAM Total**: ~12GB (75% uso)
- **CPU Total**: ~50% uso
- **GPU Total**: ~70% uso

---

## 🎉 **SUCESSO NO DEPLOY!**

**Quando tudo estiver funcionando, você terá:**

- 🤖 **Tobias (G1)** totalmente autônomo
- 👁️ **Visão AI local** com LLaVA
- 🗣️ **Conversação natural** multimodal
- 🎤 **Áudio Bluetooth** profissional
- 🧠 **Processamento local** na Jetson
- 📊 **Monitoramento** via WebSim (opcional)

**O robô do futuro está pronto! 🚀✨**
