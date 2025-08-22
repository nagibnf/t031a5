"""
Conector para captura de visão RealSense D435i no sistema t031a5.
MÉTODO TESTADO E FUNCIONANDO: pyrealsense2 640x480@30fps color+depth
"""

import logging
import asyncio
import numpy as np
import cv2
import os
from typing import Optional, Tuple, Dict, Any
from datetime import datetime
from pathlib import Path

try:
    import pyrealsense2 as rs
    REALSENSE_AVAILABLE = True
except ImportError:
    REALSENSE_AVAILABLE = False
    rs = None

logger = logging.getLogger(__name__)


class VisionCaptureConnector:
    """Conector para captura de visão - MÉTODO TESTADO REALSENSE D435i."""
    
    def __init__(self, config: dict):
        self.width = config.get("width", 640)
        self.height = config.get("height", 480)
        self.fps = config.get("fps", 30)
        self.enabled = config.get("enabled", True)
        self.output_dir = Path(config.get("output_dir", "vision/captures"))
        
        # Criar diretório se não existir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Pipeline RealSense
        self.pipeline = None
        self.config = None
        self.is_initialized = False
        
        logger.info(f"VisionCaptureConnector inicializado: {self.width}x{self.height}@{self.fps}fps")
    
    async def initialize_realsense(self) -> bool:
        """
        Inicializa RealSense D435i.
        MÉTODO TESTADO E FUNCIONANDO: 640x480@30fps color+depth
        """
        if not REALSENSE_AVAILABLE:
            logger.error("pyrealsense2 não disponível")
            return False
            
        if not self.enabled:
            logger.warning("VisionCapture desabilitado")
            return False
        
        try:
            logger.info("🔌 Inicializando RealSense D435i...")
            
            # Configurar pipeline (método testado)
            self.pipeline = rs.pipeline()
            self.config = rs.config()
            
            # MÉTODO TESTADO: Configurar streams com parâmetros validados
            self.config.enable_stream(
                rs.stream.color, 
                self.width, self.height, 
                rs.format.bgr8, 
                self.fps
            )
            self.config.enable_stream(
                rs.stream.depth, 
                self.width, self.height, 
                rs.format.z16, 
                self.fps
            )
            
            # Iniciar streams
            logger.info(f"📷 Iniciando streams {self.width}x{self.height}@{self.fps}fps...")
            profile = self.pipeline.start(self.config)
            
            # Aguardar alguns frames para estabilizar
            for i in range(5):
                frames = self.pipeline.wait_for_frames()
            
            self.is_initialized = True
            logger.info("✅ RealSense D435i inicializado com sucesso (método testado)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar RealSense: {e}")
            self.is_initialized = False
            return False
    
    async def capture_frame_realsense(self, save_files: bool = False) -> Optional[Dict[str, Any]]:
        """
        Captura frame da RealSense D435i.
        MÉTODO TESTADO: color + depth streams funcionando
        
        Returns:
            Dict com color_image, depth_image, timestamp, arquivos opcionais
        """
        if not self.is_initialized or not self.pipeline:
            logger.error("RealSense não inicializado")
            return None
        
        try:
            # Capturar frames (método testado)
            frames = self.pipeline.wait_for_frames()
            
            # Obter frames de color e depth
            color_frame = frames.get_color_frame()
            depth_frame = frames.get_depth_frame()
            
            if not color_frame or not depth_frame:
                logger.warning("Frames não capturados")
                return None
            
            # Converter para arrays numpy (método testado)
            color_image = np.asanyarray(color_frame.get_data())
            depth_image = np.asanyarray(depth_frame.get_data())
            
            timestamp = datetime.now()
            
            # Dados de retorno
            capture_data = {
                "color_image": color_image,
                "depth_image": depth_image,
                "timestamp": timestamp,
                "resolution": f"{self.width}x{self.height}",
                "fps": self.fps,
                "color_shape": color_image.shape,
                "depth_shape": depth_image.shape,
                "method": "realsense_d435i_640x480_30fps_TESTADO"
            }
            
            # Salvar arquivos se solicitado
            if save_files:
                timestamp_str = timestamp.strftime('%Y%m%d_%H%M%S')
                color_file = self.output_dir / f"color_{timestamp_str}.jpg"
                depth_file = self.output_dir / f"depth_{timestamp_str}.png"
                
                # Salvar imagem colorida
                cv2.imwrite(str(color_file), color_image)
                
                # Normalizar e salvar depth como colormap
                depth_colormap = cv2.applyColorMap(
                    cv2.convertScaleAbs(depth_image, alpha=0.03), 
                    cv2.COLORMAP_JET
                )
                cv2.imwrite(str(depth_file), depth_colormap)
                
                capture_data["color_file"] = str(color_file)
                capture_data["depth_file"] = str(depth_file)
                
                logger.debug(f"📸 Imagens salvas: {color_file.name}, {depth_file.name}")
            
            logger.debug(f"✅ Frame capturado: color{color_image.shape}, depth{depth_image.shape}")
            return capture_data
            
        except Exception as e:
            logger.error(f"Erro na captura de frame: {e}")
            return None
    
    async def test_camera(self) -> bool:
        """Testa se a RealSense está funcionando."""
        try:
            # Inicializar se necessário
            if not self.is_initialized:
                success = await self.initialize_realsense()
                if not success:
                    return False
            
            # Tentar capturar um frame
            frame_data = await self.capture_frame_realsense()
            
            if frame_data and frame_data["color_image"] is not None:
                logger.info("✅ RealSense D435i funcionando corretamente")
                return True
            else:
                logger.error("❌ RealSense não capturou frames")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao testar câmera: {e}")
            return False
    
    async def cleanup(self):
        """Limpar recursos da RealSense."""
        try:
            if self.pipeline:
                self.pipeline.stop()
                logger.info("Pipeline RealSense finalizado")
            self.is_initialized = False
        except Exception as e:
            logger.warning(f"Erro ao finalizar pipeline: {e}")
    
    def __del__(self):
        """Destructor para garantir limpeza."""
        try:
            if self.pipeline:
                self.pipeline.stop()
        except:
            pass
