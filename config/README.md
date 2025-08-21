# ⚙️ Configuração Sistema t031a5

## 📁 Arquivo Único de Produção

**`g1_production.json5`** - Configuração completa validada

### 🎯 Características:

- **Loop contínuo** a 10Hz (como OM1)
- **Sistema conversacional** sempre ativo
- **Inputs multimodais** coordenados
- **Actions sincronizadas** fala+gestos+LEDs
- **Segurança integrada** com emergency stop

### 🔧 Componentes Configurados:

- ✅ **DJI Mic 2** - escuta contínua português
- ✅ **Câmera USB** - análise visual LLaVA  
- ✅ **G1 State** - monitoramento robô
- ✅ **ElevenLabs TTS** - fala via Anker
- ✅ **G1 Arms** - 50 movimentos disponíveis
- ✅ **LEDs emocionais** - sincronizados com fala
- ✅ **WebSim** - interface port 8080

### 📋 Validação:

```bash
# Verificar configuração
python scripts/verificar_sistema.py

# Executar com configuração
python t031a5_main.py
```

**Não há configs experimentais** - apenas produção limpa.
