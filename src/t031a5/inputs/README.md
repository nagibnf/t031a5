# 🎤 Sistema de Inputs do t031a5

Este módulo contém todos os plugins de entrada do sistema t031a5, organizados para capturar dados multimodais do robô G1.

## 📁 Estrutura dos Inputs

```
src/t031a5/inputs/
├── __init__.py           # Exportações principais
├── base.py              # Classe base BaseInput
└── plugins/             # Plugins específicos do G1
    ├── __init__.py      # Exportações dos plugins
    ├── g1_voice.py      # Reconhecimento de voz
    ├── g1_vision.py     # Processamento de visão
    ├── g1_sensors.py    # Monitoramento de sensores
    ├── g1_gps.py        # Localização GPS
    └── g1_state.py      # Estado interno do robô
```

## 🔧 Componentes

### **BaseInput** (`base.py`)
Classe base abstrata para todos os inputs:
- **Inicialização**: Configuração e setup
- **Coleta de dados**: Método abstrato `collect_data()`
- **Status**: Monitoramento de saúde
- **Configuração**: Gerenciamento de parâmetros

### **Plugins G1**

#### **G1VoiceInput** (`plugins/g1_voice.py`)
- **Função**: Reconhecimento de voz
- **Dados**: Texto, confiança, idioma, timestamp
- **Configurações**: Sample rate, chunk size, VAD
- **Status**: Microfone ativo, nível de áudio

#### **G1VisionInput** (`plugins/g1_vision.py`)
- **Função**: Processamento de visão
- **Dados**: Imagens, objetos detectados, faces
- **Configurações**: Resolução, FPS, detecção
- **Status**: Câmera ativa, qualidade da imagem

#### **G1SensorsInput** (`plugins/g1_sensors.py`)
- **Função**: Monitoramento de sensores
- **Dados**: Bateria, temperatura, IMU, força
- **Configurações**: Intervalo de leitura, thresholds
- **Status**: Sensores funcionando, alertas

#### **G1GPSInput** (`plugins/g1_gps.py`)
- **Função**: Localização GPS
- **Dados**: Latitude, longitude, altitude, precisão
- **Configurações**: Frequência de atualização
- **Status**: Sinal GPS, precisão

#### **G1StateInput** (`plugins/g1_state.py`)
- **Função**: Estado interno do robô
- **Dados**: Modo, bateria, erros, comandos
- **Configurações**: Intervalo de verificação
- **Status**: Estado geral do sistema

## 🚀 Como Usar

### **Importação**
```python
from t031a5.inputs import (
    BaseInput,
    G1VoiceInput,
    G1VisionInput,
    G1SensorsInput,
    G1GPSInput,
    G1StateInput
)
```

### **Criação de Input**
```python
# Configuração
config = {
    "sample_rate": 16000,
    "chunk_size": 1024,
    "language": "pt-BR"
}

# Criação
voice_input = G1VoiceInput(config)

# Inicialização
await voice_input.initialize()

# Coleta de dados
data = await voice_input.collect_data()
```

### **Uso com Orchestrator**
```python
from t031a5.runtime.orchestrators import InputOrchestrator

# Configuração de inputs
inputs_config = [
    {
        "type": "G1Voice",
        "enabled": True,
        "priority": 1,
        "config": {"sample_rate": 16000}
    },
    {
        "type": "G1Sensors", 
        "enabled": True,
        "priority": 2,
        "config": {"interval": 0.1}
    }
]

# Criação do orchestrator
orchestrator = InputOrchestrator(inputs_config)

# Inicialização
await orchestrator.initialize()

# Coleta de dados
data = await orchestrator.collect_all_data()
```

## 📊 Dados de Saída

### **Estrutura Padrão**
```python
InputData(
    content=dict,           # Dados específicos do input
    confidence=float,       # Confiança (0.0-1.0)
    timestamp=datetime,     # Timestamp da coleta
    metadata=dict,          # Metadados adicionais
    source=str              # Nome do input
)
```

### **Exemplos de Dados**

#### **G1Voice**
```python
{
    "text": "Olá G1, como você está?",
    "confidence": 0.95,
    "language": "pt-BR",
    "audio_level": 0.7,
    "is_speech": True
}
```

#### **G1Sensors**
```python
{
    "battery": 85,
    "temperature": 32.5,
    "imu": {
        "roll": 0.1,
        "pitch": 0.2,
        "yaw": 0.3
    }
}
```

#### **G1Vision**
```python
{
    "objects": [
        {"type": "person", "confidence": 0.9, "bbox": [100, 200, 300, 400]},
        {"type": "chair", "confidence": 0.8, "bbox": [50, 150, 200, 300]}
    ],
    "faces": [
        {"age": 25, "gender": "male", "emotion": "happy"}
    ]
}
```

## ⚙️ Configurações

### **Configurações Comuns**
```python
{
    "enabled": True,           # Input ativo
    "priority": 1,             # Prioridade (1-10)
    "timeout": 5.0,            # Timeout em segundos
    "retry_attempts": 3,       # Tentativas de reconexão
    "debug": False             # Modo debug
}
```

### **Configurações Específicas**

#### **G1Voice**
```python
{
    "sample_rate": 16000,      # Taxa de amostragem
    "chunk_size": 1024,        # Tamanho do chunk
    "language": "pt-BR",       # Idioma
    "vad_enabled": True,       # Voice Activity Detection
    "noise_reduction": True    # Redução de ruído
}
```

#### **G1Sensors**
```python
{
    "interval": 0.1,           # Intervalo de leitura
    "battery_monitoring": True,
    "temperature_monitoring": True,
    "alert_thresholds": {
        "battery_low": 20,
        "temperature_high": 45
    }
}
```

## 🔍 Monitoramento

### **Status do Input**
```python
status = await input.get_status()
# {
#     "initialized": True,
#     "running": True,
#     "healthy": True,
#     "last_data": datetime,
#     "error_count": 0
# }
```

### **Health Check**
```python
health = await input.health_check()
# {
#     "status": "healthy",
#     "issues": [],
#     "metrics": {
#         "data_rate": 10.0,
#         "error_rate": 0.0,
#         "latency": 0.05
#     }
# }
```

## 🐛 Troubleshooting

### **Problemas Comuns**

#### **Input não inicializa**
```python
# Verificar configuração
print(input.config)

# Verificar dependências
print(input.dependencies)

# Verificar logs
print(input.logs)
```

#### **Dados não coletados**
```python
# Verificar se está rodando
print(await input.get_status())

# Verificar conectividade
print(await input.health_check())

# Forçar coleta
data = await input.collect_data(force=True)
```

#### **Performance ruim**
```python
# Ajustar configurações
config["interval"] = 0.2  # Mais lento
config["chunk_size"] = 512  # Chunks menores

# Verificar recursos
print(await input.get_metrics())
```

## 📝 Adicionando Novos Inputs

### **Estrutura de Plugin**
```python
from ..base import BaseInput, InputData

class NovoInput(BaseInput):
    """Plugin de input personalizado."""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.name = "NovoInput"
    
    async def _initialize(self) -> bool:
        """Inicialização específica."""
        # Setup aqui
        return True
    
    async def _collect_data(self) -> InputData:
        """Coleta de dados específica."""
        # Coleta aqui
        return InputData(
            content={"dados": "exemplo"},
            confidence=0.9,
            timestamp=datetime.now(),
            metadata={},
            source=self.name
        )
    
    async def _stop(self) -> bool:
        """Parada específica."""
        # Cleanup aqui
        return True
```

### **Registro no Sistema**
```python
# Em src/t031a5/inputs/plugins/__init__.py
from .novo_input import NovoInput

__all__ = [
    # ... outros inputs ...
    "NovoInput",
]

# Em src/t031a5/inputs/__init__.py
from .plugins.novo_input import NovoInput

__all__ = [
    # ... outros inputs ...
    "NovoInput",
]
```

## 🎯 Boas Práticas

### **Performance**
- Use timeouts apropriados
- Implemente retry logic
- Monitore recursos
- Cache dados quando possível

### **Robustez**
- Trate erros graciosamente
- Implemente fallbacks
- Valide dados de entrada
- Log detalhado para debug

### **Configuração**
- Valide configurações
- Use valores padrão sensatos
- Documente parâmetros
- Suporte hot-reload

---

**🎤 Os inputs são os olhos e ouvidos do sistema t031a5!**
