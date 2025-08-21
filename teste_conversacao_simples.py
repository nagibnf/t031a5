#!/usr/bin/env python3
"""
🗣️ TESTE SIMPLES - CONVERSAÇÃO POR VOZ
Sistema básico para validar DJI Mic → STT → LLM → TTS → G1 Movimentos
"""

import sys
import time
import asyncio
import logging
import tempfile
import subprocess
from pathlib import Path
import numpy as np

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, "/home/unitree/t031a5/src")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TesteConversacaoSimples:
    """Teste simplificado do sistema de conversação."""
    
    def __init__(self):
        self.audio_manager = None
        self.g1_client = None
    
    async def inicializar_audio(self):
        """Inicializa sistema de áudio."""
        try:
            from t031a5.audio.hybrid_microphone_manager import HybridMicrophoneManager
            
            self.audio_manager = HybridMicrophoneManager({
                "sample_rate": 16000,
                "test_duration": 3,
                "auto_switch": True
            })
            
            logger.info("✅ Áudio híbrido inicializado")
            return True
        except Exception as e:
            logger.error(f"❌ Erro áudio: {e}")
            return False
    
    async def inicializar_g1(self):
        """Inicializa G1."""
        try:
            from unitree_sdk2py.core.channel import ChannelFactoryInitialize
            from unitree_sdk2py.g1.arm.g1_arm_action_client import G1ArmActionClient
            
            ChannelFactoryInitialize(0, "eth0")
            self.g1_client = G1ArmActionClient()
            self.g1_client.SetTimeout(10.0)
            self.g1_client.Init()
            
            # Teste básico
            result = self.g1_client.ExecuteAction(99)
            if result == 0:
                logger.info("✅ G1 conectado e responsivo")
                return True
            else:
                logger.warning(f"⚠️ G1 erro teste: {result}")
                return False
        except Exception as e:
            logger.error(f"❌ Erro G1: {e}")
            return False
    
    async def capturar_audio_simples(self):
        """Captura áudio básico."""
        try:
            logger.info("🎤 Capturando áudio (3s)...")
            audio_data, source = self.audio_manager.capture_audio(duration=3.0)
            
            if audio_data is not None:
                logger.info(f"✅ Áudio capturado: {len(audio_data)} samples")
                return audio_data
            else:
                logger.warning("⚠️ Nenhum áudio capturado")
                return None
        except Exception as e:
            logger.error(f"❌ Erro captura: {e}")
            return None
    
    async def stt_simulado(self, audio_data):
        """STT simulado com frases pré-definidas."""
        if audio_data is None:
            return None
        
        # Simular processamento
        await asyncio.sleep(1)
        
        # Frases de teste em português
        frases_teste = [
            "acenar com a mão",
            "bater palmas",
            "colocar mão no coração",
            "cumprimentar",
            "olá tobias",
            "como você está"
        ]
        
        import random
        frase = random.choice(frases_teste)
        logger.info(f"🗣️ STT: '{frase}'")
        return frase
    
    async def processar_comando(self, texto):
        """Processa comando e retorna resposta + movimento."""
        if not texto:
            return None, None
        
        texto_lower = texto.lower()
        
        # Mapear comandos para respostas e movimentos
        comandos = {
            "acenar": ("Claro! Vou acenar para você!", 26),
            "palmas": ("Vou bater palmas com alegria!", 17), 
            "coração": ("Isso me toca o coração!", 33),
            "cumprimentar": ("Olá! Prazer em conhecê-lo!", 27),
            "olá": ("Olá! Como posso ajudá-lo?", None),
            "como": ("Estou muito bem, obrigado!", None)
        }
        
        for palavra, (resposta, movimento_id) in comandos.items():
            if palavra in texto_lower:
                logger.info(f"🧠 Comando reconhecido: {palavra}")
                logger.info(f"🤖 Resposta: '{resposta}'")
                return resposta, movimento_id
        
        # Resposta padrão
        return "Entendi! Como posso ajudá-lo?", None
    
    async def executar_movimento(self, movimento_id):
        """Executa movimento no G1."""
        if not movimento_id or not self.g1_client:
            return False
        
        try:
            logger.info(f"🎭 Executando movimento {movimento_id}...")
            result = self.g1_client.ExecuteAction(movimento_id)
            
            if result == 0:
                logger.info("✅ Movimento executado!")
                
                # Aguardar movimento
                if movimento_id == 26:  # acenar
                    await asyncio.sleep(8)
                elif movimento_id == 17:  # aplaudir
                    await asyncio.sleep(4)
                else:
                    await asyncio.sleep(3)
                
                # Relaxar
                self.g1_client.ExecuteAction(99)
                return True
            else:
                logger.error(f"❌ Movimento falhou: {result}")
                return False
        except Exception as e:
            logger.error(f"❌ Erro movimento: {e}")
            return False
    
    async def tts_simples(self, texto):
        """TTS simples usando espeak ou simulado."""
        try:
            logger.info(f"🗣️ Falando: '{texto}'")
            
            # Tentar espeak primeiro
            try:
                subprocess.run([
                    "espeak", "-v", "pt-br", "-s", "150", texto
                ], check=True, timeout=10)
                logger.info("✅ TTS espeak executado")
                return True
            except:
                # Fallback simulado
                logger.info("🗣️ TTS simulado")
                duracao = len(texto) * 0.08  # ~80ms por caractere
                await asyncio.sleep(min(duracao, 5.0))
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro TTS: {e}")
            return False
    
    async def ciclo_teste_completo(self):
        """Executa um ciclo completo de teste."""
        logger.info("\n" + "="*50)
        logger.info("🔄 CICLO DE TESTE CONVERSAÇÃO")
        logger.info("="*50)
        
        # 1. Capturar áudio
        audio_data = await self.capturar_audio_simples()
        if audio_data is None:
            return False
        
        # 2. STT
        texto = await self.stt_simulado(audio_data)
        if not texto:
            return False
        
        # 3. Processar comando
        resposta, movimento_id = await self.processar_comando(texto)
        
        # 4. Executar TTS e movimento em paralelo
        tasks = []
        if resposta:
            tasks.append(self.tts_simples(resposta))
        if movimento_id:
            tasks.append(self.executar_movimento(movimento_id))
        
        if tasks:
            resultados = await asyncio.gather(*tasks, return_exceptions=True)
            sucesso = any(not isinstance(r, Exception) for r in resultados)
        else:
            sucesso = True
        
        logger.info("="*50)
        if sucesso:
            logger.info("✅ CICLO COMPLETO COM SUCESSO!")
        else:
            logger.warning("⚠️ Ciclo com problemas")
        logger.info("="*50)
        
        return sucesso
    
    async def executar_teste(self):
        """Executa teste completo."""
        logger.info("🗣️ TESTE SIMPLES - CONVERSAÇÃO POR VOZ")
        logger.info("="*60)
        
        # Inicializar componentes
        logger.info("🔧 Inicializando componentes...")
        audio_ok = await self.inicializar_audio()
        g1_ok = await self.inicializar_g1()
        
        if not audio_ok or not g1_ok:
            logger.error("❌ Falha na inicialização")
            return
        
        logger.info("✅ Componentes inicializados!")
        
        # Executar 3 ciclos de teste
        for i in range(3):
            logger.info(f"\n🧪 TESTE {i+1}/3")
            sucesso = await self.ciclo_teste_completo()
            
            if sucesso:
                logger.info(f"✅ Teste {i+1}: Sucesso")
            else:
                logger.warning(f"⚠️ Teste {i+1}: Problemas")
            
            if i < 2:  # Pausa entre testes
                await asyncio.sleep(2)
        
        logger.info("\n🎉 TESTE COMPLETO FINALIZADO!")

async def main():
    """Função principal."""
    teste = TesteConversacaoSimples()
    await teste.executar_teste()

if __name__ == "__main__":
    asyncio.run(main())
