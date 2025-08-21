#!/usr/bin/env python3
"""
🎤 TESTE SIMPLES - CAPTURA E REPRODUÇÃO DE ÁUDIO
Testa se conseguimos capturar áudio real do DJI Mic 2 e reproduzir
"""

import sys
import time
import asyncio
import logging
import tempfile
import subprocess
from pathlib import Path
import numpy as np
import wave

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, "/home/unitree/t031a5/src")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TesteAudioCapturareproducao:
    """Teste simples de captura e reprodução de áudio."""
    
    def __init__(self):
        self.audio_manager = None
        self.arquivo_gravacao = None
    
    async def inicializar_audio(self):
        """Inicializa sistema de áudio."""
        try:
            from t031a5.audio.hybrid_microphone_manager import HybridMicrophoneManager
            
            self.audio_manager = HybridMicrophoneManager({
                "sample_rate": 16000,
                "test_duration": 5,
                "auto_switch": True,
                "quality_threshold": 5  # Threshold mais baixo para teste
            })
            
            logger.info("✅ Sistema de áudio inicializado")
            
            # Mostrar status dos microfones
            results = self.audio_manager.run_full_diagnostics()
            current_mic = self.audio_manager.current_source.value if self.audio_manager.current_source else "none"
            
            logger.info(f"🎤 Microfone atual: {current_mic}")
            
            # Mostrar todos os microfones detectados
            for source, test in results["tests"].items():
                if "quality_score" in test:
                    score = test["quality_score"]
                    logger.info(f"   📊 {source}: {score}/100")
                else:
                    logger.info(f"   ❌ {source}: erro")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar áudio: {e}")
            return False
    
    def analisar_audio(self, audio_data: np.ndarray) -> dict:
        """Analisa qualidade do áudio capturado."""
        if audio_data is None or len(audio_data) == 0:
            return {"valido": False, "motivo": "Áudio vazio"}
        
        try:
            # Estatísticas básicas
            rms = np.sqrt(np.mean(audio_data**2))
            peak = np.max(np.abs(audio_data))
            duration = len(audio_data) / 16000  # Sample rate 16kHz
            
            # Verificar se parece áudio real ou simulado
            # Áudio simulado geralmente tem padrões muito regulares
            variance = np.var(audio_data)
            mean_abs = np.mean(np.abs(audio_data))
            
            # Análise de frequência básica
            zero_crossings = np.sum(np.diff(np.sign(audio_data)) != 0)
            zcr_rate = zero_crossings / len(audio_data)
            
            eh_simulado = (
                variance < 0.001 and  # Muito pouca variação
                mean_abs > 0.01 and   # Mas com amplitude constante
                zcr_rate < 0.01       # Muito poucas mudanças de sinal
            )
            
            analise = {
                "valido": True,
                "samples": len(audio_data),
                "duracao": duration,
                "rms_level": rms,
                "peak_level": peak,
                "variance": variance,
                "zero_crossing_rate": zcr_rate,
                "provavelmente_simulado": eh_simulado,
                "qualidade": "REAL" if not eh_simulado else "SIMULADO"
            }
            
            return analise
            
        except Exception as e:
            return {"valido": False, "motivo": f"Erro na análise: {e}"}
    
    async def capturar_audio(self, duracao: float = 5.0):
        """Captura áudio por duração especificada."""
        if not self.audio_manager:
            logger.error("❌ Sistema de áudio não inicializado")
            return None
        
        try:
            logger.info(f"🎤 INICIANDO CAPTURA DE ÁUDIO ({duracao}s)...")
            logger.info("🗣️ FALE ALGO NO MICROFONE AGORA!")
            
            # Contador regressivo
            for i in range(3, 0, -1):
                logger.info(f"⏰ {i}...")
                await asyncio.sleep(1)
            
            logger.info("🔴 GRAVANDO...")
            
            # Capturar áudio
            audio_data, source = self.audio_manager.capture_audio(duration=duracao)
            
            if audio_data is not None:
                logger.info(f"✅ Captura concluída via {source.value}")
                return audio_data, source.value
            else:
                logger.error("❌ Falha na captura")
                return None, "erro"
                
        except Exception as e:
            logger.error(f"❌ Erro na captura: {e}")
            return None, "exceção"
    
    def salvar_audio(self, audio_data: np.ndarray, filename: str = None) -> str:
        """Salva áudio em arquivo WAV."""
        try:
            if filename is None:
                timestamp = int(time.time())
                filename = f"captura_audio_{timestamp}.wav"
            
            # Converter para int16
            if audio_data.dtype != np.int16:
                # Normalizar para range int16
                audio_data = audio_data / np.max(np.abs(audio_data))
                audio_data = (audio_data * 32767).astype(np.int16)
            
            # Salvar WAV
            with wave.open(filename, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(16000)  # 16kHz
                wav_file.writeframes(audio_data.tobytes())
            
            file_size = Path(filename).stat().st_size
            logger.info(f"💾 Áudio salvo: {filename} ({file_size} bytes)")
            self.arquivo_gravacao = filename
            return filename
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar: {e}")
            return None
    
    async def reproduzir_audio(self, filename: str) -> bool:
        """Reproduz áudio salvo."""
        if not filename or not Path(filename).exists():
            logger.error("❌ Arquivo não encontrado")
            return False
        
        try:
            logger.info(f"🔊 REPRODUZINDO: {filename}")
            
            # Tentar diferentes métodos de reprodução
            métodos = [
                ["paplay", filename],  # PulseAudio (padrão Linux)
                ["aplay", filename],   # ALSA direto
                ["play", filename],    # SoX
            ]
            
            for método in métodos:
                try:
                    result = subprocess.run(
                        método, 
                        check=True, 
                        timeout=15,
                        capture_output=True
                    )
                    logger.info(f"✅ Reprodução OK via {método[0]}")
                    return True
                except subprocess.CalledProcessError as e:
                    logger.warning(f"⚠️ {método[0]} falhou: {e}")
                except FileNotFoundError:
                    logger.warning(f"⚠️ {método[0]} não encontrado")
                except subprocess.TimeoutExpired:
                    logger.warning(f"⚠️ {método[0]} timeout")
            
            logger.error("❌ Nenhum método de reprodução funcionou")
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro na reprodução: {e}")
            return False
    
    def verificar_dispositivos_audio(self):
        """Verifica dispositivos de áudio disponíveis."""
        logger.info("🔍 VERIFICANDO DISPOSITIVOS DE ÁUDIO...")
        
        try:
            # PulseAudio - Sources (entrada)
            result = subprocess.run(
                ["pactl", "list", "sources", "short"], 
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                logger.info("📥 DISPOSITIVOS DE ENTRADA:")
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            device_id = parts[0]
                            device_name = parts[1]
                            if 'dji' in device_name.lower() or 'mic' in device_name.lower():
                                logger.info(f"   🎤 {device_id}: {device_name}")
                            else:
                                logger.info(f"   📱 {device_id}: {device_name}")
            
            # PulseAudio - Sinks (saída)
            result = subprocess.run(
                ["pactl", "list", "sinks", "short"], 
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                logger.info("📤 DISPOSITIVOS DE SAÍDA:")
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            device_id = parts[0]
                            device_name = parts[1]
                            if 'anker' in device_name.lower() or 'bluetooth' in device_name.lower():
                                logger.info(f"   🔊 {device_id}: {device_name}")
                            else:
                                logger.info(f"   🎧 {device_id}: {device_name}")
                                
        except Exception as e:
            logger.warning(f"⚠️ Erro ao verificar dispositivos: {e}")
    
    async def executar_teste_completo(self):
        """Executa teste completo de captura e reprodução."""
        logger.info("🎤🔊 TESTE CAPTURA E REPRODUÇÃO DE ÁUDIO")
        logger.info("="*60)
        
        # 1. Verificar dispositivos
        self.verificar_dispositivos_audio()
        logger.info("="*60)
        
        # 2. Inicializar sistema
        if not await self.inicializar_audio():
            logger.error("❌ Falha na inicialização")
            return
        
        logger.info("="*60)
        
        # 3. Capturar áudio
        audio_data, source = await self.capturar_audio(5.0)
        
        if audio_data is None:
            logger.error("❌ Falha na captura - teste encerrado")
            return
        
        # 4. Analisar áudio
        logger.info("🔍 ANALISANDO ÁUDIO CAPTURADO...")
        analise = self.analisar_audio(audio_data)
        
        if not analise["valido"]:
            logger.error(f"❌ Áudio inválido: {analise['motivo']}")
            return
        
        # Mostrar análise
        logger.info(f"📊 ANÁLISE DO ÁUDIO:")
        logger.info(f"   📏 Samples: {analise['samples']:,}")
        logger.info(f"   ⏱️ Duração: {analise['duracao']:.2f}s")
        logger.info(f"   📈 RMS Level: {analise['rms_level']:.4f}")
        logger.info(f"   📊 Peak Level: {analise['peak_level']:.4f}")
        logger.info(f"   🔀 Zero Crossing Rate: {analise['zero_crossing_rate']:.4f}")
        logger.info(f"   🎯 Qualidade: {analise['qualidade']}")
        
        if analise["provavelmente_simulado"]:
            logger.warning("⚠️ ATENÇÃO: Áudio parece ser SIMULADO!")
        else:
            logger.info("✅ Áudio parece ser REAL!")
        
        logger.info("="*60)
        
        # 5. Salvar arquivo
        logger.info("💾 SALVANDO ÁUDIO...")
        filename = self.salvar_audio(audio_data)
        
        if not filename:
            logger.error("❌ Falha ao salvar")
            return
        
        # 6. Aguardar um pouco
        logger.info("⏳ Aguardando 2s antes da reprodução...")
        await asyncio.sleep(2)
        
        # 7. Reproduzir
        logger.info("🔊 REPRODUZINDO ÁUDIO CAPTURADO...")
        sucesso_reproducao = await self.reproduzir_audio(filename)
        
        # 8. Resultado final
        logger.info("="*60)
        logger.info("📋 RESULTADO DO TESTE:")
        logger.info(f"   🎤 Captura: ✅ OK via {source}")
        logger.info(f"   💾 Arquivo: ✅ {filename}")
        logger.info(f"   🔊 Reprodução: {'✅ OK' if sucesso_reproducao else '❌ FALHA'}")
        logger.info(f"   🎯 Qualidade: {analise['qualidade']}")
        
        if analise["qualidade"] == "REAL" and sucesso_reproducao:
            logger.info("🎉 TESTE COMPLETO: SUCESSO TOTAL!")
        elif analise["qualidade"] == "REAL":
            logger.info("⚠️ TESTE PARCIAL: Captura OK, reprodução com problemas")
        else:
            logger.info("⚠️ TESTE LIMITADO: Usando áudio simulado")
        
        logger.info("="*60)
        
        # Limpeza opcional
        try:
            if filename and Path(filename).exists():
                keep = input("\n💾 Manter arquivo gravado? (s/n): ").lower().strip()
                if keep not in ['s', 'sim', 'y', 'yes']:
                    Path(filename).unlink()
                    logger.info(f"🗑️ Arquivo {filename} removido")
                else:
                    logger.info(f"💾 Arquivo mantido: {filename}")
        except:
            pass  # Não é crítico

async def main():
    """Função principal."""
    teste = TesteAudioCapturareproducao()
    await teste.executar_teste_completo()

if __name__ == "__main__":
    asyncio.run(main())
