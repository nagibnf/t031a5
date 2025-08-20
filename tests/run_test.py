#!/usr/bin/env python3
"""
Script helper para executar testes individuais.

Adiciona o path correto e executa o teste especificado.
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório src ao path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Muda para o diretório raiz do projeto
os.chdir(project_root)

# Executa o teste especificado
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 run_test.py <test_file>")
        sys.exit(1)
    
    test_file = sys.argv[1]
    if not test_file.endswith('.py'):
        test_file += '.py'
    
    # Executa o teste
    test_path = Path(__file__).parent / test_file
    exec(open(test_path).read())
