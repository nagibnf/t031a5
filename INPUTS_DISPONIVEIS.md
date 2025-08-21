# 🎤 INPUTS DISPONÍVEIS - SISTEMA t031a5

## 📋 **INPUTS IMPLEMENTADOS (5 plugins)**

---

## 🗣️ **1. G1Voice - INPUT DE VOZ**

### **Arquivo:** `src/t031a5/inputs/plugins/g1_voice.py`

### **Funcionalidade:**
- **Captura áudio DJI Mic 2** via Bluetooth
- **Speech-to-Text** Google + Whisper fallback  
- **Escuta contínua** sem wake word
- **Processamento tempo real** audio stream

### **Configuração atual:**
```json5
{
  "type": "G1Voice",
  "enabled": true,
  "config": {
    "device": "dji_mic_2",
    "language": "pt-BR", 
    "sensitivity": 0.7,
    "continuous_listening": true,
    "noise_suppression": true,
    "wake_word": null,
    "audio_quality": "high"
  }
}
```

### **Output format:**
```python
InputData(
    input_type="G1Voice",
    source="dji_mic_2", 
    data={
        "text": "texto reconhecido",
        "confidence": 0.95,
        "language": "pt-BR",
        "audio_data": bytes,
        "duration": 3.2,
        "noise_level": 0.1
    }
)
```

### **Status:** ✅ **100% IMPLEMENTADO E TESTADO**

---

## 👁️ **2. G1Vision - INPUT DE VISÃO**

### **Arquivo:** `src/t031a5/inputs/plugins/g1_vision.py`

### **Funcionalidade:**
- **Captura imagem** câmera USB (temporária)
- **Análise LLaVA** local para objetos/pessoas
- **Detecção facial** e reconhecimento  
- **Context visual** para conversação

### **Configuração atual:**
```json5
{
  "type": "G1Vision", 
  "enabled": true,
  "config": {
    "camera_device": 0,
    "resolution": [640, 480],
    "fps": 5,
    "analysis_interval": 2.0,
    "enable_face_detection": true,
    "enable_object_detection": true
  }
}
```

### **Output format:**
```python
InputData(
    input_type="G1Vision",
    source="usb_camera",
    data={
        "image_analysis": "descrição da cena",
        "objects_detected": ["person", "chair"],
        "faces_detected": 1,
        "image_path": "/tmp/capture.jpg",
        "timestamp_capture": "2025-08-21T10:30:00",
        "confidence": 0.88
    }
)
```

### **Status:** ✅ **100% IMPLEMENTADO E TESTADO**

---

## 🤖 **3. G1State - INPUT ESTADO ROBÔ**

### **Arquivo:** `src/t031a5/inputs/plugins/g1_state.py`

### **Funcionalidade:**
- **Monitoramento DDS** estado G1 real-time
- **Bateria, térmica** temperature monitoring
- **Articulações** e motores status
- **Safety checks** contínuo

### **Configuração atual:**
```json5
{
  "type": "G1State",
  "enabled": true, 
  "config": {
    "monitor_interval": 1.0,
    "enable_battery_monitoring": true,
    "enable_temperature_monitoring": true,
    "enable_joint_monitoring": false
  }
}
```

### **Output format:**
```python
InputData(
    input_type="G1State",
    source="g1_dds",
    data={
        "mode": "CONTROL",
        "battery_level": 85.5,
        "temperature": 32.1,
        "uptime": 3600,
        "joint_status": {...},
        "motor_status": {...},
        "safety_status": "OK"
    }
)
```

### **Status:** ✅ **100% IMPLEMENTADO E TESTADO**

---

## 🌡️ **4. G1Sensors - INPUT SENSORES AMBIENTE**

### **Arquivo:** `src/t031a5/inputs/plugins/g1_sensors.py`

### **Funcionalidade:**
- **Arduino sensores** temperatura/humidade
- **Qualidade do ar** monitoring
- **Pressão atmosférica** readings
- **Dados ambientais** context

### **Configuração disponível:**
```json5
{
  "type": "G1Sensors",
  "enabled": false,  // Desabilitado na config atual
  "config": {
    "arduino_port": "/dev/ttyUSB0",
    "sensors": ["temperature", "humidity", "pressure", "air_quality"],
    "polling_interval": 5.0,
    "calibration": {...}
  }
}
```

### **Output format:**
```python
InputData(
    input_type="G1Sensors",
    source="arduino",
    data={
        "temperature": 24.5,
        "humidity": 60.2,
        "pressure": 1013.25,
        "air_quality": "good",
        "light_level": 350,
        "noise_level": 45.3
    }
)
```

### **Status:** ⚠️ **IMPLEMENTADO MAS NÃO CONFIGURADO**

---

## 📍 **5. G1GPS - INPUT LOCALIZAÇÃO**

### **Arquivo:** `src/t031a5/inputs/plugins/g1_gps.py`

### **Funcionalidade:**
- **GPS coordinates** via Arduino module
- **Location awareness** indoor/outdoor
- **Distance calculations** between points
- **Navigation support** future

### **Configuração disponível:**
```json5
{
  "type": "G1GPS",
  "enabled": false,  // Desabilitado na config atual  
  "config": {
    "gps_port": "/dev/ttyUSB1",
    "update_interval": 2.0,
    "accuracy_threshold": 5.0,
    "enable_indoor_fallback": true
  }
}
```

### **Output format:**
```python
InputData(
    input_type="G1GPS",
    source="arduino_gps",
    data={
        "latitude": -23.5505,
        "longitude": -46.6333,
        "altitude": 760.0,
        "accuracy": 3.2,
        "speed": 0.0,
        "heading": 0.0,
        "location_type": "indoor"
    }
)
```

### **Status:** ⚠️ **IMPLEMENTADO MAS NÃO CONFIGURADO**

---

## 📊 **RESUMO STATUS INPUTS**

| Input | Status | Configurado | Testado | Hardware |
|-------|--------|-------------|---------|----------|
| **G1Voice** | ✅ 100% | ✅ Sim | ✅ Sim | DJI Mic 2 |
| **G1Vision** | ✅ 100% | ✅ Sim | ✅ Sim | USB Camera |
| **G1State** | ✅ 100% | ✅ Sim | ✅ Sim | G1 DDS |
| **G1Sensors** | ⚠️ 80% | ❌ Não | ❌ Não | Arduino |
| **G1GPS** | ⚠️ 80% | ❌ Não | ❌ Não | Arduino GPS |

---

## 🎯 **INPUTS ATIVOS NO SISTEMA**

**Na configuração atual (`g1_production.json5`):**

### **✅ ATIVOS (3 inputs):**
1. **G1Voice** - DJI Mic 2 escuta contínua
2. **G1Vision** - Câmera USB análise visual  
3. **G1State** - Monitoramento estado G1

### **❌ INATIVOS (2 inputs):**
4. **G1Sensors** - Sensores Arduino (hardware não conectado)
5. **G1GPS** - GPS Arduino (hardware não conectado)

---

## 🔧 **PRÓXIMOS PASSOS INPUTS**

### **Para ativar G1Sensors:**
1. Conectar Arduino com sensores
2. Configurar porta serial
3. Ativar na config: `"enabled": true`
4. Testar leituras

### **Para ativar G1GPS:**
1. Conectar módulo GPS no Arduino
2. Configurar porta serial  
3. Ativar na config: `"enabled": true`
4. Calibrar coordenadas

### **Para adicionar novos inputs:**
1. Criar plugin em `src/t031a5/inputs/plugins/`
2. Herdar de `BaseInput`
3. Implementar métodos abstratos
4. Adicionar mapeamento no orchestrator
5. Configurar em `g1_production.json5`

---

**🎤 Sistema com 3 inputs ativos e prontos para 2 inputs adicionais!**
