# 🔐 Credenciais - Sistema t031a5

## 📁 **Arquivos de Credenciais**

Esta pasta contém arquivos de credenciais necessários para serviços externos.

---

## 🎤 **Google ASR (Speech Recognition)**

### **Arquivo:** `google_asr.json`
**Necessário para:** G1VoiceInput com ASR provider "google"

### **Como Obter:**
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie/selecione um projeto
3. Ative a **Speech-to-Text API**
4. Crie uma **Service Account**
5. Gere uma **chave JSON**
6. Substitua o conteúdo de `google_asr.json`

### **Configuração no Sistema:**
```json5
// config/g1_production.json5
{
  "type": "G1Voice",
  "config": {
    "asr_provider": "google",  // ← Usa Google ASR
    "language": "pt-BR"
  }
}
```

### **Carregamento Automático:**
O sistema carrega automaticamente via `src/t031a5/security/api_manager.py`:
```python
google_asr_file = credentials_dir / "google_asr.json"
if google_asr_file.exists():
    os.environ["GOOGLE_ASR_CREDENTIALS_FILE"] = str(google_asr_file.absolute())
```

---

## 🔒 **Segurança**

### **⚠️ IMPORTANTE:**
- **NÃO** commit arquivos reais de credenciais no Git
- Arquivo atual é apenas **template**
- Substitua pelos valores reais do seu projeto Google Cloud

### **Arquivos Ignorados:**
```gitignore
# .gitignore já configurado
credentials/*.json
!credentials/README.md
```

---

## 📋 **Status Atual**

- ✅ **Pasta criada**: credentials/
- ✅ **Template**: google_asr.json (configurar com chaves reais)
- ✅ **Documentação**: Este README.md
- ✅ **Sistema configurado**: api_manager.py carrega automaticamente

**Configure suas chaves reais para usar G1VoiceInput com Google ASR!**
