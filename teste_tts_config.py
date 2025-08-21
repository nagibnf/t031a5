#!/usr/bin/env python3
"""🔊 Teste TTS com config do robô"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, "/home/unitree/t031a5/src")

from dotenv import load_dotenv
load_dotenv()

print('🔊 TESTANDO TTS MANAGER COM CONFIG DO ROBÔ')
print('='*50)

try:
    from t031a5.speech.tts_real_manager import TTSRealManager
    
    print('📦 Criando TTS Manager...')
    tts = TTSRealManager()
    
    print('✅ TTS Manager inicializado')
    print(f'   Voice ID: {tts.elevenlabs_voice_id}')
    print(f'   Model ID: {tts.elevenlabs_model}')
    print(f'   Stability: {tts.voice_stability}')
    print(f'   Similarity: {tts.voice_similarity}')
    print(f'   Style: {tts.voice_style}')
    print(f'   Speaker Boost: {tts.use_speaker_boost}')
    
    status = tts.get_status()
    print(f'   ElevenLabs ready: {status["elevenlabs_ready"]}')
    print(f'   Providers: {status["providers_available"]}')
    
    print('\n🎯 Teste concluído!')
    
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
