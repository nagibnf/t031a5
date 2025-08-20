# G1 State Machine Guide - Instruções Eternas (CORRIGIDO)

## 📊 Diagrama de Estados do G1 - Análise Completa

### 🔄 Visão Geral dos Modos

O G1 possui **DOIS MODOS PRINCIPAIS**:
1. **Debug Mode** (Lado esquerdo) - Para diagnósticos
2. **Normal Mode** (Lado direito) - Operação normal

### 🎮 Transições por Controle (L2 + Botões) - CORRIGIDO

#### **Debug Mode**
- **Diagnostic Action** → **Damping**: `L2+B`
- **Diagnostic Action** → **Diagnostic Action**: `L2+A` (loop)
- **Damping** → **Zero Torque**: `L2+Y`
- **Damping** → **Diagnostic Action**: `L2+A`
- **Damping** → **Damping**: `L2+B` (loop)
- **Damping** → **Normal Mode Damping**: `L2+R2`
- **Zero Torque** → **Damping**: `L2+B`
- **Zero Torque** → **Zero Torque**: `L2+Y` (loop)
- **Zero Torque** → **Normal Mode Zero Torque**: `L2+R2`

#### **Normal Mode**
- **Power On** → **Zero Torque**: Automático
- **Zero Torque** → **Damping**: `L2+B`
- **Zero Torque** → **Main Operation Control**: `L2+R2`
- **Damping** → **Zero Torque**: `L2+Y`
- **Damping** → **Get Ready**: `L2+UP`
- **Damping** → **Main Operation Control**: `L2+R2`

### 🎯 Position Mode (Modo de Posição)

#### **Get Ready** (Estado Central)
- → **Squat**: `L2+UP`
- → **Take one's seat**: `L2+LEFT`
- → **Main Operation Control**: `R1+X` ⚠️ **CORREÇÃO IMPORTANTE**
- → **Damping**: `L2+B`

#### **Squat**
- → **Get Ready**: `L2+DOWN`
- → **Main Operation Control**: `L2+DOWN`
- → **Lying Position**: `L2+X`
- → **Squatting Position**: `L2+A`

#### **Take one's seat**
- → **Get Ready**: `L2+UP`
- → **Main Operation Control**: `L2+LEFT`
- → **Squat**: `L2+LEFT`
- → **Take one's seat**: `L2+DOWN` (loop)

### 🚀 Main Operation Control

**Ponto de entrada para comandos de alto nível:**
- **Zero Torque** → **Main Operation Control**: `L2+R2`
- **Damping** → **Main Operation Control**: `L2+R2`
- **Squat** → **Main Operation Control**: `L2+DOWN`
- **Get Ready** → **Main Operation Control**: `R1+X` ⚠️ **CORREÇÃO**
- **Take one's seat** → **Main Operation Control**: `L2+LEFT`
- **Lying Position** → **Main Operation Control**
- **Squatting Position** → **Main Operation Control**

## 🔧 Mapeamento FSM IDs vs Estados

| FSM ID | Estado | Descrição |
|--------|--------|-----------|
| 0 | Zero Torque | Robô "mole", sem torque |
| 1 | Damping | Robô com amortecimento |
| 2 | Squat | Posição agachada |
| 3 | Take one's seat | Posição sentada |
| 4 | Get Ready | **ESTADO DE TRANSIÇÃO** - não suporta braços |
| 200 | Start | Iniciar operação |
| 702 | Lie2StandUp | Deitado para em pé |
| 706 | Squat2StandUp | Agachado para em pé |

## ⚠️ REGRAS CRÍTICAS (CORRIGIDAS)

### 1. **Sequência de Inicialização CORRETA**
```
Power On → Zero Torque → Damping → Get Ready → R1+X → Main Operation Control → LowStanding automático
```

### 2. **Estados para Comandos de Braço**
- **APENAS** no estado **"Main Operation Control"**
- **NUNCA** funcionará em Get Ready (FSM 4)
- **Get Ready é apenas transição**, não suporta comandos de braço

### 3. **Estados para Locomoção**
- **Main Operation Control** é necessário para movimentos
- **LowStanding automático** quando entra em Main Operation Control

### 4. **Transições Seguras**
- Sempre aguardar conclusão da transição
- **Zero Torque** → **Damping**: 3s
- **Damping** → **Get Ready**: 5s
- **Get Ready** → **Main Operation Control** (R1+X): 2s
- **Main Operation Control** → **LowStanding**: automático

## 🎯 Comandos de Braço - Regras Específicas (CORRIGIDAS)

### **Estado Correto: Main Operation Control**
- O robô DEVE estar em **Main Operation Control** para comandos de braço
- **Get Ready (FSM 4) NÃO suporta comandos de braço**
- **LowStanding é automático** quando entra em Main Operation Control

### **Sequência para Testar Braços:**
1. `FSM 0` (Zero Torque) - 3s
2. `FSM 1` (Damping) - 3s  
3. `FSM 4` (Get Ready) - 5s
4. **R1+X** para Main Operation Control - 2s
5. **AGORA** testar comandos de braço (LowStanding automático)

## 🚶 Comandos de Locomoção - Regras Específicas (CORRIGIDAS)

### **Estado Correto: Main Operation Control**
- **start** só funciona em Main Operation Control
- **zerotorque** só funciona em estados específicos
- **damp** funciona em qualquer estado
- **LowStanding automático** quando entra em Main Operation Control

### **Sequência para Locomoção:**
1. `FSM 0` (Zero Torque) - 3s
2. `FSM 1` (Damping) - 3s
3. `FSM 4` (Get Ready) - 5s
4. **R1+X** para Main Operation Control - 2s
5. **AGORA** testar locomoção (LowStanding automático)

## 📋 Checklist de Verificação (CORRIGIDO)

### ✅ Antes de Testar Braços:
- [ ] Robô em Main Operation Control?
- [ ] Aguardou 2s após R1+X?
- [ ] LowStanding ativado automaticamente?
- [ ] Verificou status do MotionSwitcher?

### ✅ Antes de Testar Locomoção:
- [ ] Robô em Main Operation Control?
- [ ] Aguardou 2s após R1+X?
- [ ] LowStanding ativado automaticamente?
- [ ] Verificou status do MotionSwitcher?

### ✅ Antes de Qualquer Comando:
- [ ] Não há obstáculos?
- [ ] Robô está estável?
- [ ] Bateria suficiente?

## 🔍 Verificação de Modo Atual (PROBLEMA IDENTIFICADO)

### **MotionSwitcher CheckMode()**
- Retorna: `{'form': '0', 'name': 'ai'}`
- **PROBLEMA**: `form` não indica estado FSM atual
- **PROBLEMA**: `name` indica modo do MotionSwitcher, não estado FSM
- **NECESSÁRIO**: Aprender como verificar estado FSM real

### **Interpretação INCORRETA (que eu fazia):**
- `form: '0'` = Zero Torque ❌ **ERRADO**
- `form: '1'` = Damping ❌ **ERRADO**  
- `form: '4'` = Get Ready ❌ **ERRADO**
- `name: 'ai'` = Modo AI ativo ✅ **CORRETO**

### **NECESSÁRIO APRENDER:**
- Como verificar estado FSM real
- Como interpretar corretamente o retorno do MotionSwitcher
- Como detectar quando está em Main Operation Control

## 🚨 Problemas Identificados (CORRIGIDOS)

### 1. **Comandos de braço não funcionam** - Status 7404
- **CAUSA**: Robô não está em Main Operation Control
- **SOLUÇÃO**: Seguir sequência: FSM 0 → FSM 1 → FSM 4 → R1+X

### 2. **Locomoção não funciona**
- **CAUSA**: Não está em Main Operation Control
- **SOLUÇÃO**: Transicionar para Main Operation Control com R1+X

### 3. **Verificação de modo incorreta** ⚠️ **PROBLEMA CRÍTICO**
- **CAUSA**: Não interpretando corretamente o retorno do MotionSwitcher
- **PROBLEMA**: Campo 'form' não indica estado FSM
- **SOLUÇÃO**: Aprender como verificar estado FSM real

### 4. **Sequência perigosa**
- **CAUSA**: Comandos sem respeitar tempos de transição
- **SOLUÇÃO**: Aguardar conclusão de cada comando

## 📝 Próximos Passos (CORRIGIDOS)

1. **Aprender como verificar estado FSM real** ⚠️ **CRÍTICO**
2. **Implementar sequência correta**: FSM 0 → FSM 1 → FSM 4 → R1+X
3. **Testar comandos de braço APENAS em Main Operation Control**
4. **Testar locomoção APENAS em Main Operation Control**
5. **Documentar tempos de transição reais**
6. **Entender LowStanding automático**

## 🎯 CORREÇÕES IMPORTANTES APRENDIDAS

1. **L2+L2 é para Debug Mode** - não para Get Ready
2. **R1+X é para Main Operation Control** - do Get Ready
3. **Main Operation Control → LowStanding automático**
4. **Get Ready (FSM 4) não suporta comandos de braço**
5. **MotionSwitcher não indica estado FSM real**
6. **Preciso aprender como verificar estado FSM real**
