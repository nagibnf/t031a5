#!/usr/bin/env python3
"""
Teste de Câmera Logitech USB para G1
Verifica se a câmera está funcionando corretamente
"""

import cv2
import time
import sys

def test_camera():
    print("📷 Teste de Câmera Logitech USB")
    print("=" * 40)
    
    # Testa diferentes índices de câmera
    for camera_index in range(4):
        print(f"\n🔍 Testando câmera no índice {camera_index}...")
        
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print(f"❌ Câmera {camera_index}: Não encontrada")
            continue
        
        # Configura propriedades
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Tenta capturar alguns frames
        success_count = 0
        for i in range(10):
            ret, frame = cap.read()
            if ret:
                success_count += 1
                print(f"  ✅ Frame {i+1}: {frame.shape}")
            else:
                print(f"  ❌ Frame {i+1}: Falha")
        
        cap.release()
        
        if success_count > 5:
            print(f"🎉 Câmera {camera_index}: FUNCIONANDO!")
            print(f"   Resolução: {frame.shape[1]}x{frame.shape[0]}")
            print(f"   Canais: {frame.shape[2]}")
            return camera_index
        else:
            print(f"⚠️  Câmera {camera_index}: Instável")
    
    print("\n❌ Nenhuma câmera funcionando encontrada!")
    return None

def test_camera_settings(camera_index):
    print(f"\n⚙️  Testando configurações da câmera {camera_index}...")
    
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print("❌ Não foi possível abrir a câmera")
        return False
    
    # Testa diferentes configurações
    settings = {
        "Autofoco": cv2.CAP_PROP_AUTOFOCUS,
        "Auto-exposição": cv2.CAP_PROP_AUTO_EXPOSURE,
        "Brilho": cv2.CAP_PROP_BRIGHTNESS,
        "Contraste": cv2.CAP_PROP_CONTRAST,
        "Saturação": cv2.CAP_PROP_SATURATION
    }
    
    for name, prop in settings.items():
        try:
            value = cap.get(prop)
            print(f"  {name}: {value}")
        except:
            print(f"  {name}: Não suportado")
    
    cap.release()
    return True

if __name__ == "__main__":
    print("🤖 Teste de Câmera para Sistema t031a5")
    print("=" * 50)
    
    # Testa câmeras disponíveis
    working_camera = test_camera()
    
    if working_camera is not None:
        print(f"\n✅ Câmera funcionando encontrada no índice {working_camera}")
        
        # Testa configurações
        test_camera_settings(working_camera)
        
        print(f"\n🎯 Para usar esta câmera:")
        print(f"   1. Configure 'camera_index': {working_camera} em config/g1_logitech.json5")
        print(f"   2. Execute: ./t031a5 logitech")
        
    else:
        print("\n🔧 Soluções:")
        print("   1. Verifique se a câmera Logitech está conectada")
        print("   2. Teste em outro computador")
        print("   3. Verifique permissões de câmera")
        print("   4. Use modo mock: ./t031a5 mock")
    
    print("\n📋 Próximos passos:")
    print("   - Conecte a câmera Logitech ao G1")
    print("   - Execute este teste no G1")
    print("   - Configure o índice correto")
    print("   - Teste: ./t031a5 logitech")
