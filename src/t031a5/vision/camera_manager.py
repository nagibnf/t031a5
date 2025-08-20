"""
Gerenciador de câmera para captura de imagens em tempo real.
"""

import cv2
import numpy as np
import logging
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
        
    async def initialize(self) -> bool:
        """Inicializa a câmera."""
        try:
            logger.info(f"📷 Inicializando câmera (ID: {self.camera_id})...")
            
            self.cap = cv2.VideoCapture(self.camera_id)
            
            if not self.cap.isOpened():
                logger.error(f"❌ Não foi possível abrir a câmera {self.camera_id}")
                return False
            
            # Configura resolução
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # Testa captura
            ret, frame = self.cap.read()
            if not ret:
                logger.error("❌ Falha na captura de teste")
                return False
            
            self.is_initialized = True
            logger.info("✅ Câmera inicializada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar câmera: {e}")
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
            
            self.is_initialized = False
            
        except Exception as e:
            logger.error(f"❌ Erro ao limpar câmera: {e}")

# Função de conveniência para captura rápida
async def quick_capture(camera_id: int = 0) -> Optional[np.ndarray]:
    """Captura rápida de uma imagem."""
    camera = CameraManager(camera_id)
    
    if await camera.initialize():
        image = await camera.capture_image()
        await camera.cleanup()
        return image
    
    return None
