"""
Plugin de GPS e navegação para G1.

Implementa localização GPS, navegação, rastreamento de rota
e integração com mapas para navegação autônoma.
"""

import asyncio
import logging
import time
import math
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Imports para GPS
try:
    import pynmea2
    NMEA_AVAILABLE = True
except ImportError:
    NMEA_AVAILABLE = False
    logging.warning("pynmea2 não disponível. G1GPS funcionará em modo mock.")

try:
    import geopy
    from geopy.distance import geodesic
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False
    logging.warning("geopy não disponível. Cálculos de distância em modo mock.")

from ..base import BaseInput, InputData


class GPSStatus(Enum):
    """Status do GPS."""
    NO_FIX = "no_fix"
    FIX_2D = "fix_2d"
    FIX_3D = "fix_3d"
    DGPS = "dgps"


@dataclass
class GPSLocation:
    """Localização GPS."""
    latitude: float
    longitude: float
    altitude: Optional[float]
    accuracy: float
    timestamp: datetime
    status: GPSStatus


@dataclass
class NavigationWaypoint:
    """Ponto de navegação."""
    latitude: float
    longitude: float
    name: str
    description: Optional[str]
    reached: bool = False


@dataclass
class RouteSegment:
    """Segmento de rota."""
    start: GPSLocation
    end: GPSLocation
    distance: float
    bearing: float
    estimated_time: float


class G1GPSInput(BaseInput):
    """
    Plugin de GPS e navegação para G1.
    
    Funcionalidades:
    - Localização GPS em tempo real
    - Navegação por waypoints
    - Rastreamento de rota
    - Cálculo de distâncias e bearings
    - Integração com mapas
    - Navegação autônoma
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.name = "G1GPS"
        
        # Configurações de GPS
        self.update_interval = config.get("update_interval", 1.0)
        self.accuracy_threshold = config.get("accuracy_threshold", 5.0)  # metros
        self.enable_navigation = config.get("enable_navigation", True)
        self.enable_route_tracking = config.get("enable_route_tracking", True)
        self.enable_autonomous_nav = config.get("enable_autonomous_nav", False)
        
        # Estado interno
        self.current_location = None
        self.previous_location = None
        self.waypoints = []
        self.current_route = []
        self.route_history = []
        self.navigation_active = False
        self.target_waypoint = None
        
        # Métricas
        self.fix_count = 0
        self.total_distance = 0.0
        self.average_speed = 0.0
        self.location_history = []
        self.speed_history = []
        
        # Configurações de navegação
        self.max_waypoints = config.get("max_waypoints", 100)
        self.waypoint_radius = config.get("waypoint_radius", 2.0)  # metros
        self.route_smoothing = config.get("route_smoothing", True)
        
        # Simulação para desenvolvimento
        self.mock_mode = config.get("mock_mode", True)
        self.mock_start_location = config.get("mock_start_location", {
            "latitude": -23.5505,  # São Paulo
            "longitude": -46.6333,
            "altitude": 760.0
        })
        self.mock_movement_speed = config.get("mock_movement_speed", 1.0)  # m/s
        
        self.logger = logging.getLogger(f"t031a5.inputs.plugins.{self.name.lower()}")
    
    async def _initialize(self) -> bool:
        """Inicializa o sistema GPS."""
        try:
            self.logger.info("Inicializando G1GPS...")
            
            if not NMEA_AVAILABLE:
                self.logger.warning("pynmea2 não disponível. Usando modo mock.")
            
            if not GEOPY_AVAILABLE:
                self.logger.warning("geopy não disponível. Cálculos de distância em modo mock.")
            
            # Inicializa GPS (simulado para desenvolvimento)
            if self.mock_mode:
                self.logger.info("Modo mock ativado para desenvolvimento")
                await self._initialize_mock_gps()
            else:
                # Para uso real com G1, aqui seria a inicialização do GPS
                await self._initialize_real_gps()
            
            # Inicializa navegação
            if self.enable_navigation:
                await self._initialize_navigation()
            
            self.logger.info("G1GPS inicializado com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na inicialização do G1GPS: {e}")
            return False
    
    async def _initialize_mock_gps(self):
        """Inicializa GPS em modo mock."""
        # Define localização inicial
        self.current_location = GPSLocation(
            latitude=self.mock_start_location["latitude"],
            longitude=self.mock_start_location["longitude"],
            altitude=self.mock_start_location["altitude"],
            accuracy=2.0,
            timestamp=datetime.now(),
            status=GPSStatus.FIX_3D
        )
        
        # Adiciona alguns waypoints de exemplo
        self.waypoints = [
            NavigationWaypoint(
                latitude=self.mock_start_location["latitude"] + 0.001,
                longitude=self.mock_start_location["longitude"] + 0.001,
                name="Waypoint 1",
                description="Primeiro ponto de navegação"
            ),
            NavigationWaypoint(
                latitude=self.mock_start_location["latitude"] + 0.002,
                longitude=self.mock_start_location["longitude"] + 0.002,
                name="Waypoint 2",
                description="Segundo ponto de navegação"
            )
        ]
        
        self.logger.info("GPS mock inicializado")
    
    async def _initialize_real_gps(self):
        """Inicializa GPS real."""
        # Aqui seria a inicialização do hardware GPS do G1
        # Por exemplo: serial connection, I2C, etc.
        self.logger.info("GPS real inicializado (simulado)")
    
    async def _initialize_navigation(self):
        """Inicializa sistema de navegação."""
        try:
            # Carrega waypoints salvos (se houver)
            await self._load_waypoints()
            
            # Inicializa rota atual
            if self.waypoints:
                await self._calculate_route()
            
            self.logger.info("Sistema de navegação inicializado")
            
        except Exception as e:
            self.logger.error(f"Erro na inicialização da navegação: {e}")
    
    async def _collect_data(self) -> InputData:
        """Coleta dados GPS."""
        try:
            # Atualiza localização
            await self._update_location()
            
            if self.current_location is None:
                return InputData(
                    content={"error": "Sem fix GPS"},
                    confidence=0.0,
                    timestamp=datetime.now(),
                    metadata={"source": self.name},
                    source=self.name
                )
            
            # Calcula métricas
            await self._calculate_metrics()
            
            # Atualiza navegação
            if self.enable_navigation:
                await self._update_navigation()
            
            # Prepara dados de saída
            gps_data = self._prepare_gps_data()
            
            # Calcula confiança baseada na qualidade do fix
            confidence = self._calculate_confidence()
            
            return InputData(
                input_type="gps",
                source=self.name,
                timestamp=datetime.now(),
                data=gps_data,
                confidence=confidence,
                metadata={
                    "fix_count": self.fix_count,
                    "total_distance": self.total_distance,
                    "average_speed": self.average_speed
                }
            )
            
        except Exception as e:
            self.logger.error(f"Erro na coleta de dados GPS: {e}")
            return InputData(
                content={"error": str(e)},
                confidence=0.0,
                timestamp=datetime.now(),
                metadata={"source": self.name},
                source=self.name
            )
    
    async def _update_location(self):
        """Atualiza localização GPS."""
        try:
            if self.mock_mode:
                await self._update_mock_location()
            else:
                await self._update_real_location()
            
            # Atualiza histórico
            if self.current_location:
                self.location_history.append(self.current_location)
                if len(self.location_history) > 1000:
                    self.location_history.pop(0)
                
                self.fix_count += 1
            
        except Exception as e:
            self.logger.error(f"Erro na atualização de localização: {e}")
    
    async def _update_mock_location(self):
        """Atualiza localização em modo mock."""
        if self.current_location is None:
            return
        
        # Simula movimento
        current_time = time.time()
        time_diff = current_time - self.current_location.timestamp.timestamp()
        distance_moved = self.mock_movement_speed * time_diff
        
        # Calcula nova posição (movimento em direção ao primeiro waypoint)
        if self.waypoints and not self.navigation_active:
            target = self.waypoints[0]
            bearing = self._calculate_bearing(
                self.current_location.latitude, self.current_location.longitude,
                target.latitude, target.longitude
            )
            
            # Move na direção do waypoint
            new_lat, new_lon = self._move_coordinates(
                self.current_location.latitude, self.current_location.longitude,
                bearing, distance_moved
            )
            
            self.previous_location = self.current_location
            self.current_location = GPSLocation(
                latitude=new_lat,
                longitude=new_lon,
                altitude=self.current_location.altitude,
                accuracy=2.0 + (time.time() % 3),  # Variação na precisão
                timestamp=datetime.now(),
                status=GPSStatus.FIX_3D
            )
        else:
            # Movimento aleatório
            bearing = (time.time() * 10) % 360
            new_lat, new_lon = self._move_coordinates(
                self.current_location.latitude, self.current_location.longitude,
                bearing, distance_moved
            )
            
            self.previous_location = self.current_location
            self.current_location = GPSLocation(
                latitude=new_lat,
                longitude=new_lon,
                altitude=self.current_location.altitude,
                accuracy=2.0 + (time.time() % 3),
                timestamp=datetime.now(),
                status=GPSStatus.FIX_3D
            )
    
    async def _update_real_location(self):
        """Atualiza localização GPS real."""
        # Aqui seria a leitura real do GPS
        # Por exemplo: ler dados NMEA, processar, etc.
        pass
    
    async def _calculate_metrics(self):
        """Calcula métricas GPS."""
        try:
            if self.previous_location and self.current_location:
                # Calcula distância percorrida
                distance = self._calculate_distance(
                    self.previous_location.latitude, self.previous_location.longitude,
                    self.current_location.latitude, self.current_location.longitude
                )
                
                self.total_distance += distance
                
                # Calcula velocidade
                time_diff = (self.current_location.timestamp - self.previous_location.timestamp).total_seconds()
                if time_diff > 0:
                    speed = distance / time_diff
                    self.speed_history.append(speed)
                    if len(self.speed_history) > 100:
                        self.speed_history.pop(0)
                    
                    self.average_speed = sum(self.speed_history) / len(self.speed_history)
            
        except Exception as e:
            self.logger.error(f"Erro no cálculo de métricas: {e}")
    
    async def _update_navigation(self):
        """Atualiza sistema de navegação."""
        try:
            if not self.waypoints or not self.current_location:
                return
            
            # Verifica se chegou ao waypoint atual
            if self.target_waypoint:
                distance_to_target = self._calculate_distance(
                    self.current_location.latitude, self.current_location.longitude,
                    self.target_waypoint.latitude, self.target_waypoint.longitude
                )
                
                if distance_to_target <= self.waypoint_radius:
                    self.target_waypoint.reached = True
                    self.logger.info(f"Waypoint alcançado: {self.target_waypoint.name}")
                    
                    # Move para o próximo waypoint
                    await self._next_waypoint()
            
            # Se não há waypoint ativo, ativa o primeiro
            if not self.target_waypoint and self.waypoints:
                await self._next_waypoint()
            
        except Exception as e:
            self.logger.error(f"Erro na atualização de navegação: {e}")
    
    async def _next_waypoint(self):
        """Move para o próximo waypoint."""
        try:
            # Encontra próximo waypoint não alcançado
            for waypoint in self.waypoints:
                if not waypoint.reached:
                    self.target_waypoint = waypoint
                    self.navigation_active = True
                    self.logger.info(f"Navegando para: {waypoint.name}")
                    return
            
            # Todos os waypoints alcançados
            self.navigation_active = False
            self.target_waypoint = None
            self.logger.info("Todos os waypoints foram alcançados")
            
        except Exception as e:
            self.logger.error(f"Erro ao avançar waypoint: {e}")
    
    def _prepare_gps_data(self) -> Dict[str, Any]:
        """Prepara dados GPS para saída."""
        if not self.current_location:
            return {"error": "Sem dados GPS"}
        
        gps_data = {
            "location": {
                "latitude": self.current_location.latitude,
                "longitude": self.current_location.longitude,
                "altitude": self.current_location.altitude,
                "accuracy": self.current_location.accuracy,
                "status": self.current_location.status.value,
                "timestamp": self.current_location.timestamp.isoformat()
            },
            "navigation": {
                "active": self.navigation_active,
                "target_waypoint": self.target_waypoint.name if self.target_waypoint else None,
                "waypoints": [
                    {
                        "name": wp.name,
                        "latitude": wp.latitude,
                        "longitude": wp.longitude,
                        "reached": wp.reached
                    }
                    for wp in self.waypoints
                ],
                "total_waypoints": len(self.waypoints),
                "reached_waypoints": sum(1 for wp in self.waypoints if wp.reached)
            },
            "metrics": {
                "total_distance": self.total_distance,
                "average_speed": self.average_speed,
                "fix_count": self.fix_count,
                "current_speed": self.speed_history[-1] if self.speed_history else 0.0
            }
        }
        
        # Adiciona informações de rota se disponível
        if self.current_route:
            gps_data["route"] = {
                "segments": len(self.current_route),
                "total_route_distance": sum(seg.distance for seg in self.current_route),
                "estimated_time": sum(seg.estimated_time for seg in self.current_route)
            }
        
        return gps_data
    
    def _calculate_confidence(self) -> float:
        """Calcula confiança baseada na qualidade do GPS."""
        if not self.current_location:
            return 0.0
        
        confidence = 0.5  # Confiança base
        
        # Ajusta baseado na precisão
        if self.current_location.accuracy <= 1.0:
            confidence += 0.3
        elif self.current_location.accuracy <= 3.0:
            confidence += 0.2
        elif self.current_location.accuracy <= 5.0:
            confidence += 0.1
        
        # Ajusta baseado no status
        if self.current_location.status == GPSStatus.FIX_3D:
            confidence += 0.2
        elif self.current_location.status == GPSStatus.FIX_2D:
            confidence += 0.1
        
        # Ajusta baseado na consistência
        if len(self.speed_history) > 10:
            speed_variance = self._calculate_variance(self.speed_history)
            if speed_variance < 1.0:  # Velocidade consistente
                confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcula distância entre duas coordenadas."""
        if GEOPY_AVAILABLE:
            return geodesic((lat1, lon1), (lat2, lon2)).meters
        else:
            # Implementação simplificada (fórmula de Haversine)
            R = 6371000  # Raio da Terra em metros
            
            lat1_rad = math.radians(lat1)
            lat2_rad = math.radians(lat2)
            delta_lat = math.radians(lat2 - lat1)
            delta_lon = math.radians(lon2 - lon1)
            
            a = (math.sin(delta_lat / 2) ** 2 +
                 math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            
            return R * c
    
    def _calculate_bearing(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcula bearing entre duas coordenadas."""
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lon = math.radians(lon2 - lon1)
        
        y = math.sin(delta_lon) * math.cos(lat2_rad)
        x = (math.cos(lat1_rad) * math.sin(lat2_rad) -
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon))
        
        bearing = math.degrees(math.atan2(y, x))
        return (bearing + 360) % 360
    
    def _move_coordinates(self, lat: float, lon: float, bearing: float, distance: float) -> Tuple[float, float]:
        """Move coordenadas por uma distância e bearing."""
        R = 6371000  # Raio da Terra em metros
        
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        bearing_rad = math.radians(bearing)
        
        angular_distance = distance / R
        
        new_lat_rad = math.asin(
            math.sin(lat_rad) * math.cos(angular_distance) +
            math.cos(lat_rad) * math.sin(angular_distance) * math.cos(bearing_rad)
        )
        
        new_lon_rad = lon_rad + math.atan2(
            math.sin(bearing_rad) * math.sin(angular_distance) * math.cos(lat_rad),
            math.cos(angular_distance) - math.sin(lat_rad) * math.sin(new_lat_rad)
        )
        
        return math.degrees(new_lat_rad), math.degrees(new_lon_rad)
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calcula variância de uma lista de valores."""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
    
    async def _calculate_route(self):
        """Calcula rota entre waypoints."""
        try:
            if len(self.waypoints) < 2:
                return
            
            self.current_route = []
            
            for i in range(len(self.waypoints) - 1):
                start = self.waypoints[i]
                end = self.waypoints[i + 1]
                
                # Cria localização temporária para o waypoint
                start_loc = GPSLocation(
                    latitude=start.latitude,
                    longitude=start.longitude,
                    altitude=None,
                    accuracy=0.0,
                    timestamp=datetime.now(),
                    status=GPSStatus.FIX_3D
                )
                
                end_loc = GPSLocation(
                    latitude=end.latitude,
                    longitude=end.longitude,
                    altitude=None,
                    accuracy=0.0,
                    timestamp=datetime.now(),
                    status=GPSStatus.FIX_3D
                )
                
                distance = self._calculate_distance(
                    start.latitude, start.longitude,
                    end.latitude, end.longitude
                )
                
                bearing = self._calculate_bearing(
                    start.latitude, start.longitude,
                    end.latitude, end.longitude
                )
                
                # Tempo estimado baseado na velocidade média
                estimated_time = distance / self.average_speed if self.average_speed > 0 else 0
                
                segment = RouteSegment(
                    start=start_loc,
                    end=end_loc,
                    distance=distance,
                    bearing=bearing,
                    estimated_time=estimated_time
                )
                
                self.current_route.append(segment)
            
            self.logger.info(f"Rota calculada com {len(self.current_route)} segmentos")
            
        except Exception as e:
            self.logger.error(f"Erro no cálculo de rota: {e}")
    
    async def _load_waypoints(self):
        """Carrega waypoints salvos."""
        # Aqui seria carregado de arquivo ou banco de dados
        # Por enquanto, usa waypoints de exemplo
        pass
    
    async def _stop(self) -> bool:
        """Para o sistema GPS."""
        try:
            self.logger.info("Parando G1GPS...")
            
            # Salva waypoints e histórico
            await self._save_waypoints()
            await self._save_route_history()
            
            self.logger.info("G1GPS parado com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao parar G1GPS: {e}")
            return False
    
    async def _save_waypoints(self):
        """Salva waypoints."""
        # Aqui seria salvo em arquivo ou banco de dados
        pass
    
    async def _save_route_history(self):
        """Salva histórico de rota."""
        # Aqui seria salvo em arquivo ou banco de dados
        pass
    
    async def get_status(self) -> Dict[str, Any]:
        """Retorna status detalhado do GPS."""
        status = await super().get_status()
        
        # Adiciona informações específicas de GPS
        status.update({
            "gps_status": self.current_location.status.value if self.current_location else "no_fix",
            "accuracy": self.current_location.accuracy if self.current_location else 0.0,
            "total_distance": self.total_distance,
            "average_speed": self.average_speed,
            "fix_count": self.fix_count,
            "navigation_active": self.navigation_active,
            "waypoints_count": len(self.waypoints),
            "reached_waypoints": sum(1 for wp in self.waypoints if wp.reached),
            "nmea_available": NMEA_AVAILABLE,
            "geopy_available": GEOPY_AVAILABLE,
            "mock_mode": self.mock_mode
        })
        
        return status
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do sistema GPS."""
        health = await super().health_check()
        
        # Verificações específicas de GPS
        issues = []
        
        if not NMEA_AVAILABLE:
            issues.append("pynmea2 não disponível")
        
        if not GEOPY_AVAILABLE:
            issues.append("geopy não disponível")
        
        if self.current_location and self.current_location.accuracy > 10.0:
            issues.append("Precisão GPS baixa")
        
        if self.fix_count > 0 and len(self.speed_history) > 10:
            if max(self.speed_history) > 50.0:  # Velocidade muito alta
                issues.append("Velocidade GPS anômala")
        
        health["issues"].extend(issues)
        health["status"] = "healthy" if not issues else "warning"
        
        return health
    
    async def _get_data(self) -> Optional[InputData]:
        """Implementação do método abstrato."""
        data = await self._collect_data()
        if data:
            return InputData(
                input_type="gps",
                source=self.name,
                timestamp=datetime.now(),
                data=data,
                confidence=data.get("confidence", 0.9),
                metadata={"source": self.name}
            )
        return None
    
    async def _start(self) -> bool:
        """Implementação do método abstrato."""
        return await self.start()
