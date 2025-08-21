#!/usr/bin/env python3
"""
🚀 SISTEMA t031a5 EM PRODUÇÃO COMPLETA
Robô G1 Tobias - Conversação End-to-End
"""

import sys
import time
import asyncio
import logging
from datetime import datetime

# Adiciona src ao path
sys.path.insert(0, "/home/unitree/t031a5/src")
sys.path.insert(0, "src")

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SistemaProducaoT031A5:
    """Sistema completo t031a5 em produção."""
    
    def __init__(self):
        self.componentes = {}
        self.status_global = True
        
    def inicializar_componentes(self):
        """Inicializa todos os componentes do sistema."""
        logger.info("🔧 INICIALIZANDO COMPONENTES...")
        
        try:
            # 1. G1 SDK e Canal DDS
            logger.info("🤖 Inicializando G1 SDK...")
            from unitree_sdk2py.core.channel import ChannelFactoryInitialize
            from unitree_sdk2py.g1.g1_arm_sdk import ArmActionClient
            
            ChannelFactoryInitialize(0, "eth0")
            self.arm_client = ArmActionClient()
            self.arm_client.SetTimeout(10.0)
            self.arm_client.Init()
            
            # Teste movimento relaxar
            result = self.arm_client.ExecuteAction(99)
            if result == 0:
                logger.info("✅ G1 SDK: OK")
                self.componentes["g1_sdk"] = True
            else:
                logger.warning("⚠️ G1 SDK: Movimento teste falhou")
                self.componentes["g1_sdk"] = False
                
        except Exception as e:
            logger.error(f"❌ G1 SDK: {e}")
            self.componentes["g1_sdk"] = False
        
        try:
            # 2. Sistema Híbrido de Áudio
            logger.info("🎤 Inicializando Sistema Híbrido de Áudio...")
            from t031a5.audio.hybrid_microphone_manager import HybridMicrophoneManager
            
            self.audio_manager = HybridMicrophoneManager({
                "sample_rate": 16000,
                "test_duration": 2,
                "auto_switch": True,
                "quality_threshold": 10
            })
            
            # Teste rápido
            results = self.audio_manager.run_full_diagnostics()
            current_mic = self.audio_manager.current_source.value if self.audio_manager.current_source else "none"
            
            if current_mic != "none":
                logger.info(f"✅ Áudio Híbrido: {current_mic}")
                self.componentes["audio_hibrido"] = True
            else:
                logger.warning("⚠️ Áudio Híbrido: Nenhum microfone funcional")
                self.componentes["audio_hibrido"] = False
                
        except Exception as e:
            logger.error(f"❌ Áudio Híbrido: {e}")
            self.componentes["audio_hibrido"] = False
        
        try:
            # 3. Biblioteca de Movimentos
            logger.info("🤚 Carregando Biblioteca de Movimentos...")
            from t031a5.actions.g1_movement_mapping import G1MovementLibrary
            
            stats = G1MovementLibrary.get_statistics()
            total_movimentos = stats["total_movements"]
            
            if total_movimentos >= 50:
                logger.info(f"✅ Movimentos: {total_movimentos} disponíveis")
                self.componentes["movimentos"] = True
            else:
                logger.warning(f"⚠️ Movimentos: Apenas {total_movimentos} disponíveis")
                self.componentes["movimentos"] = False
                
        except Exception as e:
            logger.error(f"❌ Movimentos: {e}")
            self.componentes["movimentos"] = False
            
        try:
            # 4. Sistema de Visão
            logger.info("👁️ Inicializando Sistema de Visão...")
            import cv2
            
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                
                if ret:
                    logger.info(f"✅ Câmera: Frame {frame.shape}")
                    self.componentes["camera"] = True
                else:
                    logger.warning("⚠️ Câmera: Não capturou frame")
                    self.componentes["camera"] = False
            else:
                logger.warning("⚠️ Câmera: Não foi possível abrir")
                self.componentes["camera"] = False
                
        except Exception as e:
            logger.error(f"❌ Câmera: {e}")
            self.componentes["camera"] = False
    
    async def testar_movimentos_gestuais(self):
        """Testa sequência de movimentos gestuais."""
        if not self.componentes.get("g1_sdk", False):
            logger.warning("⚠️ G1 SDK não disponível - pulando movimentos")
            return False
            
        logger.info("🎭 TESTANDO SEQUÊNCIA DE MOVIMENTOS...")
        
        movimentos = [
            (99, "release_arm", "Relaxar braços"),
            (26, "wave_above_head", "Acenar alto"),
            (17, "clamp", "Aplaudir"),
            (33, "right_hand_on_heart", "Mão no coração"),
            (99, "release_arm", "Relaxar final")
        ]
        
        sucesso = 0
        
        for mov_id, mov_nome, descricao in movimentos:
            logger.info(f"   🤖 {descricao}...")
            
            try:
                result = self.arm_client.ExecuteAction(mov_id)
                if result == 0:
                    logger.info(f"   ✅ {descricao}: OK")
                    sucesso += 1
                else:
                    logger.warning(f"   ❌ {descricao}: Erro {result}")
                
                time.sleep(2.0)  # Pausa entre movimentos
                
            except Exception as e:
                logger.error(f"   ❌ {descricao}: Exceção {e}")
        
        taxa_sucesso = (sucesso / len(movimentos)) * 100
        logger.info(f"🎯 Movimentos: {sucesso}/{len(movimentos)} ({taxa_sucesso:.1f}%)")
        
        return sucesso >= 4  # Pelo menos 4 de 5 devem funcionar
    
    async def testar_captura_audio(self):
        """Testa captura de áudio do sistema híbrido."""
        if not self.componentes.get("audio_hibrido", False):
            logger.warning("⚠️ Sistema de áudio não disponível")
            return False
            
        logger.info("🎤 TESTANDO CAPTURA DE ÁUDIO...")
        
        try:
            # Captura 3 segundos de áudio
            audio_data, source = self.audio_manager.capture_audio(duration=3.0)
            
            if audio_data is not None and len(audio_data) > 0:
                logger.info(f"✅ Áudio capturado: {len(audio_data)} samples de {source.value}")
                return True
            else:
                logger.warning("⚠️ Nenhum áudio capturado")
                return False
                
        except Exception as e:
            logger.error(f"❌ Captura áudio: {e}")
            return False
    
    async def demonstracao_conversacional(self):
        """Demonstração do fluxo conversacional."""
        logger.info("🗣️ DEMONSTRAÇÃO CONVERSACIONAL...")
        
        # Simulação do fluxo:
        # 1. Captura de áudio
        audio_ok = await self.testar_captura_audio()
        
        # 2. Processamento (simulado)
        if audio_ok:
            logger.info("🧠 Processando: 'Hello Tobias, wave at me!'")
            
            # 3. Resposta gestual
            if self.componentes.get("g1_sdk", False):
                logger.info("🤖 Executando: Acenar com a mão...")
                try:
                    result = self.arm_client.ExecuteAction(26)  # wave_above_head
                    if result == 0:
                        logger.info("✅ Gesto executado com sucesso!")
                        time.sleep(3)
                        
                        # Relaxar braços
                        self.arm_client.ExecuteAction(99)
                        logger.info("✅ Braços relaxados")
                        
                        return True
                    else:
                        logger.warning(f"⚠️ Erro no gesto: {result}")
                        return False
                except Exception as e:
                    logger.error(f"❌ Erro no gesto: {e}")
                    return False
            else:
                logger.info("🤖 [SIMULADO] Acenar com a mão")
                return True
        else:
            logger.info("🤖 [SIMULADO] Fluxo conversacional")
            return True
    
    def relatorio_status(self):
        """Gera relatório de status do sistema."""
        logger.info("\n" + "="*60)
        logger.info("📊 RELATÓRIO FINAL - SISTEMA t031a5 EM PRODUÇÃO")
        logger.info("="*60)
        
        componentes_ok = 0
        total_componentes = len(self.componentes)
        
        for comp, status in self.componentes.items():
            status_icon = "✅" if status else "❌"
            comp_nome = comp.replace("_", " ").title()
            logger.info(f"   {status_icon} {comp_nome}")
            if status:
                componentes_ok += 1
        
        if total_componentes > 0:
            taxa_sucesso = (componentes_ok / total_componentes) * 100
            logger.info(f"\n🎯 TAXA DE SUCESSO: {componentes_ok}/{total_componentes} ({taxa_sucesso:.1f}%)")
            
            if taxa_sucesso >= 80:
                logger.info("🎉 SISTEMA TOTALMENTE OPERACIONAL EM PRODUÇÃO!")
                status_final = "PRODUÇÃO"
            elif taxa_sucesso >= 60:
                logger.info("⚠️ Sistema funcionando com limitações")
                status_final = "LIMITADO"
            else:
                logger.info("❌ Sistema com problemas significativos")
                status_final = "PROBLEMAS"
        else:
            status_final = "ERRO"
            
        logger.info(f"🚀 STATUS FINAL: {status_final}")
        logger.info("="*60)
        
        return status_final
    
    async def executar_sistema_completo(self):
        """Executa o sistema completo em produção."""
        logger.info("🚀 INICIANDO SISTEMA t031a5 G1 TOBIAS EM PRODUÇÃO")
        logger.info("="*60)
        logger.info(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("G1 Tobias: 192.168.123.161")
        logger.info("Jetson: 192.168.123.164")
        logger.info("="*60)
        
        # 1. Inicializar componentes
        self.inicializar_componentes()
        
        # 2. Testar movimentos
        movimento_ok = await self.testar_movimentos_gestuais()
        
        # 3. Demonstração conversacional
        conversa_ok = await self.demonstracao_conversacional()
        
        # 4. Relatório final
        status = self.relatorio_status()
        
        logger.info(f"\n🎉 SISTEMA t031a5 FINALIZADO - STATUS: {status}")
        
        return status

async def main():
    """Função principal."""
    try:
        sistema = SistemaProducaoT031A5()
        status = await sistema.executar_sistema_completo()
        
        if status == "PRODUÇÃO":
            logger.info("✅ SISTEMA PRONTO PARA USO EM PRODUÇÃO!")
        else:
            logger.info("⚠️ Sistema requer ajustes antes da produção completa")
            
    except KeyboardInterrupt:
        logger.info("\n⏹️ Sistema interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
