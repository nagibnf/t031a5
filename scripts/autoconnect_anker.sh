#!/bin/bash
# Script de autoconexão Anker Soundcore no boot
# Adicionar ao systemd ou rc.local

ANKER_MAC="F4:2B:7D:2B:D1:B6"
LOG_FILE="/var/log/anker_autoconnect.log"

echo "$(date): Iniciando autoconexão Anker Soundcore" >> $LOG_FILE

# Aguardar sistema estar pronto
sleep 10

# Tentar conectar Anker (máximo 3 tentativas)
for i in {1..3}; do
    echo "$(date): Tentativa $i de conexão Anker" >> $LOG_FILE
    
    # Verificar se Bluetooth está ativo
    bluetoothctl show | grep "Powered: yes" > /dev/null
    if [ $? -eq 0 ]; then
        # Tentar conectar
        bluetoothctl connect $ANKER_MAC
        if [ $? -eq 0 ]; then
            echo "$(date): Anker conectado com sucesso!" >> $LOG_FILE
            
            # Aguardar e definir como default
            sleep 5
            pactl set-default-sink $(pactl list sinks short | grep bluez | cut -f2)
            echo "$(date): Anker definido como sink padrão" >> $LOG_FILE
            break
        else
            echo "$(date): Falha na tentativa $i" >> $LOG_FILE
            sleep 15
        fi
    else
        echo "$(date): Bluetooth não está ativo" >> $LOG_FILE
        sleep 10
    fi
done

echo "$(date): Script autoconexão finalizado" >> $LOG_FILE
