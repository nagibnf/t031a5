#!/usr/bin/env python3
"""
Teste Completo do Sistema t031a5 em Produção

Executa validação completa de todos os componentes do sistema para
garantir funcionamento em produção:

- Sistema de áudio (DJI Mic 2 + Anker Soundcore)
- Movimentos completos (50 movimentos)
- Sistema conversacional integrado
- Conectividade G1
- LLM e visão
- WebSim interface

IMPORTANTE: Executar na Jetson com G1 em modo CONTROL.
"""

import sys
import time
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from t031a5.actions.g1_movement_mapping import G1MovementLibrary
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.g1_arm_sdk import ArmActionClient

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ProductionSystemTester:
    """Testador completo do sistema em produção."""
    
    def __init__(self):
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
        # Componentes
        self.arm_client = None
        self.movement_library = G1MovementLibrary
        
        # Status dos componentes
        self.component_status = {
            "g1_connection": False,
            "audio_system": False,
            "movement_library": False,
            "conversation_engine": False,
            "websim_interface": False,
            "llm_provider": False,
            "vision_system": False
        }
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Registra resultado de um teste."""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASSOU"
        else:
            self.failed_tests += 1
            status = "❌ FALHOU"
        
        self.test_results[test_name] = {
            "success": success,
            "details": details,
            "timestamp": datetime.now()
        }
        
        logger.info(f"{status}: {test_name}")
        if details:
            logger.info(f"   Detalhes: {details}")
    
    async def test_g1_connection(self) -> bool:
        """Testa conexão com G1."""
        logger.info("🤖 Testando conexão com G1...")
        
        try:
            # Inicializa canal
            ChannelFactoryInitialize(0, "eth0")
            
            # Cria cliente
            self.arm_client = ArmActionClient()
            self.arm_client.SetTimeout(10.0)
            self.arm_client.Init()
            
            # Testa movimento básico (relaxar)
            result = self.arm_client.ExecuteAction(99)
            
            if result == 0:
                self.component_status["g1_connection"] = True
                self.log_test("G1 Connection", True, "Conexão estabelecida e movimento teste OK")
                return True
            else:
                self.log_test("G1 Connection", False, f"Erro no movimento teste: {result}")
                return False
                
        except Exception as e:
            self.log_test("G1 Connection", False, f"Exceção: {e}")
            return False
    
    def test_audio_system(self) -> bool:
        """Testa sistema de áudio."""
        logger.info("🎵 Testando sistema de áudio...")
        
        try:
            import pyaudio
            
            audio = pyaudio.PyAudio()
            device_count = audio.get_device_count()
            
            bluetooth_devices = []
            total_inputs = 0
            total_outputs = 0
            
            for i in range(device_count):
                try:
                    device_info = audio.get_device_info_by_index(i)
                    device_name = device_info['name'].lower()
                    
                    if device_info['maxInputChannels'] > 0:
                        total_inputs += 1
                    if device_info['maxOutputChannels'] > 0:
                        total_outputs += 1
                    
                    if ('dji' in device_name or 'mic' in device_name or 
                        'anker' in device_name or 'soundcore' in device_name or
                        'bluetooth' in device_name):
                        bluetooth_devices.append(device_info['name'])
                
                except:
                    continue
            
            audio.terminate()
            
            if bluetooth_devices and total_inputs > 0 and total_outputs > 0:
                self.component_status["audio_system"] = True
                details = f"Dispositivos Bluetooth: {len(bluetooth_devices)}, Entradas: {total_inputs}, Saídas: {total_outputs}"
                self.log_test("Audio System", True, details)
                return True
            else:
                details = f"Bluetooth: {len(bluetooth_devices)}, Entradas: {total_inputs}, Saídas: {total_outputs}"
                self.log_test("Audio System", False, details)
                return False
                
        except Exception as e:
            self.log_test("Audio System", False, f"Exceção: {e}")
            return False
    
    def test_movement_library(self) -> bool:
        """Testa biblioteca de movimentos."""
        logger.info("🤚 Testando biblioteca de movimentos...")
        
        try:
            stats = self.movement_library.get_statistics()
            
            arm_movements = stats["arm_movements"]
            fsm_states = stats["fsm_states"]
            locomotion_commands = stats["locomotion_commands"]
            total_movements = stats["total_movements"]
            
            if total_movements >= 50:
                self.component_status["movement_library"] = True
                details = f"Total: {total_movements} (Braços: {arm_movements}, FSM: {fsm_states}, Locomoção: {locomotion_commands})"
                self.log_test("Movement Library", True, details)
                return True
            else:
                details = f"Apenas {total_movements} movimentos encontrados (esperado: 50+)"
                self.log_test("Movement Library", False, details)
                return False
                
        except Exception as e:
            self.log_test("Movement Library", False, f"Exceção: {e}")
            return False
    
    async def test_sample_movements(self) -> bool:
        """Testa alguns movimentos de exemplo (APENAS gestos de braços)."""
        if not self.arm_client:
            self.log_test("Sample Movements", False, "Cliente G1 não disponível")
            return False
        
        logger.info("🎭 Testando movimentos de exemplo (gestos de braços)...")
        
        try:
            # Lista de movimentos para testar (APENAS movimentos de braços, NÃO estados FSM)
            test_movements = [
                (99, "release_arm"),           # Relaxar
                (26, "wave_above_head"),       # Acenar alto
                (32, "right_hand_on_mouth"),   # Mão na boca
                (17, "clamp"),                 # Aplaudir
                (33, "right_hand_on_heart"),   # Mão no coração
                (99, "release_arm")            # Relaxar final
            ]
            
            success_count = 0
            
            for movement_id, movement_name in test_movements:
                logger.info(f"   Testando movimento {movement_id}: {movement_name}")
                
                result = self.arm_client.ExecuteAction(movement_id)
                
                if result == 0:
                    success_count += 1
                    logger.info(f"   ✅ {movement_name} - OK")
                else:
                    logger.warning(f"   ❌ {movement_name} - Erro {result}")
                
                # Aguarda entre movimentos
                time.sleep(2.0)
            
            if success_count >= 5:  # Pelo menos 5 de 6 devem funcionar
                details = f"{success_count}/{len(test_movements)} movimentos funcionaram"
                self.log_test("Sample Movements", True, details)
                return True
            else:
                details = f"Apenas {success_count}/{len(test_movements)} movimentos funcionaram"
                self.log_test("Sample Movements", False, details)
                return False
                
        except Exception as e:
            self.log_test("Sample Movements", False, f"Exceção: {e}")
            return False
    
    def test_llm_availability(self) -> bool:
        """Testa disponibilidade do LLM."""
        logger.info("🧠 Testando disponibilidade do LLM...")
        
        try:
            # Testa importação dos módulos LLM
            from t031a5.llm.provider import LLMProvider
            from t031a5.llm.ollama_manager import OllamaManager
            
            # Verifica se o arquivo .env existe
            env_file = Path.cwd() / ".env"
            if env_file.exists():
                env_details = "Arquivo .env encontrado"
            else:
                env_details = "Arquivo .env não encontrado"
            
            self.component_status["llm_provider"] = True
            self.log_test("LLM Availability", True, env_details)
            return True
            
        except Exception as e:
            self.log_test("LLM Availability", False, f"Exceção: {e}")
            return False
    
    def test_vision_system(self) -> bool:
        """Testa sistema de visão."""
        logger.info("👁️ Testando sistema de visão...")
        
        try:
            # Testa importação dos módulos de visão
            from t031a5.vision.camera_manager import CameraManager
            from t031a5.vision.llava_manager import LLaVAManager
            
            # Verifica se a câmera está disponível
            import cv2
            
            # Tenta abrir câmera
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                
                if ret:
                    self.component_status["vision_system"] = True
                    details = f"Câmera disponível, frame capturado: {frame.shape if ret else 'N/A'}"
                    self.log_test("Vision System", True, details)
                    return True
                else:
                    self.log_test("Vision System", False, "Câmera abriu mas não capturou frame")
                    return False
            else:
                self.log_test("Vision System", False, "Não foi possível abrir câmera")
                return False
                
        except Exception as e:
            self.log_test("Vision System", False, f"Exceção: {e}")
            return False
    
    def test_websim_interface(self) -> bool:
        """Testa interface WebSim."""
        logger.info("🌐 Testando interface WebSim...")
        
        try:
            # Testa importação do WebSim
            from t031a5.simulators.websim import WebSim
            
            # Verifica se os templates existem
            templates_dir = Path.cwd() / "templates"
            static_dir = Path.cwd() / "static"
            
            templates_exist = templates_dir.exists() and (templates_dir / "index.html").exists()
            static_exist = static_dir.exists()
            
            if templates_exist and static_exist:
                self.component_status["websim_interface"] = True
                details = "Templates e static files encontrados"
                self.log_test("WebSim Interface", True, details)
                return True
            else:
                details = f"Templates: {templates_exist}, Static: {static_exist}"
                self.log_test("WebSim Interface", False, details)
                return False
                
        except Exception as e:
            self.log_test("WebSim Interface", False, f"Exceção: {e}")
            return False
    
    def test_conversation_engine(self) -> bool:
        """Testa motor de conversação."""
        logger.info("💬 Testando motor de conversação...")
        
        try:
            # Testa importação do motor de conversação
            from t031a5.conversation.engine import ConversationEngine
            
            # Verifica se a integração com movimentos funciona
            config = {
                "enable_vision_context": True,
                "enable_gesture_sync": True,
                "enable_emotion_detection": True
            }
            
            engine = ConversationEngine(config)
            
            # Verifica se a biblioteca de movimentos foi carregada
            if hasattr(engine, 'movement_library') and hasattr(engine, 'gesture_mapping'):
                gesture_count = len(engine.gesture_mapping)
                self.component_status["conversation_engine"] = True
                details = f"Engine criado, {gesture_count} categorias de gestos"
                self.log_test("Conversation Engine", True, details)
                return True
            else:
                self.log_test("Conversation Engine", False, "Biblioteca de movimentos não carregada")
                return False
                
        except Exception as e:
            self.log_test("Conversation Engine", False, f"Exceção: {e}")
            return False
    
    def print_system_status(self):
        """Imprime status completo do sistema."""
        logger.info("\n" + "="*60)
        logger.info("📊 STATUS DO SISTEMA t031a5")
        logger.info("="*60)
        
        # Status dos componentes
        logger.info("🔧 COMPONENTES:")
        for component, status in self.component_status.items():
            status_icon = "✅" if status else "❌"
            component_name = component.replace("_", " ").title()
            logger.info(f"   {status_icon} {component_name}")
        
        # Resumo dos testes
        logger.info(f"\n📋 RESUMO DOS TESTES:")
        logger.info(f"   Total: {self.total_tests}")
        logger.info(f"   ✅ Passou: {self.passed_tests}")
        logger.info(f"   ❌ Falhou: {self.failed_tests}")
        
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            logger.info(f"   📈 Taxa de Sucesso: {success_rate:.1f}%")
        
        # Detalhes dos testes que falharam
        failed_tests = [name for name, result in self.test_results.items() if not result["success"]]
        if failed_tests:
            logger.info(f"\n❌ TESTES QUE FALHARAM:")
            for test_name in failed_tests:
                details = self.test_results[test_name]["details"]
                logger.info(f"   - {test_name}: {details}")
        
        # Recomendações
        logger.info(f"\n💡 RECOMENDAÇÕES:")
        
        working_components = sum(1 for status in self.component_status.values() if status)
        total_components = len(self.component_status)
        
        if working_components == total_components:
            logger.info("   🎉 Sistema 100% operacional!")
            logger.info("   🚀 Pronto para uso em produção")
        elif working_components >= total_components * 0.8:
            logger.info("   ⚠️ Sistema majoritariamente funcional")
            logger.info("   🔧 Corrigir componentes com falha antes da produção")
        else:
            logger.info("   🚨 Sistema requer atenção significativa")
            logger.info("   🛠️ Resolver problemas críticos antes do uso")
        
        logger.info("="*60)
    
    async def run_complete_test(self):
        """Executa teste completo do sistema."""
        logger.info("🚀 INICIANDO TESTE COMPLETO DO SISTEMA t031a5")
        logger.info("="*60)
        logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*60)
        
        # Verificações de pré-requisitos
        logger.info("🔍 VERIFICAÇÕES DE PRÉ-REQUISITOS:")
        logger.info("1. G1 está em modo CONTROL? (R1 + X)")
        logger.info("2. DJI Mic 2 está conectado via Bluetooth?")
        logger.info("3. Anker Soundcore está conectado via Bluetooth?")
        logger.info("4. Espaço adequado para movimentos do robô?")
        logger.info("5. Supervisão humana ativa?")
        
        confirm = input("\n✅ Todos os pré-requisitos OK? (sim/não): ").lower().strip()
        if confirm not in ['sim', 's', 'yes', 'y']:
            logger.info("❌ Teste cancelado - pré-requisitos não atendidos")
            return
        
        logger.info("\n🧪 EXECUTANDO BATERIA DE TESTES:")
        logger.info("-" * 40)
        
        # Executa testes em sequência
        tests = [
            ("test_movement_library", self.test_movement_library),
            ("test_audio_system", self.test_audio_system),
            ("test_llm_availability", self.test_llm_availability),
            ("test_vision_system", self.test_vision_system),
            ("test_websim_interface", self.test_websim_interface),
            ("test_conversation_engine", self.test_conversation_engine),
            ("test_g1_connection", self.test_g1_connection),
            ("test_sample_movements", self.test_sample_movements),
        ]
        
        for test_name, test_func in tests:
            try:
                if asyncio.iscoroutinefunction(test_func):
                    await test_func()
                else:
                    test_func()
                
                # Pausa entre testes
                time.sleep(1.0)
                
            except Exception as e:
                self.log_test(test_name, False, f"Exceção inesperada: {e}")
        
        # Imprime status final
        self.print_system_status()
        
        # Salva relatório
        self.save_test_report()
        
        logger.info("\n🎉 TESTE COMPLETO FINALIZADO!")
    
    def save_test_report(self):
        """Salva relatório de teste."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"production_test_report_{timestamp}.txt"
            
            with open(filename, 'w') as f:
                f.write("RELATÓRIO DE TESTE DO SISTEMA t031a5\n")
                f.write("=" * 50 + "\n")
                f.write(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total de Testes: {self.total_tests}\n")
                f.write(f"Testes Aprovados: {self.passed_tests}\n")
                f.write(f"Testes Reprovados: {self.failed_tests}\n")
                
                if self.total_tests > 0:
                    success_rate = (self.passed_tests / self.total_tests) * 100
                    f.write(f"Taxa de Sucesso: {success_rate:.1f}%\n")
                
                f.write("\nCOMPONENTES:\n")
                for component, status in self.component_status.items():
                    status_text = "OK" if status else "FALHA"
                    f.write(f"- {component.replace('_', ' ').title()}: {status_text}\n")
                
                f.write("\nDETALHES DOS TESTES:\n")
                for test_name, result in self.test_results.items():
                    status_text = "PASSOU" if result["success"] else "FALHOU"
                    f.write(f"- {test_name}: {status_text}\n")
                    if result["details"]:
                        f.write(f"  Detalhes: {result["details"]}\n")
            
            logger.info(f"💾 Relatório salvo: {filename}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar relatório: {e}")


async def main():
    """Função principal."""
    try:
        tester = ProductionSystemTester()
        await tester.run_complete_test()
        
    except KeyboardInterrupt:
        logger.info("\n⏹️ Teste interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro crítico no teste: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
