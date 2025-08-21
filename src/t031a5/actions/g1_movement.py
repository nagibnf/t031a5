"""
Plugin de movimento e locomoção para G1.

Implementa controle avançado de movimento, incluindo:
- Locomoção bípede (andar, correr, pular)
- Navegação autônoma
- Controle de postura e equilíbrio
- Gestos e movimentos expressivos
- Integração com GPS e visão
"""

import asyncio
import logging
import time
import math
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .base import BaseAction, ActionRequest, ActionResult
from .g1_movement_mapping import G1MovementLibrary, G1MovementType


class MovementType(Enum):
    """Tipos de movimento."""
    WALK = "walk"
    RUN = "run"
    JUMP = "jump"
    TURN = "turn"
    STOP = "stop"
    GESTURE = "gesture"
    POSTURE = "posture"
    NAVIGATE = "navigate"


class MovementStatus(Enum):
    """Status do movimento."""
    IDLE = "idle"
    MOVING = "moving"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class PostureType(Enum):
    """Tipos de postura."""
    STANDING = "standing"
    SITTING = "sitting"
    KNEELING = "kneeling"
    LYING = "lying"
    CROUCHING = "crouching"


@dataclass
class MovementCommand:
    """Comando de movimento."""
    type: MovementType
    direction: Optional[str] = None  # "forward", "backward", "left", "right"
    distance: Optional[float] = None  # metros
    speed: Optional[float] = None    # m/s
    angle: Optional[float] = None    # graus
    duration: Optional[float] = None # segundos
    target_position: Optional[Tuple[float, float]] = None  # (x, y)
    gesture_name: Optional[str] = None
    posture_type: Optional[PostureType] = None


@dataclass
class MovementState:
    """Estado do movimento."""
    current_position: Tuple[float, float]  # (x, y)
    current_orientation: float  # graus
    current_speed: float  # m/s
    current_posture: PostureType
    is_moving: bool
    target_position: Optional[Tuple[float, float]]
    movement_history: List[Dict[str, Any]]


class G1MovementAction(BaseAction):
    """
    Plugin de movimento e locomoção para G1.
    
    Funcionalidades:
    - Locomoção bípede avançada
    - Navegação autônoma
    - Controle de postura
    - Gestos expressivos
    - Integração multimodal
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.name = "G1Movement"
        
        # Configurações de movimento
        self.max_speed = config.get("max_speed", 1.5)  # m/s
        self.max_turn_speed = config.get("max_turn_speed", 90.0)  # graus/s
        self.default_speed = config.get("default_speed", 0.5)  # m/s
        self.default_turn_speed = config.get("default_turn_speed", 30.0)  # graus/s
        
        # Configurações de segurança
        self.safety_distance = config.get("safety_distance", 0.5)  # metros
        self.obstacle_detection = config.get("obstacle_detection", True)
        self.fall_prevention = config.get("fall_prevention", True)
        self.emergency_stop_distance = config.get("emergency_stop_distance", 0.2)  # metros
        
        # Configurações de postura
        self.enable_posture_control = config.get("enable_posture_control", True)
        self.posture_transition_time = config.get("posture_transition_time", 2.0)  # segundos
        
        # Configurações de navegação
        self.enable_autonomous_navigation = config.get("enable_autonomous_navigation", True)
        self.path_planning = config.get("path_planning", True)
        self.waypoint_tolerance = config.get("waypoint_tolerance", 0.1)  # metros
        
        # Biblioteca de movimentos G1
        self.movement_library = G1MovementLibrary
        
        # Estado interno
        self.movement_state = MovementState(
            current_position=(0.0, 0.0),
            current_orientation=0.0,
            current_speed=0.0,
            current_posture=PostureType.STANDING,
            is_moving=False,
            target_position=None,
            movement_history=[]
        )
        
        # Controle de movimento
        self.current_command = None
        self.movement_start_time = None
        self.movement_status = MovementStatus.IDLE
        self.obstacles_detected = []
        self.navigation_waypoints = []
        
        # Métricas
        self.total_distance_traveled = 0.0
        self.movement_commands_executed = 0
        self.movement_errors = 0
        self.average_speed = 0.0
        
        # Simulação para desenvolvimento
        self.mock_mode = config.get("mock_mode", True)
        self.simulation_speed = config.get("simulation_speed", 1.0)  # multiplicador de velocidade
        
        # Gestos predefinidos
        self.predefined_gestures = {
            "wave": {"duration": 2.0, "description": "Acenar com a mão"},
            "point": {"duration": 1.5, "description": "Apontar com o dedo"},
            "clap": {"duration": 1.0, "description": "Bater palmas"},
            "bow": {"duration": 3.0, "description": "Fazer reverência"},
            "dance": {"duration": 5.0, "description": "Dançar"},
            "salute": {"duration": 2.0, "description": "Fazer continência"},
            "hug": {"duration": 4.0, "description": "Abraçar"},
            "high_five": {"duration": 1.5, "description": "Tocar os cinco"}
        }
        
        self.logger = logging.getLogger(f"t031a5.actions.{self.name.lower()}")
    
    async def _initialize(self) -> bool:
        """Inicializa o sistema de movimento."""
        try:
            self.logger.info("Inicializando G1Movement...")
            
            # Inicializa sistema de movimento (simulado para desenvolvimento)
            if self.mock_mode:
                self.logger.info("Modo mock ativado para desenvolvimento")
                await self._initialize_mock_movement()
            else:
                # Para uso real com G1, aqui seria a inicialização do hardware
                await self._initialize_real_movement()
            
            # Inicializa controle de postura
            if self.enable_posture_control:
                await self._initialize_posture_control()
            
            # Inicializa navegação autônoma
            if self.enable_autonomous_navigation:
                await self._initialize_navigation()
            
            # Inicializa detecção de obstáculos
            if self.obstacle_detection:
                await self._initialize_obstacle_detection()
            
            self.logger.info("G1Movement inicializado com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na inicialização do G1Movement: {e}")
            return False
    
    async def _initialize_mock_movement(self):
        """Inicializa movimento em modo mock."""
        # Define posição inicial
        self.movement_state.current_position = (0.0, 0.0)
        self.movement_state.current_orientation = 0.0
        self.movement_state.current_posture = PostureType.STANDING
        
        self.logger.info("Movimento mock inicializado")
    
    async def _initialize_real_movement(self):
        """Inicializa movimento real do robô."""
        # Aqui seria a inicialização do hardware real do G1
        # Por exemplo: motores, sensores, controladores, etc.
        self.logger.info("Movimento real inicializado (simulado)")
    
    async def _initialize_posture_control(self):
        """Inicializa controle de postura."""
        try:
            # Aqui seria inicializado o sistema de controle de postura
            self.logger.info("Controle de postura inicializado")
            
        except Exception as e:
            self.logger.error(f"Erro na inicialização do controle de postura: {e}")
    
    async def _initialize_navigation(self):
        """Inicializa sistema de navegação."""
        try:
            # Aqui seria inicializado o sistema de navegação
            self.logger.info("Sistema de navegação inicializado")
            
        except Exception as e:
            self.logger.error(f"Erro na inicialização da navegação: {e}")
    
    async def _initialize_obstacle_detection(self):
        """Inicializa detecção de obstáculos."""
        try:
            # Aqui seria inicializado o sistema de detecção de obstáculos
            self.logger.info("Detecção de obstáculos inicializada")
            
        except Exception as e:
            self.logger.error(f"Erro na inicialização da detecção de obstáculos: {e}")
    
    async def execute(self, request: ActionRequest) -> ActionResult:
        """Executa comando de movimento."""
        try:
            self.logger.info(f"Executando comando de movimento: {request.data}")
            
            # Parse do comando
            movement_command = self._parse_movement_command(request.data)
            if not movement_command:
                return ActionResult(
                    action_type="movement",
                    action_name="unknown",
                    timestamp=datetime.now(),
                    success=False,
                    data={"error": "Comando não reconhecido"}
                )
            
            # Verifica segurança
            if not await self._check_safety(movement_command):
                return ActionResult(
                    action_type="movement",
                    action_name="unknown",
                    timestamp=datetime.now(),
                    success=False,
                    data={"error": "Obstáculo detectado ou condição insegura"}
                )
            
            # Executa movimento
            success = await self._execute_movement(movement_command)
            
            if success:
                self.movement_commands_executed += 1
                return ActionResult(
                    action_type="movement",
                    action_name=movement_command.type.value,
                    timestamp=datetime.now(),
                    success=True,
                    data={
                        "command": movement_command.type.value,
                        "position": self.movement_state.current_position,
                        "orientation": self.movement_state.current_orientation,
                        "posture": self.movement_state.current_posture.value
                    }
                )
            else:
                self.movement_errors += 1
                return ActionResult(
                    action_type="movement",
                    action_name="unknown",
                    timestamp=datetime.now(),
                    success=False,
                    data={"error": "Erro interno no sistema de movimento"}
                )
            
        except Exception as e:
            self.logger.error(f"Erro na execução de movimento: {e}")
            self.movement_errors += 1
            return ActionResult(
                action_type="movement",
                action_name="unknown",
                timestamp=datetime.now(),
                success=False,
                data={"error": str(e)}
            )
    
    def _parse_movement_command(self, content: Dict[str, Any]) -> Optional[MovementCommand]:
        """Parse do comando de movimento."""
        try:
            command_type = content.get("type", "").lower()
            
            if command_type == "walk":
                return MovementCommand(
                    type=MovementType.WALK,
                    direction=content.get("direction", "forward"),
                    distance=content.get("distance"),
                    speed=content.get("speed", self.default_speed),
                    duration=content.get("duration")
                )
            
            elif command_type == "run":
                return MovementCommand(
                    type=MovementType.RUN,
                    direction=content.get("direction", "forward"),
                    distance=content.get("distance"),
                    speed=content.get("speed", self.max_speed),
                    duration=content.get("duration")
                )
            
            elif command_type == "turn":
                return MovementCommand(
                    type=MovementType.TURN,
                    angle=content.get("angle"),
                    speed=content.get("speed", self.default_turn_speed),
                    duration=content.get("duration")
                )
            
            elif command_type == "jump":
                return MovementCommand(
                    type=MovementType.JUMP,
                    direction=content.get("direction"),
                    distance=content.get("distance"),
                    duration=content.get("duration", 1.0)
                )
            
            elif command_type == "stop":
                return MovementCommand(type=MovementType.STOP)
            
            elif command_type == "gesture":
                return MovementCommand(
                    type=MovementType.GESTURE,
                    gesture_name=content.get("gesture"),
                    duration=content.get("duration")
                )
            
            elif command_type == "posture":
                posture_name = content.get("posture", "standing").upper()
                try:
                    posture_type = PostureType[posture_name]
                except KeyError:
                    posture_type = PostureType.STANDING
                
                return MovementCommand(
                    type=MovementType.POSTURE,
                    posture_type=posture_type,
                    duration=content.get("duration", self.posture_transition_time)
                )
            
            elif command_type == "navigate":
                target = content.get("target_position")
                if target and len(target) == 2:
                    return MovementCommand(
                        type=MovementType.NAVIGATE,
                        target_position=tuple(target),
                        speed=content.get("speed", self.default_speed)
                    )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erro no parse do comando: {e}")
            return None
    
    async def _check_safety(self, command: MovementCommand) -> bool:
        """Verifica segurança antes de executar movimento."""
        try:
            # Verifica se há obstáculos no caminho
            if self.obstacle_detection and self.obstacles_detected:
                for obstacle in self.obstacles_detected:
                    distance = self._calculate_distance_to_obstacle(obstacle)
                    if distance < self.emergency_stop_distance:
                        self.logger.warning(f"Obstáculo muito próximo: {distance:.2f}m")
                        return False
            
            # Verifica se o movimento é seguro para a postura atual
            if command.type in [MovementType.WALK, MovementType.RUN, MovementType.JUMP]:
                if self.movement_state.current_posture != PostureType.STANDING:
                    self.logger.warning("Movimento requer postura em pé")
                    return False
            
            # Verifica limites de velocidade
            if command.speed and command.speed > self.max_speed:
                self.logger.warning(f"Velocidade muito alta: {command.speed} m/s")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na verificação de segurança: {e}")
            return False
    
    async def _execute_movement(self, command: MovementCommand) -> bool:
        """Executa o movimento especificado."""
        try:
            self.current_command = command
            self.movement_start_time = datetime.now()
            self.movement_status = MovementStatus.MOVING
            
            self.logger.info(f"Executando movimento: {command.type.value}")
            
            if command.type == MovementType.WALK:
                return await self._execute_walk(command)
            
            elif command.type == MovementType.RUN:
                return await self._execute_run(command)
            
            elif command.type == MovementType.TURN:
                return await self._execute_turn(command)
            
            elif command.type == MovementType.JUMP:
                return await self._execute_jump(command)
            
            elif command.type == MovementType.STOP:
                return await self._execute_stop(command)
            
            elif command.type == MovementType.GESTURE:
                return await self._execute_gesture(command)
            
            elif command.type == MovementType.POSTURE:
                return await self._execute_posture(command)
            
            elif command.type == MovementType.NAVIGATE:
                return await self._execute_navigate(command)
            
            else:
                self.logger.error(f"Tipo de movimento não suportado: {command.type}")
                return False
            
        except Exception as e:
            self.logger.error(f"Erro na execução de movimento: {e}")
            self.movement_status = MovementStatus.FAILED
            return False
    
    async def _execute_walk(self, command: MovementCommand) -> bool:
        """Executa movimento de caminhada."""
        try:
            direction = command.direction or "forward"
            distance = command.distance or 1.0
            speed = command.speed or self.default_speed
            
            # Calcula tempo de movimento
            duration = distance / speed if speed > 0 else 1.0
            
            # Simula movimento
            if self.mock_mode:
                await self._simulate_movement(direction, distance, speed, duration)
            else:
                # Aqui seria executado o movimento real
                await self._execute_real_walk(direction, distance, speed)
            
            # Atualiza estado
            self._update_movement_state(direction, distance, speed)
            self.movement_status = MovementStatus.COMPLETED
            
            self.logger.info(f"Caminhada executada: {direction}, {distance}m, {speed}m/s")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na execução de caminhada: {e}")
            self.movement_status = MovementStatus.FAILED
            return False
    
    async def _execute_run(self, command: MovementCommand) -> bool:
        """Executa movimento de corrida."""
        try:
            direction = command.direction or "forward"
            distance = command.distance or 2.0
            speed = command.speed or self.max_speed
            
            # Calcula tempo de movimento
            duration = distance / speed if speed > 0 else 1.0
            
            # Simula movimento
            if self.mock_mode:
                await self._simulate_movement(direction, distance, speed, duration)
            else:
                # Aqui seria executado o movimento real
                await self._execute_real_run(direction, distance, speed)
            
            # Atualiza estado
            self._update_movement_state(direction, distance, speed)
            self.movement_status = MovementStatus.COMPLETED
            
            self.logger.info(f"Corrida executada: {direction}, {distance}m, {speed}m/s")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na execução de corrida: {e}")
            self.movement_status = MovementStatus.FAILED
            return False
    
    async def _execute_turn(self, command: MovementCommand) -> bool:
        """Executa movimento de rotação."""
        try:
            angle = command.angle or 90.0
            speed = command.speed or self.default_turn_speed
            
            # Calcula tempo de rotação
            duration = abs(angle) / speed if speed > 0 else 1.0
            
            # Simula rotação
            if self.mock_mode:
                await self._simulate_rotation(angle, speed, duration)
            else:
                # Aqui seria executada a rotação real
                await self._execute_real_turn(angle, speed)
            
            # Atualiza orientação
            self.movement_state.current_orientation = (self.movement_state.current_orientation + angle) % 360
            self.movement_status = MovementStatus.COMPLETED
            
            self.logger.info(f"Rotação executada: {angle}°, {speed}°/s")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na execução de rotação: {e}")
            self.movement_status = MovementStatus.FAILED
            return False
    
    async def _execute_jump(self, command: MovementCommand) -> bool:
        """Executa movimento de pulo."""
        try:
            direction = command.direction or "up"
            distance = command.distance or 0.5
            duration = command.duration or 1.0
            
            # Simula pulo
            if self.mock_mode:
                await self._simulate_jump(direction, distance, duration)
            else:
                # Aqui seria executado o pulo real
                await self._execute_real_jump(direction, distance)
            
            self.movement_status = MovementStatus.COMPLETED
            
            self.logger.info(f"Pulo executado: {direction}, {distance}m")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na execução de pulo: {e}")
            self.movement_status = MovementStatus.FAILED
            return False
    
    async def _execute_stop(self, command: MovementCommand) -> bool:
        """Para o movimento atual."""
        try:
            # Para movimento
            self.movement_state.is_moving = False
            self.movement_state.current_speed = 0.0
            self.movement_state.target_position = None
            self.movement_status = MovementStatus.IDLE
            
            self.logger.info("Movimento parado")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao parar movimento: {e}")
            return False
    
    async def _execute_gesture(self, command: MovementCommand) -> bool:
        """Executa gesto expressivo."""
        try:
            gesture_name = command.gesture_name or "wave"
            duration = command.duration or self.predefined_gestures.get(gesture_name, {}).get("duration", 2.0)
            
            # Verifica se o gesto é conhecido
            if gesture_name not in self.predefined_gestures:
                self.logger.warning(f"Gesto não reconhecido: {gesture_name}")
                return False
            
            # Simula gesto
            if self.mock_mode:
                await self._simulate_gesture(gesture_name, duration)
            else:
                # Aqui seria executado o gesto real
                await self._execute_real_gesture(gesture_name)
            
            self.movement_status = MovementStatus.COMPLETED
            
            self.logger.info(f"Gesto executado: {gesture_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na execução de gesto: {e}")
            self.movement_status = MovementStatus.FAILED
            return False
    
    async def _execute_posture(self, command: MovementCommand) -> bool:
        """Executa mudança de postura."""
        try:
            posture_type = command.posture_type or PostureType.STANDING
            duration = command.duration or self.posture_transition_time
            
            # Verifica se a mudança é válida
            if not self._is_posture_change_valid(posture_type):
                self.logger.warning(f"Mudança de postura inválida: {posture_type.value}")
                return False
            
            # Simula mudança de postura
            if self.mock_mode:
                await self._simulate_posture_change(posture_type, duration)
            else:
                # Aqui seria executada a mudança real
                await self._execute_real_posture_change(posture_type)
            
            # Atualiza postura
            self.movement_state.current_posture = posture_type
            self.movement_status = MovementStatus.COMPLETED
            
            self.logger.info(f"Postura alterada: {posture_type.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na mudança de postura: {e}")
            self.movement_status = MovementStatus.FAILED
            return False
    
    async def _execute_navigate(self, command: MovementCommand) -> bool:
        """Executa navegação autônoma."""
        try:
            target_position = command.target_position
            speed = command.speed or self.default_speed
            
            if not target_position:
                self.logger.error("Posição alvo não especificada")
                return False
            
            # Calcula rota para o alvo
            path = await self._calculate_path_to_target(target_position)
            if not path:
                self.logger.error("Não foi possível calcular rota para o alvo")
                return False
            
            # Executa navegação
            if self.mock_mode:
                await self._simulate_navigation(path, speed)
            else:
                # Aqui seria executada a navegação real
                await self._execute_real_navigation(path, speed)
            
            # Atualiza posição
            self.movement_state.current_position = target_position
            self.movement_state.target_position = None
            self.movement_status = MovementStatus.COMPLETED
            
            self.logger.info(f"Navegação executada para: {target_position}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na navegação: {e}")
            self.movement_status = MovementStatus.FAILED
            return False
    
    # Métodos de simulação (para desenvolvimento)
    async def _simulate_movement(self, direction: str, distance: float, speed: float, duration: float):
        """Simula movimento."""
        await asyncio.sleep(duration / self.simulation_speed)
    
    async def _simulate_rotation(self, angle: float, speed: float, duration: float):
        """Simula rotação."""
        await asyncio.sleep(duration / self.simulation_speed)
    
    async def _simulate_jump(self, direction: str, distance: float, duration: float):
        """Simula pulo."""
        await asyncio.sleep(duration / self.simulation_speed)
    
    async def _simulate_gesture(self, gesture_name: str, duration: float):
        """Simula gesto."""
        await asyncio.sleep(duration / self.simulation_speed)
    
    async def _simulate_posture_change(self, posture_type: PostureType, duration: float):
        """Simula mudança de postura."""
        await asyncio.sleep(duration / self.simulation_speed)
    
    async def _simulate_navigation(self, path: List[Tuple[float, float]], speed: float):
        """Simula navegação."""
        total_distance = sum(self._calculate_distance(path[i], path[i+1]) for i in range(len(path)-1))
        duration = total_distance / speed if speed > 0 else 1.0
        await asyncio.sleep(duration / self.simulation_speed)
    
    # Métodos para implementação real (placeholders)
    async def _execute_real_walk(self, direction: str, distance: float, speed: float):
        """Executa caminhada real."""
        # Implementação real aqui
        pass
    
    async def _execute_real_run(self, direction: str, distance: float, speed: float):
        """Executa corrida real."""
        # Implementação real aqui
        pass
    
    async def _execute_real_turn(self, angle: float, speed: float):
        """Executa rotação real."""
        # Implementação real aqui
        pass
    
    async def _execute_real_jump(self, direction: str, distance: float):
        """Executa pulo real."""
        # Implementação real aqui
        pass
    
    async def _execute_real_gesture(self, gesture_name: str):
        """Executa gesto real."""
        # Implementação real aqui
        pass
    
    async def _execute_real_posture_change(self, posture_type: PostureType):
        """Executa mudança de postura real."""
        # Implementação real aqui
        pass
    
    async def _execute_real_navigation(self, path: List[Tuple[float, float]], speed: float):
        """Executa navegação real."""
        # Implementação real aqui
        pass
    
    # Métodos auxiliares
    def _update_movement_state(self, direction: str, distance: float, speed: float):
        """Atualiza estado do movimento."""
        # Calcula nova posição baseada na direção
        x, y = self.movement_state.current_position
        
        if direction == "forward":
            x += distance * math.cos(math.radians(self.movement_state.current_orientation))
            y += distance * math.sin(math.radians(self.movement_state.current_orientation))
        elif direction == "backward":
            x -= distance * math.cos(math.radians(self.movement_state.current_orientation))
            y -= distance * math.sin(math.radians(self.movement_state.current_orientation))
        elif direction == "left":
            x -= distance * math.sin(math.radians(self.movement_state.current_orientation))
            y += distance * math.cos(math.radians(self.movement_state.current_orientation))
        elif direction == "right":
            x += distance * math.sin(math.radians(self.movement_state.current_orientation))
            y -= distance * math.cos(math.radians(self.movement_state.current_orientation))
        
        self.movement_state.current_position = (x, y)
        self.movement_state.current_speed = speed
        self.total_distance_traveled += distance
        
        # Atualiza velocidade média
        if self.movement_commands_executed > 0:
            self.average_speed = self.total_distance_traveled / self.movement_commands_executed
        
        # Adiciona ao histórico
        self.movement_state.movement_history.append({
            "timestamp": datetime.now(),
            "direction": direction,
            "distance": distance,
            "speed": speed,
            "position": self.movement_state.current_position
        })
        
        # Mantém histórico limitado
        if len(self.movement_state.movement_history) > 100:
            self.movement_state.movement_history.pop(0)
    
    def _calculate_distance_to_obstacle(self, obstacle: Dict[str, Any]) -> float:
        """Calcula distância até obstáculo."""
        # Implementação simplificada
        return obstacle.get("distance", float('inf'))
    
    def _is_posture_change_valid(self, new_posture: PostureType) -> bool:
        """Verifica se mudança de postura é válida."""
        current = self.movement_state.current_posture
        
        # Regras de transição de postura
        valid_transitions = {
            PostureType.STANDING: [PostureType.SITTING, PostureType.KNEELING, PostureType.CROUCHING],
            PostureType.SITTING: [PostureType.STANDING, PostureType.LYING],
            PostureType.KNEELING: [PostureType.STANDING, PostureType.SITTING],
            PostureType.LYING: [PostureType.SITTING, PostureType.STANDING],
            PostureType.CROUCHING: [PostureType.STANDING]
        }
        
        return new_posture in valid_transitions.get(current, [])
    
    async def _calculate_path_to_target(self, target: Tuple[float, float]) -> List[Tuple[float, float]]:
        """Calcula rota para o alvo."""
        # Implementação simplificada - linha reta
        start = self.movement_state.current_position
        return [start, target]
    
    def _calculate_distance(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calcula distância entre dois pontos."""
        return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
    
    async def _stop(self) -> bool:
        """Para o sistema de movimento."""
        try:
            self.logger.info("Parando G1Movement...")
            
            # Para movimento atual
            await self._execute_stop(MovementCommand(type=MovementType.STOP))
            
            self.logger.info("G1Movement parado com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao parar G1Movement: {e}")
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """Retorna status detalhado do sistema de movimento."""
        status = await super().get_status()
        
        # Adiciona informações específicas de movimento
        status.update({
            "movement_status": self.movement_status.value,
            "current_position": self.movement_state.current_position,
            "current_orientation": self.movement_state.current_orientation,
            "current_speed": self.movement_state.current_speed,
            "current_posture": self.movement_state.current_posture.value,
            "is_moving": self.movement_state.is_moving,
            "total_distance_traveled": self.total_distance_traveled,
            "movement_commands_executed": self.movement_commands_executed,
            "movement_errors": self.movement_errors,
            "average_speed": self.average_speed,
            "obstacles_detected": len(self.obstacles_detected),
            "mock_mode": self.mock_mode
        })
        
        return status
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do sistema de movimento."""
        health = await super().health_check()
        
        # Verificações específicas de movimento
        issues = []
        
        if self.movement_errors > 10:
            issues.append("Muitos erros de movimento")
        
        if self.movement_state.current_speed > self.max_speed:
            issues.append("Velocidade acima do limite")
        
        if self.movement_status == MovementStatus.FAILED:
            issues.append("Sistema de movimento em falha")
        
        health["issues"].extend(issues)
        health["status"] = "healthy" if not issues else "warning"
        
        return health
    
    async def _execute(self, request: ActionRequest) -> ActionResult:
        """Implementação do método abstrato."""
        result = await self.execute(request)
        if result:
            return ActionResult(
                action_type="movement",
                action_name=request.action_name,
                timestamp=datetime.now(),
                success=result.success,
                data=result.data,
                execution_time=0.5,
                metadata={"source": self.name}
            )
        return ActionResult(
            action_type="movement",
            action_name=request.action_name,
            timestamp=datetime.now(),
            success=False,
            data={},
            error_message="Falha na execução",
            metadata={"source": self.name}
        )
    
    async def _start(self) -> bool:
        """Implementação do método abstrato."""
        return await self.start()
