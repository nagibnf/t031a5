"""
Coletor de métricas para o sistema t031a5.

Coleta e gerencia métricas de performance, uso de recursos e eventos.
"""

import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from .structured_logger import StructuredLogger, LogContext


class MetricsCollector:
    """Coletor de métricas avançado."""
    
    def __init__(self, logger: Optional[StructuredLogger] = None):
        """
        Inicializa o coletor de métricas.
        
        Args:
            logger: Logger estruturado (opcional)
        """
        self.logger = logger or StructuredLogger("metrics")
        self.start_time = datetime.now()
        
        # Métricas em tempo real
        self.current_metrics = {
            "system": {
                "uptime": 0.0,
                "cpu_usage": 0.0,
                "memory_usage": 0.0,
                "disk_usage": 0.0
            },
            "performance": {
                "avg_loop_time": 0.0,
                "total_loops": 0,
                "errors": 0,
                "success_rate": 100.0
            },
            "components": defaultdict(dict),
            "events": deque(maxlen=1000)
        }
        
        # Histórico de métricas (últimas 24 horas)
        self.history = {
            "performance": deque(maxlen=8640),  # 24h * 10s
            "system": deque(maxlen=8640),
            "components": defaultdict(lambda: deque(maxlen=8640))
        }
        
        # Timers ativos
        self.active_timers = {}
        
        # Contadores
        self.counters = defaultdict(int)
        
        # Gauge values
        self.gauges = {}
    
    def start_timer(self, name: str) -> str:
        """
        Inicia um timer.
        
        Args:
            name: Nome do timer
            
        Returns:
            ID do timer
        """
        timer_id = f"{name}_{int(time.time() * 1000)}"
        self.active_timers[timer_id] = {
            "name": name,
            "start_time": time.time(),
            "context": None
        }
        return timer_id
    
    def start_timer_with_context(self, name: str, context: LogContext) -> str:
        """
        Inicia um timer com contexto.
        
        Args:
            name: Nome do timer
            context: Contexto do log
            
        Returns:
            ID do timer
        """
        timer_id = self.start_timer(name)
        self.active_timers[timer_id]["context"] = context
        return timer_id
    
    def stop_timer(self, timer_id: str) -> Optional[float]:
        """
        Para um timer e retorna a duração.
        
        Args:
            timer_id: ID do timer
            
        Returns:
            Duração em segundos ou None se timer não encontrado
        """
        if timer_id not in self.active_timers:
            return None
        
        timer = self.active_timers.pop(timer_id)
        duration = time.time() - timer["start_time"]
        
        # Log de performance
        if timer["context"]:
            self.logger.log_performance(timer["name"], duration, timer["context"])
        
        # Atualiza métricas
        self.record_performance(timer["name"], duration)
        
        return duration
    
    def record_performance(self, operation: str, duration: float):
        """
        Registra métrica de performance.
        
        Args:
            operation: Nome da operação
            duration: Duração em segundos
        """
        # Atualiza métricas atuais
        if "performance" not in self.current_metrics["components"][operation]:
            self.current_metrics["components"][operation]["performance"] = {
                "count": 0,
                "total_time": 0.0,
                "avg_time": 0.0,
                "min_time": float('inf'),
                "max_time": 0.0
            }
        
        perf = self.current_metrics["components"][operation]["performance"]
        perf["count"] += 1
        perf["total_time"] += duration
        perf["avg_time"] = perf["total_time"] / perf["count"]
        perf["min_time"] = min(perf["min_time"], duration)
        perf["max_time"] = max(perf["max_time"], duration)
        
        # Adiciona ao histórico
        self.history["components"][operation].append({
            "timestamp": datetime.now(),
            "duration": duration,
            "avg_time": perf["avg_time"]
        })
    
    def increment_counter(self, name: str, value: int = 1):
        """
        Incrementa um contador.
        
        Args:
            name: Nome do contador
            value: Valor a incrementar
        """
        self.counters[name] += value
        self.logger.log_metric(f"counter_{name}", self.counters[name])
    
    def set_gauge(self, name: str, value: Union[int, float]):
        """
        Define um valor de gauge.
        
        Args:
            name: Nome do gauge
            value: Valor
        """
        self.gauges[name] = value
        self.logger.log_metric(f"gauge_{name}", value)
    
    def record_event(self, event_type: str, event_data: Dict[str, Any]):
        """
        Registra um evento.
        
        Args:
            event_type: Tipo do evento
            event_data: Dados do evento
        """
        event = {
            "timestamp": datetime.now(),
            "type": event_type,
            "data": event_data
        }
        
        self.current_metrics["events"].append(event)
        self.logger.log_event(event_type, event_data)
    
    def update_system_metrics(self, cpu: float, memory: float, disk: float):
        """
        Atualiza métricas do sistema.
        
        Args:
            cpu: Uso de CPU (%)
            memory: Uso de memória (%)
            disk: Uso de disco (%)
        """
        self.current_metrics["system"]["cpu_usage"] = cpu
        self.current_metrics["system"]["memory_usage"] = memory
        self.current_metrics["system"]["disk_usage"] = disk
        self.current_metrics["system"]["uptime"] = (datetime.now() - self.start_time).total_seconds()
        
        # Adiciona ao histórico
        self.history["system"].append({
            "timestamp": datetime.now(),
            "cpu": cpu,
            "memory": memory,
            "disk": disk,
            "uptime": self.current_metrics["system"]["uptime"]
        })
    
    def update_performance_metrics(self, loop_time: float, total_loops: int, errors: int):
        """
        Atualiza métricas de performance do sistema.
        
        Args:
            loop_time: Tempo do último loop
            total_loops: Total de loops executados
            errors: Total de erros
        """
        self.current_metrics["performance"]["avg_loop_time"] = loop_time
        self.current_metrics["performance"]["total_loops"] = total_loops
        self.current_metrics["performance"]["errors"] = errors
        
        if total_loops > 0:
            success_rate = ((total_loops - errors) / total_loops) * 100
            self.current_metrics["performance"]["success_rate"] = success_rate
        
        # Adiciona ao histórico
        self.history["performance"].append({
            "timestamp": datetime.now(),
            "loop_time": loop_time,
            "total_loops": total_loops,
            "errors": errors,
            "success_rate": self.current_metrics["performance"]["success_rate"]
        })
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Retorna métricas atuais."""
        return self.current_metrics.copy()
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Retorna resumo das métricas."""
        summary = {
            "uptime": self.current_metrics["system"]["uptime"],
            "total_loops": self.current_metrics["performance"]["total_loops"],
            "success_rate": self.current_metrics["performance"]["success_rate"],
            "avg_loop_time": self.current_metrics["performance"]["avg_loop_time"],
            "total_events": len(self.current_metrics["events"]),
            "active_timers": len(self.active_timers),
            "counters": dict(self.counters),
            "gauges": self.gauges.copy()
        }
        
        # Resumo por componente
        component_summary = {}
        for component, metrics in self.current_metrics["components"].items():
            if "performance" in metrics:
                perf = metrics["performance"]
                component_summary[component] = {
                    "operations": perf["count"],
                    "avg_time": perf["avg_time"],
                    "min_time": perf["min_time"],
                    "max_time": perf["max_time"]
                }
        
        summary["components"] = component_summary
        return summary
    
    def get_metrics_history(self, hours: int = 1) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retorna histórico de métricas.
        
        Args:
            hours: Número de horas para retornar
            
        Returns:
            Histórico de métricas
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        history = {}
        for metric_type, data in self.history.items():
            if isinstance(data, deque):
                history[metric_type] = [
                    item for item in data 
                    if item["timestamp"] > cutoff_time
                ]
            else:
                # Para componentes
                history[metric_type] = {}
                for component, component_data in data.items():
                    history[metric_type][component] = [
                        item for item in component_data
                        if item["timestamp"] > cutoff_time
                    ]
        
        return history
    
    def export_metrics(self, format: str = "json") -> str:
        """
        Exporta métricas em formato específico.
        
        Args:
            format: Formato de exportação (json, csv)
            
        Returns:
            Métricas exportadas
        """
        import json
        
        if format.lower() == "json":
            return json.dumps({
                "current": self.get_current_metrics(),
                "summary": self.get_metrics_summary(),
                "history": self.get_metrics_history(1)
            }, indent=2, default=str)
        else:
            raise ValueError(f"Formato não suportado: {format}")
    
    def reset_metrics(self):
        """Reseta todas as métricas."""
        self.current_metrics = {
            "system": {
                "uptime": 0.0,
                "cpu_usage": 0.0,
                "memory_usage": 0.0,
                "disk_usage": 0.0
            },
            "performance": {
                "avg_loop_time": 0.0,
                "total_loops": 0,
                "errors": 0,
                "success_rate": 100.0
            },
            "components": defaultdict(dict),
            "events": deque(maxlen=1000)
        }
        
        self.history = {
            "performance": deque(maxlen=8640),
            "system": deque(maxlen=8640),
            "components": defaultdict(lambda: deque(maxlen=8640))
        }
        
        self.active_timers.clear()
        self.counters.clear()
        self.gauges.clear()
        
        self.start_time = datetime.now()
