
        class G1WebSim {
            constructor() {
                this.ws = null;
                this.reconnectAttempts = 0;
                this.maxReconnectAttempts = 5;
                this.reconnectDelay = 1000;
                this.statusUpdateInterval = null;
                
                this.init();
            }
            
            init() {
                this.connectWebSocket();
                this.setupEventListeners();
                this.startStatusUpdates();
            }
            
            connectWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws`;
                
                this.ws = new WebSocket(wsUrl);
                
                this.ws.onopen = () => {
                    console.log('WebSocket conectado');
                    this.updateConnectionStatus('connected');
                    this.reconnectAttempts = 0;
                };
                
                this.ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        this.handleMessage(data);
                    } catch (error) {
                        console.error('Erro ao processar mensagem:', error);
                    }
                };
                
                this.ws.onclose = () => {
                    console.log('WebSocket desconectado');
                    this.updateConnectionStatus('disconnected');
                    this.scheduleReconnect();
                };
                
                this.ws.onerror = (error) => {
                    console.error('Erro no WebSocket:', error);
                    this.updateConnectionStatus('disconnected');
                };
            }
            
            scheduleReconnect() {
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.reconnectAttempts++;
                    setTimeout(() => {
                        this.connectWebSocket();
                    }, this.reconnectDelay * this.reconnectAttempts);
                }
            }
            
            updateConnectionStatus(status) {
                const statusEl = document.getElementById('connection-status');
                if (statusEl) {
                    statusEl.className = `connection-status ${status}`;
                    statusEl.textContent = status === 'connected' ? 'Conectado' : 
                                         status === 'connecting' ? 'Conectando...' : 'Desconectado';
                }
            }
            
            setupEventListeners() {
                // Comandos de movimento
                document.getElementById('move-forward')?.addEventListener('click', () => {
                    this.sendCommand('move_forward', {
                        distance: parseFloat(document.getElementById('distance').value) || 0.5,
                        speed: parseFloat(document.getElementById('speed').value) || 0.3
                    });
                });
                
                document.getElementById('move-backward')?.addEventListener('click', () => {
                    this.sendCommand('move_backward', {
                        distance: parseFloat(document.getElementById('distance').value) || 0.5,
                        speed: parseFloat(document.getElementById('speed').value) || 0.3
                    });
                });
                
                document.getElementById('turn-left')?.addEventListener('click', () => {
                    this.sendCommand('turn_left', {
                        angle: parseFloat(document.getElementById('angle').value) || Math.PI/4,
                        speed: parseFloat(document.getElementById('speed').value) || 0.2
                    });
                });
                
                document.getElementById('turn-right')?.addEventListener('click', () => {
                    this.sendCommand('turn_right', {
                        angle: parseFloat(document.getElementById('angle').value) || Math.PI/4,
                        speed: parseFloat(document.getElementById('speed').value) || 0.2
                    });
                });
                
                // Gestos
                document.getElementById('perform-gesture')?.addEventListener('click', () => {
                    const gesture = document.getElementById('gesture').value;
                    const duration = parseFloat(document.getElementById('gesture-duration').value) || 2.0;
                    this.sendCommand('perform_gesture', { gesture, duration });
                });
                
                // Fala
                document.getElementById('speak-text')?.addEventListener('click', () => {
                    const text = document.getElementById('speak-text-input').value;
                    const emotion = document.getElementById('emotion').value;
                    const volume = parseFloat(document.getElementById('volume').value) || 0.7;
                    this.sendCommand('speak_text', { text, emotion, volume });
                });
                
                // Emergência
                document.getElementById('emergency-stop')?.addEventListener('click', () => {
                    if (confirm('Tem certeza que deseja executar a parada de emergência?')) {
                        this.sendCommand('emergency_stop', {});
                    }
                });
            }
            
            async sendCommand(command, parameters) {
                try {
                    console.log(`Enviando comando: ${command}`, parameters);
                    
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
                        this.showMessage(`✅ Comando '${command}' executado com sucesso!`, 'success');
                        console.log('Comando executado com sucesso:', result);
                    } else {
                        this.showMessage(`❌ Erro ao executar '${command}': ${result.error || 'Erro desconhecido'}`, 'error');
                        console.error('Erro no comando:', result);
                    }
                } catch (error) {
                    this.showMessage(`💥 Erro de conexão: ${error.message}`, 'error');
                    console.error('Erro ao enviar comando:', error);
                }
            }
            
            showMessage(message, type) {
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
            
            handleMessage(data) {
                switch (data.type) {
                    case 'status':
                        this.updateStatus(data.data);
                        break;
                    case 'command_result':
                        this.handleCommandResult(data);
                        break;
                    case 'error':
                        this.handleError(data);
                        break;
                }
            }
            
            updateStatus(status) {
                // Atualiza valores de status
                document.getElementById('robot-state').textContent = status.state;
                document.getElementById('battery-level').textContent = status.battery_level.toFixed(1) + '%';
                document.getElementById('battery-voltage').textContent = status.battery_voltage.toFixed(1) + 'V';
                document.getElementById('temperature').textContent = status.temperature.toFixed(1) + '°C';
                document.getElementById('pose-x').textContent = status.pose_x.toFixed(2) + 'm';
                document.getElementById('pose-y').textContent = status.pose_y.toFixed(2) + 'm';
                document.getElementById('pose-yaw').textContent = (status.pose_yaw * 180 / Math.PI).toFixed(1) + '°';
                
                // Atualiza histórico
                this.updateHistory(status.command_history);
            }
            
            updateHistory(history) {
                const historyList = document.getElementById('history-list');
                if (!historyList) return;
                
                historyList.innerHTML = '';
                
                history.slice(-10).reverse().forEach(item => {
                    const historyItem = document.createElement('div');
                    historyItem.className = 'history-item';
                    
                    const command = document.createElement('span');
                    command.className = 'history-command';
                    command.textContent = item.command;
                    
                    const time = document.createElement('span');
                    time.className = 'history-time';
                    time.textContent = new Date(item.timestamp * 1000).toLocaleTimeString();
                    
                    historyItem.appendChild(command);
                    historyItem.appendChild(time);
                    historyList.appendChild(historyItem);
                });
            }
            
            handleCommandResult(data) {
                if (data.success) {
                    console.log('Comando executado com sucesso:', data.command);
                } else {
                    console.error('Erro no comando:', data.error);
                    alert('Erro ao executar comando: ' + data.error);
                }
            }
            
            handleError(data) {
                console.error('Erro do servidor:', data.message);
                alert('Erro: ' + data.message);
            }
            
            startStatusUpdates() {
                // Atualizações periódicas de status
                this.statusUpdateInterval = setInterval(() => {
                    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                        this.ws.send(JSON.stringify({
                            type: 'get_status',
                            timestamp: Date.now()
                        }));
                    }
                }, 1000);
            }
            
            stop() {
                if (this.statusUpdateInterval) {
                    clearInterval(this.statusUpdateInterval);
                }
                if (this.ws) {
                    this.ws.close();
                }
            }
        }
        
        // Inicializa quando a página carrega
        document.addEventListener('DOMContentLoaded', () => {
            window.g1WebSim = new G1WebSim();
        });
        