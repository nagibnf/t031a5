# Lições Aprendidas: Testes de Dança em Baixo Nível G1

## 📋 Resumo Executivo

Durante os testes de dança em baixo nível com o Unitree G1, confirmamos que o robô é capaz de executar movimentos coordenados complexos usando controle DDS direto. Estas lições são valiosas para entender as capacidades avançadas do G1, mesmo que não sejam aplicáveis ao projeto t031a5.

## 🎯 Capacidades Confirmadas

### ✅ Dança Básica (test_g1_dance_low_level.py)
- **Movimentos**: Quadril + Braços coordenados
- **Duração**: 5 segundos (1s por movimento)
- **Gains**: Kp/Kd padrão (60/1 para pernas, 40/1 para braços)
- **Resultado**: ✅ **FUNCIONOU PERFEITAMENTE**

### ✅ Dança Suave com Pernas (test_g1_dance_smooth_with_legs.py)
- **Movimentos**: Quadril + Braços + Pernas coordenados
- **Duração**: 10 segundos (2s por movimento)
- **Gains**: Kp/Kd reduzidos (40/0.8 para pernas, 30/0.8 para braços)
- **Resultado**: ✅ **FUNCIONOU PERFEITAMENTE**

## 🔧 Configurações Técnicas

### Gains para Controle Suave
```python
# Gains reduzidos para movimentos suaves
Kp = [
    40, 40, 40, 60, 30, 30,      # legs - mais suave
    40, 40, 40, 60, 30, 30,      # legs - mais suave
    40, 30, 30,                  # waist - mais suave
    30, 30, 30, 30,  30, 30, 30, # arms - mais suave
    30, 30, 30, 30,  30, 30, 30  # arms - mais suave
]

Kd = [
    0.8, 0.8, 0.8, 1.5, 0.8, 0.8,     # legs - mais suave
    0.8, 0.8, 0.8, 1.5, 0.8, 0.8,     # legs - mais suave
    0.8, 0.8, 0.8,                     # waist - mais suave
    0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, # arms - mais suave
    0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8  # arms - mais suave
]
```

### Juntas Utilizadas
```python
class G1JointIndex:
    # Waist
    WaistYaw = 12
    
    # Arms
    LeftShoulderPitch = 15
    LeftElbow = 18
    RightShoulderPitch = 22
    RightElbow = 25
    
    # Legs
    LeftHipPitch = 0
    LeftKnee = 3
    RightHipPitch = 6
    RightKnee = 9
```

## 📊 Evidências de Funcionamento

### IMU RPY Changes
- **Dança Básica**: Mudanças significativas em Roll, Pitch e Yaw
- **Dança Suave**: Mudanças mais graduais e controladas
- **Estabilidade**: Robô manteve equilíbrio durante toda a dança

### Sequências de Movimento
1. **Balançar Quadril**: Movimento horizontal suave
2. **Levantar Pernas**: Movimento vertical coordenado
3. **Balançar Braços**: Movimento oscilatório oposto
4. **Dança Completa**: Todos os movimentos coordenados
5. **Retorno Neutro**: Volta suave à posição inicial

## 🚫 Limitações para t031a5

### Por que não aplicável:
1. **Complexidade**: Controle de baixo nível muito complexo
2. **Risco**: Movimentos podem ser instáveis
3. **Manutenção**: Código difícil de manter
4. **Foco**: t031a5 deve usar APIs de alto nível

### Alternativas Recomendadas:
- Usar `G1ArmActionClient` para movimentos de braço
- Usar `LocoClient` para locomoção
- Usar FSM states para mudanças de postura

## 📚 Arquivos de Referência

### Testes Criados:
- `test_g1_dance_low_level.py` - Dança básica
- `test_g1_dance_smooth_with_legs.py` - Dança suave com pernas

### Exemplos Base:
- `unitree_sdk2_python/example/g1/low_level/g1_low_level_example.py`
- `unitree_sdk2_python/example/g1/high_level/g1_arm5_sdk_dds_example.py`

## 🎯 Conclusões

### ✅ O que funciona:
- Controle DDS de baixo nível
- Movimentos coordenados complexos
- Dança com múltiplas juntas
- Controle de gains para suavidade

### ❌ O que não usar no t031a5:
- Controle direto de motores
- Movimentos de baixo nível
- Gains personalizados
- Sequências complexas de dança

### 📋 Para o futuro:
- Manter conhecimento para projetos avançados
- Usar apenas APIs de alto nível no t031a5
- Focar em funcionalidades práticas e seguras

## 🔄 Próximos Passos

1. **Limpar testes**: Mover para pasta de arquivo
2. **Documentar**: Manter esta documentação
3. **Focar t031a5**: Voltar às APIs de alto nível
4. **Aplicar lições**: Usar conhecimento em projetos futuros

---

**Data**: $(date)  
**Status**: ✅ Concluído  
**Aplicabilidade**: ❌ Não aplicável ao t031a5  
**Valor**: 🎯 Alto para conhecimento técnico
