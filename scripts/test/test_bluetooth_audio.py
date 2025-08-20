#!/usr/bin/env python3
"""
Teste de Áudio Bluetooth - Sistema t031a5

Testa DJI Mic 2 + Anker Soundcore Mobile 300
"""

import asyncio
import sys
from pathlib import Path

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from t031a5.audio.bluetooth_manager import BluetoothAudioManager


async def test_bluetooth_audio():
    """Testa sistema de áudio Bluetooth."""
    print("🎵 TESTE DE ÁUDIO BLUETOOTH - SISTEMA t031a5")
    print("=" * 50)
    
    manager = BluetoothAudioManager()
    
    print("🔧 Inicializando...")
    if await manager.initialize():
        print("✅ Sistema inicializado")
        
        print("\n🎤 Teste de captura (3 segundos)...")
        print("Fale algo no DJI Mic 2...")
        
        audio = await manager.capture_audio(3.0)
        if audio is not None:
            volume = np.sqrt(np.mean(audio**2))
            print(f"✅ Áudio capturado: {len(audio)} amostras")
            print(f"📊 Volume médio: {volume:.4f}")
            
            if volume > 0.001:
                print("🎵 Áudio detectado!")
                
                print("\n🔊 Reproduzindo áudio...")
                success = await manager.play_audio(audio)
                if success:
                    print("✅ Áudio reproduzido na Anker Soundcore 300")
                else:
                    print("❌ Falha ao reproduzir áudio")
            else:
                print("🔇 Sem áudio detectado")
        else:
            print("❌ Falha ao capturar áudio")
        
        await manager.cleanup()
    else:
        print("❌ Falha ao inicializar sistema")
    
    print("\n🎉 Teste concluído!")


if __name__ == "__main__":
    asyncio.run(test_bluetooth_audio())
