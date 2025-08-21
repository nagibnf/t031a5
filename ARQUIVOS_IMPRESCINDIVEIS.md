# 📁 ARQUIVOS IMPRESCINDÍVEIS - SISTEMA t031a5

## 🚀 **ARQUIVOS PRINCIPAIS**

### `t031a5_main.py`
**Sistema principal contínuo** - Ponto de entrada único
- Executa loop infinito como OM1
- Inicializa CortexRuntime
- Configura logging
- Tratamento de erros e shutdown

### `run_t031a5.py` 
**Wrapper de execução** - Script auxiliar simples
- Wrapper para executar sistema principal
- Verificações básicas
- Facilita execução

---

## ⚙️ **CONFIGURAÇÃO**

### `config/g1_production.json5`
**Configuração única de produção** - VALIDADA 100%
- Todas configurações do sistema
- Inputs, actions, fuser, LLM
- Parâmetros de hardware G1
- Loop 10Hz contínuo como OM1

---

## 🧠 **CORE DO SISTEMA**

### `src/t031a5/runtime/cortex.py`
**Loop principal contínuo** - Coração do sistema
- CortexRuntime (como OM1)
- Loop: inputs→fuser→llm→actions
- Inicialização de componentes
- Métricas e controle

### `src/t031a5/runtime/config.py`
**Gerenciador de configurações** - CORRIGIDO
- ConfigManager para JSON5
- Validação com Pydantic
- Conversão inputs/actions lista/dict
- Ambiente e logging

### `src/t031a5/runtime/orchestrators.py`
**Orquestradores inputs/actions** - Core operacional
- InputOrchestrator (coleta dados)
- ActionOrchestrator (executa ações)
- Mapeamento automático de classes
- Fallbacks com mocks

---

## 🔗 **FUSER (NLDB)**

### `src/t031a5/fuser/base.py`
**Classe base fuser** - Interface comum
- BaseFuser abstrata
- FusedData estrutura dados
- Health check e status
- Histórico e contexto

### `src/t031a5/fuser/multimodal.py`
**Fusão multimodal** - NLDB core
- MultimodalFuser principal
- Weighted, concatenate, attention
- Combina audio+visual+state
- Confiança e metadados

### `src/t031a5/fuser/__init__.py`
**Exports fuser** - Imports limpos

---

## 🧠 **LLM PROVIDER**

### `src/t031a5/llm/provider.py`
**Gerenciador LLM** - Provider principal
- LLMProvider unified interface
- BaseLLMProvider abstrata
- LLMRequest/LLMResponse structs
- Fallbacks automáticos

### `src/t031a5/llm/providers/ollama_provider.py`
**Provider Ollama** - IMPLEMENTADO
- OllamaProvider para local
- HTTP client httpx
- Health check e modelos
- Processamento local

### `src/t031a5/llm/providers/mock_provider.py`
**Provider Mock** - CORRIGIDO
- MockLLMProvider para dev/teste
- Respostas contextuais
- Simula delays e erros
- Debug mode

### `src/t031a5/llm/__init__.py`
**Exports LLM** - Imports limpos

---

## 🎤 **INPUTS**

### `src/t031a5/inputs/base.py`
**Classe base inputs** - Interface comum
- BaseInput abstrata
- InputData estrutura dados
- Health check e status
- Lifecycle management

### `src/t031a5/inputs/plugins/g1_voice.py`
**Input de voz** - DJI Mic 2
- G1VoiceInput para áudio
- Integração managers audio
- STT Google/Whisper
- Escuta contínua

### `src/t031a5/inputs/plugins/g1_vision.py`
**Input de visão** - Câmera
- G1VisionInput para imagem
- Camera manager integration
- LLaVA analysis
- Detecção objetos/pessoas

### `src/t031a5/inputs/plugins/g1_state.py`
**Input estado robô** - Monitoramento G1
- G1StateInput para DDS
- Estado bateria/thermal
- Articulações e motores
- Safety monitoring

### `src/t031a5/inputs/plugins/g1_sensors.py`
**Input sensores** - Arduino extras
- G1SensorsInput ambiente
- Temperatura/humidade/pressão
- Qualidade ar
- Dados ambientais

### `src/t031a5/inputs/plugins/g1_gps.py`
**Input GPS** - Localização
- G1GPSInput coordenadas
- Arduino GPS module
- Distance calculations
- Location awareness

### `src/t031a5/inputs/__init__.py`
**Exports inputs** - Imports limpos

---

## 🎭 **ACTIONS**

### `src/t031a5/actions/base.py`
**Classe base actions** - Interface comum
- BaseAction abstrata
- ActionRequest/ActionResult structs
- Health check e status
- Emergency stop

### `src/t031a5/actions/g1_speech.py`
**Action fala** - TTS sistema
- G1SpeechAction synthesis
- ElevenLabs + G1 native
- Audio output routing
- Portuguese support

### `src/t031a5/actions/g1_arms.py`
**Action braços** - Movimentos G1
- G1ArmsAction controller
- 50 movimentos mapeados
- G1ArmActionClient SDK
- Safety checks

### `src/t031a5/actions/g1_emotion.py`
**Action emoções** - LEDs expressivos
- G1EmotionAction controller
- 10 estados emocionais
- Sync com fala
- RGB head LEDs

### `src/t031a5/actions/g1_movement.py`
**Action locomoção** - Movimentos corpo
- G1MovementAction controller
- Locomotion patterns
- Posture control
- Safety navigation

### `src/t031a5/actions/g1_audio.py`
**Action áudio** - Reprodução sons
- G1AudioAction player
- Bluetooth Anker output
- Sound effects matrix
- Volume control

### `src/t031a5/actions/__init__.py`
**Exports actions** - Imports limpos

---

## 💬 **CONVERSATION ENGINE**

### `src/t031a5/conversation/engine.py`
**Motor conversacional** - Sistema vivo
- ConversationEngine coordenador
- Ciclo conversacional completo
- Context awareness
- Proactive responses

### `src/t031a5/conversation/__init__.py`
**Exports conversation** - Imports limpos

---

## 🔧 **MANAGERS AUXILIARES**

### `src/t031a5/audio/audio_manager_definitivo.py`
**Gerenciador áudio** - DJI Mic 2
- Sistema híbrido áudio
- DJI Mic capture
- Quality analysis
- Format conversion

### `src/t031a5/vision/camera_manager.py`
**Gerenciador câmera** - Captura imagem
- Camera lock system
- USB camera support
- Resolution control
- Protective cleanup

### `src/t031a5/vision/llava_manager.py`
**Gerenciador LLaVA** - Análise visual
- Local LLaVA model
- Image analysis
- Object detection
- Context generation

### `src/t031a5/speech/stt_real_manager.py`
**Gerenciador STT** - Speech-to-Text
- Google Speech API
- Whisper fallback
- Language detection
- Real-time processing

### `src/t031a5/speech/tts_real_manager.py`
**Gerenciador TTS** - Text-to-Speech
- ElevenLabs synthesis
- Voice selection
- Audio formatting
- Quality control

### `src/t031a5/llm/llm_real_manager.py`
**Gerenciador LLM** - Processamento linguagem
- LLM coordination
- Prompt engineering
- Response formatting
- Context management

---

## 📱 **INTERFACE**

### `src/t031a5/simulators/websim.py`
**WebSim interface** - Monitoramento
- Mobile-first design
- Real-time streaming
- Emergency stop
- Status monitoring

### `templates/index.html`
**Interface HTML** - Frontend
- Responsive design
- Control panels
- Video streaming
- Status displays

### `static/style.css`
**Estilos CSS** - Design mobile
- Mobile-first layout
- Modern UI
- Dark/light themes
- Responsive grid

### `static/websim.js`
**JavaScript frontend** - Interatividade
- WebSocket connection
- Real-time updates
- Control buttons
- Video handling

---

## 📋 **SCRIPTS ESSENCIAIS**

### `scripts/verificar_sistema.py`
**Verificação sistema** - Health check
- Testa todos componentes
- G1 connectivity
- Audio devices
- LLM availability
- Config validation

### `scripts/verificar_estado_g1.py`
**Verificação G1** - Estado robô
- G1 connectivity test
- Control mode check
- SDK validation
- Automatic guidance

---

## 📚 **DOCUMENTAÇÃO**

### `README.md`
**Documentação principal** - Uso do sistema
- Quick start guide
- Architecture overview
- Requirements list
- Execution instructions

### `config/README.md`
**Documentação config** - Configurações
- Config file structure
- Parameter explanations
- Validation process
- Production settings

---

## 📦 **DEPENDÊNCIAS**

### `pyproject.toml`
**Dependências Python** - Package management
- Required packages
- Version constraints
- Optional dependencies
- Build configuration

---

## 🚀 **RESULTADO FINAL**

**TOTAL: ~45 arquivos imprescindíveis**

- ✅ **Core**: 100% funcional validado
- ✅ **Inputs**: 5 plugins implementados  
- ✅ **Actions**: 5 plugins implementados
- ✅ **LLM**: 2 providers (Ollama + Mock)
- ✅ **Fuser**: MultimodalFuser operacional
- ✅ **Config**: Validada e corrigida
- ✅ **Interface**: WebSim mobile-first

**Sistema completo pronto para produção!**
