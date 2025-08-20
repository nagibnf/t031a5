"""
Logger estruturado para o sistema t031a5.

Fornece logging estruturado com contexto, métricas e performance.
"""

import json
import logging
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Union

from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table


class LogLevel(Enum):
    """Níveis de log disponíveis."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogContext:
    """Contexto de log estruturado."""
    
    def __init__(self, **kwargs):
        self.data = kwargs
        self.timestamp = datetime.now()
        self.session_id = kwargs.get("session_id", "default")
        self.component = kwargs.get("component", "unknown")
        self.operation = kwargs.get("operation", "unknown")
    
    def update(self, **kwargs):
        """Atualiza o contexto."""
        self.data.update(kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "session_id": self.session_id,
            "component": self.component,
            "operation": self.operation,
            **self.data
        }


class StructuredLogger:
    """Logger estruturado avançado."""
    
    def __init__(
        self,
        name: str,
        log_file: Optional[Path] = None,
        console_output: bool = True,
        json_output: bool = False,
        level: LogLevel = LogLevel.INFO
    ):
        """
        Inicializa o logger estruturado.
        
        Args:
            name: Nome do logger
            log_file: Arquivo de log (opcional)
            console_output: Se deve sair no console
            json_output: Se deve usar formato JSON
            level: Nível de log
        """
        self.name = name
        self.log_file = log_file
        self.console_output = console_output
        self.json_output = json_output
        self.level = level
        
        # Configura logger base
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.value))
        
        # Remove handlers existentes
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Configura handlers
        self._setup_handlers()
        
        # Console Rich
        self.console = Console() if console_output else None
        
        # Métricas
        self.metrics = {
            "total_logs": 0,
            "logs_by_level": {level.value: 0 for level in LogLevel},
            "logs_by_component": {},
            "performance": {
                "avg_log_time": 0.0,
                "total_log_time": 0.0
            }
        }
    
    def _setup_handlers(self):
        """Configura os handlers de log."""
        formatter = self._create_formatter()
        
        # Handler de console
        if self.console_output:
            if self.json_output:
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(formatter)
            else:
                console_handler = RichHandler(console=Console(), rich_tracebacks=True)
                console_handler.setFormatter(logging.Formatter("%(message)s"))
            
            self.logger.addHandler(console_handler)
        
        # Handler de arquivo
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def _create_formatter(self):
        """Cria o formatador apropriado."""
        if self.json_output:
            return logging.Formatter("%(message)s")
        else:
            return logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
    
    def _log_with_context(
        self,
        level: LogLevel,
        message: str,
        context: Optional[LogContext] = None,
        **kwargs
    ):
        """Log com contexto estruturado."""
        start_time = time.time()
        
        # Prepara dados do log
        log_data = {
            "level": level.value,
            "message": message,
            "logger": self.name,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }
        
        # Adiciona contexto se disponível
        if context:
            log_data["context"] = context.to_dict()
        
        # Formata mensagem
        if self.json_output:
            formatted_message = json.dumps(log_data, ensure_ascii=False)
        else:
            # Formato legível
            context_str = f" [{context.component}:{context.operation}]" if context else ""
            formatted_message = f"{message}{context_str}"
        
        # Log
        log_method = getattr(self.logger, level.value.lower())
        log_method(formatted_message)
        
        # Atualiza métricas
        self._update_metrics(level, context, time.time() - start_time)
    
    def _update_metrics(self, level: LogLevel, context: Optional[LogContext], log_time: float):
        """Atualiza métricas de logging."""
        self.metrics["total_logs"] += 1
        self.metrics["logs_by_level"][level.value] += 1
        
        if context:
            component = context.component
            if component not in self.metrics["logs_by_component"]:
                self.metrics["logs_by_component"][component] = 0
            self.metrics["logs_by_component"][component] += 1
        
        # Métricas de performance
        total_time = self.metrics["performance"]["total_log_time"] + log_time
        total_logs = self.metrics["total_logs"]
        
        self.metrics["performance"]["total_log_time"] = total_time
        self.metrics["performance"]["avg_log_time"] = total_time / total_logs
    
    def debug(self, message: str, context: Optional[LogContext] = None, **kwargs):
        """Log de debug."""
        self._log_with_context(LogLevel.DEBUG, message, context, **kwargs)
    
    def info(self, message: str, context: Optional[LogContext] = None, **kwargs):
        """Log de informação."""
        self._log_with_context(LogLevel.INFO, message, context, **kwargs)
    
    def warning(self, message: str, context: Optional[LogContext] = None, **kwargs):
        """Log de aviso."""
        self._log_with_context(LogLevel.WARNING, message, context, **kwargs)
    
    def error(self, message: str, context: Optional[LogContext] = None, **kwargs):
        """Log de erro."""
        self._log_with_context(LogLevel.ERROR, message, context, **kwargs)
    
    def critical(self, message: str, context: Optional[LogContext] = None, **kwargs):
        """Log crítico."""
        self._log_with_context(LogLevel.CRITICAL, message, context, **kwargs)
    
    def log_performance(self, operation: str, duration: float, context: Optional[LogContext] = None):
        """Log específico para performance."""
        self.info(
            f"Performance: {operation} took {duration*1000:.2f}ms",
            context,
            operation=operation,
            duration_ms=duration*1000
        )
    
    def log_metric(self, metric_name: str, value: Union[int, float, str], context: Optional[LogContext] = None):
        """Log específico para métricas."""
        self.info(
            f"Metric: {metric_name} = {value}",
            context,
            metric_name=metric_name,
            metric_value=value
        )
    
    def log_event(self, event_type: str, event_data: Dict[str, Any], context: Optional[LogContext] = None):
        """Log específico para eventos."""
        self.info(
            f"Event: {event_type}",
            context,
            event_type=event_type,
            event_data=event_data
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do logger."""
        return self.metrics.copy()
    
    def print_metrics_table(self):
        """Imprime métricas em formato de tabela."""
        if not self.console:
            return
        
        table = Table(title=f"Métricas do Logger: {self.name}")
        table.add_column("Métrica", style="cyan")
        table.add_column("Valor", style="magenta")
        
        # Métricas gerais
        table.add_row("Total de logs", str(self.metrics["total_logs"]))
        table.add_row("Tempo médio de log", f"{self.metrics['performance']['avg_log_time']*1000:.2f}ms")
        
        # Logs por nível
        for level, count in self.metrics["logs_by_level"].items():
            if count > 0:
                table.add_row(f"Logs {level}", str(count))
        
        # Logs por componente
        for component, count in self.metrics["logs_by_component"].items():
            table.add_row(f"Logs {component}", str(count))
        
        self.console.print(table)
    
    def reset_metrics(self):
        """Reseta as métricas."""
        self.metrics = {
            "total_logs": 0,
            "logs_by_level": {level.value: 0 for level in LogLevel},
            "logs_by_component": {},
            "performance": {
                "avg_log_time": 0.0,
                "total_log_time": 0.0
            }
        }


# Logger global
_global_logger: Optional[StructuredLogger] = None


def get_global_logger() -> StructuredLogger:
    """Retorna o logger global."""
    global _global_logger
    if _global_logger is None:
        _global_logger = StructuredLogger("t031a5")
    return _global_logger


def set_global_logger(logger: StructuredLogger):
    """Define o logger global."""
    global _global_logger
    _global_logger = logger
