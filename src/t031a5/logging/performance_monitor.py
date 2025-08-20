"""
Monitor de performance para o sistema t031a5.

Monitora performance do sistema, recursos e alertas.
"""

import psutil
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from .structured_logger import StructuredLogger, LogContext
from .metrics_collector import MetricsCollector


class PerformanceMonitor:
    """Monitor de performance avançado."""
    
    def __init__(
        self,
        logger: Optional[StructuredLogger] = None,
        metrics_collector: Optional[MetricsCollector] = None
    ):
        """
        Inicializa o monitor de performance.
        
        Args:
            logger: Logger estruturado (opcional)
            metrics_collector: Coletor de métricas (opcional)
        """
        self.logger = logger or StructuredLogger("performance")
        self.metrics_collector = metrics_collector or MetricsCollector(self.logger)
        
        # Configurações de alerta
        self.alert_thresholds = {
            "cpu_usage": 80.0,      # CPU > 80%
            "memory_usage": 85.0,   # Memória > 85%
            "disk_usage": 90.0,     # Disco > 90%
            "loop_time": 0.1,       # Loop > 100ms
            "error_rate": 5.0       # Taxa de erro > 5%
        }
        
        # Histórico de alertas
        self.alerts = []
        
        # Status do sistema
        self.system_status = {
            "healthy": True,
            "last_check": datetime.now(),
            "issues": []
        }
        
        # Métricas de baseline
        self.baseline_metrics = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "disk_usage": 0.0,
            "loop_time": 0.0
        }
        
        # Contador de checks
        self.check_count = 0
    
    def start_monitoring(self):
        """Inicia o monitoramento."""
        self.logger.info("Iniciando monitoramento de performance")
        self._establish_baseline()
    
    def _establish_baseline(self):
        """Estabelece métricas de baseline."""
        self.logger.info("Estabelecendo baseline de performance...")
        
        # Coleta métricas por 10 segundos para estabelecer baseline
        cpu_readings = []
        memory_readings = []
        disk_readings = []
        
        for _ in range(10):
            cpu_readings.append(psutil.cpu_percent(interval=1))
            memory_readings.append(psutil.virtual_memory().percent)
            disk_readings.append(psutil.disk_usage('/').percent)
            time.sleep(1)
        
        self.baseline_metrics["cpu_usage"] = sum(cpu_readings) / len(cpu_readings)
        self.baseline_metrics["memory_usage"] = sum(memory_readings) / len(memory_readings)
        self.baseline_metrics["disk_usage"] = sum(disk_readings) / len(disk_readings)
        
        self.logger.info(f"Baseline estabelecido: CPU={self.baseline_metrics['cpu_usage']:.1f}%, "
                        f"Memória={self.baseline_metrics['memory_usage']:.1f}%, "
                        f"Disco={self.baseline_metrics['disk_usage']:.1f}%")
    
    def check_system_health(self) -> Dict[str, Any]:
        """
        Verifica a saúde do sistema.
        
        Returns:
            Status de saúde do sistema
        """
        self.check_count += 1
        current_time = datetime.now()
        
        # Coleta métricas atuais
        cpu_usage = psutil.cpu_percent(interval=0.1)
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        
        # Atualiza métricas
        self.metrics_collector.update_system_metrics(cpu_usage, memory_usage, disk_usage)
        
        # Verifica alertas
        alerts = []
        issues = []
        
        # CPU
        if cpu_usage > self.alert_thresholds["cpu_usage"]:
            alert = {
                "type": "high_cpu_usage",
                "severity": "warning" if cpu_usage < 95 else "critical",
                "value": cpu_usage,
                "threshold": self.alert_thresholds["cpu_usage"],
                "timestamp": current_time
            }
            alerts.append(alert)
            issues.append(f"CPU usage high: {cpu_usage:.1f}%")
        
        # Memória
        if memory_usage > self.alert_thresholds["memory_usage"]:
            alert = {
                "type": "high_memory_usage",
                "severity": "warning" if memory_usage < 95 else "critical",
                "value": memory_usage,
                "threshold": self.alert_thresholds["memory_usage"],
                "timestamp": current_time
            }
            alerts.append(alert)
            issues.append(f"Memory usage high: {memory_usage:.1f}%")
        
        # Disco
        if disk_usage > self.alert_thresholds["disk_usage"]:
            alert = {
                "type": "high_disk_usage",
                "severity": "warning" if disk_usage < 98 else "critical",
                "value": disk_usage,
                "threshold": self.alert_thresholds["disk_usage"],
                "timestamp": current_time
            }
            alerts.append(alert)
            issues.append(f"Disk usage high: {disk_usage:.1f}%")
        
        # Adiciona alertas ao histórico
        self.alerts.extend(alerts)
        
        # Mantém apenas últimos 100 alertas
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        # Atualiza status do sistema
        self.system_status.update({
            "healthy": len(issues) == 0,
            "last_check": current_time,
            "issues": issues,
            "check_count": self.check_count
        })
        
        # Log de alertas
        for alert in alerts:
            context = LogContext(
                component="performance_monitor",
                operation="health_check",
                alert_type=alert["type"],
                severity=alert["severity"]
            )
            
            if alert["severity"] == "critical":
                self.logger.critical(
                    f"Critical alert: {alert['type']} = {alert['value']:.1f}%",
                    context
                )
            else:
                self.logger.warning(
                    f"Warning alert: {alert['type']} = {alert['value']:.1f}%",
                    context
                )
        
        # Log de status geral
        if len(issues) == 0:
            self.logger.info(
                f"System health check passed: CPU={cpu_usage:.1f}%, "
                f"Memory={memory_usage:.1f}%, Disk={disk_usage:.1f}%",
                LogContext(component="performance_monitor", operation="health_check")
            )
        
        return {
            "healthy": self.system_status["healthy"],
            "issues": issues,
            "alerts": alerts,
            "metrics": {
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "disk_usage": disk_usage
            }
        }
    
    def check_performance_metrics(self, loop_time: float, total_loops: int, errors: int) -> Dict[str, Any]:
        """
        Verifica métricas de performance.
        
        Args:
            loop_time: Tempo do último loop
            total_loops: Total de loops executados
            errors: Total de erros
            
        Returns:
            Status de performance
        """
        # Atualiza métricas
        self.metrics_collector.update_performance_metrics(loop_time, total_loops, errors)
        
        # Calcula taxa de erro
        error_rate = (errors / total_loops * 100) if total_loops > 0 else 0
        
        # Verifica alertas de performance
        alerts = []
        issues = []
        
        # Tempo de loop
        if loop_time > self.alert_thresholds["loop_time"]:
            alert = {
                "type": "slow_loop_time",
                "severity": "warning" if loop_time < 0.5 else "critical",
                "value": loop_time,
                "threshold": self.alert_thresholds["loop_time"],
                "timestamp": datetime.now()
            }
            alerts.append(alert)
            issues.append(f"Slow loop time: {loop_time*1000:.1f}ms")
        
        # Taxa de erro
        if error_rate > self.alert_thresholds["error_rate"]:
            alert = {
                "type": "high_error_rate",
                "severity": "warning" if error_rate < 20 else "critical",
                "value": error_rate,
                "threshold": self.alert_thresholds["error_rate"],
                "timestamp": datetime.now()
            }
            alerts.append(alert)
            issues.append(f"High error rate: {error_rate:.1f}%")
        
        # Adiciona alertas
        self.alerts.extend(alerts)
        
        # Log de alertas
        for alert in alerts:
            context = LogContext(
                component="performance_monitor",
                operation="performance_check",
                alert_type=alert["type"],
                severity=alert["severity"]
            )
            
            if alert["severity"] == "critical":
                self.logger.critical(
                    f"Critical performance alert: {alert['type']} = {alert['value']}",
                    context
                )
            else:
                self.logger.warning(
                    f"Performance warning: {alert['type']} = {alert['value']}",
                    context
                )
        
        return {
            "healthy": len(issues) == 0,
            "issues": issues,
            "alerts": alerts,
            "metrics": {
                "loop_time": loop_time,
                "total_loops": total_loops,
                "errors": errors,
                "error_rate": error_rate
            }
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retorna status completo do sistema."""
        return {
            "monitor": self.system_status,
            "baseline": self.baseline_metrics,
            "thresholds": self.alert_thresholds,
            "recent_alerts": self.alerts[-10:] if self.alerts else [],
            "metrics": self.metrics_collector.get_current_metrics()
        }
    
    def get_performance_report(self, hours: int = 1) -> Dict[str, Any]:
        """
        Gera relatório de performance.
        
        Args:
            hours: Número de horas para o relatório
            
        Returns:
            Relatório de performance
        """
        history = self.metrics_collector.get_metrics_history(hours)
        
        # Calcula estatísticas
        if history["performance"]:
            loop_times = [item["loop_time"] for item in history["performance"]]
            avg_loop_time = sum(loop_times) / len(loop_times)
            max_loop_time = max(loop_times)
            min_loop_time = min(loop_times)
        else:
            avg_loop_time = max_loop_time = min_loop_time = 0
        
        if history["system"]:
            cpu_usage = [item["cpu"] for item in history["system"]]
            memory_usage = [item["memory"] for item in history["system"]]
            avg_cpu = sum(cpu_usage) / len(cpu_usage)
            avg_memory = sum(memory_usage) / len(memory_usage)
            max_cpu = max(cpu_usage)
            max_memory = max(memory_usage)
        else:
            avg_cpu = avg_memory = max_cpu = max_memory = 0
        
        # Filtra alertas do período
        cutoff_time = datetime.now() - timedelta(hours=hours)
        period_alerts = [
            alert for alert in self.alerts
            if alert["timestamp"] > cutoff_time
        ]
        
        return {
            "period_hours": hours,
            "performance": {
                "avg_loop_time": avg_loop_time,
                "max_loop_time": max_loop_time,
                "min_loop_time": min_loop_time,
                "total_loops": len(history["performance"])
            },
            "system": {
                "avg_cpu_usage": avg_cpu,
                "avg_memory_usage": avg_memory,
                "max_cpu_usage": max_cpu,
                "max_memory_usage": max_memory
            },
            "alerts": {
                "total": len(period_alerts),
                "critical": len([a for a in period_alerts if a["severity"] == "critical"]),
                "warnings": len([a for a in period_alerts if a["severity"] == "warning"])
            },
            "summary": self.metrics_collector.get_metrics_summary()
        }
    
    def set_alert_thresholds(self, **thresholds):
        """
        Define novos thresholds de alerta.
        
        Args:
            **thresholds: Novos thresholds
        """
        for key, value in thresholds.items():
            if key in self.alert_thresholds:
                self.alert_thresholds[key] = value
                self.logger.info(f"Updated alert threshold: {key} = {value}")
    
    def reset_alerts(self):
        """Reseta histórico de alertas."""
        self.alerts.clear()
        self.logger.info("Alert history reset")
    
    def export_report(self, format: str = "json") -> str:
        """
        Exporta relatório completo.
        
        Args:
            format: Formato de exportação
            
        Returns:
            Relatório exportado
        """
        import json
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_status": self.get_system_status(),
            "performance_report": self.get_performance_report(24),
            "metrics_export": self.metrics_collector.export_metrics("json")
        }
        
        if format.lower() == "json":
            return json.dumps(report, indent=2, default=str)
        else:
            raise ValueError(f"Formato não suportado: {format}")
