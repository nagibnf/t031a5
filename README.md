# t031a5 - Sistema Integrado com Unitree G1

Sistema de IA multimodal otimizado para o robô humanóide Unitree G1, com funcionalidades confirmadas e testadas.

**🫧 Desenvolvido por Bolha**

---

## 🎯 Status Atual

**✅ FUNCIONALIDADES CONFIRMADAS:**
- **TTS (Text-to-Speech)**: Inglês (speaker_id=1) e Chinês (speaker_id=0)
- **LEDs e Emoções**: Controle completo de cores e estados emocionais
- **Movimentos**: ID 32 (Right Hand on Mouth) funcionando perfeitamente
- **WAV Playback**: Reprodução de áudio 16kHz mono
- **Sequências Integradas**: Combinação de TTS, WAV e movimentos
- **Interface de Rede**: en11 configurada e funcionando

## 🚀 Início Rápido

### 1. Configuração do Ambiente

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Verificar dependências
pip list | grep unitree
```

### 2. Teste Rápido

```bash
# Teste das funcionalidades confirmadas
python scripts/test/test_g1_confirmed_features.py

# Demonstração completa
python scripts/test/test_t031a5_integrated.py

# Exemplo básico
python examples/basic_usage.py
```

### 3. Configuração do G1

Certifique-se de que o G1 está:
- ✅ Conectado via rede (interface en11)
- ✅ Em estado "Main Operation Control"
- ✅ SDK Unitree instalado e funcionando

## 📋 Funcionalidades Detalhadas

### 🗣️ Sistema de Voz

**TTS Nativo do G1:**
- **Speaker ID 1**: Inglês (funcionando perfeitamente)
- **Speaker ID 0**: Chinês (funcionando perfeitamente)
- **Volume**: 100% (máximo)
- **Formato**: Assíncrono (retorna imediatamente, áudio demora alguns segundos)

**WAV Playback:**
- **Formato**: 16kHz mono WAV
- **Controle**: Play, Stop, Volume
- **Uso**: Para português e áudios customizados

### 🎨 Sistema de LEDs

**Cores Confirmadas:**
- **Azul claro (173, 216, 230)**: Estado original
- **Verde (0, 255, 0)**: Feliz, Inglês
- **Vermelho (255, 0, 0)**: Chinês, Erro
- **Amarelo (255, 255, 0)**: Empolgado
- **Azul (0, 0, 255)**: Triste

### 🤚 Movimentos

**Funcionando:**
- **18 movimentos de braço**: IDs 1, 11-35, 99 (Kiss, Wave, Clap, Hug, etc.)
- **10 estados FSM**: IDs 0-7, 200, 702, 706 (Zero Torque, Damping, Get Ready, etc.)
- **4 comandos de locomoção**: damp, sit, highstand, lowstand

**Não Disponíveis (Erro 7402):**
- **IDs 10, 14, 16, 20-21, 28-30, 36-50**: Movimentos não implementados

**📋 Lista Completa**: Veja `docs/g1_movements_complete_list.md` para todos os movimentos confirmados

### 🎵 Áudio

**Estratégias:**
1. **Para Inglês**: TTS nativo (speaker_id=1)
2. **Para Português**: WAV PlayStream
3. **Para Chinês**: TTS nativo (speaker_id=0)

## 🔧 Configuração

### Arquivo de Configuração

```json5
{
  "unitree_g1": {
    "interface": {
      "interface": "en11",
      "timeout": 10.0
    },
    "controller": {
      "default_volume": 100,
      "default_speaker_id": 1
    },
    "audio": {
      "tts": {
        "speaker_id_english": 1,
        "speaker_id_chinese": 0,
        "volume_max": 100
      },
      "wav": {
        "format": "16kHz_mono_16bit",
        "stream_name": "t031a5"
      }
    }
  }
}
```

### Microfone Externo

Para captura de áudio, use:
- **Microfone USB** conectado ao computador
- **Microfone Bluetooth** para mobilidade
- **Configuração**: `external_microphone: true`

## 📁 Estrutura do Projeto

```
t031a5/
├── src/t031a5/                 # Código fonte principal
│   ├── unitree/               # Interface G1
│   ├── inputs/                # Entradas multimodais
│   ├── actions/               # Ações do robô
│   ├── runtime/               # Sistema de execução
│   ├── conversation/          # Engine de conversação
│   ├── llm/                   # Provedores de LLM
│   └── logging/               # Sistema de logs
├── config/                    # Configurações
│   ├── g1_base_complete.json5 # Configuração base
│   ├── g1_test.json5          # Para testes
│   ├── g1_mock.json5          # Modo mock
│   ├── g1_production.json5    # Produção
│   └── g1_real.json5          # G1 real
├── scripts/                   # Scripts utilitários
│   ├── test/                  # Scripts de teste
│   ├── monitor/               # Monitoramento
│   ├── deploy/                # Deploy
│   └── create_config.py       # Criador de configs
├── docs/                      # Documentação
│   ├── project/               # Status e planejamento
│   ├── guides/                # Guias práticos
│   └── api/                   # Documentação técnica
├── examples/                  # Exemplos de uso
├── logs/                      # Logs do sistema
├── credentials/               # Credenciais
└── README.md                  # Este arquivo
```

## 🧪 Testes

### Teste Básico
```bash
python tests/test_g1_confirmed_features.py
```

### Teste Integrado
```bash
python tests/test_g1_integrated.py
```

### Demonstração Completa
```bash
python test_t031a5_integrated.py
```

## 🎭 Exemplos de Uso

### TTS Simples
```python
from t031a5.unitree.g1_controller import G1Controller, G1Language

controller = G1Controller(config)
await controller.initialize()

# TTS Inglês
await controller.speak("Hello! I am the G1 robot.", G1Language.ENGLISH)

# TTS Chinês
await controller.speak("你好！我是G1机器人。", G1Language.CHINESE)
```

### LEDs e Emoções
```python
from t031a5.unitree.g1_controller import G1Emotion

# Definir emoção
await controller.set_emotion(G1Emotion.HAPPY)

# LEDs personalizados
await controller.set_leds(255, 0, 0)  # Vermelho
```

### Movimentos
```python
# Executar movimento
await controller.execute_gesture(32, emotion=G1Emotion.HAPPY)

# Obter movimentos disponíveis
movements = await controller.get_available_movements()
```

### WAV Playback
```python
# Reproduzir arquivo WAV
await controller.play_audio("audio.wav", emotion=G1Emotion.EXCITED)

# Parar reprodução
await controller.stop_audio()
```

### Sequência Integrada
```python
from t031a5.unitree.g1_controller import G1AudioCommand

commands = [
    G1AudioCommand("tts", text="Hello!", speaker_id=1),
    G1AudioCommand("wav", wav_file="audio.wav"),
    G1AudioCommand("stop")
]

await controller.execute_sequence(commands)
```

## 🔍 Troubleshooting

### Problemas Comuns

**1. Erro de Conexão:**
- Verifique se o G1 está conectado via en11
- Confirme IP: 192.168.123.161
- Teste: `ping 192.168.123.161`

**2. Erro 3104 (API não implementada):**
- Movimento não disponível no firmware atual
- Use apenas movimentos confirmados (ID 32, 99)

**3. TTS em Chinês:**
- Confirme speaker_id=0
- Verifique se o texto está em chinês

**4. Volume Baixo:**
- Configure volume=100
- Verifique configurações de áudio do sistema

**5. WAV não reproduz:**
- Formato deve ser 16kHz mono
- Use `ffmpeg` para conversão:
  ```bash
  ffmpeg -i input.mp3 -ar 16000 -ac 1 -acodec pcm_s16le output.wav
  ```

### Estados do Robô

**Estados Necessários:**
- **Main Operation Control**: Para executar comandos
- **AI Mode**: Estado atual confirmado

**Transições:**
- **Get Ready** → **Main Operation Control**: R1+X
- **Relaxamento**: ID 99 entre movimentos

## 📊 Métricas e Monitoramento

O sistema inclui:
- **Logging estruturado**
- **Métricas de performance**
- **Health checks**
- **Alertas automáticos**

## 🔒 Segurança

- **Parada de emergência** implementada
- **Limites de velocidade** configurados
- **Detecção de colisão** ativa
- **Controle de força** limitado

## 🚀 Próximos Passos

1. **Teste com microfone externo**
2. **Integração com LLM**
3. **Desenvolvimento de novos movimentos**
4. **Sistema de navegação**
5. **Interface web avançada**

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique os logs em `logs/`
2. Execute os testes de diagnóstico
3. Consulte a documentação do SDK Unitree
4. Verifique a configuração de rede

---

**🎉 Sistema t031a5 funcionando perfeitamente com G1!**
