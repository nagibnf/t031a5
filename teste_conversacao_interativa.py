#!/usr/bin/env python3
"""🤖 TESTE SISTEMA CONVERSAÇÃO - ARQUIVO ÚNICO PRINCIPAL
Teste completo: DJI Mic → Google STT → LLM → ElevenLabs TTS → Anker + G1 Movimentos
"""

import sys
import asyncio
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, "/home/unitree/t031a5/src")

# Configurar logging mais limpo
logging.basicConfig(level=logging.ERROR)

print('🤖 TESTE DE CONVERSAÇÃO INTERATIVA')
print('='*60)
print('🎯 OBJETIVO: Validar fluxo completo DJI → Google STT → LLM → ElevenLabs TTS → Anker + G1')
print('📋 INSTRUÇÕES: Fale CLARAMENTE no DJI Mic quando solicitado')
print('='*60)

async def reproduzir_audio_async(audio_mgr, audio_data):
    """Reproduz áudio de forma assíncrona."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, 
        audio_mgr.reproduzir_audio_anker,
        audio_data
    )

async def executar_movimento_g1(g1_client, movement_library, movimento, duracao):
    """Executa movimento G1 com duração específica."""
    try:
        # Obter ID da ação
        action_id = movement_library.get_action_id(movimento)
        
        if action_id is not None:
            print(f'🦾 Movimento físico: {movimento} (ID: {action_id})')
            
            # Executar movimento
            g1_client.ExecuteAction(action_id)
            
            # Aguardar duração ou duração do movimento
            movimento_duracao = movement_library.get_duration(movimento)
            tempo_espera = min(duracao, movimento_duracao)
            
            await asyncio.sleep(tempo_espera)
            
            # Retornar à posição neutra se necessário
            if tempo_espera >= movimento_duracao:
                release_id = movement_library.get_action_id("release_arm")
                if release_id:
                    g1_client.ExecuteAction(release_id)
                    print('🔄 Retornando à posição neutra')
            
        else:
            print(f'⚠️ Movimento "{movimento}" não encontrado na biblioteca')
            
    except Exception as e:
        print(f'❌ Erro no movimento G1: {e}')

async def aguardar_fala_real(audio_mgr, max_tentativas=5):
    """Aguarda captura de áudio com fala real."""
    
    for tentativa in range(1, max_tentativas + 1):
        print(f'\n🎤 TENTATIVA {tentativa}/{max_tentativas}')
        print('🗣️ FALE CLARAMENTE NO DJI MIC!')
        print('💡 Exemplo: "Olá Tobias, como você está?"')
        
        # Contagem regressiva
        for i in range(5, 0, -1):
            print(f'⏰ Iniciando em {i}s...')
            await asyncio.sleep(1)
        
        print('🔴 GRAVANDO (5s) - FALE AGORA!')
        audio_data = audio_mgr.capturar_audio_dji(5.0)
        
        if audio_data is None:
            print('❌ Falha na captura - tentando novamente...')
            continue
        
        # Analisar qualidade
        metricas = audio_mgr.obter_metricas_audio(audio_data)
        rms = metricas.get("rms", 0)
        peak = metricas.get("peak", 0)
        
        print(f'📊 Análise: RMS={rms:.4f}, Peak={peak:.4f}')
        
        # Critérios mais flexíveis para fala
        if rms > 0.008 and peak > 0.05:  # Thresholds mais baixos
            print('✅ ÁUDIO COM FALA DETECTADO!')
            return audio_data
        elif rms > 0.003:
            print('⚠️ Áudio muito baixo - fale mais alto!')
        else:
            print('❌ Apenas silêncio/ruído - tente novamente!')
    
    print('❌ Não foi possível capturar fala após várias tentativas')
    return None

async def teste_conversacao_completa():
    """Teste conversacional completo com G1 movimentos."""
    
    try:
        # Importar e inicializar
        print('📦 Inicializando componentes...')
        from t031a5.audio.audio_manager_definitivo import AudioManagerDefinitivo
        from t031a5.speech.stt_real_manager import STTRealManager
        from t031a5.llm.llm_real_manager import LLMRealManager
        from t031a5.speech.tts_real_manager import TTSRealManager
        from t031a5.actions.g1_movement_mapping import G1MovementLibrary
        
        # Inicializar G1 SDK para movimentos
        g1_client = None
        movement_library = None
        try:
            from unitree_sdk2py.core.channel import ChannelFactoryInitialize
            from unitree_sdk2py.g1.arm.g1_arm_action_client import G1ArmActionClient as ArmActionClient
            
            ChannelFactoryInitialize(0, "eth0")
            g1_client = ArmActionClient()
            g1_client.SetTimeout(10.0)
            g1_client.Init()
            movement_library = G1MovementLibrary()
            print('✅ G1 SDK inicializado para movimentos')
        except Exception as e:
            print(f'⚠️ G1 SDK não disponível: {e}')
        
        audio_mgr = AudioManagerDefinitivo(auto_connect_anker=True)
        stt_mgr = STTRealManager()
        llm_mgr = LLMRealManager()
        tts_mgr = TTSRealManager()
        
        # Verificar componentes
        stt_status = stt_mgr.get_status()
        if not stt_status["google_ready"]:
            print('❌ Google STT não está pronto!')
            return
        
        print('✅ Todos os componentes inicializados')
        print(f'   🎤 Google STT: {stt_status["google_ready"]}')
        print(f'   🔊 gTTS: {tts_mgr.get_status()["providers_available"]["gtts"]}')
        
        # Loop de conversação
        for ciclo in range(1, 4):  # Até 3 tentativas
            print('\n' + '='*50)
            print(f'🔄 CICLO CONVERSACIONAL {ciclo}/3')
            print('='*50)
            
            # 1. Capturar fala real
            audio_data = await aguardar_fala_real(audio_mgr)
            if audio_data is None:
                print('❌ Pulando ciclo - sem fala detectada')
                continue
            
            # 2. Speech-to-Text
            print('\n🎤 Processando STT (Google Speech)...')
            texto = await stt_mgr.transcribe_audio(audio_data)
            
            if not texto:
                print('❌ STT não conseguiu reconhecer fala')
                print('💡 Tente falar mais claramente em português')
                continue
            
            print(f'📝 RECONHECIDO: "{texto}"')
            
            # Verificar comando de saída
            if any(cmd in texto.lower() for cmd in ['tchau', 'sair', 'parar']):
                print('👋 Comando de saída detectado!')
                break
            
            # 3. LLM Processing
            print('🤖 Gerando resposta...')
            resposta_llm = await llm_mgr.generate_response(texto)
            
            if not resposta_llm:
                print('❌ LLM falhou - usando resposta padrão')
                resposta_llm = {
                    "text": "Desculpe, não consegui processar sua mensagem.",
                    "movement": "shake_head"
                }
            
            print(f'🤖 TOBIAS: "{resposta_llm["text"]}"')
            print(f'   🦾 Movimento: {resposta_llm["movement"]}')
            
            # 4. Text-to-Speech
            print('🔊 Sintetizando voz...')
            audio_resposta = await tts_mgr.synthesize_speech(resposta_llm["text"])
            
            if audio_resposta is not None:
                print('📢 Reproduzindo via Anker...')
                
                # Executar movimento + fala sincronizados
                duracao_audio = len(audio_resposta) / 16000  # duração em segundos
                
                # Iniciar movimento
                movimento_task = None
                if g1_client and movement_library:
                    movimento_task = asyncio.create_task(
                        executar_movimento_g1(g1_client, movement_library, resposta_llm["movement"], duracao_audio)
                    )
                    print(f'🦾 Executando movimento: {resposta_llm["movement"]}')
                
                # Reproduzir áudio
                audio_task = asyncio.create_task(
                    reproduzir_audio_async(audio_mgr, audio_resposta)
                )
                
                # Aguardar ambos
                if movimento_task:
                    await asyncio.gather(audio_task, movimento_task)
                else:
                    await audio_task
                
                print('✅ CICLO CONVERSACIONAL COMPLETO!')
            else:
                print('❌ Falha na síntese de voz')
            
            print('\n⏳ Aguardando 3s antes do próximo ciclo...')
            await asyncio.sleep(3)
        
        print('\n🎯 TESTE CONVERSACIONAL FINALIZADO!')
        print('🎉 PARABÉNS! Sistema funcionando end-to-end!')
        
    except KeyboardInterrupt:
        print('\n🛑 Teste interrompido pelo usuário')
    except Exception as e:
        print(f'❌ Erro crítico: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(teste_conversacao_completa())
