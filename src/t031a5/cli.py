"""
CLI principal do sistema t031a5.

Interface de linha de comando para executar o sistema G1.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn

from .runtime import CortexRuntime

# Configuração do CLI
app = typer.Typer(
    name="t031a5",
    help="Sistema AI Multimodal para G1 - Sistema de IA multimodal para o robô humanóide G1 da Unitree",
    add_completion=False,
)

console = Console()


def setup_logging(level: str = "INFO", rich_output: bool = True):
    """Configura o sistema de logging."""
    log_level = getattr(logging, level.upper())
    
    if rich_output:
        # Usa Rich para logging colorido
        logging.basicConfig(
            level=log_level,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(console=console, rich_tracebacks=True)]
        )
    else:
        # Logging padrão
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )


@app.command()
def run(
    config: Path = typer.Option(
        None,
        "--config", "-c",
        help="Caminho para o arquivo de configuração JSON5",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    dev: bool = typer.Option(
        False,
        "--dev",
        help="Modo de desenvolvimento com logs detalhados",
    ),
    log_level: str = typer.Option(
        "INFO",
        "--log-level",
        help="Nível de logging (DEBUG, INFO, WARNING, ERROR)",
    ),
    no_rich: bool = typer.Option(
        False,
        "--no-rich",
        help="Desabilita saída colorida do Rich",
    ),
):
    """
    Executa o sistema t031a5.
    
    Exemplos:
        t031a5 run --config config/g1_basic.json5
        t031a5 run --config config/g1_advanced.json5 --dev
        t031a5 run --config config/g1_development.json5 --log-level DEBUG
    """
    
    # Configura logging
    if dev:
        log_level = "DEBUG"
    
    setup_logging(log_level, not no_rich)
    logger = logging.getLogger(__name__)
    
    # Determina arquivo de configuração
    if config is None:
        # Procura por configurações padrão
        config_candidates = [
            Path("config/local.json5"),
            Path("config/g1_basic.json5"),
            Path("config/g1_development.json5"),
        ]
        
        for candidate in config_candidates:
            if candidate.exists():
                config = candidate
                logger.info(f"Usando configuração padrão: {config}")
                break
        else:
            console.print("[red]Erro: Nenhum arquivo de configuração encontrado![/red]")
            console.print("Use --config para especificar um arquivo ou crie config/local.json5")
            sys.exit(1)
    
    # Valida arquivo de configuração
    if not config.exists():
        console.print(f"[red]Erro: Arquivo de configuração não encontrado: {config}[/red]")
        sys.exit(1)
    
    # Executa o sistema
    asyncio.run(_run_system(config, dev))


async def _run_system(config_path: Path, dev_mode: bool):
    """Executa o sistema principal."""
    logger = logging.getLogger(__name__)
    
    console.print(f"[green]🚀 Iniciando t031a5 com configuração: {config_path}[/green]")
    
    # Cria runtime
    runtime = CortexRuntime(config_path)
    
    try:
        # Inicializa sistema
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Inicializando sistema...", total=None)
            
            success = await runtime.initialize()
            
            if not success:
                console.print("[red]❌ Falha na inicialização do sistema[/red]")
                sys.exit(1)
            
            progress.update(task, description="Sistema inicializado com sucesso!")
        
        console.print("[green]✅ Sistema inicializado com sucesso![/green]")
        
        # Mostra informações do sistema
        status = await runtime.get_status()
        console.print(f"[blue]📊 Status do sistema:[/blue]")
        console.print(f"  - Configuração carregada: {'✅' if status['config_loaded'] else '❌'}")
        console.print(f"  - Componentes inicializados: {'✅' if status['components_initialized'] else '❌'}")
        console.print(f"  - Modo desenvolvimento: {'✅' if dev_mode else '❌'}")
        
        # Status do G1Controller se disponível
        if status.get('g1_controller'):
            g1_status = status['g1_controller']
            if isinstance(g1_status, dict) and not g1_status.get('error'):
                console.print(f"  - G1Controller: {'✅' if g1_status.get('controller', {}).get('initialized') else '❌'}")
            else:
                console.print(f"  - G1Controller: ❌")
        else:
            console.print(f"  - G1Controller: ⚪ Não configurado")
        
        # Status do WebSim se disponível
        if status.get('websim'):
            websim_status = status['websim']
            if isinstance(websim_status, dict) and not websim_status.get('error'):
                console.print(f"  - WebSim: {'✅' if websim_status.get('running') else '❌'}")
                if websim_status.get('running'):
                    console.print(f"    URL: http://{websim_status.get('host', 'localhost')}:{websim_status.get('port', 8080)}")
            else:
                console.print(f"  - WebSim: ❌")
        else:
            console.print(f"  - WebSim: ⚪ Não configurado")
        
        # Inicia loop principal
        console.print("[yellow]🔄 Iniciando loop principal...[/yellow]")
        console.print("[yellow]Pressione Ctrl+C para parar[/yellow]")
        
        await runtime.start()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Interrupção recebida, parando sistema...[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Erro fatal: {e}[/red]")
        logger.exception("Erro fatal no sistema")
        sys.exit(1)
    finally:
        console.print("[green]✅ Sistema finalizado[/green]")


@app.command()
def status(
    config: Optional[Path] = typer.Option(
        None,
        "--config", "-c",
        help="Caminho para o arquivo de configuração",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
):
    """
    Mostra o status da configuração do sistema.
    
    Exemplos:
        t031a5 status
        t031a5 status --config config/g1_advanced.json5
    """
    
    setup_logging("INFO", True)
    logger = logging.getLogger(__name__)
    
    # Determina arquivo de configuração
    if config is None:
        config_candidates = [
            Path("config/local.json5"),
            Path("config/g1_basic.json5"),
            Path("config/g1_development.json5"),
        ]
        
        for candidate in config_candidates:
            if candidate.exists():
                config = candidate
                break
        else:
            console.print("[red]Erro: Nenhum arquivo de configuração encontrado![/red]")
            sys.exit(1)
    
    # Carrega e mostra configuração
    try:
        from .runtime.config import ConfigManager
        
        config_manager = ConfigManager(config)
        g1_config = config_manager.load_config()
        
        console.print(f"[blue]📋 Status da configuração: {config}[/blue]")
        console.print(f"  - Nome: {g1_config.name}")
        console.print(f"  - Frequência: {g1_config.hertz} Hz")
        console.print(f"  - Interface de rede: {g1_config.unitree_ethernet}")
        
        # Inputs configurados
        inputs_config = config_manager.get_inputs_config()
        console.print(f"  - Inputs configurados: {len(inputs_config)}")
        for input_config in inputs_config:
            console.print(f"    • {input_config.get('type', 'Unknown')}")
        
        # Actions configuradas
        actions_config = config_manager.get_actions_config()
        console.print(f"  - Actions configuradas: {len(actions_config)}")
        for action_config in actions_config:
            console.print(f"    • {action_config.get('name', 'Unknown')}")
        
        # Configurações de desenvolvimento
        dev_config = g1_config.development
        console.print(f"  - Modo debug: {'✅' if dev_config.get('debug_mode') else '❌'}")
        console.print(f"  - WebSim habilitado: {'✅' if dev_config.get('websim_enabled') else '❌'}")
        console.print(f"  - Hot reload: {'✅' if dev_config.get('hot_reload') else '❌'}")
        
        # Validação do ambiente
        if config_manager.validate_environment():
            console.print("  - Ambiente: [green]✅ Válido[/green]")
        else:
            console.print("  - Ambiente: [red]❌ Inválido[/red]")
        
    except Exception as e:
        console.print(f"[red]Erro ao carregar configuração: {e}[/red]")
        sys.exit(1)


@app.command()
def validate(
    config: Path = typer.Option(
        ...,
        "--config", "-c",
        help="Caminho para o arquivo de configuração",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
):
    """
    Valida um arquivo de configuração.
    
    Exemplos:
        t031a5 validate --config config/g1_basic.json5
        t031a5 validate --config config/g1_advanced.json5
    """
    
    setup_logging("INFO", True)
    
    try:
        from .runtime.config import ConfigManager
        
        console.print(f"[blue]🔍 Validando configuração: {config}[/blue]")
        
        config_manager = ConfigManager(config)
        g1_config = config_manager.load_config()
        
        console.print("[green]✅ Configuração válida![/green]")
        console.print(f"  - Nome: {g1_config.name}")
        console.print(f"  - Frequência: {g1_config.hertz} Hz")
        
        # Validação do ambiente
        if config_manager.validate_environment():
            console.print("[green]✅ Ambiente válido![/green]")
        else:
            console.print("[yellow]⚠️  Ambiente com problemas[/yellow]")
        
    except Exception as e:
        console.print(f"[red]❌ Configuração inválida: {e}[/red]")
        sys.exit(1)


@app.command()
def test(
    config: Path = typer.Option(
        None,
        "--config", "-c",
        help="Caminho para o arquivo de configuração JSON5",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    duration: int = typer.Option(
        10,
        "--duration", "-d",
        help="Duração do teste em segundos",
        min=1,
        max=300,
    ),
):
    """
    Testa o sistema t031a5 por um período específico.
    
    Exemplos:
        t031a5 test --config config/g1_integrated.json5
        t031a5 test --config config/g1_basic.json5 --duration 30
    """
    
    setup_logging("INFO", True)
    logger = logging.getLogger(__name__)
    
    # Determina arquivo de configuração
    if config is None:
        config_candidates = [
            Path("config/g1_integrated.json5"),
            Path("config/g1_basic.json5"),
            Path("config/g1_development.json5"),
        ]
        
        for candidate in config_candidates:
            if candidate.exists():
                config = candidate
                logger.info(f"Usando configuração padrão: {config}")
                break
        else:
            console.print("[red]Erro: Nenhum arquivo de configuração encontrado![/red]")
            sys.exit(1)
    
    # Executa o teste
    asyncio.run(_test_system(config, duration))


async def _test_system(config_path: Path, duration: int):
    """Executa teste do sistema."""
    logger = logging.getLogger(__name__)
    
    console.print(f"[green]🧪 Testando t031a5 por {duration} segundos...[/green]")
    console.print(f"[blue]Configuração: {config_path}[/blue]")
    
    # Cria runtime
    runtime = CortexRuntime(config_path)
    
    try:
        # Inicializa sistema
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Inicializando sistema...", total=None)
            
            success = await runtime.initialize()
            
            if not success:
                console.print("[red]❌ Falha na inicialização do sistema[/red]")
                sys.exit(1)
            
            progress.update(task, description="Sistema inicializado com sucesso!")
        
        console.print("[green]✅ Sistema inicializado com sucesso![/green]")
        
        # Mostra status inicial
        status = await runtime.get_status()
        console.print(f"[blue]📊 Status inicial:[/blue]")
        console.print(f"  - Componentes inicializados: {'✅' if status['components_initialized'] else '❌'}")
        
        # Inicia loop em background
        console.print(f"[yellow]🔄 Executando teste por {duration} segundos...[/yellow]")
        
        # Inicia o runtime em uma task separada
        run_task = asyncio.create_task(runtime.start())
        
        # Aguarda o tempo especificado
        await asyncio.sleep(duration)
        
        # Para o sistema
        runtime.is_running = False
        await run_task
        
        # Mostra estatísticas finais
        final_status = await runtime.get_status()
        console.print(f"[blue]📊 Estatísticas finais:[/blue]")
        console.print(f"  - Loops executados: {final_status['loop_count']}")
        console.print(f"  - Tempo médio por loop: {final_status['metrics']['avg_loop_time']*1000:.2f}ms")
        console.print(f"  - Erros: {final_status['metrics']['errors']}")
        console.print(f"  - Frequência média: {final_status['loop_count']/duration:.2f} Hz")
        
        if final_status['metrics']['errors'] == 0:
            console.print("[green]✅ Teste concluído com sucesso![/green]")
        else:
            console.print(f"[yellow]⚠️  Teste concluído com {final_status['metrics']['errors']} erros[/yellow]")
        
    except Exception as e:
        console.print(f"[red]❌ Erro durante o teste: {e}[/red]")
        logger.exception("Erro durante o teste")
        sys.exit(1)
    finally:
        console.print("[green]✅ Teste finalizado[/green]")


@app.command()
def version():
    """Mostra a versão do sistema."""
    from . import __version__
    console.print(f"[blue]t031a5 versão {__version__}[/blue]")


def main():
    """Função principal do CLI."""
    app()


if __name__ == "__main__":
    main()
