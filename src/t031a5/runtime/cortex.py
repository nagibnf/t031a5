"""
CortexRuntime para o sistema t031a5.

Loop principal do sistema que coordena inputs, LLM e actions do G1.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional
from pathlib import Path

from .config import ConfigManager
from .orchestrators import InputOrchestrator, ActionOrchestrator
from ..fuser import BaseFuser
from ..llm import LLMProvider
from ..conversation import ConversationEngine

logger = logging.getLogger(__name__)


class CortexRuntime:
    """Runtime principal do sistema t031a5."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Inicializa o CortexRuntime.
        
        Args:
            config_path: Caminho para o arquivo de configuração
        """
        self.config_manager = ConfigManager(config_path)
        self.config: Optional[Any] = None
        
        # Componentes do sistema
        self.input_orchestrator: Optional[InputOrchestrator] = None
        self.action_orchestrator: Optional[ActionOrchestrator] = None
        self.fuser: Optional[BaseFuser] = None
        self.llm_provider: Optional[LLMProvider] = None
        self.conversation_engine: Optional[ConversationEngine] = None
        self.g1_controller = None
        self.websim = None
        
        # Estado do runtime
        self.is_running = False
        self.loop_count = 0
        self.start_time: Optional[float] = None
        
        # Métricas
        self.metrics = {
            "total_loops": 0,
            "avg_loop_time": 0.0,
            "errors": 0,
            "last_error": None
        }
    
    async def initialize(self) -> bool:
        """
        Inicializa o sistema.
        
        Returns:
            True se a inicialização foi bem-sucedida
        """
        try:
            logger.info("Inicializando CortexRuntime...")
            
            # Carrega configuração
            self.config = self.config_manager.load_config()
            
            # Valida ambiente
            if not self.config_manager.validate_environment():
                logger.error("Falha na validação do ambiente")
                return False
            
            # Configura logging
            self._setup_logging()
            
            # Inicializa componentes
            await self._initialize_components()
            
            logger.info("CortexRuntime inicializado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro na inicialização: {e}")
            return False
    
    async def _initialize_components(self):
        """Inicializa todos os componentes do sistema."""
        logger.info("Inicializando componentes...")
        
        # Inicializa fuser
        fuser_config = self.config_manager.get_fuser_config()
        fuser_type = fuser_config.get("type", "priority")
        
        if fuser_type == "priority":
            from ..fuser.priority import PriorityFuser
            self.fuser = PriorityFuser(fuser_config.get("config", {}))
        elif fuser_type == "multimodal":
            from ..fuser.multimodal import MultimodalFuser
            self.fuser = MultimodalFuser(fuser_config.get("config", {}))
        else:
            raise ValueError(f"Tipo de fuser não suportado: {fuser_type}")
        
        # Inicializa LLM provider
        llm_config = self.config_manager.get_llm_config()
        self.llm_provider = LLMProvider(llm_config)
        
        # Inicializa orchestrators
        self.input_orchestrator = InputOrchestrator(
            self.config_manager.get_inputs_config(),
            self.config_manager
        )
        
        self.action_orchestrator = ActionOrchestrator(
            self.config_manager.get_actions_config(),
            self.config_manager
        )
        
        # Inicializa componentes
        await self.input_orchestrator.initialize()
        await self.action_orchestrator.initialize()
        await self.fuser.initialize()
        await self.llm_provider.initialize()
        
        # Inicializa G1Controller se configurado
        await self._initialize_g1_controller()
        
        # Inicializa WebSim se configurado
        await self._initialize_websim()
        
        # Inicializa ConversationEngine se configurado
        await self._initialize_conversation_engine()
        
        logger.info("Componentes inicializados com sucesso")
    
    def _setup_logging(self):
        """Configura o sistema de logging."""
        logging_config = self.config_manager.get_logging_config()
        
        if not logging_config:
            return
        
        # Configura nível de log
        log_level = getattr(logging, logging_config.get("level", "INFO").upper())
        logging.getLogger().setLevel(log_level)
        
        # Configura arquivo de log
        log_file = logging_config.get("file")
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Configura handler de arquivo
            file_handler = logging.FileHandler(log_path)
            file_handler.setLevel(log_level)
            
            # Formato do log
            log_format = logging_config.get("log_format", "detailed")
            if log_format == "detailed":
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            else:
                formatter = logging.Formatter('%(levelname)s - %(message)s')
            
            file_handler.setFormatter(formatter)
            logging.getLogger().addHandler(file_handler)
    
    async def _initialize_g1_controller(self):
        """Inicializa o G1Controller se configurado."""
        try:
            # Verifica se deve inicializar o G1Controller
            raw_config = self.config_manager.get_raw_config()
            g1_controller_config = raw_config.get("g1_controller")
            
            if g1_controller_config and g1_controller_config.get("enabled", False):
                logger.info("Inicializando G1Controller...")
                
                from ..unitree import G1Controller
                # Remove o campo 'enabled' da configuração antes de passar para o G1Controller
                g1_init_config = {k: v for k, v in g1_controller_config.items() if k != "enabled"}
                self.g1_controller = G1Controller(g1_init_config)
                
                success = await self.g1_controller.initialize()
                if success:
                    logger.info("G1Controller inicializado com sucesso")
                else:
                    logger.warning("Falha na inicialização do G1Controller")
            else:
                logger.info("G1Controller não configurado ou desabilitado")
                
        except Exception as e:
            logger.error(f"Erro na inicialização do G1Controller: {e}")
    
    async def _initialize_websim(self):
        """Inicializa o WebSim se configurado."""
        try:
            # Verifica se deve inicializar o WebSim
            raw_config = self.config_manager.get_raw_config()
            websim_config = raw_config.get("websim")
            
            if websim_config and websim_config.get("enabled", False):
                logger.info("Inicializando WebSim...")
                
                from ..simulators import WebSim
                # Remove o campo 'enabled' da configuração antes de passar para o WebSim
                websim_init_config = {k: v for k, v in websim_config.items() if k != "enabled"}
                self.websim = WebSim(websim_init_config, self.g1_controller)
                
                success = await self.websim.initialize()
                if success:
                    # Inicia servidor WebSim
                    success = await self.websim.start()
                    if success:
                        logger.info("WebSim inicializado e servidor iniciado com sucesso")
                    else:
                        logger.warning("Falha ao iniciar servidor WebSim")
                else:
                    logger.warning("Falha na inicialização do WebSim")
            else:
                logger.info("WebSim não configurado ou desabilitado")
                
        except Exception as e:
            logger.error(f"Erro na inicialização do WebSim: {e}")
    
    async def _initialize_conversation_engine(self):
        """Inicializa o ConversationEngine se configurado."""
        try:
            # Verifica se deve inicializar o ConversationEngine
            raw_config = self.config_manager.get_raw_config()
            conversation_config = raw_config.get("conversation_engine")
            
            if conversation_config and conversation_config.get("enabled", False):
                logger.info("Inicializando ConversationEngine...")
                
                # Remove o campo 'enabled' da configuração
                conversation_init_config = {k: v for k, v in conversation_config.items() if k != "enabled"}
                self.conversation_engine = ConversationEngine(conversation_init_config)
                
                # Coleta plugins de input e action
                input_plugins = {}
                action_plugins = {}
                
                if self.input_orchestrator:
                    input_plugins = self.input_orchestrator.inputs
                
                if self.action_orchestrator:
                    action_plugins = self.action_orchestrator.actions
                
                # Inicializa com componentes
                success = await self.conversation_engine.initialize(
                    self.llm_provider,
                    input_plugins,
                    action_plugins
                )
                
                if success:
                    logger.info("ConversationEngine inicializado com sucesso")
                else:
                    logger.warning("Falha na inicialização do ConversationEngine")
            else:
                logger.info("ConversationEngine não configurado ou desabilitado")
                
        except Exception as e:
            logger.error(f"Erro na inicialização do ConversationEngine: {e}")
    
    async def start(self):
        """Inicia o loop principal do sistema."""
        if not self.config:
            raise RuntimeError("Sistema não foi inicializado. Chame initialize() primeiro.")
        
        logger.info("Iniciando loop principal do sistema...")
        self.is_running = True
        self.start_time = time.time()
        
        try:
            # Loop principal
            while self.is_running:
                loop_start = time.time()
                
                try:
                    await self._run_loop()
                    self.loop_count += 1
                    
                except Exception as e:
                    logger.error(f"Erro no loop {self.loop_count}: {e}")
                    self.metrics["errors"] += 1
                    self.metrics["last_error"] = str(e)
                
                # Controle de frequência
                loop_time = time.time() - loop_start
                target_interval = 1.0 / self.config.hertz
                
                if loop_time < target_interval:
                    await asyncio.sleep(target_interval - loop_time)
                
                # Atualiza métricas
                self._update_metrics(loop_time)
                
        except KeyboardInterrupt:
            logger.info("Interrupção recebida, parando sistema...")
        except Exception as e:
            logger.error(f"Erro fatal no runtime: {e}")
        finally:
            await self.stop()
    
    async def _run_loop(self):
        """Executa uma iteração do loop principal."""
        # Coleta inputs
        inputs_data = await self.input_orchestrator.collect_inputs()
        
        if not inputs_data:
            return
        
        # Se ConversationEngine está ativo, usa o ciclo de conversação
        if self.conversation_engine:
            conversation_response = await self.conversation_engine.process_conversation_cycle(inputs_data)
            
            if conversation_response:
                # Executa resposta multimodal coordenada
                await self.conversation_engine.execute_response(conversation_response)
        else:
            # Usa o fluxo tradicional (sem conversação integrada)
            # Fusão de inputs
            fused_data = await self.fuser.fuse(inputs_data)
            
            if not fused_data:
                return
            
            # Processamento com LLM
            llm_response = await self.llm_provider.process(
                fused_data,
                self.config.system_prompt_base
            )
            
            if not llm_response:
                return
            
            # Execução de actions
            await self.action_orchestrator.execute_actions(llm_response)
    
    def _update_metrics(self, loop_time: float):
        """Atualiza métricas do sistema."""
        self.metrics["total_loops"] += 1
        
        # Média móvel do tempo de loop
        alpha = 0.1  # Fator de suavização
        self.metrics["avg_loop_time"] = (
            alpha * loop_time + 
            (1 - alpha) * self.metrics["avg_loop_time"]
        )
    
    async def stop(self):
        """Para o sistema."""
        logger.info("Parando sistema...")
        self.is_running = False
        
        # Para componentes
        if self.input_orchestrator:
            await self.input_orchestrator.stop()
        
        if self.action_orchestrator:
            await self.action_orchestrator.stop()
        
        if self.fuser:
            await self.fuser.stop()
        
        if self.llm_provider:
            await self.llm_provider.stop()
        
        # Para ConversationEngine
        if self.conversation_engine:
            await self.conversation_engine.stop()
        
        # Para G1Controller
        if self.g1_controller:
            await self.g1_controller.stop()
        
        # Para WebSim
        if self.websim:
            await self.websim.stop()
        
        # Log de estatísticas
        if self.start_time:
            total_time = time.time() - self.start_time
            logger.info(f"Estatísticas finais:")
            logger.info(f"  - Tempo total: {total_time:.2f}s")
            logger.info(f"  - Loops executados: {self.loop_count}")
            logger.info(f"  - Frequência média: {self.loop_count/total_time:.2f} Hz")
            logger.info(f"  - Tempo médio por loop: {self.metrics['avg_loop_time']*1000:.2f}ms")
            logger.info(f"  - Erros: {self.metrics['errors']}")
        
        logger.info("Sistema parado")
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Retorna o status atual do sistema.
        
        Returns:
            Dicionário com informações de status
        """
        # Status dos componentes principais
        status = {
            "is_running": self.is_running,
            "loop_count": self.loop_count,
            "start_time": self.start_time,
            "metrics": self.metrics.copy(),
            "config_loaded": self.config is not None,
            "components_initialized": all([
                self.input_orchestrator is not None,
                self.action_orchestrator is not None,
                self.fuser is not None,
                self.llm_provider is not None
            ])
        }
        
        # Adiciona status do G1Controller se disponível
        if self.g1_controller:
            try:
                g1_status = await self.g1_controller.get_status()
                status["g1_controller"] = g1_status
            except Exception as e:
                status["g1_controller"] = {"error": str(e)}
        else:
            status["g1_controller"] = None
        
        # Adiciona status do WebSim se disponível
        if self.websim:
            try:
                websim_status = await self.websim.get_status()
                status["websim"] = websim_status
            except Exception as e:
                status["websim"] = {"error": str(e)}
        else:
            status["websim"] = None
        
        # Adiciona status do ConversationEngine se disponível
        if self.conversation_engine:
            try:
                conversation_status = await self.conversation_engine.get_status()
                status["conversation_engine"] = conversation_status
            except Exception as e:
                status["conversation_engine"] = {"error": str(e)}
        else:
            status["conversation_engine"] = None
        
        return status
    
    async def reload_config(self):
        """Recarrega a configuração do sistema."""
        logger.info("Recarregando configuração...")
        
        try:
            # Recarrega configuração
            self.config = self.config_manager.reload_config()
            
            # Reinicializa componentes se necessário
            if self.config_manager.is_development_mode():
                await self._initialize_components()
            
            logger.info("Configuração recarregada com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao recarregar configuração: {e}")
    
    async def emergency_stop(self):
        """Para o sistema de emergência."""
        logger.warning("PARADA DE EMERGÊNCIA ATIVADA!")
        
        # Para imediatamente
        self.is_running = False
        
        # Executa parada de emergência nas actions
        if self.action_orchestrator:
            await self.action_orchestrator.emergency_stop()
        
        # Executa parada de emergência no G1Controller
        if self.g1_controller:
            await self.g1_controller.emergency_stop()
        
        logger.warning("Sistema parado de emergência")
