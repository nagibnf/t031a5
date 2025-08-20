# 🤖 **GUIA DE TESTE NO ROBÔ G1**

## 📋 **CHECKLIST DE PREPARAÇÃO**

### **✅ Pré-requisitos:**
- [ ] **Unitree SDK Python** instalado na venv
- [ ] **APIs configuradas** (OpenAI, etc.)
- [ ] **Câmera Logitech** conectada ao robô
- [ ] **Rede configurada** (robô e computador na mesma rede)
- [ ] **IP do robô** conhecido (padrão: 192.168.123.161)

### **🔧 Configurações de Segurança:**
- [ ] **Modo de segurança** ativo no robô
- [ ] **Espaço livre** ao redor do robô (2m mínimo)
- [ ] **Botão de emergência** acessível
- [ ] **Supervisão** durante o teste

---

## 🚀 **PASSOS PARA TESTE**

### **1. 🔐 Configurar APIs (PRIMEIRA VEZ):**
```bash
# Configurar APIs de forma segura
./t031a5 api setup

# OU configurar individualmente:
./t031a5 api add openai openai
./t031a5 api add anthropic anthropic

# Verificar APIs configuradas:
./t031a5 api list

# Testar conectividade:
./t031a5 api test
```

### **2. 🔌 Conectar ao Robô:**
```bash
# Verificar se o robô está na rede
ping 192.168.123.161

# Testar conectividade com SDK
python -c "
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
ChannelFactoryInitialize(0, 'en0')  # ou sua interface de rede
print('✅ Conectividade OK')
"
```

### **3. 🧪 Executar Teste:**
```bash
# Teste completo no robô G1
./t031a5 test

# OU teste específico:
python -m t031a5.cli run --config config/g1_test_robot.json5
```

### **4. 🌐 Monitoramento Remoto:**
```bash
# Acessar WebSim para debug
# http://SEU_IP:8080

# Ver logs em tempo real:
./t031a5 logs
```

---

## ⚙️ **CONFIGURAÇÕES ESPECÍFICAS**

### **📷 Câmera Logitech:**
```json5
"G1Vision": {
  "enabled": true,
  "camera_index": 0,  // Testar 0, 1, 2 se necessário
  "resolution": [1280, 720],
  "fps": 15,
  "mock_mode": false
}
```

### **🔊 Áudio:**
```json5
"G1Voice": {
  "enabled": true,
  "microphone_index": 0,
  "sample_rate": 16000,
  "wake_word": "G1",
  "continuous_listening": false  // Desabilitado para teste
}
```

### **🤖 Controle do Robô:**
```json5
"g1_controller": {
  "enabled": true,
  "mock_mode": false,  // MODO REAL!
  "interface": {
    "robot_ip": "192.168.123.161",
    "safety_mode": "strict",
    "max_speed": 0.3  // Velocidade reduzida
  }
}
```

---

## 🧪 **TESTES ESPECÍFICOS**

### **🗣️ Teste de Voz:**
```bash
# Comandos de teste:
"G1, olá"
"G1, qual é o seu nome?"
"G1, como você está?"
```

### **🎨 Teste de LEDs:**
```bash
# Comandos de teste:
"G1, fique feliz"
"G1, fique triste"
"G1, fique neutro"
```

### **🦿 Teste de Movimento:**
```bash
# Comandos de teste:
"G1, acene com a mão"
"G1, levante os braços"
"G1, fique em pé"
```

### **📷 Teste de Visão:**
```bash
# Comandos de teste:
"G1, o que você está vendo?"
"G1, há alguém na frente?"
"G1, descreva o ambiente"
```

---

## 🔍 **MONITORAMENTO E DEBUG**

### **📊 Logs Detalhados:**
```bash
# Ver logs em tempo real:
tail -f logs/g1_test_robot.log

# Filtrar por componente:
grep "TTS" logs/g1_test_robot.log
grep "LED" logs/g1_test_robot.log
grep "ERROR" logs/g1_test_robot.log
```

### **🌐 WebSim Interface:**
- **URL**: `http://SEU_IP:8080`
- **Controles**: Botões para comandos manuais
- **Status**: Informações em tempo real
- **Logs**: Visualização de logs

### **📱 Monitoramento Remoto:**
```bash
# Verificar status do sistema:
./t031a5 status

# Verificar conectores nativos:
python -c "
from src.t031a5.connectors.manager import G1NativeConnectorManager
manager = G1NativeConnectorManager({})
print(manager.get_all_status())
"
```

---

## ⚠️ **PROBLEMAS COMUNS E SOLUÇÕES**

### **❌ Erro de Conectividade:**
```bash
# Verificar rede:
ifconfig | grep inet
ping 192.168.123.161

# Verificar interface de rede:
ls /sys/class/net/
```

### **❌ Erro de Câmera:**
```bash
# Testar câmera:
python test_camera.py

# Verificar dispositivos:
ls /dev/video*
```

### **❌ Erro de Áudio:**
```bash
# Verificar microfone:
python -c "
import pyaudio
p = pyaudio.PyAudio()
print('Dispositivos de áudio:', p.get_device_count())
"
```

### **❌ Erro de API:**
```bash
# Verificar APIs:
./t031a5 api validate
./t031a5 api test
```

---

## 🛡️ **SEGURANÇA E EMERGÊNCIA**

### **🚨 Botão de Emergência:**
- **Localização**: Sempre acessível
- **Função**: Para todos os movimentos do robô
- **Teste**: Pressionar antes de iniciar

### **📏 Espaço de Segurança:**
- **Distância mínima**: 2 metros do robô
- **Obstáculos**: Remover objetos próximos
- **Superfície**: Piso plano e estável

### **🔋 Monitoramento de Bateria:**
- **Nível mínimo**: 30%
- **Temperatura**: Máximo 40°C
- **Alerta**: Sistema para automaticamente

---

## 📈 **MÉTRICAS DE PERFORMANCE**

### **⚡ Otimizações Esperadas:**
- **TTS Nativo**: -40% CPU
- **LEDs Nativos**: -20% CPU
- **Áudio Nativo**: -15% CPU
- **Total**: -75% CPU

### **📊 Monitoramento:**
```bash
# Verificar uso de CPU:
htop

# Verificar uso de memória:
free -h

# Verificar logs de performance:
grep "performance" logs/g1_test_robot.log
```

---

## 🎯 **PRÓXIMOS PASSOS**

### **✅ Após Teste Bem-sucedido:**
1. **Documentar** resultados
2. **Otimizar** configurações
3. **Expandir** funcionalidades
4. **Preparar** para Jetson

### **🔧 Melhorias Futuras:**
- **ASR Nativo** (quando disponível)
- **GPT Nativo** (quando disponível)
- **Navegação** com LiDAR
- **Visão avançada** com RealSense

---

## 📞 **SUPORTE**

### **🆘 Em Caso de Problemas:**
1. **Verificar logs**: `./t031a5 logs`
2. **Testar conectividade**: `ping 192.168.123.161`
3. **Verificar APIs**: `./t031a5 api test`
4. **Reiniciar sistema**: `./t031a5 clean && ./t031a5 test`

### **📧 Contato:**
- **Logs**: `logs/g1_test_robot.log`
- **Configuração**: `config/g1_test_robot.json5`
- **Status**: `./t031a5 status`

---

**🎉 BOA SORTE NO TESTE! 🤖✨**
