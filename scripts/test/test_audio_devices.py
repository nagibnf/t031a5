#!/usr/bin/env python3
"""
Teste de Dispositivos de Áudio - Sistema t031a5

Testa e lista dispositivos de áudio disponíveis para:
- DJI Mic 2 (entrada Bluetooth)
- Anker Soundcore Mobile 300 (saída Bluetooth)
- G1 built-in (fallback)
"""

import pyaudio
import numpy as np
import time
import sys
from typing import Dict, List, Optional


class AudioDeviceTester:
    """Testador de dispositivos de áudio."""
    
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.devices = {}
        
    def list_audio_devices(self):
        """Lista todos os dispositivos de áudio."""
        print("🎵 DISPOSITIVOS DE ÁUDIO DISPONÍVEIS")
        print("=" * 50)
        
        device_count = self.audio.get_device_count()
        
        for i in range(device_count):
            try:
                device_info = self.audio.get_device_info_by_index(i)
                device_name = device_info['name']
                max_inputs = device_info['maxInputChannels']
                max_outputs = device_info['maxOutputChannels']
                
                device_type = "Entrada/Saída"
                if max_inputs > 0 and max_outputs == 0:
                    device_type = "Entrada"
                elif max_outputs > 0 and max_inputs == 0:
                    device_type = "Saída"
                
                print(f"📱 {i}: {device_name}")
                print(f"    Tipo: {device_type}")
                print(f"    Entradas: {max_inputs}")
                print(f"    Saídas: {max_outputs}")
                print(f"    Taxa: {device_info['defaultSampleRate']}Hz")
                print()
                
                # Armazena informações
                self.devices[i] = {
                    'name': device_name,
                    'type': device_type,
                    'inputs': max_inputs,
                    'outputs': max_outputs,
                    'sample_rate': device_info['defaultSampleRate']
                }
                
            except Exception as e:
                print(f"❌ Erro ao ler dispositivo {i}: {e}")
    
    def find_bluetooth_devices(self):
        """Procura dispositivos Bluetooth."""
        print("🔍 PROCURANDO DISPOSITIVOS BLUETOOTH")
        print("=" * 40)
        
        bluetooth_devices = []
        
        for device_id, device_info in self.devices.items():
            device_name = device_info['name'].lower()
            
            # Procura por DJI Mic 2
            if 'dji' in device_name or 'mic' in device_name:
                bluetooth_devices.append({
                    'id': device_id,
                    'name': device_info['name'],
                    'type': 'DJI Mic 2 (Entrada)',
                    'category': 'input'
                })
                print(f"✅ DJI Mic 2 encontrado: {device_info['name']}")
            
            # Procura por Anker Soundcore
            elif 'anker' in device_name or 'soundcore' in device_name:
                bluetooth_devices.append({
                    'id': device_id,
                    'name': device_info['name'],
                    'type': 'Anker Soundcore 300 (Saída)',
                    'category': 'output'
                })
                print(f"✅ Anker Soundcore encontrado: {device_info['name']}")
            
            # Procura por outros dispositivos Bluetooth
            elif 'bluetooth' in device_name or 'bt' in device_name:
                bluetooth_devices.append({
                    'id': device_id,
                    'name': device_info['name'],
                    'type': 'Bluetooth',
                    'category': 'unknown'
                })
                print(f"📱 Dispositivo Bluetooth: {device_info['name']}")
        
        if not bluetooth_devices:
            print("⚠️ Nenhum dispositivo Bluetooth encontrado")
            print("💡 Conecte o DJI Mic 2 e Anker Soundcore 300")
        
        return bluetooth_devices
    
    def test_input_device(self, device_id: int, duration: float = 3.0):
        """Testa dispositivo de entrada."""
        try:
            device_info = self.devices[device_id]
            print(f"🎤 Testando entrada: {device_info['name']}")
            
            # Configura stream de entrada
            stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=int(device_info['sample_rate']),
                input=True,
                input_device_index=device_id,
                frames_per_buffer=1024
            )
            
            print(f"🎤 Gravando por {duration} segundos...")
            frames = []
            
            for i in range(int(device_info['sample_rate'] / 1024 * duration)):
                data = stream.read(1024, exception_on_overflow=False)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            
            # Analisa áudio
            audio_data = np.frombuffer(b''.join(frames), dtype=np.float32)
            volume = np.sqrt(np.mean(audio_data**2))
            
            print(f"✅ Teste concluído!")
            print(f"   Volume médio: {volume:.4f}")
            print(f"   Amostras: {len(audio_data)}")
            
            if volume > 0.001:
                print("   🎵 Áudio detectado!")
            else:
                print("   🔇 Sem áudio detectado")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro no teste de entrada: {e}")
            return False
    
    def test_output_device(self, device_id: int, duration: float = 2.0):
        """Testa dispositivo de saída."""
        try:
            device_info = self.devices[device_id]
            print(f"🔊 Testando saída: {device_info['name']}")
            
            # Gera tom de teste
            sample_rate = int(device_info['sample_rate'])
            frequency = 440  # Lá 440Hz
            samples = int(sample_rate * duration)
            
            # Gera onda senoidal
            t = np.linspace(0, duration, samples, False)
            tone = np.sin(2 * np.pi * frequency * t) * 0.3
            
            # Configura stream de saída
            stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=sample_rate,
                output=True,
                output_device_index=device_id
            )
            
            print(f"🔊 Reproduzindo tom de teste por {duration} segundos...")
            stream.write(tone.astype(np.float32).tobytes())
            
            stream.stop_stream()
            stream.close()
            
            print(f"✅ Teste de saída concluído!")
            return True
            
        except Exception as e:
            print(f"❌ Erro no teste de saída: {e}")
            return False
    
    def run_complete_test(self):
        """Executa teste completo de áudio."""
        print("🎵 TESTE COMPLETO DE ÁUDIO - SISTEMA t031a5")
        print("=" * 60)
        
        # Lista dispositivos
        self.list_audio_devices()
        
        # Procura dispositivos Bluetooth
        bluetooth_devices = self.find_bluetooth_devices()
        
        print("\n🧪 TESTANDO DISPOSITIVOS")
        print("=" * 30)
        
        # Testa dispositivos de entrada
        input_devices = [d for d in self.devices.values() if d['inputs'] > 0]
        print(f"\n🎤 Dispositivos de entrada encontrados: {len(input_devices)}")
        
        for device_id, device_info in self.devices.items():
            if device_info['inputs'] > 0:
                print(f"\n--- Testando entrada {device_id} ---")
                self.test_input_device(device_id, 2.0)
        
        # Testa dispositivos de saída
        output_devices = [d for d in self.devices.values() if d['outputs'] > 0]
        print(f"\n🔊 Dispositivos de saída encontrados: {len(output_devices)}")
        
        for device_id, device_info in self.devices.items():
            if device_info['outputs'] > 0:
                print(f"\n--- Testando saída {device_id} ---")
                self.test_output_device(device_id, 1.0)
        
        print("\n📋 RESUMO")
        print("=" * 20)
        print(f"📱 Total de dispositivos: {len(self.devices)}")
        print(f"🎤 Entradas: {len(input_devices)}")
        print(f"🔊 Saídas: {len(output_devices)}")
        print(f"📡 Bluetooth: {len(bluetooth_devices)}")
        
        # Recomendações
        print("\n💡 RECOMENDAÇÕES")
        print("=" * 20)
        
        if bluetooth_devices:
            print("✅ Dispositivos Bluetooth detectados!")
            print("🎯 Configure o sistema para usar:")
            for device in bluetooth_devices:
                print(f"   - {device['type']}")
        else:
            print("⚠️ Nenhum dispositivo Bluetooth encontrado")
            print("🔗 Conecte o DJI Mic 2 e Anker Soundcore 300")
            print("📱 Verifique se estão pareados com o sistema")
        
        self.audio.terminate()


def main():
    """Função principal."""
    try:
        tester = AudioDeviceTester()
        tester.run_complete_test()
        
        print("\n🎉 Teste de áudio concluído!")
        print("🚀 Próximo passo: Configurar dispositivos Bluetooth")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
