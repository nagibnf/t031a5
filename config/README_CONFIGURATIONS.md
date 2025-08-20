# 📋 Sistema de Configurações - t031a5

## 🎯 Visão Geral

O sistema t031a5 utiliza um sistema de configurações modular baseado em JSON5, permitindo flexibilidade total para diferentes cenários de uso.

## 📁 Estrutura de Configurações

### 🔧 Configuração Base
- **`g1_base_complete.json5`** - Configuração base completa com todas as funcionalidades ativadas
- Serve como template para todas as outras configurações

### 🎭 Configurações Especializadas

#### **Teste e Desenvolvimento**
- **`g1_test.json5`** - Para testes integrados (debug ativado, timeouts reduzidos)
- **`g1_mock.json5`** - Para testes sem hardware real (modo mock ativado)
- **`g1_test_robot.json5`** - Configuração específica para testes com robô

#### **Produção**
- **`g1_production.json5`** - Otimizada para produção (segurança, backup, métricas)
- **`g1_real.json5`** - Para uso com G1 real (hardware físico)

#### **Específicas**
- **`g1_basic.json5`** - Configuração básica mínima
- **`g1_conversation.json5`** - Focada em conversação
- **`g1_elevenlabs.json5`** - Integração com ElevenLabs TTS
- **`g1_logitech.json5`** - Configuração para hardware Logitech
- **`g1_native_connectors.json5`** - Conectores nativos do G1

## 🛠️ Criando Novas Configurações

### Script Automático
```bash
# Criar configuração de teste
python scripts/create_config.py g1_meu_teste --test

# Criar configuração mock
python scripts/create_config.py g1_meu_mock --mock

# Criar configuração de produção
python scripts/create_config.py g1_meu_prod --production

# Criar configuração mínima
python scripts/create_config.py g1_meu_minimal --minimal

# Criar configuração personalizada
python scripts/create_config.py g1_personalizada
```

### Manualmente
1. Copie `g1_base_complete.json5`
2. Renomeie para sua configuração
3. Modifique apenas as seções necessárias
4. Mantenha a estrutura base intacta

## 📋 Seções de Configuração

### 🔧 Básicas
- **`name`** - Nome da configuração
- **`version`** - Versão
- **`description`** - Descrição
- **`hertz`** - Frequência do loop principal
- **`system_prompt_base`** - Prompt base do sistema

### 🎮 Desenvolvimento
- **`development`** - Configurações de desenvolvimento
  - `debug_mode` - Modo debug
  - `websim_enabled` - WebSim ativado
  - `hot_reload` - Recarregamento automático

### 🤖 G1 Específicas
- **`g1_specific`** - Características específicas do G1
  - `capabilities` - Capacidades disponíveis
  - `confirmed_features` - Funcionalidades confirmadas

### 💬 Conversação
- **`conversation_engine`** - Engine de conversação
  - `enable_vision_context` - Contexto visual
  - `enable_gesture_sync` - Sincronização de gestos
  - `enable_emotion_detection` - Detecção de emoções

### 📥 Inputs
- **`agent_inputs`** - Entradas multimodais
  - `G1Voice` - Voz e microfone
  - `G1Vision` - Visão computacional
  - `G1State` - Estado do robô
  - `G1Sensors` - Sensores
  - `G1GPS` - GPS e navegação

### 📤 Actions
- **`agent_actions`** - Ações do robô
  - `G1Speech` - Fala e TTS
  - `G1Emotion` - Emoções e LEDs
  - `G1Movement` - Movimentos
  - `G1Arms` - Controle de braços
  - `G1Audio` - Reprodução de áudio

### 🔌 Unitree G1
- **`unitree_g1`** - Configurações específicas do SDK
  - `interface` - Configurações de rede
  - `controller` - Controlador
  - `audio` - Áudio
  - `movements` - Movimentos confirmados
  - `leds` - LEDs e cores

### 🧠 LLM
- **`llm_providers`** - Provedores de LLM
  - `primary` - Provedor principal
  - `fallback` - Provedor de fallback
  - `vision` - Provedor para visão

### 📊 Sistema
- **`logging`** - Sistema de logs
- **`metrics`** - Métricas e monitoramento
- **`security`** - Segurança
- **`websim`** - WebSim para debugging
- **`performance`** - Otimizações
- **`network`** - Configurações de rede
- **`backup`** - Sistema de backup

## 🎯 Modos de Operação

### 🧪 Modo Teste
```json5
{
  "development": {
    "debug_mode": true,
    "websim_enabled": true
  },
  "logging": {
    "level": "DEBUG"
  }
}
```

### 🎭 Modo Mock
```json5
{
  "agent_inputs": {
    "G1Voice": {"mock_mode": true},
    "G1Vision": {"mock_mode": true}
  },
  "agent_actions": {
    "G1Speech": {"mock_mode": true},
    "G1Movement": {"mock_mode": true}
  }
}
```

### 🏭 Modo Produção
```json5
{
  "development": {
    "debug_mode": false,
    "websim_enabled": false
  },
  "security": {
    "access_control": {"enabled": true}
  },
  "backup": {"enabled": true}
}
```

## 🔧 Usando Configurações

### Via CLI
```bash
# Usar configuração específica
./t031a5 --config config/g1_test.json5

# Usar configuração padrão
./t031a5
```

### Via Python
```python
from t031a5.runtime.cortex import CortexRuntime
from pathlib import Path

# Carregar configuração
config_path = Path("config/g1_test.json5")
cortex = CortexRuntime(config_path)
```

### Via Scripts
```bash
# Teste com configuração específica
python test_t031a5_integrated.py --config config/g1_mock.json5

# Preparação com configuração
python prepare_g1_test.py --config config/g1_real.json5
```

## 📝 Boas Práticas

### ✅ Recomendado
- Sempre use `g1_base_complete.json5` como base
- Modifique apenas as seções necessárias
- Mantenha a estrutura hierárquica
- Use nomes descritivos para configurações
- Documente mudanças importantes

### ❌ Evitar
- Modificar a estrutura base
- Duplicar configurações desnecessariamente
- Usar configurações não testadas em produção
- Ignorar validações de configuração

## 🔍 Validação de Configurações

### Script de Validação
```bash
# Validar configuração
python scripts/validate_config.py config/g1_test.json5

# Validar todas as configurações
python scripts/validate_config.py --all
```

### Verificação Manual
1. Verificar sintaxe JSON5
2. Confirmar seções obrigatórias
3. Validar valores de configuração
4. Testar com sistema

## 📚 Exemplos

### Configuração Mínima
```json5
{
  "name": "G1 Minimal",
  "agent_inputs": {
    "G1Voice": {"enabled": true},
    "G1Vision": {"enabled": false}
  },
  "agent_actions": {
    "G1Speech": {"enabled": true},
    "G1Movement": {"enabled": false}
  }
}
```

### Configuração Completa
```json5
{
  "name": "G1 Complete",
  "agent_inputs": {
    "G1Voice": {"enabled": true, "mock_mode": false},
    "G1Vision": {"enabled": true, "mock_mode": false},
    "G1State": {"enabled": true, "mock_mode": false},
    "G1Sensors": {"enabled": true, "mock_mode": false},
    "G1GPS": {"enabled": true, "mock_mode": false}
  },
  "agent_actions": {
    "G1Speech": {"enabled": true, "mock_mode": false},
    "G1Emotion": {"enabled": true, "mock_mode": false},
    "G1Movement": {"enabled": true, "mock_mode": false},
    "G1Arms": {"enabled": true, "mock_mode": false},
    "G1Audio": {"enabled": true, "mock_mode": false}
  }
}
```

## 🚀 Próximos Passos

1. **Criar configuração personalizada** para seu caso de uso
2. **Testar configuração** com scripts de validação
3. **Documentar mudanças** específicas
4. **Compartilhar configuração** com a equipe

---

**🎯 Sistema de configurações t031a5 - Flexível e poderoso!**
