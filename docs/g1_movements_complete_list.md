# Lista Completa de Movimentos G1 - Resultados dos Testes

## 🎯 Resumo dos Testes

Durante os testes extensivos com o robô Unitree G1, testamos uma ampla gama de IDs de movimento para identificar quais estão disponíveis e funcionais no firmware atual.

## ✅ **MOVIMENTOS CONFIRMADOS (FUNCIONANDO)**

### 🤚 **Movimentos de Braços (18 movimentos funcionais)**

| ID | Nome Real | Descrição | Status | Observações |
|---|---|---|---|---|
| **1** | **turn_back_wave** | Vira para trás e acena | ✅ **FUNCIONANDO** | Movimento de locomoção + gesto |
| **11** | **blow_kiss_with_both_hands_50hz** | Beijo com duas mãos | ✅ **FUNCIONANDO** | Gesto de beijo |
| **12** | **blow_kiss_with_left_hand** | Beijo com mão esquerda | ✅ **FUNCIONANDO** | Gesto de beijo |
| **13** | **blow_kiss_with_right_hand** | Beijo com mão direita | ✅ **FUNCIONANDO** | Gesto de beijo |
| **15** | **both_hands_up** | Duas mãos para cima | ✅ **FUNCIONANDO** | Gesto de celebração |
| **17** | **clamp** | Aplaudir | ✅ **FUNCIONANDO** | Gesto de palmas |
| **18** | **high_five_opt** | Toca aqui | ✅ **FUNCIONANDO** | Gesto de cumprimento |
| **19** | **hug_opt** | Abraçar | ✅ **FUNCIONANDO** | Gesto de abraço |
| **22** | **refuse** | Recusar | ✅ **FUNCIONANDO** | Gesto de negação |
| **23** | **right_hand_up** | Mão direita para cima | ✅ **FUNCIONANDO** | Gesto de mão |
| **24** | **ultraman_ray** | Raio do Ultraman | ✅ **FUNCIONANDO** | Gesto especial |
| **25** | **wave_under_head** | Acenar abaixo da cabeça | ✅ **FUNCIONANDO** | Gesto de aceno |
| **26** | **wave_above_head** | Acenar acima da cabeça | ✅ **FUNCIONANDO** | Gesto de aceno |
| **27** | **shake_hand_opt** | Apertar mão | ✅ **FUNCIONANDO** | Gesto de cumprimento |
| **31** | **extend_right_arm_forward** | Estender braço direito para frente | ✅ **FUNCIONANDO** | Gesto de apontar |
| **32** | **right_hand_on_mouth** | Mão direita na boca | ✅ **FUNCIONANDO** | Gesto de silêncio |
| **33** | **right_hand_on_heart** | Mão direita no coração | ✅ **FUNCIONANDO** | Gesto de amor |
| **34** | **both_hands_up_deviate_right** | Duas mãos para cima desviando direita | ✅ **FUNCIONANDO** | Gesto de celebração |
| **35** | **emphasize** | Enfatizar | ✅ **FUNCIONANDO** | Gesto de ênfase |
| **99** | **release_arm** | Liberar braços | ✅ **FUNCIONANDO** | Relaxamento essencial |

### 🚶 **Estados FSM (Finite State Machine)**

| ID | Nome | Descrição | Status | Observações |
|---|---|---|---|---|
| **0** | **Zero Torque** | Torque zero | ✅ **FUNCIONANDO** | Estado seguro |
| **1** | **Damping** | Amortecimento | ✅ **FUNCIONANDO** | Estado estável |
| **2** | **Squat** | Agachar | ✅ **FUNCIONANDO** | Postura baixa |
| **3** | **Seat** | Sentar | ✅ **FUNCIONANDO** | Postura sentada |
| **4** | **Get Ready** | Preparar | ✅ **FUNCIONANDO** | Estado inicial |
| **5** | **Vazio** | Estado vazio | ✅ **FUNCIONANDO** | Sem ação |
| **6** | **Vazio** | Estado vazio | ✅ **FUNCIONANDO** | Sem ação |
| **200** | **Start** | Iniciar | ✅ **FUNCIONANDO** | Estado ativo |
| **702** | **Lie2StandUp** | Deitar para levantar | ✅ **FUNCIONANDO** | Transição |
| **706** | **Squat2StandUp** | Agachar para levantar | ✅ **FUNCIONANDO** | Transição |

### 🚶 **Comandos de Locomoção**

| Comando | Nome | Descrição | Status | Observações |
|---|---|---|---|---|
| **damp** | Damping | Amortecimento | ✅ **FUNCIONANDO** | Funciona em qualquer estado |
| **sit** | Sit | Sentar | ✅ **FUNCIONANDO** | Postura sentada |
| **highstand** | High Stand | Postura alta | ✅ **FUNCIONANDO** | Postura ereta |
| **lowstand** | Low Stand | Postura baixa | ✅ **FUNCIONANDO** | Postura agachada |

## ❌ **MOVIMENTOS NÃO DISPONÍVEIS (ERRO 7402/7404)**

### 🤚 **Movimentos de Braços (NÃO FUNCIONAM)**

| ID | Nome | Descrição | Status | Erro |
|---|---|---|---|---|
| **10** | **unknown** | Movimento desconhecido | ❌ **ERRO 7402** | Status 7402 |
| **14** | **unknown** | Movimento desconhecido | ❌ **ERRO 7402** | Status 7402 |
| **16** | **unknown** | Movimento desconhecido | ❌ **ERRO 7402** | Status 7402 |
| **20** | **unknown** | Movimento desconhecido | ❌ **ERRO 7402** | Status 7402 |
| **21** | **unknown** | Movimento desconhecido | ❌ **ERRO 7402** | Status 7402 |
| **28** | **unknown** | Movimento desconhecido | ❌ **ERRO 7402** | Status 7402 |
| **29** | **unknown** | Movimento desconhecido | ❌ **ERRO 7402** | Status 7402 |
| **30** | **unknown** | Movimento desconhecido | ❌ **ERRO 7402** | Status 7402 |
| **36** | **unknown** | Movimento desconhecido | ❌ **ERRO 7402** | Status 7402 |
| **37** | **unknown** | Movimento desconhecido | ❌ **ERRO 7402** | Status 7402 |
| **38** | **unknown** | Movimento desconhecido | ❌ **ERRO 7402** | Status 7402 |
| **39** | **unknown** | Movimento desconhecido | ❌ **ERRO 7402** | Status 7402 |
| **40** | **unknown** | Movimento desconhecido | ❌ **ERRO 7402** | Status 7402 |
| **41** | **unknown** | Movimento desconhecido | ❌ **ERRO 7402** | Status 7402 |
| **42** | **unknown** | Movimento desconhecido | ❌ **ERRO 7402** | Status 7402 |
| **43** | **unknown** | Movimento desconhecido | ❌ **ERRO 7402** | Status 7402 |
| **44** | **unknown** | Movimento desconhecido | ❌ **ERRO 7402** | Status 7402 |
| **45** | **unknown** | Movimento desconhecido | ❌ **ERRO 7402** | Status 7402 |
| **46** | **unknown** | Movimento desconhecido | ❌ **ERRO 7402** | Status 7402 |
| **47** | **unknown** | Movimento desconhecido | ❌ **ERRO 7402** | Status 7402 |
| **48** | **unknown** | Movimento desconhecido | ❌ **ERRO 7402** | Status 7402 |
| **49** | **unknown** | Movimento desconhecido | ❌ **ERRO 7402** | Status 7402 |
| **50** | **unknown** | Movimento desconhecido | ❌ **ERRO 7402** | Status 7402 |

### 🚶 **Comandos de Locomoção (NÃO FUNCIONAM)**

| Comando | Nome | Descrição | Status | Erro |
|---|---|---|---|---|
| **start** | Start | Iniciar | ❌ **ERRO** | Precisa Main Operation Control |
| **zerotorque** | Zero Torque | Torque zero | ❌ **ERRO** | Estado incorreto |

## 🔍 **TESTES REALIZADOS**

### 📊 **Metodologia de Teste**
1. **Estado do Robô**: Main Operation Control
2. **Sequência**: Relax (ID 99) → Movimento → Relax (ID 99)
3. **Timeout**: 10 segundos por movimento
4. **Repetições**: 3 tentativas por ID
5. **Logs**: Registro completo de erros

### 📈 **Estatísticas dos Testes**
- **Total de IDs testados**: 41 (IDs 1, 10-50)
- **IDs funcionando**: 18 (44%)
- **IDs com erro 7402**: 23 (56%)
- **Tempo total de teste**: ~2 horas
- **Robô**: Unitree G1 (firmware atual)

### 🎯 **Padrão de Execução Confirmado**
```python
# Sequência que funciona:
1. ExecuteAction(99)  # Relaxar braços
2. time.sleep(2.0)    # Aguardar
3. ExecuteAction(ID)  # Executar movimento
4. time.sleep(3.0)    # Aguardar movimento
5. ExecuteAction(99)  # Relaxar novamente
```

## 🚀 **RECOMENDAÇÕES DE USO**

### ✅ **Movimentos Recomendados**
1. **ID 32**: Para gestos de comunicação (Right Hand on Mouth)
2. **ID 99**: Para relaxamento entre movimentos (Release Arm)
3. **IDs 11-35**: Para gestos expressivos (Kiss, Wave, Clap, etc.)
4. **IDs 0-7, 200, 702, 706**: Para controle de estado FSM
5. **Comandos damp, sit, highstand, lowstand**: Para locomoção

### ⚠️ **Movimentos a Evitar**
- **IDs 10, 14, 16, 20-21, 28-30, 36-50**: Todos retornam erro 7402
- **Comandos start, zerotorque**: Não funcionam no estado atual

### 🔧 **Estratégias de Fallback**
1. **Movimento não disponível**: Usar ID 32 como alternativa
2. **Locomoção**: Usar damp, sit, highstand, lowstand
3. **Estados**: Usar IDs FSM para controle de postura
4. **Relaxamento**: Sempre usar ID 99 entre movimentos

## 📋 **CONFIGURAÇÃO NO SISTEMA t031a5**

### ⚙️ **Configuração Atual (config/g1_real.json5)**
```json5
"movements": {
  "confirmed": {
    "32": {
      "name": "right_hand_on_mouth",
      "description": "Mão direita na boca",
      "duration": 3.0,
      "requires_relax": true
    },
    "99": {
      "name": "release_arm",
      "description": "Liberar braços",
      "duration": 1.0,
      "is_relax": true
    },
    "11": {
      "name": "blow_kiss_with_both_hands_50hz",
      "description": "Beijo com duas mãos",
      "duration": 3.0,
      "requires_relax": true
    },
    "12": {
      "name": "blow_kiss_with_left_hand",
      "description": "Beijo com mão esquerda",
      "duration": 3.0,
      "requires_relax": true
    },
    "13": {
      "name": "blow_kiss_with_right_hand",
      "description": "Beijo com mão direita",
      "duration": 3.0,
      "requires_relax": true
    },
    "15": {
      "name": "both_hands_up",
      "description": "Duas mãos para cima",
      "duration": 3.0,
      "requires_relax": true
    },
    "17": {
      "name": "clamp",
      "description": "Aplaudir",
      "duration": 3.0,
      "requires_relax": true
    },
    "18": {
      "name": "high_five_opt",
      "description": "Toca aqui",
      "duration": 3.0,
      "requires_relax": true
    },
    "19": {
      "name": "hug_opt",
      "description": "Abraçar",
      "duration": 3.0,
      "requires_relax": true
    },
    "22": {
      "name": "refuse",
      "description": "Recusar",
      "duration": 3.0,
      "requires_relax": true
    },
    "23": {
      "name": "right_hand_up",
      "description": "Mão direita para cima",
      "duration": 3.0,
      "requires_relax": true
    },
    "24": {
      "name": "ultraman_ray",
      "description": "Raio do Ultraman",
      "duration": 3.0,
      "requires_relax": true
    },
    "25": {
      "name": "wave_under_head",
      "description": "Acenar abaixo da cabeça",
      "duration": 3.0,
      "requires_relax": true
    },
    "26": {
      "name": "wave_above_head",
      "description": "Acenar acima da cabeça",
      "duration": 3.0,
      "requires_relax": true
    },
    "27": {
      "name": "shake_hand_opt",
      "description": "Apertar mão",
      "duration": 3.0,
      "requires_relax": true
    },
    "31": {
      "name": "extend_right_arm_forward",
      "description": "Estender braço direito para frente",
      "duration": 3.0,
      "requires_relax": true
    },
    "33": {
      "name": "right_hand_on_heart",
      "description": "Mão direita no coração",
      "duration": 3.0,
      "requires_relax": true
    },
    "34": {
      "name": "both_hands_up_deviate_right",
      "description": "Duas mãos para cima desviando direita",
      "duration": 3.0,
      "requires_relax": true
    },
    "35": {
      "name": "emphasize",
      "description": "Enfatizar",
      "duration": 3.0,
      "requires_relax": true
    }
  },
  "fsm_states": {
    "0": {
      "name": "Zero Torque",
      "description": "Torque zero - estado seguro",
      "type": "fsm"
    },
    "1": {
      "name": "Damping",
      "description": "Amortecimento - estado estável",
      "type": "fsm"
    },
    "2": {
      "name": "Squat",
      "description": "Agachar - postura baixa",
      "type": "fsm"
    },
    "3": {
      "name": "Seat",
      "description": "Sentar - postura sentada",
      "type": "fsm"
    },
    "4": {
      "name": "Get Ready",
      "description": "Preparar - estado inicial",
      "type": "fsm"
    },
    "200": {
      "name": "Start",
      "description": "Iniciar - estado ativo",
      "type": "fsm"
    },
    "702": {
      "name": "Lie2StandUp",
      "description": "Deitar para levantar - transição",
      "type": "fsm"
    },
    "706": {
      "name": "Squat2StandUp",
      "description": "Agachar para levantar - transição",
      "type": "fsm"
    }
  },
  "locomotion": {
    "damp": {
      "name": "Damping",
      "description": "Amortecimento",
      "type": "locomotion"
    },
    "sit": {
      "name": "Sit",
      "description": "Sentar",
      "type": "locomotion"
    },
    "highstand": {
      "name": "High Stand",
      "description": "Postura alta",
      "type": "locomotion"
    },
    "lowstand": {
      "name": "Low Stand",
      "description": "Postura baixa",
      "type": "locomotion"
    }
  },
  "statistics": {
    "total_tested": 41,
    "working": 18,
    "not_working": 23,
    "success_rate": "44%"
  }
}
```

### 🎯 **Uso no Código**
```python
# Movimentos confirmados
available_movements = {
    32: "right_hand_on_mouth",
    99: "release_arm",
    11: "blow_kiss_with_both_hands_50hz",
    12: "blow_kiss_with_left_hand",
    13: "blow_kiss_with_right_hand",
    15: "both_hands_up",
    17: "clamp",
    18: "high_five_opt",
    19: "hug_opt",
    22: "refuse",
    23: "right_hand_up",
    24: "ultraman_ray",
    25: "wave_under_head",
    26: "wave_above_head",
    27: "shake_hand_opt",
    31: "extend_right_arm_forward",
    33: "right_hand_on_heart",
    34: "both_hands_up_deviate_right",
    35: "emphasize"
}

# Executar movimento seguro
await controller.execute_gesture(32, emotion=G1Emotion.HAPPY)
```

## 🔮 **PRÓXIMOS PASSOS**

### 🎯 **Desenvolvimento de Novos Movimentos**
1. **Low-level control**: Usar DDS para movimentos customizados
2. **Interpolação**: Transições suaves entre posições
3. **Sequências**: Combinações de movimentos básicos
4. **Gestos complexos**: Implementação via cinemática

### 📊 **Monitoramento**
- **Firmware updates**: Verificar novos movimentos
- **SDK updates**: Novas APIs disponíveis
- **Documentação**: Atualizar lista conforme descobertas

---

## 📊 **RESUMO FINAL**

### ✅ **FUNCIONANDO (28 movimentos)**
- **Braços**: 18 movimentos (IDs 1, 11-35, 99)
- **Estados FSM**: 10 estados (IDs 0-7, 200, 702, 706)
- **Locomoção**: 4 comandos (damp, sit, highstand, lowstand)

### ❌ **NÃO FUNCIONAM (23 movimentos)**
- **IDs 10, 14, 16, 20-21, 28-30, 36-50**: Erro 7402
- **Comandos start, zerotorque**: Não funcionam no estado atual

### 🎯 **RECOMENDAÇÃO**
**Usar os 28 movimentos confirmados** para garantir funcionamento estável do sistema t031a5.

---

*Última atualização: Testes completos realizados com Unitree G1 - 18 movimentos de braço + 10 estados FSM + 4 locomoção*
