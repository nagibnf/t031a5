#!/usr/bin/env python3
"""
Teste G1 - Microfone do Robô
Tenta acessar o microfone do robô G1 diretamente via SDK.
"""

import time
import sys
import json
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.audio.g1_audio_client import AudioClient
from unitree_sdk2py.g1.audio.g1_audio_api import ROBOT_API_ID_AUDIO_ASR

class G1RobotMicrophoneTest:
    """Teste do microfone do robô G1."""
    
    def __init__(self):
        self.interface = "en11"
        self.audio_client = None
        
    def initialize_sdk(self):
        """Inicializa o SDK."""
        try:
            print("🔧 Inicializando SDK...")
            ChannelFactoryInitialize(0, self.interface)
            print("✅ SDK inicializado")
            
            # Inicializar cliente de áudio
            self.audio_client = AudioClient()
            self.audio_client.SetTimeout(10.0)
            self.audio_client.Init()
            print("✅ AudioClient inicializado")
            
            return True
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            return False
    
    def test_microphone_access(self):
        """Testa acesso direto ao microfone do robô."""
        print("\n🎤 TESTE MICROFONE DO ROBÔ")
        print("=" * 40)
        
        try:
            # Tentar acessar microfone do robô
            print("🎤 Tentando acessar microfone do robô G1...")
            
            # Parâmetros para acessar microfone
            p = {}
            p["action"] = "get_microphone"
            p["duration"] = 5000  # 5 segundos
            parameter = json.dumps(p)
            
            # Chamar API para acessar microfone
            code, data = self.audio_client._Call(ROBOT_API_ID_AUDIO_ASR, parameter)
            
            print(f"📊 Resultado acesso microfone:")
            print(f"  - Código: {code}")
            print(f"  - Dados: {data}")
            
            if code == 0:
                print("✅ Microfone do robô acessado!")
                if data:
                    print(f"📝 Dados do microfone: {data}")
                return True
            else:
                print(f"❌ Erro ao acessar microfone: {code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao acessar microfone: {e}")
            return False
    
    def test_microphone_stream(self):
        """Testa stream de áudio do microfone do robô."""
        print("\n🎤 TESTE STREAM MICROFONE")
        print("=" * 40)
        
        try:
            # Tentar obter stream de áudio do microfone
            print("🎤 Tentando obter stream de áudio...")
            
            # Parâmetros para stream
            p = {}
            p["action"] = "start_microphone_stream"
            p["sample_rate"] = 16000
            p["channels"] = 1
            parameter = json.dumps(p)
            
            # Iniciar stream
            code, data = self.audio_client._Call(ROBOT_API_ID_AUDIO_ASR, parameter)
            
            print(f"📊 Iniciar stream - Código: {code}, Dados: {data}")
            
            if code == 0:
                print("✅ Stream iniciado!")
                print("🎤 Gravando 5 segundos do microfone do robô...")
                
                # Aguardar gravação
                time.sleep(5)
                
                # Parar stream
                stop_params = {"action": "stop_microphone_stream"}
                stop_parameter = json.dumps(stop_params)
                stop_code, stop_data = self.audio_client._Call(ROBOT_API_ID_AUDIO_ASR, stop_parameter)
                
                print(f"📊 Parar stream - Código: {stop_code}, Dados: {stop_data}")
                
                if stop_code == 0:
                    print("✅ Stream parado!")
                    if stop_data:
                        print(f"📝 Dados capturados: {stop_data}")
                    return True
                else:
                    print(f"❌ Erro ao parar stream: {stop_code}")
                    return False
            else:
                print(f"❌ Erro ao iniciar stream: {code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro no teste stream: {e}")
            return False
    
    def test_microphone_with_tts(self):
        """Testa microfone com TTS de confirmação."""
        print("\n🎤 TESTE MICROFONE + TTS")
        print("=" * 40)
        
        try:
            # 1. Tentar acessar microfone
            print("🎤 Acessando microfone do robô...")
            mic_params = {"action": "get_microphone", "duration": 3000}
            mic_parameter = json.dumps(mic_params)
            
            mic_code, mic_data = self.audio_client._Call(ROBOT_API_ID_AUDIO_ASR, mic_parameter)
            
            if mic_code == 0:
                print("✅ Microfone acessado!")
                
                # 2. Confirmar com TTS
                print("🗣️  Confirmando com TTS...")
                tts_text = "Microphone test completed"
                tts_result = self.audio_client.TtsMaker(tts_text, 1)  # speaker_id 1 = inglês
                
                if tts_result == 0:
                    print("✅ TTS de confirmação executado!")
                    time.sleep(3)  # Aguardar TTS
                    return True
                else:
                    print(f"❌ Erro no TTS: {tts_result}")
                    return False
            else:
                print(f"❌ Erro ao acessar microfone: {mic_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro no teste microfone + TTS: {e}")
            return False
    
    def test_microphone_status(self):
        """Testa status do microfone do robô."""
        print("\n🎤 TESTE STATUS MICROFONE")
        print("=" * 40)
        
        try:
            # Verificar status do microfone
            print("🎤 Verificando status do microfone...")
            
            status_params = {"action": "get_microphone_status"}
            status_parameter = json.dumps(status_params)
            
            status_code, status_data = self.audio_client._Call(ROBOT_API_ID_AUDIO_ASR, status_parameter)
            
            print(f"📊 Status microfone:")
            print(f"  - Código: {status_code}")
            print(f"  - Dados: {status_data}")
            
            if status_code == 0:
                print("✅ Status obtido!")
                if status_data:
                    try:
                        status = json.loads(status_data)
                        print(f"📝 Status: {status}")
                    except:
                        print(f"📝 Status bruto: {status_data}")
                return True
            else:
                print(f"❌ Erro ao obter status: {status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao verificar status: {e}")
            return False
    
    def run_test(self):
        """Executa todos os testes."""
        print("🎤 G1 TESTE MICROFONE DO ROBÔ")
        print("=" * 50)
        
        if not self.initialize_sdk():
            return False
        
        # 1. Teste acesso direto
        self.test_microphone_access()
        
        # 2. Teste stream
        self.test_microphone_stream()
        
        # 3. Teste status
        self.test_microphone_status()
        
        # 4. Teste microfone + TTS
        self.test_microphone_with_tts()
        
        print("\n🎉 TODOS OS TESTES CONCLUÍDOS!")
        
        # Resumo
        print(f"\n📊 RESUMO:")
        print("=" * 20)
        print("🎤 Microfone do robô: Testado")
        print("📝 Acesso direto: Tentativa")
        print("🔍 Verificar resultados acima")
        print("💡 Microfone pode não estar acessível via SDK")
        
        return True

def main():
    """Função principal."""
    print("🎤 G1 TESTE MICROFONE DO ROBÔ")
    print("=" * 60)
    print("🎯 OBJETIVO: Acessar microfone do robô G1")
    print("📋 TESTES:")
    print("  - Acesso direto ao microfone")
    print("  - Stream de áudio")
    print("  - Status do microfone")
    print("  - Microfone + TTS")
    print("⚠️  Microfone pode não estar acessível via SDK")
    
    response = input("\nDeseja continuar? (s/n): ").strip().lower()
    if response not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada")
        return
    
    tester = G1RobotMicrophoneTest()
    
    if tester.run_test():
        print("\n🎉 TESTE CONCLUÍDO!")
    else:
        print("\n❌ TESTE FALHOU")

if __name__ == "__main__":
    main()
