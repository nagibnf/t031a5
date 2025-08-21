#!/usr/bin/env python3
"""
🎯 EXEMPLO USO AUDIO MANAGER DEFINITIVO
Como integrar a classe AudioManagerDefinitivo em códigos futuros
"""

import sys
import logging
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, "/home/unitree/t031a5/src")

from t031a5.audio.audio_manager_definitivo import AudioManagerDefinitivo

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExemploUsoAudio:
    """Exemplos práticos de uso do AudioManagerDefinitivo."""
    
    def __init__(self):
        # ✅ PASSO 1: Criar instância com conexão automática
        self.audio_mgr = AudioManagerDefinitivo(auto_connect_anker=True)
    
    def exemplo_basico_captura_reproducao(self):
        """Exemplo básico: capturar e reproduzir."""
        logger.info("📝 EXEMPLO 1: Captura e Reprodução Básica")
        
        # Capturar 3 segundos
        audio_data = self.audio_mgr.capturar_audio_dji(duracao=3.0)
        
        if audio_data is not None:
            # Reproduzir
            sucesso = self.audio_mgr.reproduzir_audio_anker(audio_data)
            logger.info(f"Resultado: {'✅ Sucesso' if sucesso else '❌ Falha'}")
            return audio_data
        else:
            logger.error("❌ Falha na captura")
            return None
    
    def exemplo_com_validacao_qualidade(self):
        """Exemplo com análise de qualidade."""
        logger.info("📝 EXEMPLO 2: Captura com Validação de Qualidade")
        
        audio_data = self.audio_mgr.capturar_audio_dji(duracao=4.0)
        
        if audio_data is not None:
            # Obter métricas detalhadas
            metricas = self.audio_mgr.obter_metricas_audio(audio_data)
            
            logger.info("📊 MÉTRICAS DETALHADAS:")
            for chave, valor in metricas.items():
                logger.info(f"   {chave}: {valor}")
            
            # Verificar qualidade antes de prosseguir
            if metricas.get("quality_ok", False):
                logger.info("✅ Qualidade adequada - prosseguindo...")
                self.audio_mgr.reproduzir_audio_anker(audio_data)
                return audio_data
            else:
                logger.warning("⚠️ Qualidade duvidosa - investigar...")
                return None
        
        return None
    
    def exemplo_sistema_conversacao_real(self):
        """Exemplo para sistema de conversação real."""
        logger.info("📝 EXEMPLO 3: Integração Sistema Conversação")
        
        while True:
            logger.info("\n🗣️ Diga algo (ou 'sair' para parar):")
            
            # 1. Capturar fala do usuário
            audio_data = self.audio_mgr.capturar_audio_dji(duracao=5.0)
            
            if audio_data is None:
                logger.error("❌ Falha na captura - tentando novamente...")
                continue
            
            # 2. Validar qualidade
            metricas = self.audio_mgr.obter_metricas_audio(audio_data)
            if not metricas.get("quality_ok", False):
                logger.warning("⚠️ Áudio de baixa qualidade - capturando novamente...")
                continue
            
            # 3. Aqui seria a integração STT real
            texto_transcrito = self.simular_stt(audio_data)
            logger.info(f"📝 STT simulado: '{texto_transcrito}'")
            
            # Verificar comando de saída
            if "sair" in texto_transcrito.lower():
                logger.info("👋 Encerrando conversação...")
                break
            
            # 4. Aqui seria a integração LLM real
            resposta_llm = self.simular_llm(texto_transcrito)
            logger.info(f"🤖 LLM simulado: '{resposta_llm}'")
            
            # 5. Aqui seria a integração TTS real
            audio_resposta = self.simular_tts(resposta_llm)
            
            # 6. Reproduzir resposta via Anker
            if audio_resposta is not None:
                logger.info("🔊 Reproduzindo resposta...")
                self.audio_mgr.reproduzir_audio_anker(audio_resposta)
            
            logger.info("="*50)
    
    def simular_stt(self, audio_data):
        """Simula STT - substituir por Google Speech API ou Whisper."""
        # PLACEHOLDER: Aqui integraria o STT real
        # Ex: return google_speech_api.transcribe(audio_data)
        #     return whisper_model.transcribe(audio_data)
        
        metricas = self.audio_mgr.obter_metricas_audio(audio_data)
        
        # Simulação baseada em qualidade
        if metricas.get("rms", 0) > 0.02:
            return "olá como você está"
        elif metricas.get("peak", 0) > 0.1:
            return "teste do microfone"
        else:
            return "áudio não compreendido"
    
    def simular_llm(self, texto):
        """Simula LLM - substituir por Ollama ou OpenAI."""
        # PLACEHOLDER: Aqui integraria o LLM real
        # Ex: return ollama_client.generate(texto)
        #     return openai_client.chat(texto)
        
        respostas = {
            "olá": "Olá! Como posso ajudá-lo?",
            "como": "Estou funcionando muito bem, obrigado!",
            "teste": "Sistema de áudio funcionando perfeitamente!",
            "sair": "Até logo! Foi um prazer conversar.",
        }
        
        for palavra in respostas:
            if palavra in texto.lower():
                return respostas[palavra]
        
        return "Interessante! Conte-me mais sobre isso."
    
    def simular_tts(self, texto):
        """Simula TTS - substituir por ElevenLabs."""
        # PLACEHOLDER: Aqui integraria o TTS real
        # Ex: return elevenlabs_client.synthesize(texto)
        
        # Por enquanto, gerar tom baseado no comprimento do texto
        import numpy as np
        
        duration = min(len(texto) * 0.1, 3.0)  # Máximo 3s
        sample_rate = 16000
        frequency = 400 + len(texto) * 10  # Frequência baseada no texto
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_tts = np.sin(2 * np.pi * frequency * t) * 0.3
        
        # Fade in/out
        fade_samples = int(0.1 * sample_rate)
        if len(audio_tts) > fade_samples * 2:
            audio_tts[:fade_samples] *= np.linspace(0, 1, fade_samples)
            audio_tts[-fade_samples:] *= np.linspace(1, 0, fade_samples)
        
        return audio_tts
    
    def exemplo_teste_completo(self):
        """Executa teste completo do sistema."""
        logger.info("📝 EXEMPLO 4: Teste Sistema Completo")
        
        # Usar método de teste integrado
        sucesso = self.audio_mgr.testar_sistema_completo(duracao=5.0)
        
        if sucesso:
            logger.info("🎉 Sistema completamente funcional!")
        else:
            logger.error("❌ Problemas detectados no sistema")
        
        return sucesso

def main():
    """Função principal - demonstra todos os exemplos."""
    logger.info("🎯 DEMONSTRAÇÃO USO AUDIO MANAGER DEFINITIVO")
    logger.info("="*60)
    
    try:
        exemplos = ExemploUsoAudio()
        
        # Menu interativo
        while True:
            print("\n📋 ESCOLHA UM EXEMPLO:")
            print("1. ⚡ Captura e Reprodução Básica")
            print("2. 📊 Análise de Qualidade")
            print("3. 🤖 Sistema Conversação (Simulado)")
            print("4. 🧪 Teste Sistema Completo")
            print("0. 🚪 Sair")
            
            escolha = input("\nDigite o número: ").strip()
            
            if escolha == "0":
                logger.info("👋 Encerrando demonstração...")
                break
            elif escolha == "1":
                exemplos.exemplo_basico_captura_reproducao()
            elif escolha == "2":
                exemplos.exemplo_com_validacao_qualidade()
            elif escolha == "3":
                exemplos.exemplo_sistema_conversacao_real()
            elif escolha == "4":
                exemplos.exemplo_teste_completo()
            else:
                print("⚠️ Opção inválida")
    
    except KeyboardInterrupt:
        logger.info("\n👋 Interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro na demonstração: {e}")

if __name__ == "__main__":
    main()
