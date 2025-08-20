"""
Plugin de estado interno do robô G1.

Implementa monitoramento completo do estado do robô, incluindo:
- Estado dos motores e articulações
- Sistema de energia e bateria
- Temperatura e sistema térmico
- Estado de segurança e emergência
- Status de comunicação e conectividade
"""

import asyncio
import logging
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import math

from ..base import BaseInput, InputData


class RobotMode(Enum):
    """Modos de operação do robô."""
    IDLE = "idle"
    WALKING = "walking"
    STANDING = "standing"
    SITTING = "sitting"
    EMERGENCY_STOP = "emergency_stop"
    CALIBRATION = "calibration"
    MAINTENANCE = "maintenance"
    ERROR = "error"


class SafetyStatus(Enum):
    """Status de segurança."""
    SAFE = "safe"
    WARNING = "warning"
    DANGER = "danger"
    EMERGENCY = "emergency"


class BatteryStatus(Enum):
    """Status da bateria."""
    FULL = "full"
    GOOD = "good"
    LOW = "low"
    CRITICAL = "critical"
    CHARGING = "charging"


@dataclass
class JointState:
    """Estado de uma articulação."""
    name: str
    position: float  # radianos
    velocity: float  # rad/s
    effort: float    # Nm
    temperature: float  # °C
    status: str      # "normal", "warning", "error"


@dataclass
class MotorState:
    """Estado de um motor."""
    name: str
    current: float   # A
    voltage: float   # V
    temperature: float  # °C
    rpm: float       # RPM
    status: str      # "normal", "warning", "error"


@dataclass
class BatteryState:
    """Estado da bateria."""
    level: float     # 0.0-1.0
    voltage: float   # V
    current: float   # A
    temperature: float  # °C
    status: BatteryStatus
    time_remaining: Optional[float]  # minutos


@dataclass
class ThermalState:
    """Estado térmico do sistema."""
    cpu_temperature: float  # °C
    motor_temperature: float  # °C
    battery_temperature: float  # °C
    ambient_temperature: float  # °C
    cooling_status: str  # "active", "passive", "error"


@dataclass
class SafetyState:
    """Estado de segurança."""
    emergency_stop_active: bool
    safety_zones_violated: List[str]
    collision_detected: bool
    fall_detected: bool
    status: SafetyStatus
    last_incident: Optional[datetime]


class G1StateInput(BaseInput):
    """
    Plugin de estado interno do robô G1.
    
    Funcionalidades:
    - Monitoramento de articulações e motores
    - Sistema de energia e bateria
    - Controle térmico
    - Estado de segurança
    - Status de comunicação
    - Diagnóstico de saúde
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.name = "G1State"
        
        # Configurações de monitoramento
        self.update_interval = config.get("update_interval", 0.1)
        self.enable_joint_monitoring = config.get("enable_joint_monitoring", True)
        self.enable_motor_monitoring = config.get("enable_motor_monitoring", True)
        self.enable_battery_monitoring = config.get("enable_battery_monitoring", True)
        self.enable_thermal_monitoring = config.get("enable_thermal_monitoring", True)
        self.enable_safety_monitoring = config.get("enable_safety_monitoring", True)
        
        # Thresholds de alerta
        self.temperature_warning = config.get("temperature_warning", 60.0)  # °C
        self.temperature_critical = config.get("temperature_critical", 80.0)  # °C
        self.battery_warning = config.get("battery_warning", 0.2)  # 20%
        self.battery_critical = config.get("battery_critical", 0.1)  # 10%
        self.joint_effort_warning = config.get("joint_effort_warning", 50.0)  # Nm
        self.joint_effort_critical = config.get("joint_effort_critical", 80.0)  # Nm
        
        # Estado interno
        self.current_mode = RobotMode.IDLE
        self.previous_mode = RobotMode.IDLE
        self.joints = {}
        self.motors = {}
        self.battery = None
        self.thermal = None
        self.safety = None
        
        # Histórico e métricas
        self.state_history = []
        self.alert_history = []
        self.uptime = 0.0
        self.last_update = datetime.now()
        
        # Simulação para desenvolvimento
        self.mock_mode = config.get("mock_mode", True)
        self.mock_data_file = config.get("mock_data_file", None)
        
        # Configurações de articulações (baseado no G1 real)
        self.joint_names = [
            "hip_yaw_left", "hip_roll_left", "hip_pitch_left",
            "knee_pitch_left", "ankle_pitch_left", "ankle_roll_left",
            "hip_yaw_right", "hip_roll_right", "hip_pitch_right",
            "knee_pitch_right", "ankle_pitch_right", "ankle_roll_right",
            "shoulder_pitch_left", "shoulder_roll_left", "shoulder_yaw_left",
            "elbow_pitch_left", "wrist_pitch_left", "wrist_roll_left",
            "shoulder_pitch_right", "shoulder_roll_right", "shoulder_yaw_right",
            "elbow_pitch_right", "wrist_pitch_right", "wrist_roll_right"
        ]
        
        # Configurações de motores
        self.motor_names = [
            "motor_hip_left", "motor_knee_left", "motor_ankle_left",
            "motor_hip_right", "motor_knee_right", "motor_ankle_right",
            "motor_shoulder_left", "motor_elbow_left", "motor_wrist_left",
            "motor_shoulder_right", "motor_elbow_right", "motor_wrist_right"
        ]
        
        self.logger = logging.getLogger(f"t031a5.inputs.plugins.{self.name.lower()}")
    
    async def _initialize(self) -> bool:
        """Inicializa o sistema de monitoramento de estado."""
        try:
            self.logger.info("Inicializando G1State...")
            
            # Inicializa monitoramento (simulado para desenvolvimento)
            if self.mock_mode:
                self.logger.info("Modo mock ativado para desenvolvimento")
                await self._initialize_mock_state()
            else:
                # Para uso real com G1, aqui seria a inicialização do hardware
                await self._initialize_real_state()
            
            # Inicializa articulações
            if self.enable_joint_monitoring:
                await self._initialize_joints()
            
            # Inicializa motores
            if self.enable_motor_monitoring:
                await self._initialize_motors()
            
            # Inicializa bateria
            if self.enable_battery_monitoring:
                await self._initialize_battery()
            
            # Inicializa sistema térmico
            if self.enable_thermal_monitoring:
                await self._initialize_thermal()
            
            # Inicializa sistema de segurança
            if self.enable_safety_monitoring:
                await self._initialize_safety()
            
            self.logger.info("G1State inicializado com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na inicialização do G1State: {e}")
            return False
    
    async def _initialize_mock_state(self):
        """Inicializa estado em modo mock."""
        # Carrega dados mock se arquivo especificado
        if self.mock_data_file:
            try:
                with open(self.mock_data_file, 'r') as f:
                    mock_data = json.load(f)
                    self.logger.info(f"Dados mock carregados de {self.mock_data_file}")
            except Exception as e:
                self.logger.warning(f"Erro ao carregar dados mock: {e}")
                mock_data = {}
        else:
            mock_data = {}
        
        # Define estado inicial
        self.current_mode = RobotMode.IDLE
        self.uptime = 0.0
        
        self.logger.info("Estado mock inicializado")
    
    async def _initialize_real_state(self):
        """Inicializa estado real do robô."""
        # Aqui seria a inicialização do hardware real do G1
        # Por exemplo: conexão com controladores, sensores, etc.
        self.logger.info("Estado real inicializado (simulado)")
    
    async def _initialize_joints(self):
        """Inicializa monitoramento de articulações."""
        try:
            for joint_name in self.joint_names:
                self.joints[joint_name] = JointState(
                    name=joint_name,
                    position=0.0,
                    velocity=0.0,
                    effort=0.0,
                    temperature=25.0,
                    status="normal"
                )
            
            self.logger.info(f"Monitoramento de {len(self.joints)} articulações inicializado")
            
        except Exception as e:
            self.logger.error(f"Erro na inicialização de articulações: {e}")
    
    async def _initialize_motors(self):
        """Inicializa monitoramento de motores."""
        try:
            for motor_name in self.motor_names:
                self.motors[motor_name] = MotorState(
                    name=motor_name,
                    current=0.0,
                    voltage=24.0,
                    temperature=25.0,
                    rpm=0.0,
                    status="normal"
                )
            
            self.logger.info(f"Monitoramento de {len(self.motors)} motores inicializado")
            
        except Exception as e:
            self.logger.error(f"Erro na inicialização de motores: {e}")
    
    async def _initialize_battery(self):
        """Inicializa monitoramento de bateria."""
        try:
            self.battery = BatteryState(
                level=0.85,
                voltage=48.0,
                current=2.0,
                temperature=30.0,
                status=BatteryStatus.GOOD,
                time_remaining=120.0  # 2 horas
            )
            
            self.logger.info("Monitoramento de bateria inicializado")
            
        except Exception as e:
            self.logger.error(f"Erro na inicialização de bateria: {e}")
    
    async def _initialize_thermal(self):
        """Inicializa monitoramento térmico."""
        try:
            self.thermal = ThermalState(
                cpu_temperature=45.0,
                motor_temperature=35.0,
                battery_temperature=30.0,
                ambient_temperature=25.0,
                cooling_status="passive"
            )
            
            self.logger.info("Monitoramento térmico inicializado")
            
        except Exception as e:
            self.logger.error(f"Erro na inicialização térmica: {e}")
    
    async def _initialize_safety(self):
        """Inicializa sistema de segurança."""
        try:
            self.safety = SafetyState(
                emergency_stop_active=False,
                safety_zones_violated=[],
                collision_detected=False,
                fall_detected=False,
                status=SafetyStatus.SAFE,
                last_incident=None
            )
            
            self.logger.info("Sistema de segurança inicializado")
            
        except Exception as e:
            self.logger.error(f"Erro na inicialização de segurança: {e}")
    
    async def _collect_data(self) -> InputData:
        """Coleta dados de estado do robô."""
        try:
            # Atualiza estado
            await self._update_state()
            
            # Calcula métricas
            await self._calculate_metrics()
            
            # Verifica alertas
            alerts = await self._check_alerts()
            
            # Prepara dados de saída
            state_data = self._prepare_state_data()
            
            # Calcula confiança baseada na qualidade dos dados
            confidence = self._calculate_confidence()
            
            return InputData(
                input_type="state",
                source=self.name,
                timestamp=datetime.now(),
                data=state_data,
                confidence=confidence,
                metadata={
                    "uptime": self.uptime,
                    "mode": self.current_mode.value,
                    "alerts_count": len(alerts)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Erro na coleta de dados de estado: {e}")
            return InputData(
                content={"error": str(e)},
                confidence=0.0,
                timestamp=datetime.now(),
                metadata={"source": self.name},
                source=self.name
            )
    
    async def _update_state(self):
        """Atualiza estado do robô."""
        try:
            current_time = datetime.now()
            
            # Atualiza uptime
            if self.last_update:
                time_diff = (current_time - self.last_update).total_seconds()
                self.uptime += time_diff
            
            self.last_update = current_time
            
            # Atualiza modo do robô (simulado)
            await self._update_robot_mode()
            
            # Atualiza articulações
            if self.enable_joint_monitoring:
                await self._update_joints()
            
            # Atualiza motores
            if self.enable_motor_monitoring:
                await self._update_motors()
            
            # Atualiza bateria
            if self.enable_battery_monitoring:
                await self._update_battery()
            
            # Atualiza sistema térmico
            if self.enable_thermal_monitoring:
                await self._update_thermal()
            
            # Atualiza segurança
            if self.enable_safety_monitoring:
                await self._update_safety()
            
            # Salva no histórico
            self.state_history.append({
                "timestamp": current_time,
                "mode": self.current_mode.value,
                "battery_level": self.battery.level if self.battery else 0.0,
                "temperature": self.thermal.cpu_temperature if self.thermal else 0.0
            })
            
            # Mantém histórico limitado
            if len(self.state_history) > 1000:
                self.state_history.pop(0)
            
        except Exception as e:
            self.logger.error(f"Erro na atualização de estado: {e}")
    
    async def _update_robot_mode(self):
        """Atualiza modo do robô."""
        try:
            # Simulação de mudança de modo
            # Em implementação real, aqui seria lido do controlador
            current_time = time.time()
            
            # Simula mudanças de modo baseadas no tempo
            mode_cycle = int(current_time / 30) % 4  # Muda a cada 30 segundos
            
            modes = [RobotMode.IDLE, RobotMode.STANDING, RobotMode.WALKING, RobotMode.SITTING]
            new_mode = modes[mode_cycle]
            
            if new_mode != self.current_mode:
                self.previous_mode = self.current_mode
                self.current_mode = new_mode
                self.logger.info(f"Modo do robô alterado: {self.previous_mode.value} -> {self.current_mode.value}")
            
        except Exception as e:
            self.logger.error(f"Erro na atualização de modo: {e}")
    
    async def _update_joints(self):
        """Atualiza estado das articulações."""
        try:
            current_time = time.time()
            
            for joint_name, joint in self.joints.items():
                # Simula movimento das articulações
                base_position = math.sin(current_time + hash(joint_name) % 100) * 0.5
                joint.position = base_position
                joint.velocity = math.cos(current_time + hash(joint_name) % 100) * 0.1
                joint.effort = abs(math.sin(current_time * 2 + hash(joint_name) % 100)) * 30.0
                joint.temperature = 25.0 + abs(math.sin(current_time * 0.5 + hash(joint_name) % 100)) * 15.0
                
                # Atualiza status baseado em thresholds
                if joint.temperature > self.temperature_critical:
                    joint.status = "error"
                elif joint.temperature > self.temperature_warning:
                    joint.status = "warning"
                elif joint.effort > self.joint_effort_critical:
                    joint.status = "error"
                elif joint.effort > self.joint_effort_warning:
                    joint.status = "warning"
                else:
                    joint.status = "normal"
            
        except Exception as e:
            self.logger.error(f"Erro na atualização de articulações: {e}")
    
    async def _update_motors(self):
        """Atualiza estado dos motores."""
        try:
            current_time = time.time()
            
            for motor_name, motor in self.motors.items():
                # Simula estado dos motores
                motor.current = 2.0 + abs(math.sin(current_time + hash(motor_name) % 100)) * 3.0
                motor.voltage = 24.0 + (math.sin(current_time * 0.1 + hash(motor_name) % 100)) * 2.0
                motor.temperature = 30.0 + abs(math.sin(current_time * 0.3 + hash(motor_name) % 100)) * 20.0
                motor.rpm = abs(math.sin(current_time * 2 + hash(motor_name) % 100)) * 100.0
                
                # Atualiza status baseado em temperatura
                if motor.temperature > self.temperature_critical:
                    motor.status = "error"
                elif motor.temperature > self.temperature_warning:
                    motor.status = "warning"
                else:
                    motor.status = "normal"
            
        except Exception as e:
            self.logger.error(f"Erro na atualização de motores: {e}")
    
    async def _update_battery(self):
        """Atualiza estado da bateria."""
        try:
            if not self.battery:
                return
            
            current_time = time.time()
            
            # Simula descarga gradual da bateria
            discharge_rate = 0.0001  # Taxa de descarga por segundo
            self.battery.level = max(0.0, self.battery.level - discharge_rate)
            
            # Atualiza outros parâmetros
            self.battery.voltage = 48.0 * self.battery.level + (math.sin(current_time * 0.1) * 1.0)
            self.battery.current = 2.0 + abs(math.sin(current_time * 0.5)) * 1.0
            self.battery.temperature = 30.0 + abs(math.sin(current_time * 0.2)) * 10.0
            
            # Atualiza status da bateria
            if self.battery.level <= self.battery_critical:
                self.battery.status = BatteryStatus.CRITICAL
            elif self.battery.level <= self.battery_warning:
                self.battery.status = BatteryStatus.LOW
            elif self.battery.level >= 0.9:
                self.battery.status = BatteryStatus.FULL
            else:
                self.battery.status = BatteryStatus.GOOD
            
            # Calcula tempo restante
            if self.battery.current > 0:
                self.battery.time_remaining = (self.battery.level * 100) / (self.battery.current * 60)  # minutos
            else:
                self.battery.time_remaining = None
            
        except Exception as e:
            self.logger.error(f"Erro na atualização de bateria: {e}")
    
    async def _update_thermal(self):
        """Atualiza estado térmico."""
        try:
            if not self.thermal:
                return
            
            current_time = time.time()
            
            # Simula variação térmica
            self.thermal.cpu_temperature = 45.0 + abs(math.sin(current_time * 0.1)) * 15.0
            self.thermal.motor_temperature = 35.0 + abs(math.sin(current_time * 0.2)) * 20.0
            self.thermal.battery_temperature = 30.0 + abs(math.sin(current_time * 0.15)) * 10.0
            self.thermal.ambient_temperature = 25.0 + abs(math.sin(current_time * 0.05)) * 5.0
            
            # Atualiza status de resfriamento
            max_temp = max(
                self.thermal.cpu_temperature,
                self.thermal.motor_temperature,
                self.thermal.battery_temperature
            )
            
            if max_temp > self.temperature_critical:
                self.thermal.cooling_status = "error"
            elif max_temp > self.temperature_warning:
                self.thermal.cooling_status = "active"
            else:
                self.thermal.cooling_status = "passive"
            
        except Exception as e:
            self.logger.error(f"Erro na atualização térmica: {e}")
    
    async def _update_safety(self):
        """Atualiza estado de segurança."""
        try:
            if not self.safety:
                return
            
            current_time = time.time()
            
            # Simula eventos de segurança
            # Em implementação real, aqui seria lido dos sensores de segurança
            
            # Simula detecção de colisão ocasional
            if current_time % 60 < 1:  # 1 segundo a cada minuto
                self.safety.collision_detected = True
                self.safety.last_incident = datetime.now()
            else:
                self.safety.collision_detected = False
            
            # Simula violação de zona de segurança
            if current_time % 120 < 2:  # 2 segundos a cada 2 minutos
                self.safety.safety_zones_violated = ["zone_1", "zone_2"]
            else:
                self.safety.safety_zones_violated = []
            
            # Atualiza status de segurança
            if self.safety.emergency_stop_active or self.safety.collision_detected:
                self.safety.status = SafetyStatus.EMERGENCY
            elif self.safety.safety_zones_violated or self.safety.fall_detected:
                self.safety.status = SafetyStatus.DANGER
            elif len(self.safety.safety_zones_violated) > 0:
                self.safety.status = SafetyStatus.WARNING
            else:
                self.safety.status = SafetyStatus.SAFE
            
        except Exception as e:
            self.logger.error(f"Erro na atualização de segurança: {e}")
    
    async def _calculate_metrics(self):
        """Calcula métricas do sistema."""
        try:
            # Métricas podem ser calculadas aqui
            # Por exemplo: eficiência energética, performance, etc.
            pass
            
        except Exception as e:
            self.logger.error(f"Erro no cálculo de métricas: {e}")
    
    async def _check_alerts(self) -> List[Dict[str, Any]]:
        """Verifica alertas do sistema."""
        alerts = []
        
        try:
            # Verifica bateria
            if self.battery and self.battery.status in [BatteryStatus.LOW, BatteryStatus.CRITICAL]:
                alerts.append({
                    "type": "battery",
                    "level": "warning" if self.battery.status == BatteryStatus.LOW else "critical",
                    "message": f"Bateria {self.battery.status.value}: {self.battery.level:.1%}"
                })
            
            # Verifica temperatura
            if self.thermal:
                max_temp = max(
                    self.thermal.cpu_temperature,
                    self.thermal.motor_temperature,
                    self.thermal.battery_temperature
                )
                
                if max_temp > self.temperature_critical:
                    alerts.append({
                        "type": "thermal",
                        "level": "critical",
                        "message": f"Temperatura crítica: {max_temp:.1f}°C"
                    })
                elif max_temp > self.temperature_warning:
                    alerts.append({
                        "type": "thermal",
                        "level": "warning",
                        "message": f"Temperatura alta: {max_temp:.1f}°C"
                    })
            
            # Verifica segurança
            if self.safety and self.safety.status != SafetyStatus.SAFE:
                alerts.append({
                    "type": "safety",
                    "level": self.safety.status.value,
                    "message": f"Status de segurança: {self.safety.status.value}"
                })
            
            # Verifica articulações
            for joint_name, joint in self.joints.items():
                if joint.status == "error":
                    alerts.append({
                        "type": "joint",
                        "level": "critical",
                        "message": f"Articulação {joint_name} em erro"
                    })
                elif joint.status == "warning":
                    alerts.append({
                        "type": "joint",
                        "level": "warning",
                        "message": f"Articulação {joint_name} com aviso"
                    })
            
            # Adiciona alertas ao histórico
            for alert in alerts:
                self.alert_history.append({
                    "timestamp": datetime.now(),
                    **alert
                })
            
            # Mantém histórico limitado
            if len(self.alert_history) > 100:
                self.alert_history.pop(0)
            
        except Exception as e:
            self.logger.error(f"Erro na verificação de alertas: {e}")
        
        return alerts
    
    def _prepare_state_data(self) -> Dict[str, Any]:
        """Prepara dados de estado para saída."""
        state_data = {
            "robot_mode": self.current_mode.value,
            "uptime": self.uptime,
            "timestamp": datetime.now().isoformat()
        }
        
        # Adiciona dados de articulações
        if self.enable_joint_monitoring:
            state_data["joints"] = {
                name: {
                    "position": joint.position,
                    "velocity": joint.velocity,
                    "effort": joint.effort,
                    "temperature": joint.temperature,
                    "status": joint.status
                }
                for name, joint in self.joints.items()
            }
        
        # Adiciona dados de motores
        if self.enable_motor_monitoring:
            state_data["motors"] = {
                name: {
                    "current": motor.current,
                    "voltage": motor.voltage,
                    "temperature": motor.temperature,
                    "rpm": motor.rpm,
                    "status": motor.status
                }
                for name, motor in self.motors.items()
            }
        
        # Adiciona dados de bateria
        if self.enable_battery_monitoring and self.battery:
            state_data["battery"] = {
                "level": self.battery.level,
                "voltage": self.battery.voltage,
                "current": self.battery.current,
                "temperature": self.battery.temperature,
                "status": self.battery.status.value,
                "time_remaining": self.battery.time_remaining
            }
        
        # Adiciona dados térmicos
        if self.enable_thermal_monitoring and self.thermal:
            state_data["thermal"] = {
                "cpu_temperature": self.thermal.cpu_temperature,
                "motor_temperature": self.thermal.motor_temperature,
                "battery_temperature": self.thermal.battery_temperature,
                "ambient_temperature": self.thermal.ambient_temperature,
                "cooling_status": self.thermal.cooling_status
            }
        
        # Adiciona dados de segurança
        if self.enable_safety_monitoring and self.safety:
            state_data["safety"] = {
                "emergency_stop_active": self.safety.emergency_stop_active,
                "safety_zones_violated": self.safety.safety_zones_violated,
                "collision_detected": self.safety.collision_detected,
                "fall_detected": self.safety.fall_detected,
                "status": self.safety.status.value,
                "last_incident": self.safety.last_incident.isoformat() if self.safety.last_incident else None
            }
        
        return state_data
    
    def _calculate_confidence(self) -> float:
        """Calcula confiança baseada na qualidade dos dados."""
        confidence = 0.8  # Confiança base
        
        # Ajusta baseado no status geral
        if self.safety and self.safety.status == SafetyStatus.SAFE:
            confidence += 0.1
        
        if self.battery and self.battery.status in [BatteryStatus.GOOD, BatteryStatus.FULL]:
            confidence += 0.05
        
        if self.thermal and self.thermal.cooling_status == "passive":
            confidence += 0.05
        
        # Reduz confiança se há muitos alertas
        if len(self.alert_history) > 10:
            confidence -= 0.1
        
        return min(confidence, 1.0)
    
    async def _stop(self) -> bool:
        """Para o sistema de monitoramento de estado."""
        try:
            self.logger.info("Parando G1State...")
            
            # Salva estado final
            await self._save_state()
            
            self.logger.info("G1State parado com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao parar G1State: {e}")
            return False
    
    async def _save_state(self):
        """Salva estado atual."""
        # Aqui seria salvo em arquivo ou banco de dados
        pass
    
    async def get_status(self) -> Dict[str, Any]:
        """Retorna status detalhado do sistema de estado."""
        status = await super().get_status()
        
        # Adiciona informações específicas de estado
        status.update({
            "robot_mode": self.current_mode.value,
            "uptime": self.uptime,
            "joints_count": len(self.joints),
            "motors_count": len(self.motors),
            "battery_level": self.battery.level if self.battery else 0.0,
            "battery_status": self.battery.status.value if self.battery else "unknown",
            "safety_status": self.safety.status.value if self.safety else "unknown",
            "alerts_count": len(self.alert_history),
            "mock_mode": self.mock_mode
        })
        
        return status
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do sistema de estado."""
        health = await super().health_check()
        
        # Verificações específicas de estado
        issues = []
        
        if self.battery and self.battery.status in [BatteryStatus.LOW, BatteryStatus.CRITICAL]:
            issues.append(f"Bateria {self.battery.status.value}")
        
        if self.thermal and self.thermal.cooling_status == "error":
            issues.append("Sistema de resfriamento com erro")
        
        if self.safety and self.safety.status != SafetyStatus.SAFE:
            issues.append(f"Status de segurança: {self.safety.status.value}")
        
        # Verifica articulações com erro
        error_joints = [name for name, joint in self.joints.items() if joint.status == "error"]
        if error_joints:
            issues.append(f"Articulações com erro: {', '.join(error_joints)}")
        
        # Verifica motores com erro
        error_motors = [name for name, motor in self.motors.items() if motor.status == "error"]
        if error_motors:
            issues.append(f"Motores com erro: {', '.join(error_motors)}")
        
        health["issues"].extend(issues)
        health["status"] = "healthy" if not issues else "warning"
        
        return health
    
    async def _get_data(self) -> Optional[InputData]:
        """Implementação do método abstrato."""
        data = await self._collect_data()
        if data:
            return InputData(
                input_type="state",
                source=self.name,
                timestamp=datetime.now(),
                data=data,
                confidence=data.get("confidence", 0.95),
                metadata={"source": self.name}
            )
        return None
    
    async def _start(self) -> bool:
        """Implementação do método abstrato."""
        return await self.start()
