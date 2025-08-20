// WebSim JavaScript - Interface para G1
console.log('🤖 WebSim carregado!');

// Conecta WebSocket (simulado)
let isConnected = false;

// Simula conexão
setTimeout(() => {
    isConnected = true;
    updateConnectionStatus();
    addLogEntry('✅ Conectado ao Tobias (G1)');
}, 2000);

function updateConnectionStatus() {
    const statusElement = document.getElementById('connection-status');
    if (isConnected) {
        statusElement.textContent = 'Conectado';
        statusElement.className = 'connection-status connected';
        
        // Atualiza status do robô
        document.getElementById('robot-state').textContent = 'Ativo';
        document.getElementById('battery-level').textContent = '85.3%';
        document.getElementById('robot-position').textContent = 'Estúdio';
        document.getElementById('connections').textContent = '1';
    } else {
        statusElement.textContent = 'Desconectado';
        statusElement.className = 'connection-status disconnected';
    }
}

function sendCommand(command) {
    if (!isConnected) {
        addLogEntry('❌ Não conectado ao robô');
        return;
    }
    
    addLogEntry(`🤖 Comando enviado: ${command}`);
    
    // Simula resposta do robô
    setTimeout(() => {
        let response = '';
        switch(command) {
            case 'wave_hello':
                response = '👋 Tobias acenou!';
                break;
            case 'thumbs_up':
                response = '👍 Tobias fez positivo!';
                break;
            case 'led_happy':
                response = '😊 LEDs brilhando feliz!';
                break;
            case 'move_forward':
                response = '⬆️ Movendo para frente...';
                break;
            default:
                response = `✅ Executado: ${command}`;
        }
        addLogEntry(response);
    }, 500);
}

function sendSpeech() {
    const textInput = document.getElementById('speech-text');
    const text = textInput.value.trim();
    
    if (!text) {
        addLogEntry('❌ Digite um texto para falar');
        return;
    }
    
    if (!isConnected) {
        addLogEntry('❌ Não conectado ao robô');
        return;
    }
    
    addLogEntry(`🗣️ Tobias falando: "${text}"`);
    textInput.value = '';
    
    // Simula TTS
    setTimeout(() => {
        addLogEntry('✅ Fala concluída');
    }, 2000);
}

function addLogEntry(message) {
    const logContainer = document.getElementById('activity-log');
    const timestamp = new Date().toLocaleTimeString();
    
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    entry.textContent = `[${timestamp}] ${message}`;
    
    logContainer.appendChild(entry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

// Atualiza status inicial
updateConnectionStatus();