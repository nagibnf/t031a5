#!/usr/bin/env python3
"""
Captura posições das juntas em tempo real usando DDS.
Útil para capturar posições de movimentos específicos.
"""

import time
import sys
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_

class PositionCapture:
    """Captura posições das juntas em tempo real."""
    
    def __init__(self):
        self.interface = "en11"
        self.low_state = None
        self.first_update = False
        
    def initialize_sdk(self):
        """Inicializa o SDK."""
        try:
            print("🔧 Inicializando SDK...")
            ChannelFactoryInitialize(0, self.interface)
            print("✅ SDK inicializado")
            return True
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            return False
    
    def init_subscriber(self):
        """Inicializa subscriber para capturar posições."""
        try:
            self.lowstate_subscriber = ChannelSubscriber("rt/lowstate", LowState_)
            self.lowstate_subscriber.Init(self.low_state_handler, 10)
            print("✅ Subscriber inicializado")
            return True
        except Exception as e:
            print(f"❌ Erro no subscriber: {e}")
            return False
    
    def low_state_handler(self, msg: LowState_):
        """Handler para mensagens de estado."""
        self.low_state = msg
        if not self.first_update:
            self.first_update = True
    
    def get_right_arm_positions(self):
        """Obtém posições do braço direito."""
        if not self.low_state:
            return None
        
        positions = {
            "RightShoulderPitch": self.low_state.motor_state[22].q,
            "RightShoulderRoll": self.low_state.motor_state[23].q,
            "RightShoulderYaw": self.low_state.motor_state[24].q,
            "RightElbow": self.low_state.motor_state[25].q,
            "RightWristRoll": self.low_state.motor_state[26].q
        }
        
        return positions
    
    def capture_positions(self, duration=10):
        """Captura posições por um período de tempo."""
        print(f"📊 Capturando posições por {duration} segundos...")
        print("🎯 Execute o movimento desejado durante este período")
        print("=" * 60)
        
        start_time = time.time()
        last_print_time = 0
        
        while time.time() - start_time < duration:
            if self.low_state:
                positions = self.get_right_arm_positions()
                current_time = time.time() - start_time
                
                # Imprimir a cada 0.5 segundos
                if current_time - last_print_time >= 0.5:
                    print(f"⏱️  {current_time:.1f}s:")
                    for joint, pos in positions.items():
                        print(f"   {joint}: {pos:.4f} rad")
                    print()
                    last_print_time = current_time
            
            time.sleep(0.1)
        
        # Posições finais
        if self.low_state:
            final_positions = self.get_right_arm_positions()
            print("📋 POSIÇÕES FINAIS:")
            print("=" * 30)
            for joint, pos in final_positions.items():
                print(f"{joint}: {pos:.4f} rad")
            
            # Formato para usar no código
            print("\n📝 FORMATO PARA CÓDIGO:")
            print("=" * 30)
            print("self.right_arm_positions = {")
            for joint, pos in final_positions.items():
                print(f"    G1JointIndex.{joint}: {pos:.4f},")
            print("}")
    
    def run_capture(self):
        """Executa a captura."""
        print("📊 CAPTURA DE POSIÇÕES EM TEMPO REAL")
        print("=" * 50)
        
        if not self.initialize_sdk():
            return False
        
        if not self.init_subscriber():
            return False
        
        # Aguardar primeiro estado
        print("⏳ Aguardando dados do robô...")
        while not self.first_update:
            time.sleep(0.1)
        
        print("✅ Dados recebidos! Iniciando captura...")
        
        # Capturar posições
        self.capture_positions(10)  # 10 segundos
        
        return True

def main():
    """Função principal."""
    print("📊 CAPTURA DE POSIÇÕES - BRAÇO DIREITO")
    print("=" * 50)
    print("🎯 OBJETIVO: Capturar posições em tempo real")
    print("📋 INSTRUÇÕES:")
    print("1. Execute este script")
    print("2. Execute o movimento desejado no robô")
    print("3. Observe as posições capturadas")
    
    response = input("Deseja continuar? (s/n): ").strip().lower()
    if response not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada")
        return
    
    capturer = PositionCapture()
    capturer.run_capture()

if __name__ == "__main__":
    main()
