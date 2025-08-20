#!/usr/bin/env python3
"""
Teste G1 - ROS Microfone
Demonstra como acessar o microfone do G1 via ROS usando unitreeg1_ROS_mic.
"""

import subprocess
import os
from pathlib import Path

class G1ROSMicrophoneSetup:
    """Setup para usar o microfone do G1 via ROS."""
    
    def __init__(self):
        self.workspace_path = Path.home() / "g1_mic_ws"
        self.src_path = self.workspace_path / "src"
    
    def create_workspace(self):
        """Cria o workspace ROS."""
        print("🔧 Criando workspace ROS...")
        self.workspace_path.mkdir(exist_ok=True)
        self.src_path.mkdir(exist_ok=True)
        print(f"✅ Workspace criado: {self.workspace_path}")
    
    def clone_repositories(self):
        """Clona os repositórios necessários."""
        print("📦 Clonando repositórios...")
        
        repos = [
            "https://github.com/ros-naoqi/naoqi_bridge_msgs.git",
            "https://github.com/dcuevasa/unitreeg1_ROS_mic.git"
        ]
        
        os.chdir(self.src_path)
        
        for repo in repos:
            repo_name = repo.split("/")[-1].replace(".git", "")
            if not Path(repo_name).exists():
                print(f"📥 Clonando {repo_name}...")
                result = subprocess.run(["git", "clone", repo], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ {repo_name} clonado com sucesso")
                else:
                    print(f"❌ Erro ao clonar {repo_name}: {result.stderr}")
            else:
                print(f"✅ {repo_name} já existe")
    
    def build_workspace(self):
        """Compila o workspace."""
        print("🔨 Compilando workspace...")
        os.chdir(self.workspace_path)
        
        result = subprocess.run(["catkin_make"], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Workspace compilado com sucesso")
            return True
        else:
            print(f"❌ Erro na compilação: {result.stderr}")
            return False
    
    def generate_usage_script(self):
        """Gera script de uso."""
        script_content = f"""#!/bin/bash
# Script para usar o microfone do G1 via ROS

# 1. Source do ambiente ROS
source /opt/ros/noetic/setup.bash
source {self.workspace_path}/devel/setup.bash

# 2. Executar o nó do microfone
echo "🎤 Iniciando nó do microfone G1..."
rosrun unitreeg1_ROS_mic unitreeg1_ROS_mic_node

# Tópicos disponíveis:
# - /unitreeg1_ROS_mic/audio_raw  (sensor_msgs/AudioData)
# - /unitreeg1_ROS_mic/audio_info (naoqi_bridge_msgs/AudioBuffer)
"""
        
        script_path = self.workspace_path / "run_g1_microphone.sh"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Tornar executável
        os.chmod(script_path, 0o755)
        print(f"✅ Script gerado: {script_path}")
    
    def show_instructions(self):
        """Mostra instruções de uso."""
        print("\n🎯 INSTRUÇÕES DE USO:")
        print("=" * 50)
        print("1. Certifique-se que o ROS Noetic está instalado")
        print("2. Execute o setup:")
        print(f"   cd {self.workspace_path}")
        print("   source devel/setup.bash")
        print()
        print("3. Para usar o microfone:")
        print("   rosrun unitreeg1_ROS_mic unitreeg1_ROS_mic_node")
        print()
        print("4. Tópicos disponíveis:")
        print("   /unitreeg1_ROS_mic/audio_raw")
        print("   /unitreeg1_ROS_mic/audio_info")
        print()
        print("5. Para escutar o áudio:")
        print("   rostopic echo /unitreeg1_ROS_mic/audio_raw")
    
    def setup_complete(self):
        """Executa o setup completo."""
        print("🤖 G1 ROS MICROFONE SETUP")
        print("=" * 40)
        
        try:
            self.create_workspace()
            self.clone_repositories()
            
            if self.build_workspace():
                self.generate_usage_script()
                self.show_instructions()
                print("\n🎉 SETUP CONCLUÍDO COM SUCESSO!")
                return True
            else:
                print("\n❌ SETUP FALHOU NA COMPILAÇÃO")
                return False
                
        except Exception as e:
            print(f"❌ Erro no setup: {e}")
            return False

def main():
    """Função principal."""
    print("🎤 G1 ROS MICROFONE SETUP")
    print("=" * 60)
    print("🎯 OBJETIVO: Configurar acesso ao microfone do G1 via ROS")
    print("📦 PACOTE: unitreeg1_ROS_mic")
    print("🔗 FONTE: https://github.com/dcuevasa/unitreeg1_ROS_mic")
    
    response = input("\nDeseja continuar com o setup? (s/n): ").strip().lower()
    if response not in ['s', 'sim', 'y', 'yes']:
        print("❌ Setup cancelado")
        return
    
    setup = G1ROSMicrophoneSetup()
    
    if setup.setup_complete():
        print("\n✅ MICROFONE DO G1 CONFIGURADO!")
        print("💡 Use o script gerado para facilitar o uso")
    else:
        print("\n❌ FALHA NO SETUP")
        print("💡 Verifique se o ROS Noetic está instalado")

if __name__ == "__main__":
    main()
