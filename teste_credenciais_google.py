#!/usr/bin/env python3
"""🔑 Teste de credenciais Google Speech"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, "/home/unitree/t031a5/src")

print('🔑 TESTANDO CARREGAMENTO DE CREDENCIAIS')
print('='*50)

# Carregar .env
try:
    from dotenv import load_dotenv
    load_dotenv()
    print('✅ Arquivo .env carregado')
except ImportError:
    print('❌ python-dotenv não disponível')

# Verificar variável
google_creds = os.getenv('GOOGLE_SPEECH_CREDENTIALS_JSON')
print(f'📋 GOOGLE_SPEECH_CREDENTIALS_JSON: {google_creds}')

# Verificar arquivo de credenciais
if google_creds:
    creds_file = Path(google_creds)
    if not creds_file.is_absolute():
        creds_file = Path(__file__).parent / creds_file
    
    print(f'📁 Caminho completo: {creds_file}')
    print(f'📄 Arquivo existe: {creds_file.exists()}')
    
    if creds_file.exists():
        try:
            import json
            with open(creds_file, 'r') as f:
                creds_data = json.load(f)
            print(f'✅ JSON válido - Project ID: {creds_data.get("project_id", "N/A")}')
            print(f'✅ Client Email: {creds_data.get("client_email", "N/A")}')
        except Exception as e:
            print(f'❌ Erro lendo JSON: {e}')

# Testar STT Manager
print('\n🎤 Testando STT Manager...')
try:
    from t031a5.speech.stt_real_manager import STTRealManager
    stt = STTRealManager()
    status = stt.get_status()
    print(f'✅ STT criado - Google ready: {status.get("google_ready", False)}')
    print(f'📊 Providers: {status.get("providers_available", {})}')
except Exception as e:
    print(f'❌ Erro STT Manager: {e}')

print('\n🎯 Teste concluído!')
