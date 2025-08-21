#!/usr/bin/env python3
"""🧪 Teste de imports dos componentes IA"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, "/home/unitree/t031a5/src")

print('📦 Testando imports dos componentes IA...')
print('='*50)

# AudioManagerDefinitivo
try:
    from t031a5.audio.audio_manager_definitivo import AudioManagerDefinitivo
    print('✅ AudioManagerDefinitivo: OK')
except Exception as e:
    print(f'❌ AudioManagerDefinitivo: {e}')

# STTRealManager
try:
    from t031a5.speech.stt_real_manager import STTRealManager
    print('✅ STTRealManager: OK')
except Exception as e:
    print(f'❌ STTRealManager: {e}')

# LLMRealManager
try:
    from t031a5.llm.llm_real_manager import LLMRealManager  
    print('✅ LLMRealManager: OK')
except Exception as e:
    print(f'❌ LLMRealManager: {e}')

# TTSRealManager
try:
    from t031a5.speech.tts_real_manager import TTSRealManager
    print('✅ TTSRealManager: OK')
except Exception as e:
    print(f'❌ TTSRealManager: {e}')

# Dependências externas
print('\n📦 Testando dependências externas...')
deps_externas = [
    ('OpenAI', 'openai'),
    ('ElevenLabs', 'elevenlabs'),
    ('Google Speech', 'google.cloud.speech'),
    ('gTTS', 'gtts'),
    ('Pyttsx3', 'pyttsx3'),
    ('AioHTTP', 'aiohttp'),
    ('SciPy', 'scipy'),
]

for nome, modulo in deps_externas:
    try:
        __import__(modulo)
        print(f'✅ {nome}: OK')
    except ImportError:
        print(f'❌ {nome}: FALHOU')

print('\n🎯 Teste de imports concluído!')
