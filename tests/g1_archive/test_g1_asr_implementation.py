#!/usr/bin/env python3
"""
Teste G1 - Implementação ASR
Tenta implementar ASR (Speech Recognition) no G1 usando a API registrada.
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

class G1ASRTest:
    """Teste de implementação ASR no G1."""
    
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
    
    def test_asr_api_direct(self):
        """Testa chamada direta da API ASR."""
        print("\n🎤 TESTE API ASR DIRETA")
        print("=" * 40)
        
        try:
            # Tentar chamar a API ASR diretamente
            print("🎤 Tentando chamar API ASR...")
            
            # Parâmetros para ASR
            p = {}
            p["language"] = "en"  # Inglês
            p["timeout"] = 5000   # 5 segundos
            parameter = json.dumps(p)
            
            # Chamar API ASR diretamente
            code, data = self.audio_client._Call(ROBOT_API_ID_AUDIO_ASR, parameter)
            
            print(f"📊 Resultado ASR:")
            print(f"  - Código: {code}")
            print(f"  - Dados: {data}")
            
            if code == 0:
                print("✅ API ASR funcionou!")
                if data:
                    try:
                        result = json.loads(data)
                        print(f"📝 Texto reconhecido: {result}")
                    except:
                        print(f"📝 Dados brutos: {data}")
                return True
            else:
                print(f"❌ API ASR falhou com código: {code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao chamar API ASR: {e}")
            return False
    
    def test_asr_start_stop(self):
        """Testa iniciar e parar ASR."""
        print("\n🎤 TESTE ASR START/STOP")
        print("=" * 40)
        
        try:
            # 1. Iniciar ASR
            print("🎤 Iniciando ASR...")
            start_params = {
                "action": "start",
                "language": "en",
                "timeout": 10000
            }
            start_parameter = json.dumps(start_params)
            
            start_code, start_data = self.audio_client._Call(ROBOT_API_ID_AUDIO_ASR, start_parameter)
            print(f"📊 Start ASR - Código: {start_code}, Dados: {start_data}")
            
            if start_code == 0:
                print("✅ ASR iniciado com sucesso!")
                
                # 2. Aguardar um pouco
                print("⏳ Aguardando 5 segundos para captura...")
                print("🗣️  Fale algo durante este tempo...")
                time.sleep(5)
                
                # 3. Parar ASR
                print("🎤 Parando ASR...")
                stop_params = {
                    "action": "stop"
                }
                stop_parameter = json.dumps(stop_params)
                
                stop_code, stop_data = self.audio_client._Call(ROBOT_API_ID_AUDIO_ASR, stop_parameter)
                print(f"📊 Stop ASR - Código: {stop_code}, Dados: {stop_data}")
                
                if stop_code == 0:
                    print("✅ ASR parado com sucesso!")
                    if stop_data:
                        try:
                            result = json.loads(stop_data)
                            print(f"📝 Resultado final: {result}")
                        except:
                            print(f"📝 Dados finais: {stop_data}")
                    return True
                else:
                    print(f"❌ Erro ao parar ASR: {stop_code}")
                    return False
            else:
                print(f"❌ Erro ao iniciar ASR: {start_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro no teste ASR start/stop: {e}")
            return False
    
    def test_asr_continuous(self):
        """Testa ASR contínuo."""
        print("\n🎤 TESTE ASR CONTÍNUO")
        print("=" * 40)
        
        try:
            # Configurar ASR contínuo
            print("🎤 Configurando ASR contínuo...")
            config_params = {
                "mode": "continuous",
                "language": "en",
                "confidence_threshold": 0.7
            }
            config_parameter = json.dumps(config_params)
            
            config_code, config_data = self.audio_client._Call(ROBOT_API_ID_AUDIO_ASR, config_parameter)
            print(f"📊 Config ASR - Código: {config_code}, Dados: {config_data}")
            
            if config_code == 0:
                print("✅ ASR contínuo configurado!")
                print("🗣️  Fale algo por 10 segundos...")
                
                # Monitorar por 10 segundos
                for i in range(10):
                    time.sleep(1)
                    print(f"⏳ {10-i} segundos restantes...")
                    
                    # Tentar obter resultado
                    try:
                        result_params = {"action": "get_result"}
                        result_parameter = json.dumps(result_params)
                        result_code, result_data = self.audio_client._Call(ROBOT_API_ID_AUDIO_ASR, result_parameter)
                        
                        if result_code == 0 and result_data:
                            print(f"📝 Resultado: {result_data}")
                    except:
                        pass
                
                # Parar ASR contínuo
                stop_params = {"action": "stop"}
                stop_parameter = json.dumps(stop_params)
                stop_code, stop_data = self.audio_client._Call(ROBOT_API_ID_AUDIO_ASR, stop_parameter)
                print(f"📊 Stop contínuo - Código: {stop_code}")
                
                return True
            else:
                print(f"❌ Erro ao configurar ASR contínuo: {config_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro no teste ASR contínuo: {e}")
            return False
    
    def test_asr_with_tts(self):
        """Testa ASR com TTS de confirmação."""
        print("\n🎤 TESTE ASR + TTS")
        print("=" * 40)
        
        try:
            # 1. Iniciar ASR
            print("🎤 Iniciando ASR...")
            start_params = {"action": "start", "language": "en"}
            start_parameter = json.dumps(start_params)
            
            start_code, start_data = self.audio_client._Call(ROBOT_API_ID_AUDIO_ASR, start_parameter)
            
            if start_code == 0:
                print("✅ ASR iniciado!")
                print("🗣️  Fale algo...")
                
                # 2. Aguardar captura
                time.sleep(5)
                
                # 3. Parar ASR e obter resultado
                stop_params = {"action": "stop"}
                stop_parameter = json.dumps(stop_params)
                stop_code, stop_data = self.audio_client._Call(ROBOT_API_ID_AUDIO_ASR, stop_parameter)
                
                if stop_code == 0 and stop_data:
                    print(f"📝 Texto capturado: {stop_data}")
                    
                    # 4. Confirmar com TTS
                    print("🗣️  Confirmando com TTS...")
                    tts_text = f"I heard: {stop_data}"
                    tts_result = self.audio_client.TtsMaker(tts_text, 1)  # speaker_id 1 = inglês
                    
                    if tts_result == 0:
                        print("✅ TTS de confirmação executado!")
                        time.sleep(3)  # Aguardar TTS
                        return True
                    else:
                        print(f"❌ Erro no TTS: {tts_result}")
                        return False
                else:
                    print("❌ Nenhum texto capturado")
                    return False
            else:
                print(f"❌ Erro ao iniciar ASR: {start_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro no teste ASR + TTS: {e}")
            return False
    
    def run_test(self):
        """Executa todos os testes."""
        print("🎤 G1 TESTE IMPLEMENTAÇÃO ASR")
        print("=" * 50)
        
        if not self.initialize_sdk():
            return False
        
        # 1. Teste API direta
        self.test_asr_api_direct()
        
        # 2. Teste start/stop
        self.test_asr_start_stop()
        
        # 3. Teste contínuo
        self.test_asr_continuous()
        
        # 4. Teste ASR + TTS
        self.test_asr_with_tts()
        
        print("\n🎉 TODOS OS TESTES CONCLUÍDOS!")
        
        # Resumo
        print(f"\n📊 RESUMO:")
        print("=" * 20)
        print("🎤 ASR API: Testada")
        print("📝 Implementação: Tentativa")
        print("🔍 Verificar resultados acima")
        print("💡 ASR pode não estar implementado no SDK")
        
        return True

def main():
    """Função principal."""
    print("🎤 G1 TESTE IMPLEMENTAÇÃO ASR")
    print("=" * 60)
    print("🎯 OBJETIVO: Tentar implementar ASR no G1")
    print("📋 TESTES:")
    print("  - API ASR direta")
    print("  - ASR start/stop")
    print("  - ASR contínuo")
    print("  - ASR + TTS")
    print("⚠️  ASR pode não estar implementado no SDK")
    
    response = input("\nDeseja continuar? (s/n): ").strip().lower()
    if response not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada")
        return
    
    tester = G1ASRTest()
    
    if tester.run_test():
        print("\n🎉 TESTE CONCLUÍDO!")
    else:
        print("\n❌ TESTE FALHOU")

if __name__ == "__main__":
    main()
