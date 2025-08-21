"""
Sistema de Segurança para G1 Tobias
Inclui botão STOP, regras de proteção e monitoramento contínuo
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)


class SafetyLevel(Enum):
    """Níveis de segurança do sistema."""
    SAFE = "safe"
    WARNING = "warning"
    DANGER = "danger"
    EMERGENCY = "emergency"


class SafetyRule(Enum):
    """Regras de segurança disponíveis."""
    PROXIMITY_CHECK = "proximity_check"
    BATTERY_LEVEL = "battery_level"
    TIMEOUT_CHECK = "timeout_check"
    MOVEMENT_BOUNDS = "movement_bounds"
    AUDIO_LIMITS = "audio_limits"
    EMERGENCY_STOP = "emergency_stop"


@dataclass
class SafetyEvent:
    """Evento de segurança detectado."""
    timestamp: float
    rule: SafetyRule
    level: SafetyLevel
    description: str
    data: Dict[str, Any]
    handled: bool = False


@dataclass
class SafetyConfig:
    """Configuração do sistema de segurança."""
    # Proximidade
    min_distance_meters: float = 0.5
    proximity_check_interval: float = 1.0
    
    # Bateria
    battery_warning_level: float = 20.0
    battery_critical_level: float = 10.0
    
    # Timeouts
    max_operation_time: float = 300.0  # 5 minutos
    max_idle_time: float = 600.0      # 10 minutos
    
    # Movimentos
    max_speed: float = 0.5
    movement_bounds: Dict[str, float] = None
    
    # Áudio
    max_volume: int = 80
    max_audio_duration: float = 30.0
    
    # Geral
    enable_emergency_stop: bool = True
    auto_recovery: bool = True
    log_all_events: bool = True


class SafetyManager:
    """Gerenciador de segurança do robô G1."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o gerenciador de segurança.
        
        Args:
            config: Configuração do sistema
        """
        self.config = SafetyConfig(**config.get("safety", {}))
        self.name = "SafetyManager"
        
        # Estado do sistema
        self.is_initialized = False
        self.is_monitoring = False
        self.emergency_stop_active = False
        
        # Eventos e histórico
        self.events: List[SafetyEvent] = []
        self.max_events = config.get("max_safety_events", 1000)
        
        # Callbacks
        self.on_safety_event: Optional[Callable] = None
        self.on_emergency_stop: Optional[Callable] = None
        self.on_safety_clear: Optional[Callable] = None
        
        # Estado operacional
        self.last_activity_time = time.time()
        self.operation_start_time = time.time()
        self.current_level = SafetyLevel.SAFE
        
        # Monitoramento
        self.monitoring_task: Optional[asyncio.Task] = None
        self.rules_enabled: Dict[SafetyRule, bool] = {}
        
        # Inicializa regras
        self._initialize_rules()
        
        logger.debug("SafetyManager configurado")
    
    def _initialize_rules(self):
        """Inicializa regras de segurança."""
        default_rules = {
            SafetyRule.PROXIMITY_CHECK: True,
            SafetyRule.BATTERY_LEVEL: True,
            SafetyRule.TIMEOUT_CHECK: True,
            SafetyRule.MOVEMENT_BOUNDS: True,
            SafetyRule.AUDIO_LIMITS: True,
            SafetyRule.EMERGENCY_STOP: True
        }
        self.rules_enabled.update(default_rules)
    
    async def initialize(self) -> bool:
        """
        Inicializa o sistema de segurança.
        
        Returns:
            True se a inicialização foi bem-sucedida
        """
        try:
            logger.info("Inicializando SafetyManager...")
            
            # Reset estado
            self.emergency_stop_active = False
            self.current_level = SafetyLevel.SAFE
            self.last_activity_time = time.time()
            self.operation_start_time = time.time()
            
            # Inicia monitoramento
            await self.start_monitoring()
            
            self.is_initialized = True
            
            logger.info("SafetyManager inicializado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro na inicialização do SafetyManager: {e}")
            return False
    
    async def start_monitoring(self):
        """Inicia o monitoramento contínuo."""
        if self.monitoring_task and not self.monitoring_task.done():
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Monitoramento de segurança iniciado")
    
    async def stop_monitoring(self):
        """Para o monitoramento."""
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("Monitoramento de segurança parado")
    
    async def emergency_stop(self, reason: str = "Manual emergency stop") -> bool:
        """
        Ativa parada de emergência.
        
        Args:
            reason: Motivo da parada
            
        Returns:
            True se a parada foi ativada
        """
        try:
            logger.warning(f"🚨 PARADA DE EMERGÊNCIA: {reason}")
            
            self.emergency_stop_active = True
            self.current_level = SafetyLevel.EMERGENCY
            
            # Registra evento
            event = SafetyEvent(
                timestamp=time.time(),
                rule=SafetyRule.EMERGENCY_STOP,
                level=SafetyLevel.EMERGENCY,
                description=f"Emergency stop activated: {reason}",
                data={"reason": reason}
            )
            await self._handle_safety_event(event)
            
            # Callback
            if self.on_emergency_stop:
                await self.on_emergency_stop(reason)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na parada de emergência: {e}")
            return False
    
    async def clear_emergency_stop(self) -> bool:
        """
        Limpa a parada de emergência.
        
        Returns:
            True se a parada foi limpa
        """
        try:
            if not self.emergency_stop_active:
                return True
            
            logger.info("🟢 Limpando parada de emergência...")
            
            self.emergency_stop_active = False
            self.current_level = SafetyLevel.SAFE
            self.last_activity_time = time.time()
            
            # Callback
            if self.on_safety_clear:
                await self.on_safety_clear()
            
            logger.info("✅ Parada de emergência limpa")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao limpar parada de emergência: {e}")
            return False
    
    async def check_movement_safety(self, x: float, y: float, yaw: float, speed: float) -> bool:
        """
        Verifica se um movimento é seguro.
        
        Args:
            x: Movimento X
            y: Movimento Y 
            yaw: Rotação
            speed: Velocidade
            
        Returns:
            True se o movimento é seguro
        """
        try:
            if self.emergency_stop_active:
                return False
            
            # Verifica velocidade máxima
            if speed > self.config.max_speed:
                await self._create_safety_event(
                    SafetyRule.MOVEMENT_BOUNDS,
                    SafetyLevel.WARNING,
                    f"Velocidade muito alta: {speed} > {self.config.max_speed}",
                    {"speed": speed, "max_speed": self.config.max_speed}
                )
                return False
            
            # Verifica limites de movimento
            if self.config.movement_bounds:
                bounds = self.config.movement_bounds
                if (abs(x) > bounds.get("max_x", 1.0) or 
                    abs(y) > bounds.get("max_y", 1.0) or 
                    abs(yaw) > bounds.get("max_yaw", 1.0)):
                    
                    await self._create_safety_event(
                        SafetyRule.MOVEMENT_BOUNDS,
                        SafetyLevel.WARNING,
                        f"Movimento fora dos limites: x={x}, y={y}, yaw={yaw}",
                        {"x": x, "y": y, "yaw": yaw, "bounds": bounds}
                    )
                    return False
            
            # Atualiza atividade
            self.last_activity_time = time.time()
            return True
            
        except Exception as e:
            logger.error(f"Erro na verificação de movimento: {e}")
            return False
    
    async def check_audio_safety(self, volume: int, duration: float = None) -> bool:
        """
        Verifica se comando de áudio é seguro.
        
        Args:
            volume: Volume do áudio
            duration: Duração estimada
            
        Returns:
            True se o áudio é seguro
        """
        try:
            if self.emergency_stop_active:
                return False
            
            # Verifica volume máximo
            if volume > self.config.max_volume:
                await self._create_safety_event(
                    SafetyRule.AUDIO_LIMITS,
                    SafetyLevel.WARNING,
                    f"Volume muito alto: {volume} > {self.config.max_volume}",
                    {"volume": volume, "max_volume": self.config.max_volume}
                )
                return False
            
            # Verifica duração máxima
            if duration and duration > self.config.max_audio_duration:
                await self._create_safety_event(
                    SafetyRule.AUDIO_LIMITS,
                    SafetyLevel.WARNING,
                    f"Áudio muito longo: {duration}s > {self.config.max_audio_duration}s",
                    {"duration": duration, "max_duration": self.config.max_audio_duration}
                )
                return False
            
            # Atualiza atividade
            self.last_activity_time = time.time()
            return True
            
        except Exception as e:
            logger.error(f"Erro na verificação de áudio: {e}")
            return False
    
    async def update_battery_level(self, battery_level: float):
        """Atualiza nível da bateria e verifica segurança."""
        try:
            if battery_level <= self.config.battery_critical_level:
                await self._create_safety_event(
                    SafetyRule.BATTERY_LEVEL,
                    SafetyLevel.EMERGENCY,
                    f"Bateria crítica: {battery_level}%",
                    {"battery_level": battery_level}
                )
                await self.emergency_stop("Bateria crítica")
                
            elif battery_level <= self.config.battery_warning_level:
                await self._create_safety_event(
                    SafetyRule.BATTERY_LEVEL,
                    SafetyLevel.WARNING,
                    f"Bateria baixa: {battery_level}%",
                    {"battery_level": battery_level}
                )
                
        except Exception as e:
            logger.error(f"Erro ao atualizar bateria: {e}")
    
    async def _monitoring_loop(self):
        """Loop principal de monitoramento."""
        try:
            while self.is_monitoring:
                # Verifica timeouts
                await self._check_timeouts()
                
                # Verifica proximidade (placeholder)
                await self._check_proximity()
                
                # Atualiza nível de segurança
                await self._update_safety_level()
                
                # Aguarda próxima verificação
                await asyncio.sleep(self.config.proximity_check_interval)
                
        except asyncio.CancelledError:
            logger.debug("Monitoramento cancelado")
        except Exception as e:
            logger.error(f"Erro no loop de monitoramento: {e}")
    
    async def _check_timeouts(self):
        """Verifica timeouts de operação."""
        try:
            current_time = time.time()
            
            # Timeout de operação
            operation_time = current_time - self.operation_start_time
            if operation_time > self.config.max_operation_time:
                await self._create_safety_event(
                    SafetyRule.TIMEOUT_CHECK,
                    SafetyLevel.WARNING,
                    f"Tempo de operação excedido: {operation_time:.1f}s",
                    {"operation_time": operation_time}
                )
            
            # Timeout de inatividade
            idle_time = current_time - self.last_activity_time
            if idle_time > self.config.max_idle_time:
                await self._create_safety_event(
                    SafetyRule.TIMEOUT_CHECK,
                    SafetyLevel.WARNING,
                    f"Sistema inativo por muito tempo: {idle_time:.1f}s",
                    {"idle_time": idle_time}
                )
                
        except Exception as e:
            logger.error(f"Erro na verificação de timeouts: {e}")
    
    async def _check_proximity(self):
        """Verifica proximidade (placeholder - integrar com sensores)."""
        # TODO: Integrar com sensores de proximidade quando disponíveis
        pass
    
    async def _update_safety_level(self):
        """Atualiza nível geral de segurança."""
        try:
            if self.emergency_stop_active:
                self.current_level = SafetyLevel.EMERGENCY
                return
            
            # Conta eventos recentes por nível
            recent_time = time.time() - 60  # Últimos 60 segundos
            recent_events = [e for e in self.events if e.timestamp > recent_time]
            
            danger_events = len([e for e in recent_events if e.level == SafetyLevel.DANGER])
            warning_events = len([e for e in recent_events if e.level == SafetyLevel.WARNING])
            
            if danger_events > 0:
                self.current_level = SafetyLevel.DANGER
            elif warning_events > 2:  # Múltiplos warnings = perigo
                self.current_level = SafetyLevel.DANGER
            elif warning_events > 0:
                self.current_level = SafetyLevel.WARNING
            else:
                self.current_level = SafetyLevel.SAFE
                
        except Exception as e:
            logger.error(f"Erro ao atualizar nível de segurança: {e}")
    
    async def _create_safety_event(self, rule: SafetyRule, level: SafetyLevel, 
                                  description: str, data: Dict[str, Any]):
        """Cria e processa evento de segurança."""
        event = SafetyEvent(
            timestamp=time.time(),
            rule=rule,
            level=level,
            description=description,
            data=data
        )
        await self._handle_safety_event(event)
    
    async def _handle_safety_event(self, event: SafetyEvent):
        """Processa evento de segurança."""
        try:
            # Adiciona ao histórico
            self.events.append(event)
            
            # Limita histórico
            if len(self.events) > self.max_events:
                self.events.pop(0)
            
            # Log
            if self.config.log_all_events:
                logger.warning(f"🚨 Evento de segurança [{event.level.value}]: {event.description}")
            
            # Callback
            if self.on_safety_event:
                await self.on_safety_event(event)
            
            # Auto-recovery para eventos não críticos
            if (self.config.auto_recovery and 
                event.level != SafetyLevel.EMERGENCY and 
                not self.emergency_stop_active):
                # Implementar recuperação automática
                pass
            
            event.handled = True
            
        except Exception as e:
            logger.error(f"Erro ao processar evento de segurança: {e}")
    
    async def get_status(self) -> Dict[str, Any]:
        """Retorna status do sistema de segurança."""
        recent_events = [e for e in self.events if e.timestamp > time.time() - 300]  # 5 min
        
        return {
            "initialized": self.is_initialized,
            "monitoring": self.is_monitoring,
            "emergency_stop": self.emergency_stop_active,
            "current_level": self.current_level.value,
            "total_events": len(self.events),
            "recent_events": len(recent_events),
            "operation_time": time.time() - self.operation_start_time,
            "idle_time": time.time() - self.last_activity_time,
            "rules_enabled": {rule.value: enabled for rule, enabled in self.rules_enabled.items()}
        }
    
    async def get_recent_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retorna eventos recentes."""
        recent = sorted(self.events, key=lambda e: e.timestamp, reverse=True)[:limit]
        return [
            {
                "timestamp": e.timestamp,
                "rule": e.rule.value,
                "level": e.level.value,
                "description": e.description,
                "data": e.data,
                "handled": e.handled
            }
            for e in recent
        ]
    
    async def stop(self) -> bool:
        """Para o sistema de segurança."""
        try:
            logger.info("Parando SafetyManager...")
            
            await self.stop_monitoring()
            self.is_initialized = False
            
            logger.info("SafetyManager parado")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao parar SafetyManager: {e}")
            return False
