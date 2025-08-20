#!/usr/bin/env python3
"""
Script de teste para o sistema de logging estruturado t031a5.

Testa StructuredLogger, MetricsCollector e PerformanceMonitor.
"""

import sys
import asyncio
import time
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from t031a5.logging import (
    StructuredLogger, 
    LogLevel, 
    LogContext,
    MetricsCollector,
    PerformanceMonitor
)


def test_structured_logger():
    """Testa o StructuredLogger."""
    print("🔍 Testando StructuredLogger...")
    
    try:
        # Cria logger
        logger = StructuredLogger(
            name="test_logger",
            console_output=True,
            json_output=False,
            level=LogLevel.DEBUG
        )
        
        # Testa diferentes níveis de log
        logger.debug("Mensagem de debug")
        logger.info("Mensagem de informação")
        logger.warning("Mensagem de aviso")
        logger.error("Mensagem de erro")
        
        # Testa log com contexto
        context = LogContext(
            component="test_component",
            operation="test_operation",
            session_id="test_session"
        )
        
        logger.info("Mensagem com contexto", context)
        
        # Testa logs específicos
        logger.log_performance("test_operation", 0.123, context)
        logger.log_metric("test_metric", 42, context)
        logger.log_event("test_event", {"data": "test"}, context)
        
        # Mostra métricas
        metrics = logger.get_metrics()
        print(f"    ✅ Total de logs: {metrics['total_logs']}")
        print(f"    ✅ Logs por nível: {metrics['logs_by_level']}")
        print(f"    ✅ Logs por componente: {metrics['logs_by_component']}")
        
        # Imprime tabela de métricas
        logger.print_metrics_table()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_metrics_collector():
    """Testa o MetricsCollector."""
    print("\n🔍 Testando MetricsCollector...")
    
    try:
        # Cria logger e coletor
        logger = StructuredLogger("metrics_test")
        collector = MetricsCollector(logger)
        
        # Testa timers
        timer_id = collector.start_timer("test_operation")
        time.sleep(0.1)  # Simula operação
        duration = collector.stop_timer(timer_id)
        print(f"    ✅ Timer test_operation: {duration*1000:.2f}ms")
        
        # Testa timer com contexto
        context = LogContext(component="test", operation="timed_operation")
        timer_id = collector.start_timer_with_context("context_operation", context)
        time.sleep(0.05)
        duration = collector.stop_timer(timer_id)
        print(f"    ✅ Timer com contexto: {duration*1000:.2f}ms")
        
        # Testa contadores
        collector.increment_counter("test_counter", 5)
        collector.increment_counter("test_counter", 3)
        print(f"    ✅ Contador test_counter: {collector.counters['test_counter']}")
        
        # Testa gauges
        collector.set_gauge("test_gauge", 42.5)
        print(f"    ✅ Gauge test_gauge: {collector.gauges['test_gauge']}")
        
        # Testa eventos
        collector.record_event("test_event", {"value": 123, "status": "success"})
        print(f"    ✅ Eventos registrados: {len(collector.current_metrics['events'])}")
        
        # Testa métricas de sistema
        collector.update_system_metrics(25.5, 60.2, 45.8)
        system_metrics = collector.current_metrics["system"]
        print(f"    ✅ CPU: {system_metrics['cpu_usage']}%")
        print(f"    ✅ Memória: {system_metrics['memory_usage']}%")
        print(f"    ✅ Disco: {system_metrics['disk_usage']}%")
        
        # Testa métricas de performance
        collector.update_performance_metrics(0.05, 100, 2)
        perf_metrics = collector.current_metrics["performance"]
        print(f"    ✅ Loops: {perf_metrics['total_loops']}")
        print(f"    ✅ Erros: {perf_metrics['errors']}")
        print(f"    ✅ Taxa de sucesso: {perf_metrics['success_rate']:.1f}%")
        
        # Testa resumo
        summary = collector.get_metrics_summary()
        print(f"    ✅ Uptime: {summary['uptime']:.1f}s")
        print(f"    ✅ Timers ativos: {summary['active_timers']}")
        print(f"    ✅ Contadores: {len(summary['counters'])}")
        print(f"    ✅ Gauges: {len(summary['gauges'])}")
        
        # Testa exportação
        export = collector.export_metrics("json")
        print(f"    ✅ Exportação JSON: {len(export)} caracteres")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_performance_monitor():
    """Testa o PerformanceMonitor."""
    print("\n🔍 Testando PerformanceMonitor...")
    
    try:
        # Cria monitor
        logger = StructuredLogger("performance_test")
        collector = MetricsCollector(logger)
        monitor = PerformanceMonitor(logger, collector)
        
        # Inicia monitoramento
        monitor.start_monitoring()
        print("    ✅ Monitoramento iniciado")
        
        # Testa verificação de saúde do sistema
        health_status = monitor.check_system_health()
        print(f"    ✅ Sistema saudável: {health_status['healthy']}")
        print(f"    ✅ Issues: {len(health_status['issues'])}")
        print(f"    ✅ Alertas: {len(health_status['alerts'])}")
        
        # Mostra métricas do sistema
        metrics = health_status['metrics']
        print(f"    ✅ CPU: {metrics['cpu_usage']:.1f}%")
        print(f"    ✅ Memória: {metrics['memory_usage']:.1f}%")
        print(f"    ✅ Disco: {metrics['disk_usage']:.1f}%")
        
        # Testa verificação de performance
        perf_status = monitor.check_performance_metrics(0.08, 150, 3)
        print(f"    ✅ Performance saudável: {perf_status['healthy']}")
        print(f"    ✅ Issues de performance: {len(perf_status['issues'])}")
        print(f"    ✅ Alertas de performance: {len(perf_status['alerts'])}")
        
        # Mostra métricas de performance
        perf_metrics = perf_status['metrics']
        print(f"    ✅ Tempo de loop: {perf_metrics['loop_time']*1000:.1f}ms")
        print(f"    ✅ Total de loops: {perf_metrics['total_loops']}")
        print(f"    ✅ Erros: {perf_metrics['errors']}")
        print(f"    ✅ Taxa de erro: {perf_metrics['error_rate']:.1f}%")
        
        # Testa status do sistema
        system_status = monitor.get_system_status()
        print(f"    ✅ Status do monitor: {system_status['monitor']['healthy']}")
        print(f"    ✅ Checks realizados: {system_status['monitor']['check_count']}")
        print(f"    ✅ Alertas recentes: {len(system_status['recent_alerts'])}")
        
        # Testa relatório de performance
        report = monitor.get_performance_report(1)
        print(f"    ✅ Período do relatório: {report['period_hours']}h")
        print(f"    ✅ Loops no período: {report['performance']['total_loops']}")
        print(f"    ✅ Alertas no período: {report['alerts']['total']}")
        
        # Testa configuração de thresholds
        monitor.set_alert_thresholds(cpu_usage=70.0, memory_usage=80.0)
        print("    ✅ Thresholds atualizados")
        
        # Testa exportação de relatório
        export = monitor.export_report("json")
        print(f"    ✅ Relatório exportado: {len(export)} caracteres")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_integration():
    """Testa integração dos componentes de logging."""
    print("\n🔍 Testando integração dos componentes...")
    
    try:
        # Cria sistema completo
        logger = StructuredLogger("integration_test")
        collector = MetricsCollector(logger)
        monitor = PerformanceMonitor(logger, collector)
        
        # Simula operação completa
        context = LogContext(
            component="integration_test",
            operation="full_test",
            session_id="integration_session"
        )
        
        # Log inicial
        logger.info("Iniciando teste de integração", context)
        
        # Timer para operação
        timer_id = collector.start_timer_with_context("integration_operation", context)
        
        # Simula trabalho
        time.sleep(0.2)
        
        # Para timer
        duration = collector.stop_timer(timer_id)
        
        # Atualiza métricas
        collector.update_system_metrics(30.5, 65.2, 50.1)
        collector.update_performance_metrics(0.15, 200, 5)
        
        # Verifica saúde
        health = monitor.check_system_health()
        perf = monitor.check_performance_metrics(0.15, 200, 5)
        
        # Log final
        logger.info(
            f"Teste de integração concluído: {duration*1000:.1f}ms",
            context,
            health_status=health['healthy'],
            perf_status=perf['healthy']
        )
        
        # Mostra resumo
        summary = collector.get_metrics_summary()
        print(f"    ✅ Operações: {summary['total_loops']}")
        print(f"    ✅ Taxa de sucesso: {summary['success_rate']:.1f}%")
        print(f"    ✅ Tempo médio de loop: {summary['avg_loop_time']*1000:.1f}ms")
        print(f"    ✅ Eventos: {summary['total_events']}")
        
        # Mostra métricas do logger
        logger_metrics = logger.get_metrics()
        print(f"    ✅ Total de logs: {logger_metrics['total_logs']}")
        print(f"    ✅ Logs por componente: {logger_metrics['logs_by_component']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


async def main():
    """Função principal de teste."""
    print("🚀 Testando sistema de logging estruturado t031a5\n")
    
    results = []
    
    # Teste do StructuredLogger
    print("Teste 1: StructuredLogger")
    results.append(test_structured_logger())
    
    # Teste do MetricsCollector
    print("\nTeste 2: MetricsCollector")
    results.append(test_metrics_collector())
    
    # Teste do PerformanceMonitor
    print("\nTeste 3: PerformanceMonitor")
    results.append(test_performance_monitor())
    
    # Teste de integração
    print("\nTeste 4: Integração")
    results.append(test_integration())
    
    # Resultado final
    print("\n" + "="*60)
    print("📊 RESULTADO FINAL DOS TESTES DE LOGGING")
    print("="*60)
    
    # Filtra valores None e conta sucessos
    valid_results = [r for r in results if r is not None]
    passed = sum(valid_results)
    total = len(valid_results)
    
    print(f"Testes passaram: {passed}/{total}")
    
    if passed == total:
        print("🎉 TODOS OS TESTES DE LOGGING PASSARAM!")
        print("O sistema de logging estruturado está funcionando perfeitamente!")
        print("\n💡 Funcionalidades disponíveis:")
        print("   - Logging estruturado com contexto")
        print("   - Coleta de métricas em tempo real")
        print("   - Monitoramento de performance")
        print("   - Alertas automáticos")
        print("   - Relatórios detalhados")
        print("   - Exportação de dados")
    else:
        print("❌ Alguns testes de logging falharam")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
