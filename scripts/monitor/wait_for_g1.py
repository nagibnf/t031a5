#!/usr/bin/env python3
"""
Script de Monitoramento - Aguardar G1 Ligar

Este script monitora quando o G1 estiver ligado e conectado,
e então executa automaticamente o teste integrado.
"""

import time
import subprocess
import sys
from pathlib import Path

def check_g1_connection():
    """Verifica se o G1 está conectado."""
    try:
        # Tentar ping para o IP do G1
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '2', '192.168.123.161'],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False

def check_interface_en11():
    """Verifica se a interface en11 está ativa."""
    try:
        result = subprocess.run(
            ['ifconfig', 'en11'],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False

def run_g1_test():
    """Executa o teste integrado do G1."""
    print("\n🚀 EXECUTANDO TESTE INTEGRADO...")
    
    try:
        # Executar teste integrado
        result = subprocess.run([
            './venv/bin/python', 'test_t031a5_integrated.py'
        ], capture_output=False)
        
        if result.returncode == 0:
            print("✅ Teste integrado concluído com sucesso!")
        else:
            print("❌ Teste integrado falhou")
            
    except Exception as e:
        print(f"❌ Erro ao executar teste: {e}")

def main():
    """Função principal."""
    print("🎯 MONITORAMENTO G1 - SISTEMA t031a5")
    print("=" * 50)
    print("Aguardando G1 ligar e conectar...")
    print("Pressione Ctrl+C para parar\n")
    
    check_count = 0
    last_status = False
    
    try:
        while True:
            check_count += 1
            
            # Verificar conexão
            g1_connected = check_g1_connection()
            interface_active = check_interface_en11()
            
            # Status atual
            status = g1_connected and interface_active
            
            # Mostrar status
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] Verificação #{check_count:03d}")
            print(f"  🌐 G1 Conectado: {'✅' if g1_connected else '❌'}")
            print(f"  🔌 Interface en11: {'✅' if interface_active else '❌'}")
            
            # Se status mudou
            if status != last_status:
                if status:
                    print(f"\n🎉 G1 DETECTADO! Iniciando teste...")
                    run_g1_test()
                    break
                else:
                    print(f"  ⚠️  G1 desconectado")
            
            last_status = status
            
            # Aguardar antes da próxima verificação
            print(f"  ⏳ Aguardando 10 segundos...\n")
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoramento interrompido pelo usuário")
        print("Para executar teste manualmente:")
        print("  python test_t031a5_integrated.py")

if __name__ == "__main__":
    main()
