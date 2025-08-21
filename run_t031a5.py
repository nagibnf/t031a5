#!/usr/bin/env python3
"""
🚀 SCRIPT DE EXECUÇÃO PRINCIPAL - SISTEMA t031a5
Wrapper simples para executar o sistema principal
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Executa o sistema principal."""
    
    print("🤖 Iniciando Sistema t031a5...")
    
    # Verifica se estamos na Jetson ou Mac
    main_script = Path("t031a5_main.py")
    
    if not main_script.exists():
        print("❌ Arquivo principal não encontrado!")
        return 1
    
    try:
        # Executa o sistema principal
        result = subprocess.run([sys.executable, str(main_script)], check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro na execução: {e}")
        return e.returncode
    except KeyboardInterrupt:
        print("\n🛑 Sistema interrompido pelo usuário")
        return 0

if __name__ == "__main__":
    sys.exit(main())
