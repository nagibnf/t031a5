#!/usr/bin/env python3
"""
Download do Modelo LLM - Sistema t031a5

Download do Llama-3.1-8B-Instruct para Jetson Orin NX 16GB
"""

import requests
import sys
from pathlib import Path
from tqdm import tqdm


def download_model():
    """Download do modelo Llama-3.1-8B-Instruct."""
    model_url = "https://huggingface.co/TheBloke/Llama-3.1-8B-Instruct-GGUF/resolve/main/llama-3.1-8b-instruct-q4_k_m.gguf"
    model_path = Path("models/llama-3.1-8b-instruct-q4_k_m.gguf")
    
    # Cria diretório se não existir
    model_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Verifica se já existe
    if model_path.exists():
        print(f"✅ Modelo já existe: {model_path}")
        return True
    
    print(f"📥 Download do modelo: {model_url}")
    print(f"💾 Salvar em: {model_path}")
    print(f"📦 Tamanho: ~4.5GB")
    
    try:
        # Download com barra de progresso
        response = requests.get(model_url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(model_path, 'wb') as f:
            with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    pbar.update(len(chunk))
        
        print(f"✅ Download concluído: {model_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erro no download: {e}")
        return False


if __name__ == "__main__":
    success = download_model()
    sys.exit(0 if success else 1)
