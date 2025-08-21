// ======================================
// G1 Tobias - WebSim Mobile JavaScript  
// Sistema t031a5 - Interface Responsiva
// 🫧 Desenvolvido por Bolha
// ======================================

console.log('🤖 WebSim Mobile carregado!');

// Estado da aplicação
let appState = {
    isConnected: false,
    currentTab: 'controls',
    cameraActive: false,
    brightness: 100,
    volume: 80,
    emergencyStopActive: false,
    lastUpdate: null,
    robotStatus: {
        battery: '--',
        state: '--',
        position: '--',
        temperature: '--°C',
        connectivity: '--',
        performance: '--'
    }
};

// WebSocket connection (real implementation)
let websocket = null;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;

// ==================== INICIALIZAÇÃO ==================== 
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Inicializando WebSim Mobile...');
    
    // Inicializa componentes
    initializeWebSocket();
    setupEventListeners();
    setupCharacterCounter();
    updateLastUpdateTime();
    
    // Auto-conecta em modo de desenvolvimento
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        setTimeout(() => {
            simulateConnection();
        }, 2000);
    }
    
    console.log('✅ WebSim Mobile inicializado');
});

// ==================== WEBSOCKET ==================== 
function initializeWebSocket() {
    try {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        websocket = new WebSocket(wsUrl);
        
        websocket.onopen = function(event) {
            console.log('🔗 WebSocket conectado');
            handleConnection(true);
            reconnectAttempts = 0;
        };
        
        websocket.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);
                handleWebSocketMessage(data);
            } catch (error) {
                console.error('❌ Erro ao processar mensagem WebSocket:', error);
            }
        };
        
        websocket.onclose = function(event) {
            console.log('🔌 WebSocket desconectado');
            handleConnection(false);
            
            // Auto-reconectar
            if (reconnectAttempts < maxReconnectAttempts) {
                reconnectAttempts++;
                setTimeout(() => {
                    console.log(`🔄 Tentativa de reconexão ${reconnectAttempts}/${maxReconnectAttempts}`);
                    initializeWebSocket();
                }, 3000);
            }
        };
        
        websocket.onerror = function(error) {
            console.error('❌ Erro WebSocket:', error);
        };
        
    } catch (error) {
        console.error('❌ Erro ao inicializar WebSocket:', error);
        // Fallback para modo simulado
        setTimeout(simulateConnection, 3000);
    }
}

function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'status_update':
            updateRobotStatus(data.data);
            break;
        case 'command_response':
            addLogEntry(`✅ ${data.message}`, 'system');
            break;
        case 'error':
            addLogEntry(`❌ ${data.message}`, 'error');
            break;
        case 'warning':
            addLogEntry(`⚠️ ${data.message}`, 'warning');
            break;
        default:
            console.log('📥 Mensagem WebSocket:', data);
    }
}

function sendWebSocketMessage(type, data) {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        const message = {
            type: type,
            data: data,
            timestamp: Date.now()
        };
        websocket.send(JSON.stringify(message));
        return true;
    } else {
        console.warn('⚠️ WebSocket não conectado');
        return false;
    }
}

// ==================== CONEXÃO E STATUS ==================== 
function handleConnection(connected) {
    appState.isConnected = connected;
    updateConnectionStatus();
    
    if (connected) {
        addLogEntry('✅ Conectado ao Tobias (G1)', 'system');
        // Solicita status inicial
        sendWebSocketMessage('get_status', {});
    } else {
        addLogEntry('❌ Desconectado do Tobias', 'error');
        resetRobotStatus();
    }
}

function updateConnectionStatus() {
    const statusElement = document.getElementById('connection-status');
    
    if (appState.isConnected) {
        statusElement.textContent = 'Conectado';
        statusElement.className = 'connection-status connected';
    } else {
        statusElement.textContent = 'Desconectado';
        statusElement.className = 'connection-status disconnected';
    }
}

function updateRobotStatus(status) {
    appState.robotStatus = { ...appState.robotStatus, ...status };
    
    // Atualiza elementos na interface
    updateElement('robot-state', status.state || '--');
    updateElement('battery-level', status.battery || '--');
    updateElement('robot-position', status.position || '--');
    updateElement('detailed-battery', status.battery || '--');
    updateElement('temperature', status.temperature || '--°C');
    updateElement('connectivity', status.connectivity || '--');
    updateElement('performance', status.performance || '--');
    
    // Atualiza tempo de última atualização
    updateLastUpdateTime();
}

function resetRobotStatus() {
    const defaultStatus = {
        state: '--',
        battery: '--',
        position: '--',
        temperature: '--°C',
        connectivity: '--',
        performance: '--'
    };
    updateRobotStatus(defaultStatus);
}

function updateElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
}

function updateLastUpdateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('pt-BR', { 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
    });
    updateElement('last-update', `Última atualização: ${timeString}`);
    appState.lastUpdate = now;
}

// ==================== NAVEGAÇÃO POR ABAS ==================== 
function switchTab(tabName) {
    // Remove active de todas as abas
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Ativa a aba selecionada
    const activeBtn = document.querySelector(`[onclick="switchTab('${tabName}')"]`);
    if (activeBtn) {
        activeBtn.classList.add('active');
    }
    
    const activeContent = document.getElementById(`tab-${tabName}`);
    if (activeContent) {
        activeContent.classList.add('active');
    }
    
    appState.currentTab = tabName;
    
    // Log da mudança de aba
    addLogEntry(`📱 Aba alterada: ${tabName}`, 'system');
}

// ==================== CONTROLES DO ROBÔ ==================== 
function sendCommand(command) {
    if (!appState.isConnected) {
        addLogEntry('❌ Não conectado ao robô', 'error');
        return;
    }
    
    if (appState.emergencyStopActive && command !== 'emergency_stop') {
        addLogEntry('🛑 Sistema em EMERGENCY STOP - comando bloqueado', 'warning');
        return;
    }
    
    // Envia comando via WebSocket
    const sent = sendWebSocketMessage('command', { action: command });
    
    if (sent) {
        addLogEntry(`🤖 Comando enviado: ${getCommandDescription(command)}`, 'system');
        
        // Simula resposta se não há WebSocket real
        if (!websocket || websocket.readyState !== WebSocket.OPEN) {
            setTimeout(() => {
                simulateCommandResponse(command);
            }, 500);
        }
    } else {
        addLogEntry('❌ Falha ao enviar comando', 'error');
    }
}

function getCommandDescription(command) {
    const descriptions = {
        'move_forward': 'Mover para frente',
        'move_backward': 'Mover para trás', 
        'turn_left': 'Virar à esquerda',
        'turn_right': 'Virar à direita',
        'stop': 'Parar movimento',
        'release_arm': 'Relaxar braços',
        'clap': 'Aplaudir',
        'shake_hand': 'Cumprimentar',
        'high_five': 'High five',
        'hug': 'Abraçar',
        'right_hand_up': 'Mão direita para cima'
    };
    return descriptions[command] || command;
}

function simulateCommandResponse(command) {
    const responses = {
        'release_arm': '🤲 Braços relaxados',
        'clap': '👏 Tobias aplaudiu!',
        'shake_hand': '🤝 Tobias cumprimentou!',
        'high_five': '🙏 High five!',
        'hug': '🤗 Abraço!',
        'right_hand_up': '✋ Mão direita levantada',
        'move_forward': '⬆️ Movendo para frente',
        'move_backward': '⬇️ Movendo para trás',
        'turn_left': '⬅️ Virando à esquerda',
        'turn_right': '➡️ Virando à direita',
        'stop': '⏹️ Movimento parado'
    };
    
    const response = responses[command] || `✅ Executado: ${command}`;
    addLogEntry(response, 'system');
}

// ==================== EXPRESSÕES E EMOÇÕES ==================== 
function sendEmotion(emotion) {
    if (!appState.isConnected) {
        addLogEntry('❌ Não conectado ao robô', 'error');
        return;
    }
    
    const sent = sendWebSocketMessage('emotion', { 
        emotion: emotion, 
        brightness: appState.brightness / 100 
    });
    
    if (sent) {
        addLogEntry(`🎭 Emoção: ${getEmotionDescription(emotion)}`, 'system');
        
        // Simula resposta
        if (!websocket || websocket.readyState !== WebSocket.OPEN) {
            setTimeout(() => {
                addLogEntry(`✨ LEDs brilhando: ${emotion}`, 'system');
            }, 300);
        }
    } else {
        addLogEntry('❌ Falha ao definir emoção', 'error');
    }
}

function getEmotionDescription(emotion) {
    const descriptions = {
        'happy': 'Feliz (Verde)',
        'sad': 'Triste (Azul)',
        'excited': 'Empolgado (Amarelo)',
        'calm': 'Calmo (Azul claro)',
        'angry': 'Bravo (Vermelho)',
        'surprised': 'Surpreso (Laranja)',
        'thinking': 'Pensando (Roxo)',
        'neutral': 'Neutro (Branco)'
    };
    return descriptions[emotion] || emotion;
}

function setBrightness(value) {
    appState.brightness = parseInt(value);
    document.getElementById('brightness-value').textContent = `${value}%`;
    
    // Envia atualização em tempo real
    if (appState.isConnected) {
        sendWebSocketMessage('brightness', { brightness: appState.brightness / 100 });
    }
}

// ==================== SISTEMA DE FALA ==================== 
function sendSpeech() {
    const textInput = document.getElementById('speech-text');
    const text = textInput.value.trim();
    
    if (!text) {
        addLogEntry('❌ Digite um texto para falar', 'error');
        return;
    }
    
    if (!appState.isConnected) {
        addLogEntry('❌ Não conectado ao robô', 'error');
        return;
    }
    
    const sent = sendWebSocketMessage('speech', { 
        text: text, 
        volume: appState.volume 
    });
    
    if (sent) {
        addLogEntry(`🗣️ Tobias falando: "${text}"`, 'system');
        textInput.value = '';
        updateCharCount();
        
        // Simula TTS
        if (!websocket || websocket.readyState !== WebSocket.OPEN) {
            setTimeout(() => {
                addLogEntry('✅ Fala concluída', 'system');
            }, text.length * 50); // Simula tempo baseado no tamanho do texto
        }
    } else {
        addLogEntry('❌ Falha ao enviar comando de fala', 'error');
    }
}

function quickSpeech(text) {
    document.getElementById('speech-text').value = text;
    updateCharCount();
    sendSpeech();
}

function setVolume(value) {
    appState.volume = parseInt(value);
    document.getElementById('volume-value').textContent = `${value}%`;
    
    // Envia atualização em tempo real
    if (appState.isConnected) {
        sendWebSocketMessage('volume', { volume: appState.volume });
    }
}

// ==================== CÂMERA E STREAMING ==================== 
function toggleCamera() {
    appState.cameraActive = !appState.cameraActive;
    
    const toggleIcon = document.getElementById('camera-toggle-icon');
    const streamContainer = document.getElementById('camera-stream');
    
    if (appState.cameraActive) {
        // Ativar câmera
        toggleIcon.textContent = '⏹️';
        startCameraStream();
        addLogEntry('📹 Câmera ativada', 'system');
    } else {
        // Desativar câmera
        toggleIcon.textContent = '📹';
        stopCameraStream();
        addLogEntry('📹 Câmera desativada', 'system');
    }
}

function startCameraStream() {
    const streamContainer = document.getElementById('camera-stream');
    
    // Simula início do streaming
    streamContainer.innerHTML = `
        <div class="stream-active">
            <div class="stream-status">
                <span class="stream-indicator"></span>
                <span>LIVE</span>
            </div>
            <div class="stream-overlay">
                <p>📹 Streaming Ativo</p>
                <small>640x480 @ 30fps</small>
            </div>
        </div>
    `;
    
    // Adiciona CSS para stream ativo
    const style = document.createElement('style');
    style.textContent = `
        .stream-active {
            height: 100%;
            background: linear-gradient(45deg, #1e3c72, #2a5298);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: white;
            position: relative;
        }
        .stream-status {
            position: absolute;
            top: 12px;
            right: 12px;
            background: rgba(239, 68, 68, 0.9);
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .stream-indicator {
            width: 6px;
            height: 6px;
            background: white;
            border-radius: 50%;
            animation: blink 1s infinite;
        }
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0.3; }
        }
        .stream-overlay {
            text-align: center;
        }
    `;
    document.head.appendChild(style);
    
    // Em uma implementação real, aqui você iniciaria o stream da câmera
    if (appState.isConnected) {
        sendWebSocketMessage('camera_start', {});
    }
}

function stopCameraStream() {
    const streamContainer = document.getElementById('camera-stream');
    
    streamContainer.innerHTML = `
        <div class="stream-placeholder">
            <span class="stream-icon">📹</span>
            <p>Camera Desconectada</p>
            <small>Toque para conectar</small>
        </div>
    `;
    
    if (appState.isConnected) {
        sendWebSocketMessage('camera_stop', {});
    }
}

function takeSnapshot() {
    if (!appState.cameraActive) {
        addLogEntry('❌ Câmera não está ativa', 'error');
        return;
    }
    
    if (appState.isConnected) {
        sendWebSocketMessage('camera_snapshot', {});
        addLogEntry('📸 Snapshot capturado', 'system');
    } else {
        addLogEntry('❌ Não conectado para capturar snapshot', 'error');
    }
}

// ==================== EMERGENCY STOP ==================== 
function emergencyStop() {
    console.log('🚨 EMERGENCY STOP ativado!');
    
    appState.emergencyStopActive = !appState.emergencyStopActive;
    
    const emergencyBtn = document.querySelector('.emergency-button');
    
    if (appState.emergencyStopActive) {
        // Ativar emergency stop
        emergencyBtn.style.background = 'linear-gradient(135deg, #b91c1c 0%, #991b1b 100%)';
        emergencyBtn.style.transform = 'scale(1.1)';
        emergencyBtn.innerHTML = `
            <span class="emergency-icon">⏹️</span>
            <span class="emergency-text">ATIVO</span>
        `;
        
        addLogEntry('🛑 EMERGENCY STOP ATIVADO!', 'warning');
        
        // Envia comando de parada
        if (appState.isConnected) {
            sendWebSocketMessage('emergency_stop', { active: true });
        }
        
        // Para câmera se ativa
        if (appState.cameraActive) {
            toggleCamera();
        }
        
    } else {
        // Desativar emergency stop
        emergencyBtn.style.background = 'linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)';
        emergencyBtn.style.transform = 'scale(1)';
        emergencyBtn.innerHTML = `
            <span class="emergency-icon">⏹️</span>
            <span class="emergency-text">STOP</span>
        `;
        
        addLogEntry('🟢 Emergency stop desativado', 'system');
        
        if (appState.isConnected) {
            sendWebSocketMessage('emergency_stop', { active: false });
        }
    }
}

// ==================== CONTROLES DE SISTEMA ==================== 
function systemCommand(command) {
    if (!appState.isConnected) {
        addLogEntry('❌ Não conectado ao robô', 'error');
        return;
    }
    
    const confirmations = {
        'restart': 'Deseja realmente reiniciar o sistema?',
        'shutdown': 'Deseja realmente desligar o robô?',
        'reset': 'Deseja resetar configurações para padrão?'
    };
    
    if (confirm(confirmations[command])) {
        sendWebSocketMessage('system', { command: command });
        addLogEntry(`⚙️ Sistema: ${command}`, 'warning');
        
        if (command === 'shutdown') {
            setTimeout(() => {
                handleConnection(false);
            }, 2000);
        }
    }
}

// ==================== LOG DE ATIVIDADES ==================== 
function addLogEntry(message, type = 'info') {
    const logContainer = document.getElementById('activity-log');
    const timestamp = new Date().toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit', 
        second: '2-digit'
    });
    
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    
    entry.innerHTML = `
        <span class="log-time">${timestamp}</span>
        <span class="log-message">${message}</span>
    `;
    
    logContainer.appendChild(entry);
    logContainer.scrollTop = logContainer.scrollHeight;
    
    // Limita número de entradas do log
    const entries = logContainer.querySelectorAll('.log-entry');
    if (entries.length > 100) {
        entries[0].remove();
    }
}

// ==================== UTILITÁRIOS ==================== 
function setupEventListeners() {
    // Contador de caracteres para speech
    const speechText = document.getElementById('speech-text');
    if (speechText) {
        speechText.addEventListener('input', updateCharCount);
        speechText.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendSpeech();
            }
        });
    }
    
    // Atualização automática do tempo
    setInterval(updateLastUpdateTime, 30000); // A cada 30 segundos
    
    // Detecta orientação do dispositivo
    window.addEventListener('orientationchange', function() {
        setTimeout(() => {
            console.log('📱 Orientação alterada');
        }, 100);
    });
}

function setupCharacterCounter() {
    updateCharCount();
}

function updateCharCount() {
    const speechText = document.getElementById('speech-text');
    const charCount = document.getElementById('char-count');
    
    if (speechText && charCount) {
        const count = speechText.value.length;
        charCount.textContent = count;
        
        // Muda cor se próximo do limite
        if (count > 180) {
            charCount.style.color = '#dc2626';
        } else if (count > 150) {
            charCount.style.color = '#d97706';
        } else {
            charCount.style.color = '#64748b';
        }
    }
}

// ==================== MODO SIMULADO ==================== 
function simulateConnection() {
    console.log('🔧 Iniciando modo simulado...');
    
    handleConnection(true);
    
    // Simula dados do robô
    const mockStatus = {
        state: 'Ativo',
        battery: '87.3%',
        position: 'Estúdio',
        temperature: '45°C',
        connectivity: 'Excelente',
        performance: '92%'
    };
    
    updateRobotStatus(mockStatus);
    
    // Simula atualizações periódicas
    setInterval(() => {
        if (appState.isConnected) {
            const randomBattery = (85 + Math.random() * 10).toFixed(1);
            updateRobotStatus({ 
                battery: `${randomBattery}%`,
                temperature: `${(40 + Math.random() * 10).toFixed(0)}°C`
            });
        }
    }, 10000);
}

// ==================== INICIALIZAÇÃO FINAL ==================== 
// Atualiza status inicial após carregamento
setTimeout(() => {
    updateConnectionStatus();
    updateLastUpdateTime();
}, 100);