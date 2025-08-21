#!/usr/bin/env python3
"""
Teste Básico Sistema t031a5 na Jetson
"""

import subprocess
import sys
import os

# Adiciona src ao path
sys.path.insert(0, "/home/unitree/t031a5/src")
sys.path.insert(0, "src")

print("=" * 60)
print("🚀 TESTE BÁSICO SISTEMA t031a5")
print("=" * 60)
print(f"Python: {sys.version}")
print(f"Diretório: {os.getcwd()}")

# Teste 1: Ping G1
print("\n🤖 Testando conectividade G1...")
try:
    result = subprocess.run(["ping", "-c", "2", "192.168.123.161"], 
                          capture_output=True, timeout=10)
    if result.returncode == 0:
        print("✅ G1 Ping: OK")
    else:
        print("❌ G1 Ping: FALHA")
except Exception as e:
    print(f"❌ G1 Ping: ERRO - {e}")

# Teste 2: Import Sistema Híbrido Audio
print("\n🎤 Testando sistema híbrido de áudio...")
try:
    from t031a5.audio.hybrid_microphone_manager import HybridMicrophoneManager
    print("✅ Híbrido Audio: Import OK")
    
    # Teste rápido
    manager = HybridMicrophoneManager({
        "sample_rate": 16000,
        "test_duration": 1,
        "auto_switch": True
    })
    print("✅ Híbrido Audio: Manager criado")
    
except Exception as e:
    print(f"❌ Híbrido Audio: {e}")

# Teste 3: Import G1 SDK
print("\n🤖 Testando G1 SDK...")
try:
    from unitree_sdk2py.core.channel import ChannelFactoryInitialize
    print("✅ G1 SDK: Import OK")
    
    # Inicialização básica
    ChannelFactoryInitialize(0, "eth0")
    print("✅ G1 SDK: Canal inicializado")
    
except Exception as e:
    print(f"❌ G1 SDK: {e}")

# Teste 4: Outros imports críticos
print("\n📦 Testando outros imports...")
modules = [
    ("pyaudio", "PyAudio"),
    ("numpy", "NumPy"),
    ("cv2", "OpenCV"),
]

for module_name, display_name in modules:
    try:
        __import__(module_name)
        print(f"✅ {display_name}: OK")
    except Exception as e:
        print(f"❌ {display_name}: {e}")

print("\n" + "=" * 60)
print("✅ TESTE BÁSICO COMPLETO")
print("=" * 60)
