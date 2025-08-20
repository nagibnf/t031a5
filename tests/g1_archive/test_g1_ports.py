#!/usr/bin/env python3
"""
Teste de portas no G1.
"""

import socket
import time

def test_port(ip, port, timeout=2):
    """Testa se uma porta está aberta."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

def scan_g1_ports():
    """Escaneia portas comuns no G1."""
    
    g1_ip = "192.168.123.161"
    
    # Portas comuns para testar
    common_ports = [
        8080,   # Porta atual
        8081,   # Alternativa comum
        8082,   # Alternativa
        9090,   # ROS2 comum
        9091,   # ROS2 alternativa
        11311,  # ROS1 master
        11411,  # ROS1 alternativa
        5000,   # API comum
        5001,   # API alternativa
        3000,   # Web comum
        3001,   # Web alternativa
        22,     # SSH
        80,     # HTTP
        443,    # HTTPS
    ]
    
    print(f"🔍 Escaneando portas no G1 ({g1_ip})...")
    print("=" * 50)
    
    open_ports = []
    
    for port in common_ports:
        print(f"🔌 Testando porta {port}...", end=" ")
        if test_port(g1_ip, port):
            print("✅ ABERTA")
            open_ports.append(port)
        else:
            print("❌ FECHADA")
    
    print("\n" + "=" * 50)
    print("📊 RESULTADO:")
    
    if open_ports:
        print(f"✅ Portas abertas encontradas: {open_ports}")
        print("\n💡 Sugestões:")
        for port in open_ports:
            if port == 8080:
                print(f"  - Porta {port}: Padrão Unitree (atual)")
            elif port == 9090:
                print(f"  - Porta {port}: ROS2 padrão")
            elif port == 5000:
                print(f"  - Porta {port}: API REST comum")
            else:
                print(f"  - Porta {port}: Verificar documentação")
    else:
        print("❌ Nenhuma porta aberta encontrada")
        print("💡 Verificar:")
        print("  - G1 está ligado?")
        print("  - Rede está correta?")
        print("  - Firewall bloqueando?")

if __name__ == "__main__":
    scan_g1_ports()
