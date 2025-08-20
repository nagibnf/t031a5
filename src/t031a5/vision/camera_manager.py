"""
Gerenciador de câmera para captura de imagens em tempo real.
"""

import cv2
import numpy as np
import logging
import os
import time
import fcntl
import atexit
import signal
import subprocess
from typing import Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class CameraManager:
    def __init__(self, camera_id: int = 0):
        """
        Inicializa o gerenciador de câmera.
        
        Args:
            camera_id: ID da câmera (0 = câmera padrão)
        """
        self.camera_id = camera_id
        self.cap = None
        self.is_initialized = False
        self.lock_file = None
        self.lock_path = f"/tmp/camera_{camera_id}.lock"
        
        # Registrar cleanup automático
        atexit.register(self._emergency_cleanup)
        signal.signal(signal.SIGTERM, self._signal_cleanup)
        signal.signal(signal.SIGINT, self._signal_cleanup)
        
    async def initialize(self) -> bool:
        """Inicializa a câmera."""
        try:
            logger.info(f"📷 Inicializando câmera (ID: {self.camera_id})...")
            
            # 1. Verificar e limpar processos conflitantes
            if not self._check_and_cleanup_conflicts():
                logger.warning("⚠️ Conflitos detectados, tentando resolever...")
                
            # 2. Tentar adquirir lock da câmera
            if not self._acquire_camera_lock():
                logger.error("❌ Não foi possível adquirir lock da câmera")
                return False
            
            # 3. Tentar diferentes métodos de inicialização
            methods = [
                # Método 1: MJPG com backend V4L2
                lambda: self._init_mjpg_v4l2(),
                # Método 2: GStreamer pipeline
                lambda: self._init_gstreamer(),
                # Método 3: OpenCV padrão
                lambda: self._init_default()
            ]
            
            for i, method in enumerate(methods, 1):
                logger.info(f"🔍 Tentativa {i}: {method.__name__}")
                if method():
                    self.is_initialized = True
                    logger.info("✅ Câmera inicializada com sucesso")
                    return True
            
            logger.error("❌ Todos os métodos de inicialização falharam")
            self._release_camera_lock()
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar câmera: {e}")
            self._release_camera_lock()
            return False
    
    def _init_mjpg_v4l2(self) -> bool:
        """Inicializa com MJPG e backend V4L2."""
        try:
            self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_V4L2)
            
            if not self.cap.isOpened():
                return False
            
            # Configurar MJPG
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Teste de captura
            ret, frame = self.cap.read()
            if ret and frame is not None:
                logger.info("✅ MJPG V4L2 funcionando")
                return True
                
        except Exception as e:
            logger.debug(f"MJPG V4L2 falhou: {e}")
        
        return False
    
    def _init_gstreamer(self) -> bool:
        """Inicializa com pipeline GStreamer."""
        try:
            pipeline = f"v4l2src device=/dev/video{self.camera_id} ! image/jpeg,width=640,height=480,framerate=30/1 ! jpegdec ! videoconvert ! appsink"
            self.cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
            
            if not self.cap.isOpened():
                return False
            
            # Teste de captura
            ret, frame = self.cap.read()
            if ret and frame is not None:
                logger.info("✅ GStreamer funcionando")
                return True
                
        except Exception as e:
            logger.debug(f"GStreamer falhou: {e}")
        
        return False
    
    def _init_default(self) -> bool:
        """Inicializa com método padrão OpenCV."""
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            
            if not self.cap.isOpened():
                return False
            
            # Configurações básicas
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # Teste de captura
            ret, frame = self.cap.read()
            if ret and frame is not None:
                logger.info("✅ Método padrão funcionando")
                return True
                
        except Exception as e:
            logger.debug(f"Método padrão falhou: {e}")
        
        return False
    
    async def capture_image(self) -> Optional[np.ndarray]:
        """Captura uma imagem da câmera."""
        if not self.is_initialized or not self.cap:
            logger.warning("❌ Câmera não inicializada")
            return None
        
        try:
            ret, frame = self.cap.read()
            if not ret:
                logger.error("❌ Falha na captura de imagem")
                return None
            
            # Converte BGR para RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return frame_rgb
            
        except Exception as e:
            logger.error(f"❌ Erro ao capturar imagem: {e}")
            return None
    
    async def save_image(self, image: np.ndarray, filename: str = "capture.jpg") -> bool:
        """Salva uma imagem em disco."""
        try:
            # Converte RGB para BGR para salvar
            image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Cria diretório se não existir
            save_dir = Path("captures")
            save_dir.mkdir(exist_ok=True)
            
            save_path = save_dir / filename
            success = cv2.imwrite(str(save_path), image_bgr)
            
            if success:
                logger.info(f"✅ Imagem salva: {save_path}")
                return True
            else:
                logger.error(f"❌ Falha ao salvar imagem: {save_path}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao salvar imagem: {e}")
            return False
    
    async def get_camera_info(self) -> dict:
        """Retorna informações da câmera."""
        if not self.is_initialized or not self.cap:
            return {"error": "Câmera não inicializada"}
        
        try:
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            return {
                "camera_id": self.camera_id,
                "width": width,
                "height": height,
                "fps": fps,
                "is_initialized": self.is_initialized
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def cleanup(self):
        """Limpa recursos da câmera."""
        try:
            if self.cap:
                self.cap.release()
                logger.info("✅ Câmera liberada")
            
            self._release_camera_lock()
            self.is_initialized = False
            
        except Exception as e:
            logger.error(f"❌ Erro ao limpar câmera: {e}")
    
    def _check_and_cleanup_conflicts(self) -> bool:
        """Verifica e limpa processos conflitantes usando a câmera."""
        try:
            device_path = f"/dev/video{self.camera_id}"
            
            # Verificar se dispositivo existe
            if not os.path.exists(device_path):
                logger.error(f"❌ Dispositivo {device_path} não existe")
                return False
            
            # Verificar processos usando a câmera
            try:
                result = subprocess.run(
                    ["lsof", device_path], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    logger.warning(f"⚠️ Processos usando {device_path}:")
                    lines = result.stdout.strip().split('\n')[1:]  # Skip header
                    
                    for line in lines:
                        if line.strip():
                            parts = line.split()
                            if len(parts) >= 2:
                                command = parts[0]
                                pid = parts[1]
                                logger.warning(f"  📋 {command} (PID: {pid})")
                                
                                # Tentar finalizar processo educadamente
                                try:
                                    os.kill(int(pid), signal.SIGTERM)
                                    time.sleep(2)
                                    logger.info(f"  ✅ Processo {pid} finalizado")
                                except (ProcessLookupError, ValueError):
                                    logger.debug(f"  ℹ️ Processo {pid} já finalizado")
                                except PermissionError:
                                    logger.warning(f"  ⚠️ Sem permissão para finalizar {pid}")
                
            except (subprocess.TimeoutExpired, FileNotFoundError):
                logger.debug("🔍 lsof não disponível ou timeout")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar conflitos: {e}")
            return False
    
    def _acquire_camera_lock(self) -> bool:
        """Adquire lock exclusivo da câmera."""
        try:
            # Remover lock antigo se existir e estiver órfão
            if os.path.exists(self.lock_path):
                try:
                    with open(self.lock_path, 'r') as f:
                        old_pid = int(f.read().strip())
                    
                    # Verificar se processo ainda existe
                    try:
                        os.kill(old_pid, 0)  # Não mata, só verifica
                        logger.warning(f"⚠️ Câmera já em uso pelo processo {old_pid}")
                        return False
                    except ProcessLookupError:
                        # Processo morto, remover lock órfão
                        os.remove(self.lock_path)
                        logger.info("🧹 Lock órfão removido")
                        
                except (ValueError, FileNotFoundError):
                    # Lock inválido, remover
                    os.remove(self.lock_path)
            
            # Criar novo lock
            self.lock_file = open(self.lock_path, 'w')
            fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.lock_file.write(str(os.getpid()))
            self.lock_file.flush()
            
            logger.info(f"🔒 Lock da câmera {self.camera_id} adquirido")
            return True
            
        except (BlockingIOError, OSError):
            logger.error("❌ Câmera já está sendo usada por outro processo")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao adquirir lock: {e}")
            return False
    
    def _release_camera_lock(self):
        """Libera lock da câmera."""
        try:
            if self.lock_file:
                fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
                self.lock_file.close()
                self.lock_file = None
            
            if os.path.exists(self.lock_path):
                os.remove(self.lock_path)
                logger.info(f"🔓 Lock da câmera {self.camera_id} liberado")
                
        except Exception as e:
            logger.error(f"❌ Erro ao liberar lock: {e}")
    
    def _emergency_cleanup(self):
        """Cleanup de emergência chamado pelo atexit."""
        try:
            if self.cap:
                self.cap.release()
            self._release_camera_lock()
        except:
            pass  # Silencioso em cleanup de emergência
    
    def _signal_cleanup(self, signum, frame):
        """Cleanup chamado por sinais."""
        logger.info(f"📡 Sinal {signum} recebido, limpando câmera...")
        self._emergency_cleanup()
        exit(0)

# Função de conveniência para captura rápida
async def quick_capture(camera_id: int = 0) -> Optional[np.ndarray]:
    """Captura rápida de uma imagem."""
    camera = CameraManager(camera_id)
    
    if await camera.initialize():
        image = await camera.capture_image()
        await camera.cleanup()
        return image
    
    return None
