#!/usr/bin/env python3
"""
📦 INSTALADOR DEPENDÊNCIAS IA REAL
Instala todas as dependências necessárias para STT/LLM/TTS reais
"""

import subprocess
import sys
import logging
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InstaladorDependenciasIA:
    """Instalador automático de dependências para IA real."""
    
    def __init__(self):
        self.dependencias_pip = [
            # Google Speech API
            "google-cloud-speech==2.21.0",
            
            # OpenAI (Whisper + GPT)
            "openai==1.3.0",
            
            # ElevenLabs TTS
            "elevenlabs==0.2.26",
            
            # Whisper local (opcional)
            "openai-whisper==20231117",
            
            # TTS fallbacks
            "gTTS==2.4.0",
            "pyttsx3==2.90",
            
            # Processamento de áudio
            "scipy==1.11.4",
            "librosa==0.10.1",
            
            # HTTP requests assíncronos
            "aiohttp==3.9.1",
            
            # Processamento de dados
            "pandas==2.1.3",
            "python-dotenv==1.0.0"
        ]
        
        self.dependencias_sistema = {
            "ubuntu": [
                "ffmpeg",
                "pulseaudio-utils",
                "alsa-utils",
                "sox",
                "espeak",
                "espeak-data",
                "libportaudio2",
                "libportaudiocpp0",
                "portaudio19-dev"
            ]
        }
    
    def detectar_sistema(self):
        """Detecta sistema operacional."""
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read().lower()
                if 'ubuntu' in content or 'debian' in content:
                    return 'ubuntu'
                elif 'centos' in content or 'rhel' in content:
                    return 'centos'
        except:
            pass
        
        return 'unknown'
    
    def instalar_dependencias_sistema(self):
        """Instala dependências do sistema operacional."""
        sistema = self.detectar_sistema()
        
        if sistema == 'ubuntu':
            logger.info("🐧 Detectado Ubuntu/Debian - instalando dependências...")
            
            # Atualizar repositórios
            subprocess.run(["sudo", "apt", "update"], check=True)
            
            # Instalar pacotes
            for pacote in self.dependencias_sistema['ubuntu']:
                try:
                    logger.info(f"📦 Instalando {pacote}...")
                    subprocess.run(["sudo", "apt", "install", "-y", pacote], check=True)
                    logger.info(f"✅ {pacote} instalado")
                except subprocess.CalledProcessError as e:
                    logger.warning(f"⚠️ Falha ao instalar {pacote}: {e}")
        else:
            logger.warning(f"⚠️ Sistema {sistema} não suportado automaticamente")
            logger.info("📋 Instale manualmente: ffmpeg, pulseaudio-utils, alsa-utils, sox, espeak")
    
    def verificar_venv(self):
        """Verifica se está em ambiente virtual."""
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            logger.info("✅ Ambiente virtual detectado")
            return True
        else:
            logger.warning("⚠️ Não está em ambiente virtual - recomendado usar venv")
            return False
    
    def instalar_dependencias_python(self):
        """Instala dependências Python via pip."""
        logger.info("🐍 Instalando dependências Python...")
        
        for dep in self.dependencias_pip:
            try:
                logger.info(f"📦 Instalando {dep}...")
                subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
                logger.info(f"✅ {dep} instalado")
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Falha ao instalar {dep}: {e}")
                logger.info("💡 Tente instalar manualmente: pip install " + dep)
    
    def verificar_ffmpeg(self):
        """Verifica se ffmpeg está disponível."""
        try:
            result = subprocess.run(["ffmpeg", "-version"], capture_output=True)
            if result.returncode == 0:
                logger.info("✅ FFmpeg disponível")
                return True
        except FileNotFoundError:
            pass
        
        logger.warning("⚠️ FFmpeg não encontrado - necessário para TTS")
        return False
    
    def configurar_credenciais(self):
        """Configura credenciais de APIs."""
        logger.info("🔑 CONFIGURAÇÃO DE CREDENCIAIS")
        logger.info("="*50)
        
        env_file = Path(__file__).parent.parent / ".env"
        
        print("\n📋 CREDENCIAIS NECESSÁRIAS:")
        print("1. 🗣️ Google Speech API:")
        print("   - GOOGLE_SPEECH_CREDENTIALS_JSON (JSON das credenciais)")
        print("2. 🤖 OpenAI API:")
        print("   - OPENAI_API_KEY")
        print("3. 🔊 ElevenLabs API:")
        print("   - ELEVENLABS_API_KEY")
        
        print(f"\n📄 Configure no arquivo: {env_file}")
        print("\nExemplo:")
        print("OPENAI_API_KEY=sk-...")
        print("ELEVENLABS_API_KEY=...")
        print('GOOGLE_SPEECH_CREDENTIALS_JSON={"type":"service_account",...}')
        
    def testar_instalacao(self):
        """Testa se as instalações foram bem-sucedidas."""
        logger.info("🧪 TESTANDO INSTALAÇÕES...")
        
        testes = [
            ("Google Cloud Speech", "google.cloud.speech"),
            ("OpenAI", "openai"),
            ("ElevenLabs", "elevenlabs"),
            ("Whisper", "whisper"),
            ("gTTS", "gtts"),
            ("Pyttsx3", "pyttsx3"),
            ("SciPy", "scipy"),
            ("Librosa", "librosa"),
            ("AioHTTP", "aiohttp"),
            ("NumPy", "numpy"),
            ("Wave", "wave")
        ]
        
        sucessos = 0
        total = len(testes)
        
        for nome, modulo in testes:
            try:
                __import__(modulo)
                logger.info(f"✅ {nome}: OK")
                sucessos += 1
            except ImportError:
                logger.warning(f"❌ {nome}: FALHOU")
        
        logger.info(f"📊 RESULTADO: {sucessos}/{total} módulos disponíveis")
        
        if sucessos == total:
            logger.info("🎉 TODAS AS DEPENDÊNCIAS INSTALADAS COM SUCESSO!")
            return True
        else:
            logger.warning("⚠️ Algumas dependências falharam - verifique logs")
            return False
    
    def executar_instalacao_completa(self):
        """Executa instalação completa."""
        logger.info("🚀 INICIANDO INSTALAÇÃO COMPLETA DE DEPENDÊNCIAS IA")
        logger.info("="*70)
        
        try:
            # 1. Verificar ambiente
            self.verificar_venv()
            
            # 2. Instalar dependências do sistema
            self.instalar_dependencias_sistema()
            
            # 3. Verificar FFmpeg
            self.verificar_ffmpeg()
            
            # 4. Instalar dependências Python
            self.instalar_dependencias_python()
            
            # 5. Testar instalação
            sucesso = self.testar_instalacao()
            
            # 6. Mostrar configuração de credenciais
            self.configurar_credenciais()
            
            if sucesso:
                logger.info("🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
                logger.info("📋 Próximos passos:")
                logger.info("   1. Configure as credenciais no .env")
                logger.info("   2. Execute: python3 sistema_conversacao_real_completo.py")
            else:
                logger.warning("⚠️ Instalação parcial - verifique dependências faltantes")
                
        except Exception as e:
            logger.error(f"❌ Erro na instalação: {e}")

def main():
    """Função principal."""
    instalador = InstaladorDependenciasIA()
    instalador.executar_instalacao_completa()

if __name__ == "__main__":
    main()
