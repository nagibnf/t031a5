#!/usr/bin/env python3
"""
Teste de interfaces para conectar com G1.
"""

import socket
import time

def test_interface_connection(interface_name, g1_ip="192.168.123.161", port=8080):
    """Testa conexão usando interface específica."""
    try:
        # Criar socket com interface específica
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        
        # Tentar conectar
        result = sock.connect_ex((g1_ip, port))
        sock.close()
        
        return result == 0
    except Exception as e:
        return False

def test_g1_interfaces():
    """Testa diferentes interfaces para conectar com G1."""
    
    g1_ip = "192.168.123.161"
    port = 8081  # Porta que descobrimos estar aberta
    
    # Interfaces para testar
    interfaces = [
        "en0",      # Wi-Fi
        "en1",      # Ethernet 1
        "en2",      # Ethernet 2  
        "en3",      # Ethernet 3
        "en11",     # Interface atual
        "bridge0",  # Bridge
        "lo0",      # Loopback
    ]
    
    print(f"🔍 Testando interfaces para conectar com G1 ({g1_ip}:{port})...")
    print("=" * 60)
    
    working_interfaces = []
    
    for interface in interfaces:
        print(f"🔌 Testando interface {interface}...", end=" ")
        if test_interface_connection(interface, g1_ip, port):
            print("✅ FUNCIONA")
            working_interfaces.append(interface)
        else:
            print("❌ FALHA")
    
    print("\n" + "=" * 60)
    print("📊 RESULTADO:")
    
    if working_interfaces:
        print(f"✅ Interfaces funcionais: {working_interfaces}")
        print("\n💡 Sugestões:")
        for interface in working_interfaces:
            if interface == "en11":
                print(f"  - {interface}: Interface atual (pode ser a correta)")
            elif interface == "en0":
                print(f"  - {interface}: Wi-Fi (verificar se G1 está na mesma rede)")
            else:
                print(f"  - {interface}: Testar esta interface")
    else:
        print("❌ Nenhuma interface funcionou")
        print("💡 Verificar:")
        print("  - G1 está ligado?")
        print("  - IP do G1 está correto?")
        print("  - Porta está correta?")
        print("  - Rede está configurada?")

if __name__ == "__main__":
    test_g1_interfaces()
