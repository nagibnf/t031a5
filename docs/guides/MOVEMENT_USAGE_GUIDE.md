# Guia de Uso dos Movimentos G1 - Sistema t031a5

## 🎯 Separação de Responsabilidades

O sistema t031a5 possui **50 movimentos totais** organizados em **3 categorias** com usos específicos:

### **🤚 MOVIMENTOS DE BRAÇOS (20) - Para Conversação**
**USO**: Sistema conversacional, gestos expressivos, interação social

```
IDs Válidos: 1, 11-35, 99
Tipo: G1MovementType.ARM_GESTURE
Contexto: ConversationEngine, gestos sincronizados
```

**Exemplos:**
- **ID 26**: `wave_above_head` - Acenar durante saudação
- **ID 32**: `right_hand_on_mouth` - Gesto de pensamento
- **ID 17**: `clap` - Aplaudir durante celebração
- **ID 99**: `release_arm` - Relaxar braços (essencial)

### **🚶 ESTADOS FSM (8) - Para Controle de Postura**
**USO**: Controle direto do robô, mudanças de postura, preparação

```
IDs: 0-4, 200, 702, 706
Tipo: G1MovementType.FSM_STATE
Contexto: Setup do robô, controle manual, emergências
```

**⚠️ IMPORTANTE**: Estados FSM **NÃO devem ser usados** no sistema conversacional!

**Exemplos:**
- **ID 1**: `damping` - Amortecimento seguro
- **ID 4**: `get_ready` - Preparar para operação
- **ID 702**: `lie2standup` - Levantar quando deitado

### **🚶 COMANDOS DE LOCOMOÇÃO (22) - Para Movimento**
**USO**: Sistema conversacional, navegação, movimentos direcionais

```
Comandos: Strings como "move_forward", "rotate_left_medium"
Tipo: G1MovementType.LOCOMOTION
Contexto: ConversationEngine, navegação autônoma
```

**Exemplos:**
- **"move_forward"**: Mover para frente
- **"rotate_left_medium"**: Girar à esquerda (velocidade média)
- **"circular_movement"**: Movimento circular complexo

---

## 🎭 Sistema Conversacional - Uso Correto

### **✅ MOVIMENTOS PERMITIDOS na Conversação:**

```python
# GESTOS DE BRAÇOS (IDs numéricos)
conversation_gestures = {
    "greeting": [26, 18],     # wave_above_head + high_five_opt
    "thinking": [32],         # right_hand_on_mouth
    "celebration": [15, 24],  # both_hands_up + ultraman_ray
    "love": [33, 13],        # right_hand_on_heart + blow_kiss_with_right_hand
}

# COMANDOS DE LOCOMOÇÃO (strings)
conversation_movements = {
    "move_forward": ["move_forward"],
    "turn_left": ["rotate_left_medium"],
    "dance": ["circular_movement"],
}
```

### **❌ MOVIMENTOS PROIBIDOS na Conversação:**

```python
# ESTADOS FSM - NÃO USAR NO SISTEMA CONVERSACIONAL!
forbidden_in_conversation = [0, 1, 2, 3, 4, 200, 702, 706]
# Estes são para controle direto do robô apenas
```

---

## 🔧 Implementação Técnica

### **ConversationEngine - Validação Automática:**

```python
# O sistema agora valida automaticamente
if (arm_movement and 
    arm_movement.movement_type == G1MovementType.ARM_GESTURE):
    # ✅ Executa movimento de braço
    execute_arm_gesture(movement_id)
else:
    # ❌ Ignora estados FSM
    logger.warning(f"Ignorando estado FSM {gesture} em contexto conversacional")
```

### **Uso Direto para Controle de Postura:**

```python
# Para controle direto do robô (fora da conversação)
def setup_robot_posture():
    client.ExecuteAction(0)   # Zero torque
    time.sleep(2)
    client.ExecuteAction(1)   # Damping
    time.sleep(2) 
    client.ExecuteAction(4)   # Get ready
    # etc...
```

---

## 📊 Estatísticas Atualizadas

### **TOTAL: 50 MOVIMENTOS**
- **🤚 Braços (Conversação)**: 20 movimentos
- **🚶 Estados FSM (Controle)**: 8 estados  
- **🚶 Locomoção (Conversação/Navegação)**: 22 comandos

### **SISTEMA CONVERSACIONAL: 42 MOVIMENTOS**
- **🤚 Gestos de Braços**: 20 (IDs 1, 11-35, 99)
- **🚶 Comandos de Locomoção**: 22 (strings)
- **❌ Estados FSM Excluídos**: 8 (IDs 0-4, 200, 702, 706)

---

## 🎯 Casos de Uso Práticos

### **1. Durante Conversação Normal:**
```python
# ✅ Correto - Usar gestos de braços
user_input = "Olá, como você está?"
response_gestures = [26, 18]  # wave + high_five

# ✅ Correto - Usar locomoção se necessário
user_input = "Pode vir aqui?"
response_gestures = ["move_forward"]

# ❌ Incorreto - NÃO usar estados FSM
# response_gestures = [1, 4]  # NUNCA FAZER ISSO!
```

### **2. Setup/Controle Direto do Robô:**
```python
# ✅ Correto - Usar estados FSM para controle
def prepare_robot():
    execute_fsm_state(1)  # Damping
    execute_fsm_state(4)  # Get ready
    
# ✅ Correto - Usar gestos para teste
def test_robot_gestures():
    execute_arm_movement(99)  # Relax
    execute_arm_movement(26)  # Wave
    execute_arm_movement(99)  # Relax
```

### **3. Navegação Autônoma:**
```python
# ✅ Correto - Usar comandos de locomoção
def navigate_to_target():
    execute_locomotion("move_forward")
    execute_locomotion("rotate_right_medium") 
    execute_locomotion("move_forward")
    execute_locomotion("stop_movement")
```

---

## ⚠️ Regras Importantes

### **DO's (Fazer):**
1. **Usar gestos de braços** para expressão durante conversação
2. **Usar comandos de locomoção** para movimento durante conversação  
3. **Usar estados FSM** apenas para controle direto do robô
4. **Sempre relaxar braços** (ID 99) entre gestos
5. **Validar tipo de movimento** antes de executar

### **DON'Ts (Não Fazer):**
1. **❌ NÃO usar estados FSM** no sistema conversacional
2. **❌ NÃO misturar** controle direto com conversação
3. **❌ NÃO esquecer** de relaxar braços entre movimentos
4. **❌ NÃO executar** movimentos sem validação de tipo
5. **❌ NÃO usar** IDs de estado (0-4, 200, 702, 706) em gestos

---

## 🚀 Próximos Passos

1. **✅ Sistema conversacional atualizado** - Estados FSM removidos
2. **✅ Validação automática implementada** - Tipo checking
3. **✅ Documentação completa** - Guia de uso claro
4. **🎯 Teste em produção** - Validar comportamento correto

**Sistema agora está corretamente organizado para uso em produção!** 🤖✨
