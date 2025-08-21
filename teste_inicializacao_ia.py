#!/usr/bin/env python3
"""🧪 Teste de inicialização dos componentes IA"""

import sys
import asyncio
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, "/home/unitree/t031a5/src")

# Configurar logging
logging.basicConfig(level=logging.WARNING)  # Reduzir logs para teste

print('🧪 TESTANDO INICIALIZAÇÃO DOS COMPONENTES IA')
print('='*60)

async def testar_componentes():
    """Testa inicialização de todos os componentes."""
    
    # 1. AudioManagerDefinitivo
    print('🎧 Testando AudioManagerDefinitivo...')
    try:
        from t031a5.audio.audio_manager_definitivo import AudioManagerDefinitivo
        # Não conectar Anker automaticamente para teste
        audio_mgr = AudioManagerDefinitivo(auto_connect_anker=False)
        status_audio = audio_mgr.get_status() if hasattr(audio_mgr, 'get_status') else {"initialized": True}
        print(f'✅ AudioManager: Inicializado - DJI: {audio_mgr.verificar_dji_disponivel()}')
    except Exception as e:
        print(f'❌ AudioManager: {e}')
    
    # 2. STTRealManager
    print('\n🎤 Testando STTRealManager...')
    try:
        from t031a5.speech.stt_real_manager import STTRealManager
        stt_mgr = STTRealManager()
        status_stt = stt_mgr.get_status()
        print(f'✅ STT Manager: Inicializado')
        print(f'   Providers: {status_stt["providers_available"]}')
    except Exception as e:
        print(f'❌ STT Manager: {e}')
    
    # 3. LLMRealManager
    print('\n🤖 Testando LLMRealManager...')
    try:
        from t031a5.llm.llm_real_manager import LLMRealManager
        llm_mgr = LLMRealManager()
        status_llm = llm_mgr.get_status()
        print(f'✅ LLM Manager: Inicializado')
        print(f'   Ollama: {status_llm["providers_available"]["ollama"]}')
        print(f'   OpenAI: {status_llm["openai_ready"]}')
    except Exception as e:
        print(f'❌ LLM Manager: {e}')
    
    # 4. TTSRealManager
    print('\n🔊 Testando TTSRealManager...')
    try:
        from t031a5.speech.tts_real_manager import TTSRealManager
        tts_mgr = TTSRealManager()
        status_tts = tts_mgr.get_status()
        print(f'✅ TTS Manager: Inicializado')
        print(f'   Providers: {status_tts["providers_available"]}')
    except Exception as e:
        print(f'❌ TTS Manager: {e}')
    
    print('\n' + '='*60)
    print('🎯 TESTE DE INICIALIZAÇÃO CONCLUÍDO!')
    print('\n💡 Próximos passos:')
    print('   1. Configure credenciais no .env')
    print('   2. Execute sistema completo')

if __name__ == "__main__":
    asyncio.run(testar_componentes())
