# Guia de Instalação - t031a5

Este guia explica como instalar e configurar o sistema t031a5 para o robô humanóide G1 da Unitree.

## 📋 Pré-requisitos

### Sistema Operacional
- **Linux**: Ubuntu 20.04+ (recomendado)
- **macOS**: 12.0+ (para desenvolvimento)
- **Windows**: Windows 10+ (para desenvolvimento)

### Python
- **Python 3.9+** (recomendado: Python 3.11)
- **pip** ou **uv** (gerenciador de pacotes)

### Hardware
- **Robô G1 da Unitree** (para produção)
- **Câmera USB** (para desenvolvimento)
- **Microfone** (para desenvolvimento)
- **Rede Ethernet** (para comunicação com G1)

### Software
- **SDK Unitree G1 Python** (obrigatório)
- **CycloneDDS** (para comunicação ROS2)
- **FFmpeg** (para processamento de áudio)

## 🚀 Instalação Rápida

### 1. Clone o Repositório

```bash
git clone https://github.com/t031a5/t031a5.git
cd t031a5
```

### 2. Instale as Dependências

#### Usando uv (Recomendado)

```bash
# Instale uv se não tiver
curl -LsSf https://astral.sh/uv/install.sh | sh

# Instale as dependências
uv sync
```

#### Usando pip

```bash
# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate     # Windows

# Instale o projeto
pip install -e .
```

### 3. Configure o Ambiente

```bash
# Copie a configuração básica
cp config/g1_basic.json5 config/local.json5

# Edite as configurações conforme necessário
nano config/local.json5
```

### 4. Configure Variáveis de Ambiente

```bash
# Adicione ao seu ~/.bashrc ou ~/.zshrc
export OPENAI_API_KEY="sua_chave_api_aqui"
export ELEVENLABS_API_KEY="sua_chave_elevenlabs_aqui"

# Recarregue o shell
source ~/.bashrc
```

## 🔧 Instalação Detalhada

### Instalação do SDK Unitree G1

#### 1. Baixe o SDK Python

```bash
git clone https://github.com/unitreerobotics/unitree_sdk2_python.git
cd unitree_sdk2_python
```

#### 2. Instale Dependências do SDK

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3-pip python3-dev build-essential

# macOS
brew install python3

# Windows
# Use o instalador do Python
```

#### 3. Instale o SDK

```bash
pip install -e .
```

#### 4. Configure CycloneDDS

```bash
# Ubuntu/Debian
sudo apt install -y cyclonedds

# macOS
brew install cyclonedds

# Configure variáveis de ambiente
export CYCLONEDDS_URI="<udp/6/192.168.123.161/7400>"
export CYCLONEDDS_DOMAIN=0
```

### Instalação de Dependências de Áudio

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install -y \
    portaudio19-dev \
    python3-pyaudio \
    ffmpeg \
    libsndfile1-dev \
    libasound2-dev
```

#### macOS

```bash
brew install portaudio ffmpeg libsndfile
```

#### Windows

```bash
# Instale via conda ou baixe binários
conda install -c conda-forge portaudio ffmpeg libsndfile
```

### Instalação de Dependências de Visão

#### Ubuntu/Debian

```bash
sudo apt install -y \
    libopencv-dev \
    python3-opencv \
    libgl1-mesa-glx \
    libglib2.0-0
```

#### macOS

```bash
brew install opencv
```

#### Windows

```bash
pip install opencv-python
```

## 🧪 Verificação da Instalação

### 1. Teste Básico

```bash
# Verifique se o CLI funciona
t031a5 version

# Valide uma configuração
t031a5 validate --config config/g1_basic.json5

# Mostre status da configuração
t031a5 status --config config/g1_basic.json5
```

### 2. Teste de Conectividade com G1

```bash
# Teste conexão com G1 (se disponível)
python -c "
from unitree_sdk2_python import LocoClient
client = LocoClient()
client.Init()
print('✅ Conexão com G1 estabelecida')
"
```

### 3. Teste de Áudio

```bash
# Teste captura de áudio
python -c "
import pyaudio
p = pyaudio.PyAudio()
print(f'✅ PyAudio funcionando: {p.get_device_count()} dispositivos')
"
```

### 4. Teste de Visão

```bash
# Teste OpenCV
python -c "
import cv2
print(f'✅ OpenCV funcionando: versão {cv2.__version__}')
"
```

## 🔧 Configuração Avançada

### Configuração de Rede

Para comunicação com o G1, configure a interface de rede:

```bash
# Configure IP estático (exemplo)
sudo ip addr add 192.168.123.100/24 dev en0
sudo ip route add 192.168.123.0/24 dev en0

# Ou configure no arquivo de configuração
# "unitree_ethernet": "en0"
```

### Configuração de Áudio

Para usar a câmera do G1 como microfone (desenvolvimento):

```json5
{
  "agent_inputs": [
    {
      "type": "G1Voice",
      "config": {
        "use_g1_microphone": false,  // Usar câmera para desenvolvimento
        "device_name": "Camera"      // Nome do dispositivo de áudio
      }
    }
  ]
}
```

### Configuração de Segurança

```json5
{
  "g1_specific": {
    "safety_mode": "development",    // Modo de desenvolvimento
    "emergency_stop": true,          // Parada de emergência habilitada
    "battery_conservation": false,   // Desabilitado para desenvolvimento
    "thermal_management": true       // Gerenciamento térmico habilitado
  }
}
```

## 🚨 Solução de Problemas

### Erro: "SDK Unitree não encontrado"

```bash
# Verifique se o SDK está instalado
pip list | grep unitree

# Reinstale se necessário
pip uninstall unitree_sdk2_python
pip install -e /path/to/unitree_sdk2_python
```

### Erro: "PortAudio não encontrado"

```bash
# Ubuntu/Debian
sudo apt install -y portaudio19-dev python3-pyaudio

# macOS
brew install portaudio
pip install pyaudio

# Windows
pip install pyaudio
```

### Erro: "OpenCV não encontrado"

```bash
# Ubuntu/Debian
sudo apt install -y python3-opencv

# macOS
brew install opencv
pip install opencv-python

# Windows
pip install opencv-python
```

### Erro: "CycloneDDS não encontrado"

```bash
# Ubuntu/Debian
sudo apt install -y cyclonedds

# macOS
brew install cyclonedds

# Configure variáveis de ambiente
export CYCLONEDDS_URI="<udp/6/192.168.123.161/7400>"
```

### Erro: "API Key não configurada"

```bash
# Configure as variáveis de ambiente
export OPENAI_API_KEY="sua_chave_aqui"
export ELEVENLABS_API_KEY="sua_chave_aqui"

# Ou adicione ao arquivo de configuração
{
  "llm": {
    "api_key": "sua_chave_aqui"
  }
}
```

## 📚 Próximos Passos

Após a instalação bem-sucedida:

1. **Leia o [Guia de Configuração](configuration.md)**
2. **Explore os [Exemplos](examples.md)**
3. **Consulte a [API Reference](api.md)**
4. **Participe da [Comunidade](https://discord.gg/t031a5)**

## 🤝 Suporte

Se encontrar problemas:

1. **Verifique os [Issues](https://github.com/t031a5/t031a5/issues)**
2. **Consulte a [Documentação](https://docs.t031a5.org)**
3. **Entre no [Discord](https://discord.gg/t031a5)**
4. **Abra um novo Issue** com detalhes do problema

---

**t031a5** - Transformando a interação humano-robô com IA multimodal no G1 🤖✨
