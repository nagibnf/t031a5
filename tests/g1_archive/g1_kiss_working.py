#!/usr/bin/env python3
"""
G1 Kiss - Arquivo funcional que respeita as regras do G1.
- Aguarda conclusão do comando
- Volta ao estado inicial
- Usa interface correta
"""

import time
import sys
import asyncio
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class G1KissController:
    """Controlador de beijos do G1 com regras corretas."""
    
    def __init__(self):
        self.interface = "en11"
        self.robot_ip = "192.168.123.161"
        self.command_delay = 5.0  # Aguardar conclusão
        self.return_to_initial = True
        
    def initialize_sdk(self):
        """Inicializa o SDK com interface correta."""
        try:
            from unitree_sdk2py.core.channel import ChannelFactoryInitialize
            from unitree_sdk2py.comm.motion_switcher.motion_switcher_client import MotionSwitcherClient
            
            print("🔧 Inicializando SDK...")
            ChannelFactoryInitialize(0, self.interface)
            print("✅ SDK inicializado com interface en11")
            
            self.msc = MotionSwitcherClient()
            self.msc.SetTimeout(5.0)
            self.msc.Init()
            print("✅ MotionSwitcherClient inicializado")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            return False
    
    def check_mode(self):
        """Verifica o modo atual do G1."""
        try:
            status, result = self.msc.CheckMode()
            print(f"📊 Status: {status}, Modo: {result}")
            return status == 0
        except Exception as e:
            print(f"❌ Erro ao verificar modo: {e}")
            return False
    
    def send_kiss_command(self, kiss_type="two-hand kiss"):
        """Envia comando de beijo respeitando as regras."""
        try:
            print(f"💋 Enviando comando: {kiss_type}")
            
            # Enviar comando
            result = self.msc.SelectMode(kiss_type)
            print(f"✅ Comando enviado: {result}")
            
            # AGUARDAR CONCLUSÃO (regra crítica)
            print(f"⏳ Aguardando {self.command_delay} segundos para conclusão...")
            time.sleep(self.command_delay)
            
            # VOLTAR AO ESTADO INICIAL (regra crítica)
            if self.return_to_initial:
                print("🔄 Voltando ao estado inicial...")
                self.msc.ReleaseMode()
                time.sleep(2.0)  # Aguardar retorno
                print("✅ Estado inicial restaurado")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro no comando: {e}")
            return False
    
    def list_available_commands(self):
        """Lista comandos disponíveis."""
        commands = [
            ("left kiss", 7),
            ("right kiss", 14),
            ("two-hand kiss", 15),
            ("heart", 8),
            ("hug", 3),
            ("high five", 2),
            ("shake hand", 1),
            ("clap", 5)
        ]
        
        print("📋 Comandos disponíveis:")
        for name, id in commands:
            print(f"  - {name} (ID: {id})")
        
        return commands
    
    def interactive_kiss(self):
        """Modo interativo para enviar beijos."""
        print("💋 G1 Kiss Controller - Modo Interativo")
        print("=" * 50)
        
        if not self.initialize_sdk():
            return
        
        if not self.check_mode():
            print("⚠️  Modo não detectado, mas continuando...")
        
        self.list_available_commands()
        
        while True:
            print("\n🎯 Escolha um comando:")
            print("1. left kiss")
            print("2. right kiss") 
            print("3. two-hand kiss")
            print("4. heart")
            print("5. hug")
            print("0. Sair")
            
            choice = input("Digite sua escolha (0-5): ").strip()
            
            if choice == "0":
                print("👋 Saindo...")
                break
            elif choice == "1":
                self.send_kiss_command("left kiss")
            elif choice == "2":
                self.send_kiss_command("right kiss")
            elif choice == "3":
                self.send_kiss_command("two-hand kiss")
            elif choice == "4":
                self.send_kiss_command("heart")
            elif choice == "5":
                self.send_kiss_command("hug")
            else:
                print("❌ Escolha inválida")

def main():
    """Função principal."""
    controller = G1KissController()
    controller.interactive_kiss()

if __name__ == "__main__":
    main()
