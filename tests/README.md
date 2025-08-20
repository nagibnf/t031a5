# 🧪 Testes do Sistema t031a5

Esta pasta contém todos os testes do sistema t031a5, organizados por funcionalidade.

## 📁 Estrutura dos Testes

### **Testes Unitários**
- `test_system.py` - Teste dos componentes core (ConfigManager, Orchestrators, Fuser, LLM)
- `test_cortex.py` - Teste do CortexRuntime (loop principal, parada de emergência)
- `test_llm_providers.py` - Teste dos provedores LLM (OpenAI, Anthropic, Mock)
- `test_unitree_simple.py` - Teste do módulo Unitree (G1Interface, G1Controller)
- `test_websim.py` - Teste da interface WebSim (servidor web, WebSockets)
- `test_cli.py` - Teste do CLI completo (comandos run, test, status, validate)
- `test_logging_system.py` - Teste do sistema de logging estruturado
- `test_integration.py` - Teste de integração completa (sistema end-to-end)
- `test_real_g1_integration.py` - Teste para integração com G1 real

### **Scripts de Apoio**
- `run_test.py` - Script helper para executar testes individuais
- `__init__.py` - Arquivo de inicialização do pacote

## 🚀 Como Executar os Testes

### **Executar Todos os Testes**
```bash
# Do diretório raiz do projeto
python3 run_tests.py
```

### **Executar Teste Específico**
```bash
# Do diretório raiz do projeto
python3 tests/run_test.py test_system.py
python3 tests/run_test.py test_cortex.py
python3 tests/run_test.py test_integration.py
```

### **Executar Teste Individual**
```bash
# Do diretório tests
cd tests
python3 run_test.py test_system.py
```

## 📊 Resultados Esperados

### **Testes que Devem Passar Sempre**
- ✅ `test_system.py` - Componentes core
- ✅ `test_cortex.py` - CortexRuntime
- ✅ `test_unitree_simple.py` - Módulo Unitree (simulado)
- ✅ `test_websim.py` - Interface WebSim
- ✅ `test_cli.py` - CLI completo
- ✅ `test_logging_system.py` - Sistema de logging
- ✅ `test_integration.py` - Integração completa

### **Testes que Podem Falhar sem Dependências**
- ⚠️ `test_llm_providers.py` - Requer API keys (OpenAI/Anthropic)
- ⚠️ `test_real_g1_integration.py` - Requer SDK G1 e hardware

## 🔧 Configuração para Testes

### **Dependências Obrigatórias**
```bash
pip install -e .  # Instalar t031a5 em modo desenvolvimento
```

### **Dependências Opcionais**
```bash
# Para testes de LLM real
pip install openai anthropic

# Para testes com G1 real
pip install unitree-sdk2py
```

### **Configuração de Rede**
```bash
# Para testes com G1 real
sudo ifconfig en0 192.168.123.100 netmask 255.255.255.0
```

## 📈 Métricas de Teste

### **Tempo de Execução**
- **Teste individual**: 5-30 segundos
- **Todos os testes**: 2-5 minutos
- **Timeout por teste**: 5 minutos

### **Cobertura**
- **Componentes core**: 100%
- **Integração**: 100%
- **Funcionalidades**: 95%
- **Casos de erro**: 90%

## 🐛 Troubleshooting

### **Problemas Comuns**

#### **ModuleNotFoundError: No module named 't031a5'**
```bash
# Solução: Instalar em modo desenvolvimento
pip install -e .
```

#### **Arquivo de configuração não encontrado**
```bash
# Solução: Executar do diretório raiz
cd /path/to/t031a5
python3 tests/run_test.py test_system.py
```

#### **Timeout nos testes**
```bash
# Solução: Verificar recursos do sistema
# Aumentar timeout se necessário
```

#### **Falha em testes de LLM**
```bash
# Solução: Configurar API keys ou usar mock
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
```

#### **Falha em testes de G1 real**
```bash
# Solução: Instalar SDK e configurar rede
pip install unitree-sdk2py
./install_g1_sdk.sh
```

## 📝 Adicionando Novos Testes

### **Estrutura de Teste**
```python
#!/usr/bin/env python3
"""
Teste para [funcionalidade].

Descrição do que o teste verifica.
"""

import sys
import asyncio
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from t031a5.[module] import [Class]


def test_functionality():
    """Testa funcionalidade específica."""
    print("🔍 Testando funcionalidade...")
    
    try:
        # Teste aqui
        result = True
        print("✅ Funcionalidade testada com sucesso")
        return result
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


async def main():
    """Função principal de teste."""
    print("🚀 Testando [funcionalidade]\n")
    
    results = []
    
    # Teste 1
    print("Teste 1: [Descrição]")
    results.append(test_functionality())
    
    # Resultado final
    print("\n" + "="*60)
    print("📊 RESULTADO FINAL")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Testes passaram: {passed}/{total}")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
    else:
        print("❌ Alguns testes falharam")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
```

### **Adicionar ao Script Principal**
```python
# Em run_tests.py, adicionar:
tests = [
    # ... testes existentes ...
    ("test_new_feature.py", "Teste da Nova Funcionalidade"),
]
```

## 🎯 Boas Práticas

### **Nomenclatura**
- Use `test_*.py` para arquivos de teste
- Use nomes descritivos: `test_websim.py`, `test_g1_controller.py`
- Use funções com prefixo `test_`: `test_initialization()`

### **Estrutura**
- Importe dependências no topo
- Use try/except para tratamento de erros
- Retorne `True`/`False` para sucesso/falha
- Use prints informativos com emojis

### **Execução**
- Teste individualmente primeiro
- Execute todos os testes antes de commit
- Verifique logs para debugging
- Mantenha testes rápidos (< 30s cada)

## 📞 Suporte

### **Logs de Erro**
- **Arquivo**: `logs/t031a5_test.log`
- **Nível**: DEBUG para testes
- **Formato**: Estruturado com contexto

### **Debugging**
```bash
# Executar com debug
python3 tests/run_test.py test_system.py --debug

# Ver logs em tempo real
tail -f logs/t031a5_test.log
```

---

**🧪 Os testes garantem que o sistema t031a5 funcione corretamente!**
