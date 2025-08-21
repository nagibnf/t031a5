"""
Plugin de visão Intel RealSense D435i para G1.

Implementa captura RGB-D, detecção de objetos, reconhecimento facial
e análise de cena com profundidade.
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Imports para visão computacional
import numpy as np

try:
    import cv2
    from PIL import Image
    CV_AVAILABLE = True
except ImportError:
    CV_AVAILABLE = False
    logging.warning("OpenCV não disponível. G1Vision funcionará em modo mock.")

try:
    import pyrealsense2 as rs
    REALSENSE_AVAILABLE = True
except ImportError:
    REALSENSE_AVAILABLE = False
    logging.warning("pyrealsense2 não disponível. Usando modo mock.")

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    logging.warning("face_recognition não disponível. Reconhecimento facial em modo mock.")

from ..base import BaseInput, InputData


@dataclass
class DetectedObject:
    """Objeto detectado na imagem."""
    type: str
    confidence: float
    bbox: List[int]  # [x, y, width, height]
    center: List[float]  # [x, y]
    area: float
    distance: Optional[float] = None  # Distância em metros (D435i)


@dataclass
class DetectedFace:
    """Face detectada na imagem."""
    age: Optional[int]
    gender: Optional[str]
    emotion: Optional[str]
    bbox: List[int]  # [x, y, width, height]
    distance: Optional[float] = None  # Distância em metros (D435i)
    known_person: Optional[str] = None


class G1VisionInput(BaseInput):
    """Input de visão computacional com Intel RealSense D435i."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o G1VisionInput.
        
        Args:
            config: Configuração do input de visão
        """
        super().__init__(config)
        
        # Configurações da câmera D435i
        self.camera_device = config.get("camera_device", "realsense")
        self.resolution = config.get("resolution", [848, 480])  # D435i native
        self.fps = config.get("fps", 15)
        self.analysis_interval = config.get("analysis_interval", 2.0)
        
        # Configurações de detecção
        self.enable_face_detection = config.get("enable_face_detection", True)
        self.enable_object_detection = config.get("enable_object_detection", True)
        self.enable_depth = config.get("enable_depth", True)
        self.depth_range = config.get("depth_range", [0.1, 10.0])  # metros
        
        # Estado interno
        self.pipeline = None
        self.profile = None
        self.align = None
        self.mock_mode = False
        self.last_analysis_time = 0
        self.frame_count = 0
        
        # Cache de rostos conhecidos
        self.known_faces = {}
        
        self.logger = logging.getLogger(__name__)
        
    async def _initialize(self) -> bool:
        """
        Inicialização específica do G1VisionInput.
        
        Returns:
            True se a inicialização foi bem-sucedida
        """
        try:
            self.logger.info("Inicializando G1Vision com Intel RealSense D435i...")
            
            if not REALSENSE_AVAILABLE:
                self.logger.warning("Intel RealSense D435i não disponível, usando modo mock")
                self.mock_mode = True
                return True
            
            # Configura pipeline RealSense
            self.pipeline = rs.pipeline()
            config = rs.config()
            
            # Configura streams RGB e Depth
            config.enable_stream(rs.stream.color, self.resolution[0], self.resolution[1], rs.format.bgr8, self.fps)
            
            if self.enable_depth:
                config.enable_stream(rs.stream.depth, self.resolution[0], self.resolution[1], rs.format.z16, self.fps)
                # Align depth to color
                self.align = rs.align(rs.stream.color)
            
            # Inicia pipeline
            self.profile = self.pipeline.start(config)
            
            # Aquece a câmera
            for _ in range(30):
                self.pipeline.wait_for_frames()
            
            self.logger.info("Intel RealSense D435i inicializada com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na inicialização do D435i: {e}")
            self.logger.warning("Usando modo mock para desenvolvimento")
            self.mock_mode = True
            return True
    
    async def _get_data(self) -> Optional[InputData]:
        """
        Coleta dados da câmera D435i.
        
        Returns:
            Dados de visão ou None se não disponível
        """
        try:
            current_time = time.time()
            
            if self.mock_mode:
                return await self._get_mock_data()
            
            # Captura frame
            frames = self.pipeline.wait_for_frames()
            
            if self.enable_depth and self.align:
                # Alinha depth com color
                aligned_frames = self.align.process(frames)
                color_frame = aligned_frames.get_color_frame()
                depth_frame = aligned_frames.get_depth_frame()
            else:
                color_frame = frames.get_color_frame()
                depth_frame = None
            
            if not color_frame:
                return None
            
            # Converte para numpy array
            color_image = np.asanyarray(color_frame.get_data())
            depth_image = np.asanyarray(depth_frame.get_data()) if depth_frame else None
            
            self.frame_count += 1
            
            # Análise periódica (não todo frame)
            analysis_data = {}
            if current_time - self.last_analysis_time >= self.analysis_interval:
                analysis_data = await self._analyze_frame(color_image, depth_image)
                self.last_analysis_time = current_time
            
            # Dados básicos sempre presentes
            data = {
                "frame_count": self.frame_count,
                "resolution": self.resolution,
                "fps": self.fps,
                "depth_enabled": self.enable_depth,
                "timestamp_capture": datetime.now().isoformat(),
                **analysis_data
            }
            
            return InputData(
                input_type="G1Vision",
                source="realsense_d435i",
                timestamp=datetime.now(),
                data=data,
                confidence=0.95,
                metadata={
                    "camera_type": "realsense_d435i",
                    "depth_available": depth_image is not None,
                    "analysis_performed": bool(analysis_data)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Erro na captura D435i: {e}")
            return None
    
    async def _analyze_frame(self, color_image: np.ndarray, depth_image: Optional[np.ndarray]) -> Dict[str, Any]:
        """
        Analisa frame RGB-D para detecção de objetos e faces.
        
        Args:
            color_image: Imagem RGB
            depth_image: Imagem de profundidade (opcional)
            
        Returns:
            Dados de análise
        """
        analysis = {
            "objects_detected": [],
            "faces_detected": [],
            "scene_description": "",
            "depth_stats": {}
        }
        
        try:
            # Detecção de objetos (simplificada para exemplo)
            if self.enable_object_detection:
                objects = await self._detect_objects(color_image, depth_image)
                analysis["objects_detected"] = objects
            
            # Detecção de faces
            if self.enable_face_detection:
                faces = await self._detect_faces(color_image, depth_image)
                analysis["faces_detected"] = faces
            
            # Estatísticas de profundidade
            if depth_image is not None:
                analysis["depth_stats"] = self._calculate_depth_stats(depth_image)
            
            # Descrição da cena (integração futura com LLaVA)
            analysis["scene_description"] = self._generate_scene_description(analysis)
            
        except Exception as e:
            self.logger.error(f"Erro na análise do frame: {e}")
        
        return analysis
    
    async def _detect_objects(self, color_image: np.ndarray, depth_image: Optional[np.ndarray]) -> List[Dict[str, Any]]:
        """Detecção simples de objetos."""
        objects = []
        
        try:
            # Implementação simplificada - detecta contornos grandes
            gray = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (11, 11), 0)
            
            # Threshold adaptativo
            thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
            
            # Encontra contornos
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 1000:  # Objetos grandes apenas
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Calcula distância se depth disponível
                    distance = None
                    if depth_image is not None:
                        center_x, center_y = x + w//2, y + h//2
                        depth_value = depth_image[center_y, center_x]
                        if depth_value > 0:
                            distance = depth_value * 0.001  # mm para metros
                    
                    objects.append({
                        "type": "object",
                        "confidence": 0.7,
                        "bbox": [x, y, w, h],
                        "center": [x + w//2, y + h//2],
                        "area": area,
                        "distance": distance
                    })
            
        except Exception as e:
            self.logger.error(f"Erro na detecção de objetos: {e}")
        
        return objects[:10]  # Máximo 10 objetos
    
    async def _detect_faces(self, color_image: np.ndarray, depth_image: Optional[np.ndarray]) -> List[Dict[str, Any]]:
        """Detecção de faces com distance."""
        faces = []
        
        try:
            if not FACE_RECOGNITION_AVAILABLE:
                return []
            
            # Converte BGR para RGB
            rgb_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
            
            # Detecta faces
            face_locations = face_recognition.face_locations(rgb_image)
            
            for (top, right, bottom, left) in face_locations:
                # Calcula distância se depth disponível
                distance = None
                if depth_image is not None:
                    center_x = (left + right) // 2
                    center_y = (top + bottom) // 2
                    depth_value = depth_image[center_y, center_x]
                    if depth_value > 0:
                        distance = depth_value * 0.001  # mm para metros
                
                faces.append({
                    "bbox": [left, top, right - left, bottom - top],
                    "center": [(left + right) // 2, (top + bottom) // 2],
                    "distance": distance,
                    "confidence": 0.8
                })
            
        except Exception as e:
            self.logger.error(f"Erro na detecção de faces: {e}")
        
        return faces
    
    def _calculate_depth_stats(self, depth_image: np.ndarray) -> Dict[str, float]:
        """Calcula estatísticas da imagem de profundidade."""
        try:
            # Remove zeros (pixels inválidos)
            valid_depths = depth_image[depth_image > 0] * 0.001  # mm para metros
            
            if len(valid_depths) == 0:
                return {}
            
            return {
                "min_distance": float(np.min(valid_depths)),
                "max_distance": float(np.max(valid_depths)),
                "mean_distance": float(np.mean(valid_depths)),
                "median_distance": float(np.median(valid_depths)),
                "valid_pixels_percentage": float(len(valid_depths) / depth_image.size * 100)
            }
            
        except Exception as e:
            self.logger.error(f"Erro no cálculo de estatísticas de profundidade: {e}")
            return {}
    
    def _generate_scene_description(self, analysis: Dict[str, Any]) -> str:
        """Gera descrição textual da cena."""
        try:
            objects_count = len(analysis.get("objects_detected", []))
            faces_count = len(analysis.get("faces_detected", []))
            
            description_parts = []
            
            if faces_count > 0:
                description_parts.append(f"{faces_count} pessoa(s) detectada(s)")
                
                # Adiciona informação de distância das faces
                faces_with_distance = [f for f in analysis["faces_detected"] if f.get("distance")]
                if faces_with_distance:
                    closest_face = min(faces_with_distance, key=lambda f: f["distance"])
                    description_parts.append(f"pessoa mais próxima a {closest_face['distance']:.1f}m")
            
            if objects_count > 0:
                description_parts.append(f"{objects_count} objeto(s) detectado(s)")
            
            if not description_parts:
                description_parts.append("cena sem objetos ou pessoas detectados")
            
            # Adiciona informação de profundidade geral
            depth_stats = analysis.get("depth_stats", {})
            if depth_stats:
                mean_dist = depth_stats.get("mean_distance", 0)
                if mean_dist > 0:
                    description_parts.append(f"distância média da cena: {mean_dist:.1f}m")
            
            return ", ".join(description_parts)
            
        except Exception as e:
            self.logger.error(f"Erro na geração de descrição: {e}")
            return "erro na análise da cena"
    
    async def _get_mock_data(self) -> InputData:
        """Retorna dados mock para desenvolvimento."""
        return InputData(
            input_type="G1Vision",
            source="mock_realsense",
            timestamp=datetime.now(),
            data={
                "frame_count": self.frame_count,
                "objects_detected": [
                    {
                        "type": "person",
                        "confidence": 0.9,
                        "bbox": [100, 50, 200, 300],
                        "center": [200, 200],
                        "area": 60000,
                        "distance": 2.5
                    }
                ],
                "faces_detected": [
                    {
                        "bbox": [120, 60, 160, 200],
                        "center": [200, 160],
                        "distance": 2.5,
                        "confidence": 0.85
                    }
                ],
                "scene_description": "1 pessoa detectada, pessoa mais próxima a 2.5m",
                "depth_stats": {
                    "min_distance": 0.8,
                    "max_distance": 8.5,
                    "mean_distance": 3.2,
                    "median_distance": 2.8,
                    "valid_pixels_percentage": 95.2
                },
                "depth_enabled": True,
                "resolution": self.resolution,
                "fps": self.fps
            },
            confidence=0.8,
            metadata={
                "camera_type": "mock_realsense_d435i",
                "depth_available": True,
                "analysis_performed": True
            }
        )
    
    async def _start(self) -> bool:
        """
        Início específico do G1VisionInput.
        
        Returns:
            True se o início foi bem-sucedido
        """
        try:
            self.logger.info("G1Vision iniciado")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar G1Vision: {e}")
            return False
    
    async def _stop(self) -> bool:
        """
        Parada específica do G1VisionInput.
        
        Returns:
            True se a parada foi bem-sucedida
        """
        try:
            if self.pipeline and not self.mock_mode:
                self.pipeline.stop()
                self.pipeline = None
            
            self.logger.info("G1Vision parado")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao parar G1Vision: {e}")
            return False
    
    async def _health_check(self) -> bool:
        """
        Verificação específica de saúde do G1VisionInput.
        
        Returns:
            True se está saudável
        """
        try:
            if self.mock_mode:
                return True
            
            # Testa captura de frame
            if self.pipeline:
                frames = self.pipeline.wait_for_frames()
                color_frame = frames.get_color_frame()
                return color_frame is not None
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erro na verificação de saúde: {e}")
            return False
