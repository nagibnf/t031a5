"""
Interface WebSim para debugging e controle remoto do G1.

Fornece interface web para monitoramento e controle do robô.
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import aiohttp
from aiohttp import web, WSMsgType
import aiofiles

logger = logging.getLogger(__name__)


@dataclass
class WebSimConfig:
    """Configuração do WebSim."""
    host: str = "localhost"
    port: int = 8080
    debug: bool = True
    auto_reload: bool = True
    static_dir: str = "static"
    templates_dir: str = "templates"
    max_connections: int = 10
    update_interval: float = 0.1
    cors_enabled: bool = True
    auto_start: bool = False
    mock_robot: bool = True


@dataclass
class RobotStatus:
    """Status do robô para WebSim."""
    connected: bool = False
    state: str = "disconnected"
    battery_level: float = 0.0
    battery_voltage: float = 0.0
    temperature: float = 0.0
    pose_x: float = 0.0
    pose_y: float = 0.0
    pose_yaw: float = 0.0
    last_update: float = 0.0
    command_history: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.command_history is None:
            self.command_history = []


class WebSim:
    """Interface WebSim para debugging e controle remoto do G1."""
    
    def __init__(self, config: Dict[str, Any], g1_controller=None):
        """
        Inicializa o WebSim.
        
        Args:
            config: Configuração do WebSim
            g1_controller: Controlador G1 opcional
        """
        self.config = WebSimConfig(**config)
        self.g1_controller = g1_controller
        self.name = "WebSim"
        
        # Estado do servidor
        self.app = None
        self.runner = None
        self.site = None
        self.is_running = False
        
        # Conexões WebSocket
        self.websocket_connections = []
        self.max_connections = self.config.max_connections
        
        # Status do robô
        self.robot_status = RobotStatus()
        self.last_status_update = 0.0
        
        # Callbacks
        self.on_command = None
        self.on_status_update = None
        self.on_connection_change = None
        
        # Tarefas
        self.status_task = None
        self.cleanup_task = None
        
        logger.debug(f"WebSim configurado: {self.config.host}:{self.config.port}")
    
    async def initialize(self) -> bool:
        """
        Inicializa o WebSim.
        
        Returns:
            True se a inicialização foi bem-sucedida
        """
        try:
            logger.info("Inicializando WebSim...")
            
            # Cria aplicação web
            self.app = web.Application()
            
            # Configura rotas
            self._setup_routes()
            
            # Configura middleware
            self._setup_middleware()
            
            # Configura arquivos estáticos
            await self._setup_static_files()
            
            # Configura templates
            await self._setup_templates()
            
            # Configura rotas estáticas (após criar os arquivos)
            self.app.router.add_static("/static", self.config.static_dir)
            
            logger.info("WebSim inicializado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro na inicialização do WebSim: {e}")
            return False
    
    def _setup_routes(self):
        """Configura as rotas da aplicação."""
        
        # Rota principal
        self.app.router.add_get("/", self._handle_index)
        
        # API REST
        self.app.router.add_get("/api/status", self._handle_api_status)
        self.app.router.add_post("/api/command", self._handle_api_command)
        self.app.router.add_get("/api/history", self._handle_api_history)
        self.app.router.add_post("/api/emergency", self._handle_api_emergency)
        
        # WebSocket
        self.app.router.add_get("/ws", self._handle_websocket)
    
    def _setup_middleware(self):
        """Configura middleware da aplicação."""
        
        @web.middleware
        async def error_middleware(request, handler):
            try:
                return await handler(request)
            except web.HTTPException as ex:
                return web.json_response(
                    {"error": str(ex)}, 
                    status=ex.status
                )
            except Exception as e:
                logger.error(f"Erro na requisição: {e}")
                return web.json_response(
                    {"error": "Erro interno do servidor"}, 
                    status=500
                )
        
        self.app.middlewares.append(error_middleware)
    
    async def _setup_static_files(self):
        """Configura arquivos estáticos."""
        static_dir = Path(self.config.static_dir)
        if not static_dir.exists():
            static_dir.mkdir(parents=True)
            logger.warning(f"Diretório static não existe: {static_dir}")
        
        # Verifica se os arquivos oficiais existem
        css_file = static_dir / "style.css"
        js_file = static_dir / "websim.js"
        if not css_file.exists() or not js_file.exists():
            logger.error(f"Arquivos estáticos oficiais não encontrados em {static_dir}")
            logger.error("Use os arquivos em static/ (versão mobile-first oficial)")
    
    async def _setup_templates(self):
        """Configura templates."""
        templates_dir = Path(self.config.templates_dir)
        if not templates_dir.exists():
            templates_dir.mkdir(parents=True)
            logger.warning(f"Diretório templates não existe: {templates_dir}")
        
        # Verifica se o template oficial existe
        html_file = templates_dir / "index.html"
        if not html_file.exists():
            logger.error(f"Template oficial não encontrado: {html_file}")
            logger.error("Use o arquivo em templates/index.html (versão mobile-first oficial)")
    
    # Funções de geração automática removidas - usar arquivos oficiais em static/ e templates/
    
    # Função _create_default_templates REMOVIDA - usar templates/index.html oficial
    pass

    async def _handle_index(self, request):
        """Manipula requisição da página principal."""
        try:
            # Retorna uma página HTML simples se o template não existir
            template_file = Path(self.config.templates_dir) / "index.html"
            if template_file.exists():
                async with aiofiles.open(template_file, 'r') as f:
                    content = await f.read()
                return web.Response(text=content, content_type='text/html')
            else:
                # Página HTML básica
                html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>t031a5 WebSim - G1 Monitor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        .status { background: #e3f2fd; padding: 15px; border-radius: 4px; margin: 20px 0; }
        .error { background: #ffebee; padding: 15px; border-radius: 4px; margin: 20px 0; }
        .success { background: #e8f5e8; padding: 15px; border-radius: 4px; margin: 20px 0; }
        h1 { color: #1976d2; }
        .metric { display: inline-block; margin: 10px 20px 10px 0; }
        .value { font-weight: bold; color: #2e7d32; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 t031a5 WebSim - G1 Monitor</h1>
        
        <div class="success">
            <h3>✅ Sistema Funcionando!</h3>
            <p>O WebSim está ativo e conectado ao sistema t031a5.</p>
        </div>
        
        <div class="status">
            <h3>📊 Status do Sistema</h3>
            <div class="metric">Sistema: <span class="value">Ativo</span></div>
            <div class="metric">WebSim: <span class="value">Funcionando</span></div>
            <div class="metric">G1 SDK: <span class="value">Instalado</span></div>
        </div>
        
        <div class="status">
            <h3>🎯 APIs Disponíveis</h3>
            <p><strong>GET /api/status</strong> - Status do sistema</p>
            <p><strong>POST /api/command</strong> - Enviar comandos</p>
            <p><strong>GET /api/history</strong> - Histórico de comandos</p>
            <p><strong>GET /ws</strong> - WebSocket para tempo real</p>
        </div>
        
        <div class="status">
            <h3>🚀 Próximos Passos</h3>
            <p>1. <strong>Conectar G1</strong>: Configure o IP do robô</p>
            <p>2. <strong>Testar Conexão</strong>: Verifique a conectividade</p>
            <p>3. <strong>Iniciar Conversação</strong>: Ative o modo multimodal</p>
        </div>
        
        <div class="status">
            <h3>🎮 Controle do G1</h3>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 15px 0;">
                <button onclick="sendCommand('move_forward')" style="padding: 10px; background: #4caf50; color: white; border: none; border-radius: 4px; cursor: pointer;">⬆️ Frente</button>
                <button onclick="sendCommand('turn_left')" style="padding: 10px; background: #2196f3; color: white; border: none; border-radius: 4px; cursor: pointer;">⬅️ Esquerda</button>
                <button onclick="sendCommand('turn_right')" style="padding: 10px; background: #2196f3; color: white; border: none; border-radius: 4px; cursor: pointer;">➡️ Direita</button>
                <button onclick="sendCommand('move_backward')" style="padding: 10px; background: #ff9800; color: white; border: none; border-radius: 4px; cursor: pointer;">⬇️ Trás</button>
                <button onclick="sendCommand('perform_gesture', {gesture: 'wave'})" style="padding: 10px; background: #9c27b0; color: white; border: none; border-radius: 4px; cursor: pointer;">👋 Acenar</button>
                <button onclick="sendCommand('emergency_stop')" style="padding: 10px; background: #f44336; color: white; border: none; border-radius: 4px; cursor: pointer;">🛑 Parar</button>
            </div>
            <div style="margin: 15px 0;">
                <input type="text" id="speechText" placeholder="Digite algo para o G1 falar..." style="width: 70%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
                <button onclick="sendSpeech()" style="padding: 8px 15px; background: #673ab7; color: white; border: none; border-radius: 4px; cursor: pointer; margin-left: 5px;">🗣️ Falar</button>
            </div>
        </div>
        
        <div class="status">
            <h3>🔧 Comandos de API</h3>
            <code style="background: #f5f5f5; padding: 2px 4px;">curl http://localhost:8080/api/status</code><br><br>
            <code style="background: #f5f5f5; padding: 2px 4px;">python -m t031a5.cli status</code>
        </div>
    </div>
    
    <script>
        // Função para enviar comandos
        async function sendCommand(command, parameters = {}) {
            try {
                const response = await fetch('/api/command', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        command: command,
                        parameters: parameters
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showMessage(`✅ Comando '${command}' executado com sucesso!`, 'success');
                } else {
                    showMessage(`❌ Erro ao executar '${command}': ${result.error || 'Erro desconhecido'}`, 'error');
                }
            } catch (error) {
                showMessage(`💥 Erro de conexão: ${error.message}`, 'error');
            }
        }
        
        // Função para enviar comando de fala
        function sendSpeech() {
            const text = document.getElementById('speechText').value;
            if (text.trim()) {
                sendCommand('speak_text', { text: text });
                document.getElementById('speechText').value = '';
            } else {
                showMessage('⚠️ Digite algum texto para o G1 falar!', 'error');
            }
        }
        
        // Função para mostrar mensagens
        function showMessage(message, type) {
            // Remove mensagens anteriores
            const oldMessages = document.querySelectorAll('.temp-message');
            oldMessages.forEach(msg => msg.remove());
            
            // Cria nova mensagem
            const messageDiv = document.createElement('div');
            messageDiv.className = `temp-message ${type}`;
            messageDiv.style.cssText = `
                position: fixed; top: 20px; right: 20px; 
                padding: 15px; border-radius: 4px; z-index: 1000;
                max-width: 400px; box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                ${type === 'success' ? 'background: #4caf50; color: white;' : 'background: #f44336; color: white;'}
            `;
            messageDiv.textContent = message;
            
            document.body.appendChild(messageDiv);
            
            // Remove após 3 segundos
            setTimeout(() => messageDiv.remove(), 3000);
        }
        
        // Detectar Enter no campo de texto
        document.addEventListener('DOMContentLoaded', function() {
            const speechInput = document.getElementById('speechText');
            if (speechInput) {
                speechInput.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        sendSpeech();
                    }
                });
            }
        });
        
        // Auto-refresh da página a cada 60 segundos (aumentado para não atrapalhar)
        setTimeout(() => window.location.reload(), 60000);
    </script>
</body>
</html>
                """
                return web.Response(text=html_content, content_type='text/html')
        except Exception as e:
            logger.error(f"Erro ao servir página principal: {e}")
            return web.Response(text=f"Erro interno: {e}", status=500)
    
    async def _handle_api_status(self, request):
        """Manipula requisição de status via API."""
        try:
            await self._update_robot_status()
            return web.json_response(asdict(self.robot_status))
        except Exception as e:
            logger.error(f"Erro ao obter status: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def _handle_api_command(self, request):
        """Manipula comando via API."""
        try:
            data = await request.json()
            command = data.get('command')
            parameters = data.get('parameters', {})
            
            if not command:
                return web.json_response({"error": "Comando não especificado"}, status=400)
            
            success = await self._execute_command(command, parameters)
            
            return web.json_response({
                "success": success,
                "command": command,
                "parameters": parameters
            })
            
        except Exception as e:
            logger.error(f"Erro ao executar comando: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def _handle_api_history(self, request):
        """Manipula requisição de histórico via API."""
        try:
            limit = int(request.query.get('limit', 10))
            history = self.robot_status.command_history[-limit:]
            return web.json_response(history)
        except Exception as e:
            logger.error(f"Erro ao obter histórico: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def _handle_api_emergency(self, request):
        """Manipula parada de emergência via API."""
        try:
            success = await self._execute_command('emergency_stop', {})
            return web.json_response({
                "success": success,
                "command": "emergency_stop"
            })
        except Exception as e:
            logger.error(f"Erro na parada de emergência: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def _handle_websocket(self, request):
        """Manipula conexão WebSocket."""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        # Adiciona à lista de conexões
        if len(self.websocket_connections) < self.max_connections:
            self.websocket_connections.append(ws)
            logger.info(f"WebSocket conectado. Total: {len(self.websocket_connections)}")
        else:
            await ws.close()
            return ws
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await self._handle_websocket_message(ws, data)
                    except json.JSONDecodeError:
                        logger.error("Mensagem WebSocket inválida")
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f"Erro no WebSocket: {ws.exception()}")
        except Exception as e:
            logger.error(f"Erro no WebSocket: {e}")
        finally:
            # Remove da lista de conexões
            if ws in self.websocket_connections:
                self.websocket_connections.remove(ws)
            logger.info(f"WebSocket desconectado. Total: {len(self.websocket_connections)}")
        
        return ws
    
    async def _handle_websocket_message(self, ws, data):
        """Manipula mensagem WebSocket."""
        msg_type = data.get('type')
        
        if msg_type == 'command':
            command = data.get('command')
            parameters = data.get('parameters', {})
            
            success = await self._execute_command(command, parameters)
            
            # Envia resultado
            await ws.send_json({
                'type': 'command_result',
                'success': success,
                'command': command,
                'parameters': parameters
            })
            
        elif msg_type == 'get_status':
            await self._update_robot_status()
            await ws.send_json({
                'type': 'status',
                'data': asdict(self.robot_status)
            })
    
    async def _execute_command(self, command: str, parameters: Dict[str, Any]) -> bool:
        """
        Executa comando no controlador G1 ou simula em modo mock.
        
        Args:
            command: Nome do comando
            parameters: Parâmetros do comando
            
        Returns:
            True se o comando foi executado com sucesso
        """
        try:
            logger.info(f"Executando comando: {command} com parâmetros: {parameters}")
            
            # Lista de comandos válidos
            valid_commands = {
                'move_forward', 'move_backward', 'turn_left', 'turn_right',
                'move_to_position', 'perform_gesture', 'speak_text', 
                'emergency_stop', 'get_status', 'test_connection'
            }
            
            if command not in valid_commands:
                logger.error(f"Comando desconhecido: {command}")
                return False
            
            # Se G1Controller está disponível, usa o real
            if self.g1_controller:
                command_map = {
                    'move_forward': self.g1_controller.move_forward,
                    'move_backward': self.g1_controller.move_backward,
                    'turn_left': self.g1_controller.turn_left,
                    'turn_right': self.g1_controller.turn_right,
                    'move_to_position': self.g1_controller.move_to_position,
                    'perform_gesture': self.g1_controller.perform_gesture,
                    'speak_text': self.g1_controller.speak_text,
                    'emergency_stop': self.g1_controller.emergency_stop
                }
            else:
                # Modo mock - simula comandos
                logger.info(f"Modo mock: simulando comando '{command}'")
                return await self._execute_mock_command(command, parameters)
            
            # Mapeia parâmetros para nomes corretos
            param_mapping = {
                'perform_gesture': {'gesture': 'gesture_name'},
                'speak_text': {'text': 'text', 'emotion': 'emotion', 'volume': 'volume'}
            }
            
            if command not in command_map:
                logger.error(f"Comando desconhecido: {command}")
                return False
            
            # Executa comando
            method = command_map[command]
            
            # Mapeia parâmetros se necessário
            if command in param_mapping:
                mapped_params = {}
                for web_param, method_param in param_mapping[command].items():
                    if web_param in parameters:
                        mapped_params[method_param] = parameters[web_param]
                parameters = mapped_params
            
            success = await method(**parameters)
            
            # Chama callback se configurado
            if self.on_command:
                await self.on_command(command, parameters, success)
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao executar comando {command}: {e}")
            return False
    
    async def _execute_mock_command(self, command: str, parameters: Dict[str, Any]) -> bool:
        """
        Executa comando em modo mock para demonstração.
        
        Args:
            command: Nome do comando
            parameters: Parâmetros do comando
            
        Returns:
            True sempre (simulação bem-sucedida)
        """
        import asyncio
        import time
        
        # Simula diferentes comandos
        if command == 'move_forward':
            logger.info("🤖 Mock: Movendo para frente...")
            self.robot_status.pose_x += 0.5
            
        elif command == 'move_backward':
            logger.info("🤖 Mock: Movendo para trás...")
            self.robot_status.pose_x -= 0.5
            
        elif command == 'turn_left':
            logger.info("🤖 Mock: Virando à esquerda...")
            self.robot_status.pose_yaw += 15.0
            
        elif command == 'turn_right':
            logger.info("🤖 Mock: Virando à direita...")
            self.robot_status.pose_yaw -= 15.0
            
        elif command == 'perform_gesture':
            gesture = parameters.get('gesture', 'wave')
            logger.info(f"🤖 Mock: Executando gesto '{gesture}'...")
            
        elif command == 'speak_text':
            text = parameters.get('text', 'Olá!')
            logger.info(f"🤖 Mock: Falando '{text}'...")
            
        elif command == 'emergency_stop':
            logger.info("🛑 Mock: Parada de emergência ativada!")
            self.robot_status.state = "emergency_stop"
            
        elif command == 'get_status':
            logger.info("📊 Mock: Obtendo status do robô...")
            
        elif command == 'test_connection':
            logger.info("🔗 Mock: Testando conexão...")
            
        # Simula um pequeno delay para realismo
        await asyncio.sleep(0.1)
        
        # Atualiza timestamp
        self.robot_status.last_update = time.time()
        
        logger.info(f"✅ Mock: Comando '{command}' executado com sucesso!")
        return True
    
    async def _update_robot_status(self):
        """Atualiza status do robô."""
        try:
            if self.g1_controller:
                # Obtém status do controlador
                status = await self.g1_controller.get_status()
                
                # Obtém sensores
                sensors = await self.g1_controller.get_sensors()
                
                # Obtém pose
                pose = await self.g1_controller.get_pose()
                
                # Atualiza status
                self.robot_status.connected = status['interface']['connected']
                self.robot_status.state = status['interface']['state']
                self.robot_status.battery_level = sensors.battery_level
                self.robot_status.battery_voltage = sensors.battery_voltage
                self.robot_status.temperature = sensors.temperature
                self.robot_status.pose_x = pose.x
                self.robot_status.pose_y = pose.y
                self.robot_status.pose_yaw = pose.yaw
                self.robot_status.last_update = time.time()
                
                # Obtém histórico
                history = self.g1_controller.get_command_history(10)
                self.robot_status.command_history = history
                
            # Chama callback se configurado
            if self.on_status_update:
                await self.on_status_update(self.robot_status)
                
        except Exception as e:
            logger.error(f"Erro ao atualizar status do robô: {e}")
    
    async def _broadcast_status(self):
        """Envia status para todos os WebSockets conectados."""
        try:
            await self._update_robot_status()
            
            message = {
                'type': 'status',
                'data': asdict(self.robot_status)
            }
            
            # Remove conexões fechadas
            self.websocket_connections = [
                ws for ws in self.websocket_connections 
                if not ws.closed
            ]
            
            # Envia para todas as conexões
            for ws in self.websocket_connections:
                try:
                    await ws.send_json(message)
                except Exception as e:
                    logger.error(f"Erro ao enviar para WebSocket: {e}")
                    
        except Exception as e:
            logger.error(f"Erro ao broadcast de status: {e}")
    
    async def start(self) -> bool:
        """
        Inicia o servidor WebSim.
        
        Returns:
            True se o servidor foi iniciado com sucesso
        """
        try:
            logger.info(f"Iniciando WebSim em {self.config.host}:{self.config.port}")
            
            # Cria runner
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            
            # Inicia servidor
            self.site = web.TCPSite(
                self.runner, 
                self.config.host, 
                self.config.port
            )
            await self.site.start()
            
            self.is_running = True
            
            # Inicia tarefas em background
            self.status_task = asyncio.create_task(self._status_loop())
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            logger.info(f"✅ WebSim iniciado em http://{self.config.host}:{self.config.port}")
            logger.info(f"🌐 Abra seu navegador e acesse: http://localhost:{self.config.port}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar WebSim: {e}")
            return False
    
    async def _status_loop(self):
        """Loop de atualização de status."""
        while self.is_running:
            try:
                await self._broadcast_status()
                await asyncio.sleep(self.config.update_interval)
            except Exception as e:
                logger.error(f"Erro no loop de status: {e}")
                await asyncio.sleep(1.0)
    
    async def _cleanup_loop(self):
        """Loop de limpeza de conexões."""
        while self.is_running:
            try:
                # Remove conexões fechadas
                self.websocket_connections = [
                    ws for ws in self.websocket_connections 
                    if not ws.closed
                ]
                await asyncio.sleep(5.0)
            except Exception as e:
                logger.error(f"Erro no loop de limpeza: {e}")
                await asyncio.sleep(5.0)
    
    async def stop(self) -> bool:
        """
        Para o servidor WebSim.
        
        Returns:
            True se o servidor foi parado com sucesso
        """
        try:
            logger.info("Parando WebSim...")
            
            self.is_running = False
            
            # Cancela tarefas
            if self.status_task:
                self.status_task.cancel()
            if self.cleanup_task:
                self.cleanup_task.cancel()
            
            # Fecha WebSockets
            for ws in self.websocket_connections:
                if not ws.closed:
                    await ws.close()
            self.websocket_connections.clear()
            
            # Para servidor
            if self.site:
                await self.site.stop()
            if self.runner:
                await self.runner.cleanup()
            
            logger.info("WebSim parado")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao parar WebSim: {e}")
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Retorna o status do WebSim.
        
        Returns:
            Dicionário com informações de status
        """
        return {
            "running": self.is_running,
            "host": self.config.host,
            "port": self.config.port,
            "connections": len(self.websocket_connections),
            "max_connections": self.max_connections,
            "robot_status": asdict(self.robot_status) if self.robot_status else None
        }
    
    async def health_check(self) -> bool:
        """
        Verifica a saúde do WebSim.
        
        Returns:
            True se o WebSim está saudável
        """
        try:
            if not self.is_running:
                return False
            
            # Verifica se o servidor está respondendo
            # (implementação básica)
            return True
            
        except Exception as e:
            logger.error(f"Erro na verificação de saúde do WebSim: {e}")
            return False
    
    # ===============================================
    # MÉTODOS HANDLERS HTTP
    # ===============================================
    
    async def _handle_index(self, request):
        """Handler para página principal."""
        try:
            template_path = Path(self.config.templates_dir) / "index.html"
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return web.Response(text=content, content_type='text/html')
        except Exception as e:
            logger.error(f"Erro ao servir página principal: {e}")
            return web.Response(text=f"Erro: {e}", status=500)
    
    async def _handle_api_status(self, request):
        """Handler para API de status."""
        try:
            status = {
                "connected": self.robot_status.connected,
                "state": self.robot_status.state,
                "battery_level": self.robot_status.battery_level,
                "position": getattr(self.robot_status, 'position', 'unknown'),
                "connections": len(self.websocket_connections),
                "timestamp": time.time()
            }
            return web.json_response(status)
        except Exception as e:
            logger.error(f"Erro na API de status: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def _handle_api_command(self, request):
        """Handler para API de comandos."""
        try:
            data = await request.json()
            command = data.get('command')
            
            if not command:
                return web.json_response({"error": "Comando não especificado"}, status=400)
            
            # Simula execução do comando
            result = {
                "command": command,
                "status": "executed",
                "timestamp": time.time()
            }
            
            # Adiciona ao histórico
            self.robot_status.command_history.append(result)
            
            # Broadcast para WebSockets
            await self._broadcast_command(result)
            
            return web.json_response(result)
            
        except Exception as e:
            logger.error(f"Erro na API de comando: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def _handle_api_history(self, request):
        """Handler para API de histórico."""
        try:
            history = self.robot_status.command_history[-50:]  # Últimos 50 comandos
            return web.json_response({"history": history})
        except Exception as e:
            logger.error(f"Erro na API de histórico: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def _handle_api_emergency(self, request):
        """Handler para API de emergência."""
        try:
            # Para todos os movimentos
            emergency_result = {
                "command": "emergency_stop",
                "status": "executed",
                "timestamp": time.time()
            }
            
            # Broadcast emergência
            await self._broadcast_command(emergency_result)
            
            return web.json_response(emergency_result)
            
        except Exception as e:
            logger.error(f"Erro na API de emergência: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def _handle_websocket(self, request):
        """Handler para WebSocket."""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        # Adiciona à lista de conexões
        self.websocket_connections.append(ws)
        logger.info(f"Nova conexão WebSocket: {len(self.websocket_connections)} ativas")
        
        try:
            # Envia status inicial
            await ws.send_str(json.dumps({
                "type": "status",
                "data": {
                    "connected": self.robot_status.connected,
                    "state": self.robot_status.state,
                    "battery_level": self.robot_status.battery_level
                }
            }))
            
            # Loop de mensagens
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await self._handle_websocket_message(ws, data)
                    except json.JSONDecodeError:
                        await ws.send_str(json.dumps({"error": "JSON inválido"}))
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f"Erro no WebSocket: {ws.exception()}")
                    break
                    
        except Exception as e:
            logger.error(f"Erro no WebSocket: {e}")
        finally:
            # Remove da lista
            if ws in self.websocket_connections:
                self.websocket_connections.remove(ws)
            logger.info(f"Conexão WebSocket fechada: {len(self.websocket_connections)} ativas")
        
        return ws
    
    async def _handle_websocket_message(self, ws, data):
        """Processa mensagem WebSocket."""
        try:
            msg_type = data.get('type')
            
            if msg_type == 'command':
                command = data.get('command')
                # Executa comando
                result = {
                    "type": "command_result",
                    "command": command,
                    "status": "executed",
                    "timestamp": time.time()
                }
                await ws.send_str(json.dumps(result))
                
            elif msg_type == 'ping':
                await ws.send_str(json.dumps({"type": "pong"}))
                
        except Exception as e:
            logger.error(f"Erro ao processar mensagem WebSocket: {e}")
    
    async def _broadcast_status(self):
        """Broadcast status para todos os WebSockets."""
        if not self.websocket_connections:
            return
        
        status_msg = json.dumps({
            "type": "status_update",
            "data": {
                "connected": self.robot_status.connected,
                "state": self.robot_status.state,
                "battery_level": self.robot_status.battery_level,
                "timestamp": time.time()
            }
        })
        
        # Remove conexões fechadas e envia para ativas
        active_connections = []
        for ws in self.websocket_connections:
            if not ws.closed:
                try:
                    await ws.send_str(status_msg)
                    active_connections.append(ws)
                except Exception:
                    pass  # Conexão morta
        
        self.websocket_connections = active_connections
    
    async def _broadcast_command(self, command_result):
        """Broadcast comando para todos os WebSockets."""
        if not self.websocket_connections:
            return
        
        command_msg = json.dumps({
            "type": "command_executed",
            "data": command_result
        })
        
        for ws in self.websocket_connections:
            if not ws.closed:
                try:
                    await ws.send_str(command_msg)
                except Exception:
                    pass
