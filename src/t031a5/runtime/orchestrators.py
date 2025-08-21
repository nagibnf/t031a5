"""
Orchestrators para o sistema t031a5.

Coordenação de inputs e execução de actions do sistema G1.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Type
from datetime import datetime

from ..inputs.base import BaseInput, InputData
from ..actions.base import BaseAction, ActionRequest, ActionResult
from ..runtime.config import ConfigManager

logger = logging.getLogger(__name__)


class InputOrchestrator:
    """Orquestrador de inputs do sistema t031a5."""
    
    def __init__(self, inputs_config: List[Dict[str, Any]], config_manager: ConfigManager):
        """
        Inicializa o InputOrchestrator.
        
        Args:
            inputs_config: Lista de configurações de inputs
            config_manager: Gerenciador de configuração
        """
        self.inputs_config = inputs_config
        self.config_manager = config_manager
        self.inputs: Dict[str, BaseInput] = {}
        self.is_initialized = False
        self.is_running = False
        
        logger.debug(f"InputOrchestrator configurado com {len(inputs_config)} inputs")
    
    async def initialize(self) -> bool:
        """
        Inicializa todos os inputs configurados.
        
        Returns:
            True se a inicialização foi bem-sucedida
        """
        try:
            logger.info("Inicializando InputOrchestrator...")
            
            # Cria e inicializa cada input
            for input_config in self.inputs_config:
                success = await self._create_and_initialize_input(input_config)
                if not success:
                    logger.error(f"Falha ao inicializar input: {input_config.get('type', 'Unknown')}")
            
            if self.inputs:
                self.is_initialized = True
                logger.info(f"InputOrchestrator inicializado com {len(self.inputs)} inputs")
                return True
            else:
                logger.error("Nenhum input foi inicializado com sucesso")
                return False
                
        except Exception as e:
            logger.error(f"Erro na inicialização do InputOrchestrator: {e}")
            return False
    
    async def _create_and_initialize_input(self, input_config: Dict[str, Any]) -> bool:
        """
        Cria e inicializa um input específico.
        
        Args:
            input_config: Configuração do input
            
        Returns:
            True se a criação e inicialização foi bem-sucedida
        """
        try:
            input_type = input_config.get("type")
            if not input_type:
                logger.error("Tipo de input não especificado")
                return False
            
            # Cria o input apropriado
            input_instance = await self._create_input(input_type, input_config)
            if not input_instance:
                return False
            
            # Inicializa o input
            success = await input_instance.initialize()
            if success:
                self.inputs[input_type] = input_instance
                logger.info(f"Input {input_type} inicializado com sucesso")
                return True
            else:
                logger.error(f"Falha na inicialização do input {input_type}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao criar/inicializar input: {e}")
            return False
    
    async def _create_input(self, input_type: str, config: Dict[str, Any]) -> Optional[BaseInput]:
        """
        Cria uma instância do input apropriado.
        
        Args:
            input_type: Tipo do input
            config: Configuração do input
            
        Returns:
            Instância do input ou None se falhar
        """
        try:
            # Mapeamento de tipos para classes
            input_classes = {
                "G1Voice": self._get_g1_voice_class(),
                "G1Vision": self._get_g1_vision_class(),
                "G1State": self._get_g1_state_class(),
            }
            
            input_class = input_classes.get(input_type)
            if not input_class:
                logger.error(f"Tipo de input não suportado: {input_type}")
                return None
            
            # Cria instância
            input_instance = input_class(config.get("config", {}))
            return input_instance
            
        except Exception as e:
            logger.error(f"Erro ao criar input {input_type}: {e}")
            return None
    
    def _get_g1_voice_class(self) -> Type[BaseInput]:
        """Retorna a classe G1VoiceInput."""
        try:
            from ..inputs.plugins.g1_voice import G1VoiceInput
            return G1VoiceInput
        except ImportError:
            logger.warning("G1VoiceInput não disponível, usando mock")
            return self._create_mock_input_class("G1Voice")
    
    def _get_g1_vision_class(self) -> Type[BaseInput]:
        """Retorna a classe G1VisionInput (Intel RealSense D435i)."""
        try:
            from ..inputs.plugins.g1_vision_d435i import G1VisionInput
            return G1VisionInput
        except ImportError:
            logger.warning("G1VisionInput D435i não disponível, usando mock")
            return self._create_mock_input_class("G1Vision")
    

    
    def _get_g1_state_class(self) -> Type[BaseInput]:
        """Retorna a classe G1StateInput."""
        try:
            from ..inputs.plugins.g1_state import G1StateInput
            return G1StateInput
        except ImportError:
            logger.warning("G1StateInput não disponível, usando mock")
            return self._create_mock_input_class("G1State")
    
    def _create_mock_input_class(self, input_type: str) -> Type[BaseInput]:
        """Cria uma classe mock para inputs não implementados."""
        class MockInput(BaseInput):
            def __init__(self, config: Dict[str, Any]):
                super().__init__(config)
                self.input_type = input_type
            
            async def _initialize(self) -> bool:
                logger.info(f"Mock {input_type} inicializado")
                return True
            
            async def _start(self) -> bool:
                logger.info(f"Mock {input_type} iniciado")
                return True
            
            async def _stop(self) -> bool:
                logger.info(f"Mock {input_type} parado")
                return True
            
            async def _get_data(self):
                # Retorna dados mock
                return InputData(
                    input_type=input_type,
                    source="mock",
                    timestamp=datetime.now(),
                    data={"mock_data": True, "timestamp": datetime.now().isoformat()},
                    confidence=0.8
                )
        
        return MockInput
    
    async def start(self) -> bool:
        """
        Inicia todos os inputs.
        
        Returns:
            True se o início foi bem-sucedido
        """
        try:
            if not self.is_initialized:
                logger.error("InputOrchestrator não foi inicializado")
                return False
            
            logger.info("Iniciando InputOrchestrator...")
            
            # Inicia cada input
            for input_type, input_instance in self.inputs.items():
                success = await input_instance.start()
                if not success:
                    logger.error(f"Falha ao iniciar input {input_type}")
            
            self.is_running = True
            logger.info("InputOrchestrator iniciado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao iniciar InputOrchestrator: {e}")
            return False
    
    async def stop(self) -> bool:
        """
        Para todos os inputs.
        
        Returns:
            True se a parada foi bem-sucedida
        """
        try:
            logger.info("Parando InputOrchestrator...")
            
            # Para cada input
            for input_type, input_instance in self.inputs.items():
                await input_instance.stop()
            
            self.is_running = False
            logger.info("InputOrchestrator parado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao parar InputOrchestrator: {e}")
            return False
    
    async def collect_inputs(self) -> List[InputData]:
        """
        Coleta dados de todos os inputs ativos.
        
        Returns:
            Lista de dados de inputs
        """
        try:
            if not self.is_running:
                logger.debug("InputOrchestrator não está rodando")
                return []
            
            inputs_data = []
            
            # Coleta dados de cada input
            for input_type, input_instance in self.inputs.items():
                try:
                    data = await input_instance.get_data()
                    if data:
                        inputs_data.append(data)
                        logger.debug(f"Dados coletados de {input_type}")
                except Exception as e:
                    logger.error(f"Erro ao coletar dados de {input_type}: {e}")
            
            if inputs_data:
                logger.debug(f"Coletados dados de {len(inputs_data)} inputs")
            
            return inputs_data
            
        except Exception as e:
            logger.error(f"Erro na coleta de inputs: {e}")
            return []
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Retorna o status de todos os inputs.
        
        Returns:
            Dicionário com status dos inputs
        """
        status = {
            "initialized": self.is_initialized,
            "running": self.is_running,
            "total_inputs": len(self.inputs),
            "inputs": {}
        }
        
        for input_type, input_instance in self.inputs.items():
            status["inputs"][input_type] = await input_instance.get_status()
        
        return status
    
    async def health_check(self) -> bool:
        """
        Verifica a saúde de todos os inputs.
        
        Returns:
            True se todos os inputs estão saudáveis
        """
        try:
            if not self.inputs:
                return False
            
            health_status = []
            for input_type, input_instance in self.inputs.items():
                healthy = await input_instance.health_check()
                health_status.append(healthy)
                
                if not healthy:
                    logger.warning(f"Input {input_type} não está saudável")
            
            return all(health_status)
            
        except Exception as e:
            logger.error(f"Erro na verificação de saúde dos inputs: {e}")
            return False


class ActionOrchestrator:
    """Orquestrador de actions do sistema t031a5."""
    
    def __init__(self, actions_config: List[Dict[str, Any]], config_manager: ConfigManager):
        """
        Inicializa o ActionOrchestrator.
        
        Args:
            actions_config: Lista de configurações de actions
            config_manager: Gerenciador de configuração
        """
        self.actions_config = actions_config
        self.config_manager = config_manager
        self.actions: Dict[str, BaseAction] = {}
        self.is_initialized = False
        self.is_running = False
        
        logger.debug(f"ActionOrchestrator configurado com {len(actions_config)} actions")
    
    async def initialize(self) -> bool:
        """
        Inicializa todas as actions configuradas.
        
        Returns:
            True se a inicialização foi bem-sucedida
        """
        try:
            logger.info("Inicializando ActionOrchestrator...")
            
            # Cria e inicializa cada action
            for action_config in self.actions_config:
                success = await self._create_and_initialize_action(action_config)
                if not success:
                    logger.error(f"Falha ao inicializar action: {action_config.get('name', 'Unknown')}")
            
            if self.actions:
                self.is_initialized = True
                logger.info(f"ActionOrchestrator inicializado com {len(self.actions)} actions")
                return True
            else:
                logger.error("Nenhuma action foi inicializada com sucesso")
                return False
                
        except Exception as e:
            logger.error(f"Erro na inicialização do ActionOrchestrator: {e}")
            return False
    
    async def _create_and_initialize_action(self, action_config: Dict[str, Any]) -> bool:
        """
        Cria e inicializa uma action específica.
        
        Args:
            action_config: Configuração da action
            
        Returns:
            True se a criação e inicialização foi bem-sucedida
        """
        try:
            action_name = action_config.get("name")
            connector = action_config.get("connector")
            
            if not action_name or not connector:
                logger.error("Nome ou connector da action não especificado")
                return False
            
            # Cria a action apropriada
            action_instance = await self._create_action(connector, action_config)
            if not action_instance:
                return False
            
            # Inicializa a action
            success = await action_instance.initialize()
            if success:
                self.actions[action_name] = action_instance
                logger.info(f"Action {action_name} inicializada com sucesso")
                return True
            else:
                logger.error(f"Falha na inicialização da action {action_name}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao criar/inicializar action: {e}")
            return False
    
    async def _create_action(self, connector: str, config: Dict[str, Any]) -> Optional[BaseAction]:
        """
        Cria uma instância da action apropriada.
        
        Args:
            connector: Tipo do connector
            config: Configuração da action
            
        Returns:
            Instância da action ou None se falhar
        """
        try:
            # Mapeamento de connectors para classes
            action_classes = {
                "g1_speech": self._get_g1_speech_class(),
                "g1_emotion": self._get_g1_emotion_class(),
                "g1_movement": self._get_g1_movement_class(),
                "g1_arms": self._get_g1_arms_class(),
                "g1_audio": self._get_g1_audio_class(),
            }
            
            action_class = action_classes.get(connector)
            if not action_class:
                logger.error(f"Connector de action não suportado: {connector}")
                return None
            
            # Cria instância
            action_instance = action_class(config.get("config", {}))
            return action_instance
            
        except Exception as e:
            logger.error(f"Erro ao criar action {connector}: {e}")
            return None
    
    def _get_g1_speech_class(self) -> Type[BaseAction]:
        """Retorna a classe G1SpeechAction."""
        try:
            from ..actions.g1_speech import G1SpeechAction
            return G1SpeechAction
        except ImportError:
            logger.warning("G1SpeechAction não disponível, usando mock")
            return self._create_mock_action_class("g1_speech")
    
    def _get_g1_emotion_class(self) -> Type[BaseAction]:
        """Retorna a classe G1EmotionAction."""
        try:
            from ..actions.g1_emotion import G1EmotionAction
            return G1EmotionAction
        except ImportError:
            logger.warning("G1EmotionAction não disponível, usando mock")
            return self._create_mock_action_class("g1_emotion")
    
    def _get_g1_movement_class(self) -> Type[BaseAction]:
        """Retorna a classe G1MovementAction."""
        try:
            from ..actions.g1_movement import G1MovementAction
            return G1MovementAction
        except ImportError:
            logger.warning("G1MovementAction não disponível, usando mock")
            return self._create_mock_action_class("g1_movement")
    
    def _get_g1_arms_class(self) -> Type[BaseAction]:
        """Retorna a classe G1ArmsAction."""
        try:
            from ..actions.g1_arms import G1ArmsAction
            return G1ArmsAction
        except ImportError:
            logger.warning("G1ArmsAction não disponível, usando mock")
            return self._create_mock_action_class("g1_arms")
    
    def _get_g1_audio_class(self) -> Type[BaseAction]:
        """Retorna a classe G1AudioAction."""
        try:
            from ..actions.g1_audio import G1AudioAction
            return G1AudioAction
        except ImportError:
            logger.warning("G1AudioAction não disponível, usando mock")
            return self._create_mock_action_class("g1_audio")
    
    def _create_mock_action_class(self, action_type: str) -> Type[BaseAction]:
        """Cria uma classe mock para actions não implementadas."""
        class MockAction(BaseAction):
            def __init__(self, config: Dict[str, Any]):
                super().__init__(config)
                self.action_type = action_type
            
            async def _initialize(self) -> bool:
                logger.info(f"Mock {action_type} inicializado")
                return True
            
            async def _start(self) -> bool:
                logger.info(f"Mock {action_type} iniciado")
                return True
            
            async def _stop(self) -> bool:
                logger.info(f"Mock {action_type} parado")
                return True
            
            async def _execute(self, request: ActionRequest) -> ActionResult:
                # Retorna resultado mock
                return ActionResult(
                    action_type=action_type,
                    action_name=request.action_name,
                    timestamp=datetime.now(),
                    success=True,
                    data={"mock_result": True, "action": request.action_name},
                    execution_time=0.1
                )
        
        return MockAction
    
    async def start(self) -> bool:
        """
        Inicia todas as actions.
        
        Returns:
            True se o início foi bem-sucedido
        """
        try:
            if not self.is_initialized:
                logger.error("ActionOrchestrator não foi inicializado")
                return False
            
            logger.info("Iniciando ActionOrchestrator...")
            
            # Inicia cada action
            for action_name, action_instance in self.actions.items():
                success = await action_instance.start()
                if not success:
                    logger.error(f"Falha ao iniciar action {action_name}")
            
            self.is_running = True
            logger.info("ActionOrchestrator iniciado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao iniciar ActionOrchestrator: {e}")
            return False
    
    async def stop(self) -> bool:
        """
        Para todas as actions.
        
        Returns:
            True se a parada foi bem-sucedida
        """
        try:
            logger.info("Parando ActionOrchestrator...")
            
            # Para cada action
            for action_name, action_instance in self.actions.items():
                await action_instance.stop()
            
            self.is_running = False
            logger.info("ActionOrchestrator parado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao parar ActionOrchestrator: {e}")
            return False
    
    async def execute_actions(self, llm_response: str) -> List[ActionResult]:
        """
        Executa actions baseado na resposta do LLM.
        
        Args:
            llm_response: Resposta do LLM
            
        Returns:
            Lista de resultados das actions
        """
        try:
            if not self.is_running:
                logger.debug("ActionOrchestrator não está rodando")
                return []
            
            # Parse da resposta do LLM para extrair actions
            actions_to_execute = self._parse_llm_response(llm_response)
            
            results = []
            
            # Executa cada action
            for action_request in actions_to_execute:
                try:
                    action_name = action_request.action_name
                    if action_name in self.actions:
                        result = await self.actions[action_name].execute(action_request)
                        results.append(result)
                        logger.debug(f"Action {action_name} executada")
                    else:
                        logger.warning(f"Action {action_name} não encontrada")
                except Exception as e:
                    logger.error(f"Erro ao executar action {action_request.action_name}: {e}")
            
            if results:
                logger.debug(f"Executadas {len(results)} actions")
            
            return results
            
        except Exception as e:
            logger.error(f"Erro na execução de actions: {e}")
            return []
    
    def _parse_llm_response(self, llm_response: str) -> List[ActionRequest]:
        """
        Parse da resposta do LLM para extrair actions.
        
        Args:
            llm_response: Resposta do LLM
            
        Returns:
            Lista de requisições de action
        """
        # Implementação básica - em uma versão mais avançada,
        # isso seria um parser mais sofisticado
        actions = []
        
        # Exemplo simples: procura por comandos específicos
        if "falar" in llm_response.lower() or "dizer" in llm_response.lower():
            actions.append(ActionRequest(
                action_type="speech",
                action_name="speak",
                timestamp=datetime.now(),
                data={"text": llm_response}
            ))
        
        if "feliz" in llm_response.lower() or "alegre" in llm_response.lower():
            actions.append(ActionRequest(
                action_type="emotion",
                action_name="set_emotion",
                timestamp=datetime.now(),
                data={"emotion": "happy"}
            ))
        
        return actions
    
    async def emergency_stop(self) -> bool:
        """
        Para de emergência de todas as actions.
        
        Returns:
            True se a parada de emergência foi bem-sucedida
        """
        try:
            logger.warning("Parada de emergência do ActionOrchestrator")
            
            # Para de emergência cada action
            for action_name, action_instance in self.actions.items():
                await action_instance.emergency_stop()
            
            self.is_running = False
            logger.warning("ActionOrchestrator parado de emergência com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro na parada de emergência do ActionOrchestrator: {e}")
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Retorna o status de todas as actions.
        
        Returns:
            Dicionário com status das actions
        """
        status = {
            "initialized": self.is_initialized,
            "running": self.is_running,
            "total_actions": len(self.actions),
            "actions": {}
        }
        
        for action_name, action_instance in self.actions.items():
            status["actions"][action_name] = await action_instance.get_status()
        
        return status
    
    async def health_check(self) -> bool:
        """
        Verifica a saúde de todas as actions.
        
        Returns:
            True se todas as actions estão saudáveis
        """
        try:
            if not self.actions:
                return False
            
            health_status = []
            for action_name, action_instance in self.actions.items():
                healthy = await action_instance.health_check()
                health_status.append(healthy)
                
                if not healthy:
                    logger.warning(f"Action {action_name} não está saudável")
            
            return all(health_status)
            
        except Exception as e:
            logger.error(f"Erro na verificação de saúde das actions: {e}")
            return False
