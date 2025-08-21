#!/usr/bin/env python3
"""🤖 Teste de conversação básica com Google STT + fallbacks"""

import sys
import asyncio
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, "/home/unitree/t031a5/src")

# Configurar logging
logging.basicConfig(level=logging.WARNING)  # Reduzir logs

print('🤖 TESTE DE CONVERSAÇÃO BÁSICA')
print('='*60)
print('📋 Componentes: Google STT + gTTS + LLM fallback')
print('🎤 DJI Mic 2 → 🗣️ Google Speech → 🤖 LLM → 🔊 gTTS → 📢 Anker')
print('='*60)

async def teste_conversacao_simples():
    """Teste conversacional básico."""
    
    try:
        # 1. Importar componentes
        print('📦 Carregando componentes...')
        from t031a5.audio.audio_manager_definitivo import AudioManagerDefinitivo
        from t031a5.speech.stt_real_manager import STTRealManager
        from t031a5.llm.llm_real_manager import LLMRealManager
        from t031a5.speech.tts_real_manager import TTSRealManager
        
        # 2. Inicializar componentes
        print('🔧 Inicializando sistema...')
        audio_mgr = AudioManagerDefinitivo(auto_connect_anker=True)
        stt_mgr = STTRealManager()
        llm_mgr = LLMRealManager()
        tts_mgr = TTSRealManager()
        
        # 3. Verificar status
        stt_status = stt_mgr.get_status()
        tts_status = tts_mgr.get_status()
        
        print(f'✅ Sistema inicializado')
        print(f'   STT Google: {stt_status["google_ready"]}')
        print(f'   TTS gTTS: {tts_status["providers_available"]["gtts"]}')
        
        # 4. Teste de conversação
        print('\n🎬 INICIANDO TESTE CONVERSACIONAL')
        print('='*40)
        
        for ciclo in range(1, 3):  # 2 ciclos de teste
            print(f'\n🔄 CICLO {ciclo}/2')
            print('🗣️ Fale algo no DJI Mic!')
            
            # Contagem regressiva
            for i in range(3, 0, -1):
                print(f'⏰ {i}...')
                await asyncio.sleep(1)
            
            # Captura
            print('🔴 GRAVANDO (5s)...')
            audio_data = audio_mgr.capturar_audio_dji(5.0)
            
            if audio_data is None:
                print('❌ Falha na captura - pulando ciclo')
                continue
            
            # Análise
            metricas = audio_mgr.obter_metricas_audio(audio_data)
            print(f'📊 RMS: {metricas.get("rms", 0):.4f}')
            
            # STT
            print('🎤 Processando STT...')
            texto = await stt_mgr.transcribe_audio(audio_data)
            
            if texto:
                print(f'📝 Reconhecido: "{texto}"')
                
                # LLM
                print('🤖 Processando LLM...')
                resposta_llm = await llm_mgr.generate_response(texto)
                
                if resposta_llm:
                    print(f'🤖 Tobias: "{resposta_llm["text"]}"')
                    print(f'   Movimento: {resposta_llm["movement"]}')
                    
                    # TTS
                    print('🔊 Sintetizando voz...')
                    audio_resposta = await tts_mgr.synthesize_speech(resposta_llm["text"])
                    
                    if audio_resposta is not None:
                        print('📢 Reproduzindo via Anker...')
                        sucesso = audio_mgr.reproduzir_audio_anker(audio_resposta)
                        print(f'✅ Reprodução: {"OK" if sucesso else "FALHA"}')
                    else:
                        print('❌ Falha na síntese TTS')
                else:
                    print('❌ Falha no LLM')
            else:
                print('❌ Falha no STT - não reconheceu fala')
            
            print('─' * 40)
        
        print('\n🎯 TESTE CONVERSACIONAL CONCLUÍDO!')
        print('🎉 Sistema básico funcionando!')
        
    except Exception as e:
        print(f'❌ Erro no teste: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(teste_conversacao_simples())
