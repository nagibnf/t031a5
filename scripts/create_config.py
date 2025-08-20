#!/usr/bin/env python3
"""
Script para criar novas configurações baseadas na configuração base completa.

USO:
    python scripts/create_config.py <nome_config> [opções]

EXEMPLOS:
    python scripts/create_config.py g1_test
    python scripts/create_config.py g1_production --mock
    python scripts/create_config.py g1_minimal --minimal
"""

import sys
import json
import shutil
from pathlib import Path
from typing import Dict, Any, List

def load_base_config() -> Dict[str, Any]:
    """Carrega a configuração base completa."""
    base_path = Path("config/g1_base_complete.json5")
    
    if not base_path.exists():
        print(f"❌ Arquivo base não encontrado: {base_path}")
        sys.exit(1)
    
    try:
        import json5
        with open(base_path, 'r') as f:
            return json5.load(f)
    except Exception as e:
        print(f"❌ Erro ao carregar configuração base: {e}")
        sys.exit(1)

def create_minimal_config(base_config: Dict[str, Any]) -> Dict[str, Any]:
    """Cria uma configuração mínima baseada na base."""
    config = base_config.copy()
    
    # Desativa funcionalidades não essenciais
    config["name"] = "G1 Minimal"
    config["description"] = "Configuração mínima para testes básicos"
    
    # Desativa inputs não essenciais
    config["agent_inputs"]["G1GPS"]["enabled"] = False
    config["agent_inputs"]["G1Sensors"]["enabled"] = False
    
    # Desativa actions não essenciais
    config["agent_actions"]["G1Arms"]["enabled"] = False
    
    # Simplifica conversação
    config["conversation_engine"]["enable_vision_context"] = False
    config["conversation_engine"]["enable_gesture_sync"] = False
    config["conversation_engine"]["enable_emotion_detection"] = False
    
    # Desativa métricas avançadas
    config["metrics"]["dashboards"]["enabled"] = False
    config["backup"]["enabled"] = False
    
    return config

def create_mock_config(base_config: Dict[str, Any]) -> Dict[str, Any]:
    """Cria uma configuração com modo mock ativado."""
    config = base_config.copy()
    
    config["name"] = "G1 Mock"
    config["description"] = "Configuração para testes sem hardware real"
    
    # Ativa modo mock em todos os componentes
    config["agent_inputs"]["G1Voice"]["mock_mode"] = True
    config["agent_inputs"]["G1Vision"]["mock_mode"] = True
    config["agent_inputs"]["G1State"]["mock_mode"] = True
    config["agent_inputs"]["G1Sensors"]["mock_mode"] = True
    config["agent_inputs"]["G1GPS"]["mock_mode"] = True
    
    config["agent_actions"]["G1Speech"]["mock_mode"] = True
    config["agent_actions"]["G1Emotion"]["mock_mode"] = True
    config["agent_actions"]["G1Movement"]["mock_mode"] = True
    config["agent_actions"]["G1Arms"]["mock_mode"] = True
    config["agent_actions"]["G1Audio"]["mock_mode"] = True
    
    # Ativa WebSim
    config["websim"]["enabled"] = True
    config["websim"]["mock_robot"] = True
    
    return config

def create_production_config(base_config: Dict[str, Any]) -> Dict[str, Any]:
    """Cria uma configuração para produção."""
    config = base_config.copy()
    
    config["name"] = "G1 Production"
    config["description"] = "Configuração otimizada para produção"
    
    # Desativa modo debug
    config["development"]["debug_mode"] = False
    config["development"]["websim_enabled"] = False
    
    # Ativa todas as funcionalidades reais
    config["agent_inputs"]["G1Voice"]["mock_mode"] = False
    config["agent_inputs"]["G1Vision"]["mock_mode"] = False
    config["agent_inputs"]["G1State"]["mock_mode"] = False
    config["agent_inputs"]["G1Sensors"]["mock_mode"] = False
    config["agent_inputs"]["G1GPS"]["mock_mode"] = False
    
    config["agent_actions"]["G1Speech"]["mock_mode"] = False
    config["agent_actions"]["G1Emotion"]["mock_mode"] = False
    config["agent_actions"]["G1Movement"]["mock_mode"] = False
    config["agent_actions"]["G1Arms"]["mock_mode"] = False
    config["agent_actions"]["G1Audio"]["mock_mode"] = False
    
    # Desativa WebSim
    config["websim"]["enabled"] = False
    
    # Ativa backup e métricas
    config["backup"]["enabled"] = True
    config["metrics"]["enabled"] = True
    
    # Configurações de segurança
    config["security"]["access_control"]["enabled"] = True
    config["security"]["data_protection"]["privacy_mode"] = True
    
    return config

def create_test_config(base_config: Dict[str, Any]) -> Dict[str, Any]:
    """Cria uma configuração para testes."""
    config = base_config.copy()
    
    config["name"] = "G1 Test"
    config["description"] = "Configuração para testes integrados"
    
    # Ativa modo debug
    config["development"]["debug_mode"] = True
    config["development"]["websim_enabled"] = True
    
    # Configurações de teste
    config["logging"]["level"] = "DEBUG"
    config["metrics"]["enabled"] = True
    
    # Timeouts menores para testes
    config["unitree_g1"]["interface"]["timeout"] = 5.0
    config["unitree_g1"]["controller"]["audio_timeout"] = 3.0
    
    return config

def save_config(config: Dict[str, Any], filename: str):
    """Salva a configuração em arquivo JSON5."""
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    filepath = config_dir / f"{filename}.json5"
    
    try:
        # Converter para JSON5 (com comentários)
        json5_content = json.dumps(config, indent=2, ensure_ascii=False)
        
        # Adicionar cabeçalho
        header = f"""// ========================================
// CONFIGURAÇÃO: {config['name']}
// ========================================
// 
// Baseada em: config/g1_base_complete.json5
// Criada em: {Path().cwd()}
// 
// ========================================

"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(header + json5_content)
        
        print(f"✅ Configuração salva: {filepath}")
        
    except Exception as e:
        print(f"❌ Erro ao salvar configuração: {e}")
        sys.exit(1)

def print_usage():
    """Mostra como usar o script."""
    print("""
🎯 CRIADOR DE CONFIGURAÇÕES - SISTEMA t031a5

USO:
    python scripts/create_config.py <nome_config> [opções]

OPÇÕES:
    --minimal     Cria configuração mínima (apenas funcionalidades essenciais)
    --mock        Cria configuração com modo mock ativado
    --production  Cria configuração otimizada para produção
    --test        Cria configuração para testes integrados
    --help        Mostra esta ajuda

EXEMPLOS:
    python scripts/create_config.py g1_test
    python scripts/create_config.py g1_production --production
    python scripts/create_config.py g1_mock --mock
    python scripts/create_config.py g1_minimal --minimal

CONFIGURAÇÕES CRIADAS:
    - config/<nome_config>.json5
""")

def main():
    """Função principal."""
    if len(sys.argv) < 2 or "--help" in sys.argv:
        print_usage()
        return
    
    config_name = sys.argv[1]
    
    # Validar nome da configuração
    if not config_name.replace("_", "").replace("-", "").isalnum():
        print("❌ Nome da configuração deve conter apenas letras, números, _ e -")
        sys.exit(1)
    
    print(f"🎯 Criando configuração: {config_name}")
    
    # Carregar configuração base
    base_config = load_base_config()
    print("✅ Configuração base carregada")
    
    # Determinar tipo de configuração
    config = base_config.copy()
    
    if "--minimal" in sys.argv:
        print("📦 Criando configuração mínima...")
        config = create_minimal_config(base_config)
    elif "--mock" in sys.argv:
        print("🎭 Criando configuração mock...")
        config = create_mock_config(base_config)
    elif "--production" in sys.argv:
        print("🏭 Criando configuração de produção...")
        config = create_production_config(base_config)
    elif "--test" in sys.argv:
        print("🧪 Criando configuração de teste...")
        config = create_test_config(base_config)
    else:
        print("📋 Criando configuração padrão...")
        config["name"] = f"G1 {config_name.title()}"
        config["description"] = f"Configuração personalizada: {config_name}"
    
    # Salvar configuração
    save_config(config, config_name)
    
    print(f"\n🎉 Configuração '{config_name}' criada com sucesso!")
    print(f"📁 Arquivo: config/{config_name}.json5")
    print(f"📋 Para usar: --config config/{config_name}.json5")

if __name__ == "__main__":
    main()
