#!/usr/bin/env python3
"""
Captura as posições reais do movimento ID 32 (mão na boca)
para usar no movimento personalizado de riso.
"""

import time
import sys
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.arm.g1_arm_action_client import G1ArmActionClient
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient
from unitree_sdk2py.comm.motion_switcher.motion_switcher_client import MotionSwitcherClient

class Movement32Capture:
    """Captura posições do movimento ID 32."""
    
    def __init__(self):
        self.interface = "en11"
        self.arm_client = None
        self.loco_client = None
        self.motion_switcher = None
        
    def initialize_sdk(self):
        """Inicializa o SDK."""
        try:
            print("🔧 Inicializando SDK...")
            ChannelFactoryInitialize(0, self.interface)
            print("✅ SDK inicializado")
            
            # Inicializar clientes
            self.arm_client = G1ArmActionClient()
            self.arm_client.SetTimeout(5.0)
            self.arm_client.Init()
            
            self.loco_client = LocoClient()
            self.loco_client.SetTimeout(5.0)
            self.loco_client.Init()
            
            self.motion_switcher = MotionSwitcherClient()
            self.motion_switcher.SetTimeout(5.0)
            self.motion_switcher.Init()
            
            print("✅ Clientes inicializados")
            return True
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            return False
    
    def check_current_state(self):
        """Verifica o estado atual do robô."""
        try:
            status, result = self.motion_switcher.CheckMode()
            print(f"📊 Status atual: {status}")
            
            if result:
                print(f"📊 Modo atual: {result}")
                if isinstance(result, dict) and result.get('name') == 'ai':
                    print("✅ Robô já está em Main Operation Control!")
                    return True
                else:
                    print(f"⚠️  Robô está em modo: {result}")
                    return False
            else:
                print("❌ Não foi possível verificar o modo atual")
                return False
        except Exception as e:
            print(f"❌ Erro ao verificar estado: {e}")
            return False
    
    def setup_main_operation_control(self):
        """Configura o robô para Main Operation Control se necessário."""
        if self.check_current_state():
            print("✅ Robô já está pronto para comandos de braço!")
            return True
        
        print("🚀 Configurando Main Operation Control...")
        
        # Zero Torque → Damping → Get Ready
        print("1️⃣ Zero Torque...")
        self.loco_client.SetFsmId(0)
        time.sleep(2)
        
        print("2️⃣ Damping...")
        self.loco_client.SetFsmId(1)
        time.sleep(2)
        
        print("3️⃣ Get Ready...")
        self.loco_client.SetFsmId(4)
        time.sleep(3)
        
        print("4️⃣ Use R1+X no controle físico para Main Operation Control")
        input("Pressione Enter após R1+X...")
        
        return self.check_current_state()
    
    def capture_movement_32(self):
        """Captura as posições do movimento ID 32."""
        print("🎯 CAPTURANDO MOVIMENTO ID 32 (mão na boca)")
        print("=" * 50)
        
        # 1. Verificar estado inicial
        print("📊 Estado inicial do braço direito:")
        print("   (Execute manualmente o movimento ID 32 para ver as posições)")
        
        # 2. Executar movimento ID 32
        print("\n🤚 Executando movimento ID 32...")
        result = self.arm_client.ExecuteAction(32)  # right_hand_on_mouth
        
        if result == 0:
            print("✅ Movimento ID 32 executado com sucesso!")
            print("\n📋 INSTRUÇÕES:")
            print("1. Observe o braço direito na posição 'mão na boca'")
            print("2. Use o script 'capture_positions.py' para capturar as posições")
            print("3. Ou me informe as posições observadas")
            
            # Aguardar um pouco para estabilizar
            time.sleep(3)
            
            # 3. Voltar ao estado inicial
            print("\n🔄 Voltando ao estado inicial...")
            self.arm_client.ExecuteAction(99)  # release_arm
            time.sleep(2)
            
            return True
        else:
            print(f"❌ Movimento ID 32 falhou (Status: {result})")
            return False
    
    def run_capture(self):
        """Executa a captura completa."""
        print("🎯 CAPTURA DE MOVIMENTO ID 32")
        print("=" * 40)
        
        if not self.initialize_sdk():
            return False
        
        if not self.setup_main_operation_control():
            return False
        
        return self.capture_movement_32()

def main():
    """Função principal."""
    print("🎯 CAPTURA DE MOVIMENTO ID 32 - MÃO NA BOCA")
    print("=" * 50)
    print("🎯 OBJETIVO: Capturar posições reais do movimento ID 32")
    
    response = input("Deseja continuar? (s/n): ").strip().lower()
    if response not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada")
        return
    
    capturer = Movement32Capture()
    capturer.run_capture()

if __name__ == "__main__":
    main()
