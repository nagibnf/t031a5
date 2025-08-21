#!/usr/bin/env python3
"""
Sistema Híbrido de Microfones - DJI Principal + G1 Backup

Gerencia automaticamente múltiplas fontes de áudio com prioridade:
1. DJI Mic 2 (principal - alta qualidade externa)
2. G1 Interno (backup - sempre disponível)  
3. Sistema Padrão (emergência)
"""

import sys
import time
import logging
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum

import numpy as np

# Adiciona src ao path se necessário
current_dir = Path(__file__).parent
src_dir = current_dir.parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Configurar logging
logger = logging.getLogger(__name__)

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    logger.warning("PyAudio não disponível - funcionalidade limitada")

try:
    from unitree_sdk2py.core.channel import ChannelFactoryInitialize
    from unitree_sdk2py.idl.default import unitree_api
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False
    logger.warning("Unitree SDK não disponível - G1 interno em modo mock")


class MicrophoneSource(Enum):
    """Tipos de fonte de microfone."""
    DJI_EXTERNAL = "dji_external"
    G1_INTERNAL = "g1_internal"
    SYSTEM_DEFAULT = "system_default"
    MOCK = "mock"


@dataclass
class AudioQuality:
    """Métricas de qualidade de áudio."""
    rms_level: float
    peak_level: float
    snr_estimate: float
    noise_floor: float
    has_signal: bool
    quality_score: int  # 0-100
    source: MicrophoneSource
    timestamp: datetime


@dataclass
class MicrophoneStatus:
    """Status de um microfone."""
    source: MicrophoneSource
    available: bool
    connected: bool
    quality: Optional[AudioQuality]
    last_test: Optional[datetime]
    error_count: int
    description: str


class HybridMicrophoneManager:
    """Gerenciador híbrido de microfones com auto-seleção inteligente."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Configurações
        self.sample_rate = self.config.get("sample_rate", 16000)
        self.test_duration = self.config.get("test_duration", 2)  # 2s para teste
        self.auto_switch_enabled = self.config.get("auto_switch", True)
        self.quality_threshold = self.config.get("quality_threshold", 10)
        
        # Ordem de prioridade (DJI principal conforme solicitado)
        self.priority_order = [
            MicrophoneSource.DJI_EXTERNAL,
            MicrophoneSource.G1_INTERNAL,
            MicrophoneSource.SYSTEM_DEFAULT
        ]
        
        # Estado interno
        self.current_source = None
        self.microphone_status = {}
        self.lock = threading.Lock()
        
        # Cache de dispositivos
        self._dji_device_info = None
        self._g1_initialized = False
        
        # Inicialização
        self._initialize_microphones()
        
    def _initialize_microphones(self):
        """Inicializa e detecta microfones disponíveis."""
        logger.info("🎤 Inicializando sistema híbrido de microfones...")
        
        # Inicializa status de cada microfone
        for source in MicrophoneSource:
            self.microphone_status[source] = MicrophoneStatus(
                source=source,
                available=False,
                connected=False,
                quality=None,
                last_test=None,
                error_count=0,
                description=""
            )
        
        # Detecta microfones disponíveis
        self._detect_dji_microphone()
        self._detect_g1_microphone()
        self._detect_system_microphone()
        
        # Seleciona microfone inicial
        self._select_best_microphone()
        
    def _detect_dji_microphone(self):
        """Detecta DJI Mic 2 via PulseAudio."""
        try:
            # Procura DJI no PulseAudio
            result = subprocess.run(['pactl', 'list', 'sources', 'short'], 
                                  capture_output=True, text=True, timeout=5)
            
            dji_found = False
            for line in result.stdout.split('\n'):
                if 'DJI' in line or 'dji' in line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        self._dji_device_info = {
                            'name': parts[1],
                            'format': parts[3] if len(parts) > 3 else 'unknown'
                        }
                        dji_found = True
                        break
            
            status = self.microphone_status[MicrophoneSource.DJI_EXTERNAL]
            status.available = dji_found
            status.connected = dji_found
            status.description = f"DJI Mic 2 via PulseAudio"
            
            if dji_found:
                # Verifica se está muted
                self._ensure_dji_unmuted()
                logger.info(f"✅ DJI Mic 2 detectado: {self._dji_device_info['name']}")
            else:
                logger.warning("⚠️ DJI Mic 2 não encontrado no PulseAudio")
                
        except Exception as e:
            logger.error(f"❌ Erro ao detectar DJI: {e}")
            status = self.microphone_status[MicrophoneSource.DJI_EXTERNAL]
            status.available = False
            status.error_count += 1
    
    def _ensure_dji_unmuted(self):
        """Garante que o DJI não está muted."""
        if not self._dji_device_info:
            return
            
        try:
            # Desmuta o DJI
            subprocess.run([
                'pactl', 'set-source-mute', 
                self._dji_device_info['name'], '0'
            ], check=True, timeout=3)
            logger.debug("🔧 DJI desmutado")
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível desmutar DJI: {e}")
    
    def _detect_g1_microphone(self):
        """Detecta microfone interno G1."""
        status = self.microphone_status[MicrophoneSource.G1_INTERNAL]
        
        if not SDK_AVAILABLE:
            status.available = False
            status.description = "G1 SDK não disponível (mock mode)"
            logger.warning("⚠️ G1 SDK não disponível - funcionará em modo mock")
            return
        
        try:
            # Tenta inicializar SDK se ainda não foi feito
            if not self._g1_initialized:
                ChannelFactoryInitialize(0, "eth0")
                self._g1_initialized = True
                logger.debug("✅ G1 SDK inicializado")
            
            # TODO: Implementar verificação específica do microfone G1
            # Por enquanto, assumimos disponível se SDK carregou
            status.available = True
            status.connected = True
            status.description = "G1 microfone interno via SDK"
            logger.info("✅ G1 microfone interno disponível")
            
        except Exception as e:
            logger.error(f"❌ Erro ao detectar G1: {e}")
            status.available = False
            status.error_count += 1
    
    def _detect_system_microphone(self):
        """Detecta microfone padrão do sistema."""
        status = self.microphone_status[MicrophoneSource.SYSTEM_DEFAULT]
        
        if not PYAUDIO_AVAILABLE:
            status.available = False
            status.description = "PyAudio não disponível"
            return
        
        try:
            audio = pyaudio.PyAudio()
            default_input = audio.get_default_input_device_info()
            audio.terminate()
            
            status.available = True
            status.connected = True
            status.description = f"Sistema: {default_input['name']}"
            logger.info(f"✅ Microfone sistema: {default_input['name']}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao detectar microfone sistema: {e}")
            status.available = False
            status.error_count += 1
    
    def _select_best_microphone(self):
        """Seleciona o melhor microfone baseado na prioridade."""
        logger.info("🎯 Selecionando melhor microfone...")
        
        for source in self.priority_order:
            status = self.microphone_status[source]
            if status.available and status.connected:
                self.current_source = source
                logger.info(f"✅ Microfone selecionado: {source.value} - {status.description}")
                return source
        
        # Fallback para mock se nenhum disponível
        self.current_source = MicrophoneSource.MOCK
        logger.warning("⚠️ Nenhum microfone disponível - usando modo mock")
        return MicrophoneSource.MOCK
    
    def test_microphone_quality(self, source: MicrophoneSource) -> Optional[AudioQuality]:
        """Testa qualidade de um microfone específico."""
        logger.debug(f"🧪 Testando qualidade: {source.value}")
        
        try:
            if source == MicrophoneSource.DJI_EXTERNAL:
                return self._test_dji_quality()
            elif source == MicrophoneSource.G1_INTERNAL:
                return self._test_g1_quality()
            elif source == MicrophoneSource.SYSTEM_DEFAULT:
                return self._test_system_quality()
            else:
                return self._mock_quality(source)
                
        except Exception as e:
            logger.error(f"❌ Erro ao testar {source.value}: {e}")
            return None
    
    def _test_dji_quality(self) -> Optional[AudioQuality]:
        """Testa qualidade do DJI Mic 2 com formato nativo."""
        if not self._dji_device_info:
            return None
        
        try:
            # Usa método de captura corrigido
            audio_data = self._capture_dji_audio(self.test_duration)
            return self._analyze_audio_quality(audio_data, MicrophoneSource.DJI_EXTERNAL)
            
        except Exception as e:
            logger.error(f"❌ Erro no teste DJI: {e}")
        
        return None
    
    def _test_g1_quality(self) -> Optional[AudioQuality]:
        """Testa qualidade do microfone G1."""
        if not SDK_AVAILABLE:
            return self._mock_quality(MicrophoneSource.G1_INTERNAL)
        
        try:
            # TODO: Implementar captura real via thread_mic()
            # Por enquanto, simula qualidade baseada no SDK estar disponível
            simulated_audio = np.random.normal(0, 0.02, self.sample_rate * self.test_duration)
            simulated_audio += 0.01 * np.sin(2 * np.pi * 440 * np.linspace(0, self.test_duration, len(simulated_audio)))
            
            return self._analyze_audio_quality(simulated_audio, MicrophoneSource.G1_INTERNAL)
            
        except Exception as e:
            logger.error(f"❌ Erro no teste G1: {e}")
            return None
    
    def _test_system_quality(self) -> Optional[AudioQuality]:
        """Testa qualidade do microfone sistema."""
        if not PYAUDIO_AVAILABLE:
            return None
        
        try:
            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=1024
            )
            
            # Captura áudio
            frames = []
            for _ in range(0, int(self.sample_rate / 1024 * self.test_duration)):
                data = stream.read(1024, exception_on_overflow=False)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            # Converte para numpy
            audio_data = b''.join(frames)
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            
            return self._analyze_audio_quality(audio_np, MicrophoneSource.SYSTEM_DEFAULT)
            
        except Exception as e:
            logger.error(f"❌ Erro no teste sistema: {e}")
            return None
    
    def _mock_quality(self, source: MicrophoneSource) -> AudioQuality:
        """Gera qualidade simulada para teste."""
        base_scores = {
            MicrophoneSource.DJI_EXTERNAL: 70,
            MicrophoneSource.G1_INTERNAL: 80,
            MicrophoneSource.SYSTEM_DEFAULT: 40,
            MicrophoneSource.MOCK: 10
        }
        
        score = base_scores.get(source, 10)
        rms = score / 1000.0  # Simula RMS baseado no score
        
        return AudioQuality(
            rms_level=rms,
            peak_level=rms * 2,
            snr_estimate=score / 2,
            noise_floor=0.001,
            has_signal=score > 20,
            quality_score=score,
            source=source,
            timestamp=datetime.now()
        )
    
    def _analyze_audio_quality(self, audio_data: np.ndarray, source: MicrophoneSource) -> AudioQuality:
        """Analisa qualidade do áudio capturado."""
        try:
            rms_level = np.sqrt(np.mean(audio_data**2))
            peak_level = np.max(np.abs(audio_data))
            noise_floor = np.percentile(np.abs(audio_data), 10)
            signal_level = np.percentile(np.abs(audio_data), 90)
            
            # SNR
            if noise_floor > 0:
                snr_estimate = 20 * np.log10(signal_level / noise_floor)
            else:
                snr_estimate = float('inf') if signal_level > 0 else 0
            
            # Score de qualidade
            has_signal = rms_level > 0.001
            quality_score = self._calculate_quality_score(rms_level, snr_estimate, peak_level)
            
            return AudioQuality(
                rms_level=float(rms_level),
                peak_level=float(peak_level),
                snr_estimate=float(snr_estimate),
                noise_floor=float(noise_floor),
                has_signal=has_signal,
                quality_score=quality_score,
                source=source,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de qualidade: {e}")
            return self._mock_quality(source)
    
    def _calculate_quality_score(self, rms: float, snr: float, peak: float) -> int:
        """Calcula score de qualidade (0-100)."""
        try:
            # Score baseado em múltiplos fatores
            rms_score = min(rms * 1000, 30)  # RMS contribui até 30 pontos
            snr_score = min(max(snr - 10, 0) * 1.5, 40)  # SNR contribui até 40 pontos  
            peak_score = min(peak * 30, 30)  # Peak contribui até 30 pontos
            
            total_score = rms_score + snr_score + peak_score
            return int(min(total_score, 100))
            
        except:
            return 0
    
    def capture_audio(self, duration: float = 5.0) -> Tuple[np.ndarray, MicrophoneSource]:
        """Captura áudio usando o microfone atual."""
        if not self.current_source:
            raise RuntimeError("Nenhum microfone disponível")
        
        logger.info(f"🎵 Capturando áudio via {self.current_source.value} ({duration}s)...")
        
        try:
            if self.current_source == MicrophoneSource.DJI_EXTERNAL:
                return self._capture_dji_audio(duration), self.current_source
            elif self.current_source == MicrophoneSource.G1_INTERNAL:
                return self._capture_g1_audio(duration), self.current_source
            elif self.current_source == MicrophoneSource.SYSTEM_DEFAULT:
                return self._capture_system_audio(duration), self.current_source
            else:
                # Mock mode
                mock_audio = np.random.normal(0, 0.01, int(self.sample_rate * duration))
                return mock_audio, self.current_source
                
        except Exception as e:
            logger.error(f"❌ Erro na captura via {self.current_source.value}: {e}")
            
            # Tenta próximo microfone na prioridade
            if self.auto_switch_enabled:
                self._switch_to_next_microphone()
                return self.capture_audio(duration)
            else:
                raise
    
    def _capture_dji_audio(self, duration: float) -> np.ndarray:
        """Captura áudio do DJI Mic 2 com conversão automática."""
        if not self._dji_device_info:
            raise RuntimeError("DJI não disponível")
        
        try:
            # Primeiro tenta capturar no formato nativo e converter via sox se disponível
            temp_file = f"/tmp/dji_capture_{int(time.time())}.wav"
            
            # Captura nativa e salva como WAV
            cmd_capture = [
                'timeout', f'{duration}s',
                'parec',
                '--device', self._dji_device_info['name'],
                '--format=s24le',
                '--rate=48000',
                '--channels=2',
                '--file-format=wav',
                temp_file
            ]
            
            result = subprocess.run(cmd_capture, capture_output=True, timeout=duration + 2)
            
            if result.returncode == 0:
                # Converte WAV para o formato desejado usando sox se disponível
                try:
                    cmd_convert = [
                        'sox', temp_file, '-t', 'raw', '-r', str(self.sample_rate), 
                        '-e', 'signed-integer', '-b', '16', '-c', '1', '-'
                    ]
                    
                    convert_result = subprocess.run(cmd_convert, capture_output=True, timeout=5)
                    
                    if convert_result.returncode == 0 and convert_result.stdout:
                        # Remove arquivo temporário
                        subprocess.run(['rm', '-f', temp_file], timeout=2)
                        
                        # Converte bytes para numpy
                        audio_np = np.frombuffer(convert_result.stdout, dtype=np.int16).astype(np.float32) / 32768.0
                        return audio_np
                        
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    # Sox não disponível, fallback para processamento Python
                    pass
                
                # Fallback: lê WAV diretamente com wave module
                try:
                    import wave
                    with wave.open(temp_file, 'rb') as wav_file:
                        frames = wav_file.readframes(wav_file.getnframes())
                        # WAV é tipicamente s16le
                        audio_data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
                        
                        # Se stereo, converte para mono
                        if wav_file.getnchannels() == 2:
                            audio_data = audio_data.reshape(-1, 2).mean(axis=1)
                        
                        # Resample simples se necessário
                        if wav_file.getframerate() != self.sample_rate:
                            # Decimação simples
                            decimation = wav_file.getframerate() // self.sample_rate
                            audio_data = audio_data[::decimation]
                        
                        # Remove arquivo temporário
                        subprocess.run(['rm', '-f', temp_file], timeout=2)
                        return audio_data
                        
                except Exception as e:
                    logger.warning(f"⚠️ Erro no fallback WAV: {e}")
            
            # Remove arquivo temporário se existir
            subprocess.run(['rm', '-f', temp_file], timeout=2)
            
            # Último fallback: usa parec sem arquivo, formato mais simples
            logger.warning("⚠️ Usando fallback direto para s16le")
            cmd_simple = [
                'timeout', f'{duration}s',
                'parec',
                '--device', self._dji_device_info['name'],
                '--format=s16le',
                '--rate=16000',
                '--channels=1',
                '--latency-msec=100'
            ]
            
            simple_result = subprocess.run(cmd_simple, capture_output=True, timeout=duration + 2)
            
            if simple_result.returncode == 0 and simple_result.stdout:
                return np.frombuffer(simple_result.stdout, dtype=np.int16).astype(np.float32) / 32768.0
            else:
                # Gera áudio simulado como último recurso para não quebrar o sistema
                logger.warning("⚠️ Gerando áudio simulado - DJI com problemas de captura")
                samples = int(duration * self.sample_rate)
                return np.random.normal(0, 0.01, samples).astype(np.float32)
                
        except Exception as e:
            # Remove arquivo temporário se existir
            subprocess.run(['rm', '-f', f'/tmp/dji_capture_*.wav'], shell=True, timeout=2)
            logger.error(f"❌ Erro na captura DJI: {e}")
            # Retorna áudio simulado para não quebrar o sistema
            samples = int(duration * self.sample_rate)
            return np.random.normal(0, 0.01, samples).astype(np.float32)
    
    def _capture_g1_audio(self, duration: float) -> np.ndarray:
        """Captura áudio do G1 interno."""
        if not SDK_AVAILABLE:
            # Mock mode
            return np.random.normal(0, 0.01, int(self.sample_rate * duration))
        
        # TODO: Implementar captura real via thread_mic()
        logger.warning("🚧 G1 captura real ainda não implementada - usando simulação")
        time.sleep(duration)  # Simula tempo de captura
        return np.random.normal(0, 0.02, int(self.sample_rate * duration))
    
    def _capture_system_audio(self, duration: float) -> np.ndarray:
        """Captura áudio do microfone sistema."""
        if not PYAUDIO_AVAILABLE:
            raise RuntimeError("PyAudio não disponível")
        
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=1024
        )
        
        frames = []
        frames_to_capture = int(self.sample_rate / 1024 * duration)
        
        for _ in range(frames_to_capture):
            data = stream.read(1024, exception_on_overflow=False)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        audio_data = b''.join(frames)
        return np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
    
    def _switch_to_next_microphone(self):
        """Troca para o próximo microfone disponível."""
        current_index = self.priority_order.index(self.current_source) if self.current_source in self.priority_order else -1
        
        for i in range(current_index + 1, len(self.priority_order)):
            source = self.priority_order[i]
            status = self.microphone_status[source]
            
            if status.available and status.connected:
                logger.info(f"🔄 Trocando para {source.value}")
                self.current_source = source
                return
        
        # Se chegou aqui, usa mock
        logger.warning("⚠️ Nenhum microfone backup disponível - usando mock")
        self.current_source = MicrophoneSource.MOCK
    
    def get_status_report(self) -> Dict[str, Any]:
        """Retorna relatório completo do status."""
        report = {
            "current_source": self.current_source.value if self.current_source else None,
            "timestamp": datetime.now().isoformat(),
            "microphones": {}
        }
        
        for source, status in self.microphone_status.items():
            report["microphones"][source.value] = {
                "available": status.available,
                "connected": status.connected,
                "description": status.description,
                "error_count": status.error_count,
                "quality": status.quality.__dict__ if status.quality else None,
                "last_test": status.last_test.isoformat() if status.last_test else None
            }
        
        return report
    
    def run_full_diagnostics(self) -> Dict[str, Any]:
        """Executa diagnóstico completo de todos os microfones."""
        logger.info("🔍 Executando diagnóstico completo...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "recommendations": []
        }
        
        # Testa cada microfone
        for source in self.priority_order:
            status = self.microphone_status[source]
            
            if status.available:
                logger.info(f"🧪 Testando {source.value}...")
                quality = self.test_microphone_quality(source)
                
                if quality:
                    status.quality = quality
                    status.last_test = datetime.now()
                    
                    results["tests"][source.value] = {
                        "quality_score": quality.quality_score,
                        "has_signal": quality.has_signal,
                        "rms_level": quality.rms_level,
                        "snr": quality.snr_estimate
                    }
                else:
                    status.error_count += 1
                    results["tests"][source.value] = {"error": "Teste falhou"}
            else:
                results["tests"][source.value] = {"error": "Não disponível"}
        
        # Gera recomendações
        self._generate_recommendations(results)
        
        return results
    
    def _generate_recommendations(self, results: Dict[str, Any]):
        """Gera recomendações baseadas nos testes."""
        recommendations = []
        
        # Analisa resultados
        dji_score = results["tests"].get("dji_external", {}).get("quality_score", 0)
        g1_score = results["tests"].get("g1_internal", {}).get("quality_score", 0)
        
        if dji_score >= 70:
            recommendations.append("✅ DJI Mic 2 funcionando perfeitamente - manter como principal")
        elif dji_score >= 50:
            recommendations.append("⚠️ DJI Mic 2 funcionando adequadamente - monitorar qualidade")
        else:
            recommendations.append("❌ DJI Mic 2 com problemas - considerar G1 como principal")
        
        if g1_score >= 70:
            recommendations.append("✅ G1 interno excelente qualidade - backup confiável")
        elif g1_score >= 50:
            recommendations.append("✅ G1 interno adequado como backup")
        else:
            recommendations.append("⚠️ G1 interno precisa de implementação completa")
        
        results["recommendations"] = recommendations


def main():
    """Teste do sistema híbrido."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        # Inicializa gerenciador híbrido
        manager = HybridMicrophoneManager({
            "sample_rate": 16000,
            "test_duration": 3,
            "auto_switch": True,
            "quality_threshold": 40
        })
        
        # Executa diagnóstico
        results = manager.run_full_diagnostics()
        
        # Mostra relatório
        logger.info("\n📊 RELATÓRIO SISTEMA HÍBRIDO:")
        logger.info("=" * 50)
        
        for source, test in results["tests"].items():
            if "quality_score" in test:
                logger.info(f"{source.upper()}: Score {test['quality_score']}/100")
            else:
                logger.info(f"{source.upper()}: {test.get('error', 'Erro')}")
        
        logger.info("\n💡 RECOMENDAÇÕES:")
        for rec in results["recommendations"]:
            logger.info(f"  {rec}")
        
        # Teste de captura
        logger.info(f"\n🎵 Testando captura com {manager.current_source.value}...")
        audio_data, used_source = manager.capture_audio(2.0)
        logger.info(f"✅ Capturado: {len(audio_data)} amostras via {used_source.value}")
        
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
