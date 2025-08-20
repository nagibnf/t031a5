# Guia de Locomoção e Rotação do G1

## 🎯 Resumo das Capacidades

Com base na pesquisa da documentação oficial e análise do SDK, o Unitree G1 possui as seguintes capacidades de movimento e rotação:

### 🦴 **Articulações do Quadril**

As especificações oficiais indicam que o G1 possui articulações no quadril com as seguintes amplitudes:

- **Pitch (P):** ±154° (movimento para frente/trás)
- **Roll (R):** -30° a +170° (movimento lateral)
- **Yaw (Y):** ±158° (rotação horizontal)

### 🚶 **API de Locomoção (LocoClient)**

O SDK fornece os seguintes métodos para controle de movimento:

#### **Métodos Principais**

```python
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient

loco_client = LocoClient()
loco_client.Init()

# 1. Movimento com velocidade
loco_client.Move(vx, vy, vyaw, continous_move=False)
# vx: velocidade para frente/trás (m/s)
# vy: velocidade lateral (m/s) 
# vyaw: velocidade de rotação (rad/s)
# continous_move: movimento contínuo (True) ou por duração (False)

# 2. Controle de velocidade preciso
loco_client.SetVelocity(vx, vy, omega, duration=1.0)
# omega: velocidade angular (rad/s)
# duration: duração em segundos

# 3. Parar movimento
loco_client.StopMove()

# 4. Controle de balanceamento
loco_client.BalanceStand(balance_mode)
# balance_mode: 0, 1, 2 (diferentes modos)

# 5. Controle de altura
loco_client.HighStand()
loco_client.LowStand()
```

#### **Estados FSM Necessários**

Antes de usar comandos de locomoção, o robô deve estar preparado:

```python
# Sequência de preparação
loco_client.SetFsmId(0)  # Zero Torque
time.sleep(3)
loco_client.SetFsmId(1)  # Damping  
time.sleep(3)
loco_client.SetFsmId(4)  # Get Ready
time.sleep(5)

# ⚠️ CRÍTICO: Após FSM 4, é OBRIGATÓRIO usar o controle físico!
# No controle físico, pressione: R1 + X
# Isso coloca o robô em "Main Operation Control"
```

#### **⚠️ ATENÇÃO ESPECIAL: Main Operation Control**

**A sequência FSM sozinha NÃO é suficiente para locomoção!**

Após `SetFsmId(4)`, é **OBRIGATÓRIO**:
1. Pegar o controle físico do robô
2. Pressionar **R1 + X** simultaneamente  
3. O robô entrará automaticamente em "Lowstanding"
4. Aguardar estabilização antes de comandos de movimento

**Sem este passo, todos os comandos de locomoção falharão!**

## 🧪 **Testes Propostos**

### **Teste 1: Movimentos Básicos**

```python
# Movimentos direcionais
movements = [
    ("Frente", 0.2, 0.0, 0.0),
    ("Trás", -0.2, 0.0, 0.0),
    ("Esquerda", 0.0, 0.2, 0.0),
    ("Direita", 0.0, -0.2, 0.0),
    ("Rotação esquerda", 0.0, 0.0, 0.5),
    ("Rotação direita", 0.0, 0.0, -0.5),
]

for name, vx, vy, vyaw in movements:
    loco_client.Move(vx, vy, vyaw)
    time.sleep(3)
    loco_client.StopMove()
```

### **Teste 2: Padrões de Rotação**

```python
# Teste de rotação com diferentes velocidades
rotations = [
    ("Lenta", 0.2),    # 0.2 rad/s
    ("Média", 0.5),    # 0.5 rad/s  
    ("Rápida", 1.0),   # 1.0 rad/s
    ("Máxima", 1.5),   # 1.5 rad/s
]

for name, vyaw in rotations:
    loco_client.SetVelocity(0.0, 0.0, vyaw, 3.0)
    time.sleep(3)
    loco_client.StopMove()
```

### **Teste 3: Movimento Circular**

```python
# Movimento circular: avanço + rotação
loco_client.SetVelocity(0.1, 0.0, 0.4, 10.0)  # 10 segundos
time.sleep(10)
loco_client.StopMove()
```

### **Teste 4: Movimento em Figura 8**

```python
# Primeira curva
loco_client.SetVelocity(0.1, 0.0, 0.5, 3.0)
time.sleep(3)

# Transição
loco_client.SetVelocity(0.1, 0.0, 0.0, 1.0)  
time.sleep(1)

# Segunda curva (direção oposta)
loco_client.SetVelocity(0.1, 0.0, -0.5, 3.0)
time.sleep(3)

loco_client.StopMove()
```

## ⚠️ **Considerações de Segurança**

### **Limites Recomendados**

- **Velocidade linear máxima**: 0.5 m/s (para testes iniciais)
- **Velocidade angular máxima**: 1.0 rad/s (para testes iniciais)
- **Espaço mínimo**: 3x3 metros livre
- **Superfície**: Plana e antiderrapante

### **Procedimentos de Segurança**

1. **SEMPRE verificar estado do robô** antes de qualquer comando
2. **Sempre verificar espaço** antes de iniciar movimento
3. **Manter controle remoto** próximo para emergência
4. **Usar velocidades baixas** nos primeiros testes
5. **Monitorar estado do robô** durante movimento
6. **Implementar timeout** em todos os comandos

### **⚠️ VERIFICAÇÃO DE ESTADO OBRIGATÓRIA**

**ANTES de qualquer comando, SEMPRE verificar:**

```python
def check_robot_state(expected_mode="control"):
    """Verifica o estado atual do robô."""
    status, result = motion_switcher.CheckMode()
    if status == 0 and result:
        current_mode = result.get('name', 'unknown')
        if current_mode == expected_mode:
            return True
        else:
            print(f"⚠️ Robô está em modo {current_mode}, esperado: {expected_mode}")
            return False
    return False

# USAR ANTES DE CADA COMANDO:
if not check_robot_state("control"):
    print("❌ Robô não está no modo correto!")
    return
```

## 🎯 **Objetivos dos Testes**

### **Primários**
- [ ] Verificar responsividade dos comandos de movimento
- [ ] Testar limites de velocidade de rotação
- [ ] Avaliar estabilidade durante rotação
- [ ] Confirmar funcionamento dos comandos de parada

### **Secundários**
- [ ] Medir precisão de movimentos angulares
- [ ] Testar combinações de movimento linear + angular
- [ ] Avaliar suavidade das transições
- [ ] Documentar comportamentos inesperados

## 📊 **Estrutura do Teste**

O arquivo `test_g1_locomotion_rotation.py` implementa:

1. **Inicialização**: SDK + LocoClient + MotionSwitcher
2. **Preparação**: Sequência FSM (0→1→4)
3. **Testes básicos**: Movimentos direcionais
4. **Testes avançados**: Padrões de rotação
5. **Testes complexos**: Circular e figura 8
6. **Testes de limites**: Velocidades máximas
7. **Testes de balanceamento**: Diferentes modos

## 🔧 **Como Executar**

```bash
# 1. Ativar ambiente virtual
source venv/bin/activate

# 2. Conectar ao G1 (interface en11)
# Verificar conexão de rede

# 3. Executar teste
python test_g1_locomotion_rotation.py

# 4. Seguir instruções na tela
# Confirmar espaço disponível
# Monitorar robô durante testes
```

## 📝 **Resultados Esperados**

### **Sucessos**
- Movimentos básicos (frente, trás, lateral)
- Rotações em diferentes velocidades
- Parada imediata com StopMove()
- Transições suaves entre movimentos

### **Limitações Possíveis**
- Velocidades muito altas podem causar instabilidade
- Superfícies irregulares podem afetar precisão
- Alguns comandos podem ter latência
- Movimentos complexos podem precisar ajuste

## 🔮 **Próximos Passos**

Após os testes iniciais:

1. **Integrar no sistema t031a5**
2. **Criar comandos de voz** para movimento
3. **Implementar navegação autônoma**
4. **Adicionar detecção de obstáculos**
5. **Desenvolver coreografias** complexas

---

*Baseado na documentação oficial do Unitree G1 e análise do SDK2 Python*
