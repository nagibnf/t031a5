# 📦 Arquivo - Testes e Experimentos

## 📋 O que foi arquivado

Este diretório contém todos os testes experimentais e avançados que foram realizados durante o desenvolvimento do projeto t031a5. Estes arquivos são mantidos para referência técnica e conhecimento futuro.

## 🗂️ Estrutura do Arquivo

### 📁 dance_tests/
**Testes de dança em baixo nível DDS**
- `test_g1_dance_low_level.py` - Dança básica (quadril + braços)
- `test_g1_dance_smooth_with_legs.py` - Dança suave com pernas

**Resultado**: ✅ **FUNCIONOU PERFEITAMENTE**
- Confirma que G1 pode dançar em baixo nível
- Movimentos coordenados complexos possíveis
- **NÃO aplicável ao t031a5** (muito complexo)

### 📁 hip_tests/
**Testes de movimento do quadril**
- `test_g1_hip_movement_simple.py` - Teste simples de quadril
- `test_g1_waist_yaw_*.py` - Testes específicos WAIST_YAW
- `test_g1_joints_debug_mode.py` - Testes em modo debugging

**Resultado**: ❌ **QUADRIL LIMITADO**
- G1 tem apenas 1 DOF no quadril (WAIST_YAW)
- Movimento limitado a rotação horizontal
- **Aplicável ao t031a5** (usar WAIST_YAW quando necessário)

### 📁 audio_tests/
**Testes de áudio e TTS**
- Testes de TTS nativo
- Testes de reprodução de áudio
- Testes de controle de speaker

**Resultado**: ✅ **ÁUDIO FUNCIONANDO**
- TTS nativo em português (speaker_id 1)
- Reprodução de WAV 16kHz mono
- **Aplicável ao t031a5** (já implementado)

## 🎯 Lições Aprendidas

### ✅ O que funciona:
1. **Controle DDS de baixo nível** - Muito poderoso
2. **Dança coordenada** - Movimentos complexos possíveis
3. **TTS nativo** - Funciona bem em português
4. **Reprodução de áudio** - WAV 16kHz mono

### ❌ O que não usar no t031a5:
1. **Controle de baixo nível** - Muito complexo
2. **Dança avançada** - Não aplicável
3. **Gains personalizados** - Risco de instabilidade

### 📋 Para o futuro:
1. **Projetos avançados** - Usar conhecimento de baixo nível
2. **Customização** - Movimentos personalizados
3. **Pesquisa** - Experimentos com controle direto

## 🔧 Configurações Técnicas

### Gains para Movimentos Suaves
```python
Kp = [40, 40, 40, 60, 30, 30, ...]  # Reduzidos para suavidade
Kd = [0.8, 0.8, 0.8, 1.5, 0.8, 0.8, ...]  # Damping reduzido
```

### Juntas Importantes
```python
WaistYaw = 12          # Única junta do quadril
LeftShoulderPitch = 15 # Braço esquerdo
RightShoulderPitch = 22 # Braço direito
LeftHipPitch = 0       # Perna esquerda
RightHipPitch = 6      # Perna direita
```

## 📚 Documentação Relacionada

- `docs/lessons_learned_g1_dance_tests.md` - Lições detalhadas
- `docs/g1_movements_complete_list.md` - Lista de movimentos
- `PROJECT_STATUS_FINAL.md` - Status final do projeto

## 🚀 Como Usar (Se Necessário)

### Para Executar Testes de Dança:
```bash
cd archive/dance_tests/
python test_g1_dance_low_level.py
python test_g1_dance_smooth_with_legs.py
```

### Para Executar Testes de Quadril:
```bash
cd archive/hip_tests/
python test_g1_hip_movement_simple.py
```

### Para Executar Testes de Áudio:
```bash
cd archive/audio_tests/
python test_g1_audio_*.py
```

## ⚠️ Avisos Importantes

1. **Risco**: Testes de baixo nível podem ser instáveis
2. **Complexidade**: Código avançado, difícil de manter
3. **Aplicabilidade**: Não usar no t031a5
4. **Conhecimento**: Manter para projetos futuros

---

**Status**: 📦 **Arquivado para referência**  
**Aplicabilidade**: ❌ **Não aplicável ao t031a5**  
**Valor**: 🎯 **Alto para conhecimento técnico**  
**Data**: $(date)
