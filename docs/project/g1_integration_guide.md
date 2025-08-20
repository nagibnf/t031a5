# Guia de Integração com G1 Real

Este guia explica como configurar e usar o sistema t031a5 com o robô humanóide G1 real da Unitree.

## 📋 Pré-requisitos

### Hardware
- **Robô G1** da Unitree
- **Computador** com Python 3.9+
- **Cabo Ethernet** para conexão direta ou **Rede WiFi** configurada

### Software
- Python 3.9 ou superior
- SDK2 Python da Unitree
- Dependências do t031a5

## 🚀 Instalação

### 1. Instalar SDK2 Python

```bash
# Instalar SDK oficial da Unitree
pip install unitree-sdk2py

# Verificar instalação
python -c "import unitree_sdk2py; print('SDK instalado com sucesso')"
```

### 2. Configurar Rede

#### Opção A: Conexão Direta (Recomendado)
1. Conecte o cabo Ethernet entre o G1 e o computador
2. Configure o IP do computador:
   ```bash
   # macOS/Linux
   sudo ifconfig en0 192.168.123.100 netmask 255.255.255.0
   
   # Windows
   netsh interface ip set address "Ethernet" static 192.168.123.100 255.255.255.0
   ```

#### Opção B: Rede WiFi
1. Conecte G1 e computador à mesma rede WiFi
2. Descubra o IP do G1:
   ```bash
   # No G1, execute:
   ifconfig
   # ou
   ip addr show
   ```

### 3. Verificar Conectividade

```bash
# Teste de conectividade
ping 192.168.123.161

# Teste de porta
telnet 192.168.123.161 8080
```

## ⚙️ Configuração

### 1. Configuração do Sistema

O arquivo `config/g1_real.json5` já foi criado automaticamente. Verifique e ajuste:

```json5
{
  "g1_controller": {
    "enabled": true,
    "interface": {
      "robot_ip": "192.168.123.161",  // IP do seu G1
      "robot_port": 8080,
      "timeout": 5.0,
      "retry_attempts": 3
    }
  }
}
```

### 2. Configuração de Segurança

```json5
{
  "g1_specific": {
    "safety_mode": "normal",        // normal, conservative, aggressive
    "emergency_stop": true,
    "battery_conservation": true,
    "thermal_management": true,
    "network_timeout": 5.0
  }
}
```

## 🧪 Testes

### 1. Teste Básico de Conectividade

```bash
python3 test_real_g1_integration.py
```

### 2. Teste do Sistema Completo

```bash
# Teste com configuração real
python3 -m t031a5.cli test --config config/g1_real.json5 --duration 30
```

### 3. Execução Completa

```bash
# Executar sistema completo
python3 -m t031a5.cli run --config config/g1_real.json5
```

## 🌐 Interface Web

Após iniciar o sistema, acesse a interface web:

```
http://localhost:8080
```

### Funcionalidades Disponíveis:
- **Status em Tempo Real**: Bateria, temperatura, estado
- **Controle de Movimento**: Andar, girar, gestos
- **Controle de Voz**: Falar, emoções
- **Monitoramento**: Logs, métricas, alertas

## 🔧 Comandos Disponíveis

### Via CLI
```bash
# Executar sistema
t031a5 run --config config/g1_real.json5

# Testar por tempo específico
t031a5 test --config config/g1_real.json5 --duration 60

# Verificar status
t031a5 status --config config/g1_real.json5

# Validar configuração
t031a5 validate --config config/g1_real.json5
```

### Via Interface Web
- **Movimento**: Botões para andar, girar, parar
- **Gestos**: Wave, bow, dance, etc.
- **Voz**: Campo de texto para falar
- **Emoções**: Botões para diferentes emoções
- **Emergência**: Botão de parada de emergência

## 📊 Monitoramento

### Logs
- **Arquivo**: `logs/t031a5_real.log`
- **Nível**: INFO (configurável)
- **Formato**: Estruturado com contexto

### Métricas
- **Performance**: Tempo de loop, taxa de erro
- **Sistema**: CPU, memória, disco
- **G1**: Bateria, temperatura, estado

### Alertas
- **Bateria baixa**: < 20%
- **Temperatura alta**: > 45°C
- **Performance**: Loop > 100ms
- **Erros**: Taxa > 5%

## 🚨 Segurança

### Parada de Emergência
- **CLI**: `Ctrl+C`
- **Web**: Botão "Emergency Stop"
- **Hardware**: Botão físico no G1

### Modos de Segurança
- **Normal**: Operação padrão
- **Conservative**: Movimentos mais lentos
- **Aggressive**: Movimentos mais rápidos

### Configurações de Segurança
```json5
{
  "g1_controller": {
    "interface": {
      "safety_mode": "normal",
      "emergency_stop": true,
      "max_speed": 0.5,        // Velocidade máxima
      "max_turn_speed": 0.3    // Velocidade máxima de giro
    }
  }
}
```

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. SDK não instalado
```bash
# Solução
pip install unitree-sdk2py
```

#### 2. Não consegue conectar com G1
```bash
# Verificar IP
ping 192.168.123.161

# Verificar porta
telnet 192.168.123.161 8080

# Verificar rede
ifconfig en0
```

#### 3. G1 não responde
- Verificar se G1 está ligado
- Verificar bateria
- Verificar conexão de rede
- Reiniciar G1 se necessário

#### 4. Movimentos não funcionam
- Verificar modo de segurança
- Verificar velocidade máxima
- Verificar se G1 está em modo de controle

### Logs de Debug

```bash
# Executar com debug
python3 -m t031a5.cli run --config config/g1_real.json5 --log-level DEBUG

# Ver logs em tempo real
tail -f logs/t031a5_real.log
```

## 📈 Performance

### Métricas Esperadas
- **Frequência**: 10 Hz (configurável)
- **Latência**: < 100ms
- **Taxa de erro**: < 5%
- **Uso de CPU**: < 30%
- **Uso de memória**: < 500MB

### Otimizações
- Ajustar frequência de loop
- Configurar timeouts adequados
- Usar modo de segurança apropriado
- Monitorar recursos do sistema

## 🔄 Atualizações

### Atualizar SDK
```bash
pip install --upgrade unitree-sdk2py
```

### Atualizar t031a5
```bash
git pull origin main
pip install -e .
```

## 📞 Suporte

### Recursos
- **Documentação**: [docs/](docs/)
- **Exemplos**: [examples/](examples/)
- **Testes**: [test_*.py](test_*.py)

### Logs de Erro
- **Sistema**: `logs/t031a5_real.log`
- **WebSim**: Console do navegador
- **G1**: Logs internos do robô

### Contato
- **Issues**: GitHub Issues
- **Documentação**: README.md
- **Exemplos**: examples/

## 🎯 Próximos Passos

### Funcionalidades Avançadas
1. **Visão Computacional**: G1Vision plugin
2. **Navegação**: G1GPS plugin
3. **Interação Avançada**: Gestos complexos
4. **Aprendizado**: Machine Learning

### Otimizações
1. **Performance**: Tuning de parâmetros
2. **Segurança**: Validações avançadas
3. **Interface**: UI/UX melhorada
4. **Documentação**: Guias avançados

---

**🎉 Parabéns! Você está pronto para usar o t031a5 com G1 real!**
