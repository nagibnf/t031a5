#!/usr/bin/env python3
"""
Exemplo de Verificação de Estado do G1
======================================

Este exemplo demonstra a prática CORRETA de sempre verificar
o estado do robô antes de executar qualquer comando.

REGRAS OBRIGATÓRIAS:
1. SEMPRE verificar estado antes de qualquer ação
2. Para locomoção: modo "control"
3. Para braços: modo "ai"
4. Se estado incorreto: NÃO executar comando
"""

import time
import sys
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient
from unitree_sdk2py.g1.arm.g1_arm_action_client import G1ArmActionClient
from unitree_sdk2py.comm.motion_switcher.motion_switcher_client import MotionSwitcherClient

class G1StateVerificationExample:
    """Exemplo de verificação de estado correta."""
    
    def __init__(self):
        self.interface = "en11"
        self.loco_client = None
        self.arm_client = None
        self.motion_switcher = None
        
    def initialize_sdk(self):
        """Inicializa o SDK."""
        try:
            print("🔧 Inicializando SDK...")
            ChannelFactoryInitialize(0, self.interface)
            
            self.loco_client = LocoClient()
            self.loco_client.SetTimeout(10.0)
            self.loco_client.Init()
            
            self.arm_client = G1ArmActionClient()
            self.arm_client.SetTimeout(10.0)
            self.arm_client.Init()
            
            self.motion_switcher = MotionSwitcherClient()
            self.motion_switcher.SetTimeout(10.0)
            self.motion_switcher.Init()
            
            print("✅ SDK inicializado")
            return True
            
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            return False
    
    def check_robot_state(self, expected_mode="control"):
        """
        Verifica o estado atual do robô.
        
        Args:
            expected_mode: Modo esperado ("control" para locomoção, "ai" para braços)
            
        Returns:
            True se está no modo correto, False caso contrário
        """
        try:
            status, result = self.motion_switcher.CheckMode()
            if status == 0 and result:
                current_mode = result.get('name', 'unknown')
                current_form = result.get('form', 'unknown')
                
                print(f"📊 Estado atual: {result}")
                print(f"   Modo: {current_mode}")
                print(f"   Form: {current_form}")
                
                if current_mode == expected_mode:
                    print(f"✅ Robô está no modo correto: {current_mode}")
                    return True
                else:
                    print(f"⚠️  Robô está em modo {current_mode}, esperado: {expected_mode}")
                    print(f"❌ COMANDO NÃO EXECUTADO - Estado incorreto!")
                    return False
            else:
                print(f"❌ Erro ao verificar estado: {status}, {result}")
                return False
                
        except Exception as e:
            print(f"❌ Erro na verificação de estado: {e}")
            return False
    
    def safe_move(self, vx, vy, vyaw, description=""):
        """
        Executa movimento com verificação de estado.
        
        Args:
            vx, vy, vyaw: Parâmetros de movimento
            description: Descrição do movimento
        """
        print(f"\n🔄 Tentando movimento: {description}")
        
        # SEMPRE verificar estado antes de executar
        if not self.check_robot_state("control"):
            print(f"   ❌ Movimento '{description}' CANCELADO - Estado incorreto")
            return False
        
        try:
            print(f"   🚀 Executando movimento...")
            self.loco_client.Move(vx, vy, vyaw, continous_move=True)
            time.sleep(3)
            self.loco_client.StopMove()
            print(f"   ✅ Movimento '{description}' executado com sucesso")
            return True
            
        except Exception as e:
            print(f"   ❌ Erro no movimento '{description}': {e}")
            return False
    
    def safe_arm_action(self, action_id, description=""):
        """
        Executa ação de braço com verificação de estado.
        
        Args:
            action_id: ID da ação
            description: Descrição da ação
        """
        print(f"\n🤚 Tentando ação de braço: {description}")
        
        # SEMPRE verificar estado antes de executar
        if not self.check_robot_state("ai"):
            print(f"   ❌ Ação '{description}' CANCELADA - Estado incorreto")
            return False
        
        try:
            print(f"   🚀 Executando ação...")
            result = self.arm_client.ExecuteAction(action_id)
            if result == 0:
                print(f"   ✅ Ação '{description}' executada com sucesso")
                return True
            else:
                print(f"   ❌ Erro na ação '{description}': {result}")
                return False
                
        except Exception as e:
            print(f"   ❌ Erro na ação '{description}': {e}")
            return False
    
    def demonstrate_state_verification(self):
        """Demonstra a verificação de estado correta."""
        print("🤖 DEMONSTRAÇÃO DE VERIFICAÇÃO DE ESTADO")
        print("=" * 50)
        
        # 1. Verificar estado atual
        print("\n1️⃣ Verificando estado atual...")
        self.check_robot_state()
        
        # 2. Tentar movimento sem estado correto
        print("\n2️⃣ Tentando movimento SEM estado correto...")
        self.safe_move(0.1, 0.0, 0.0, "Movimento teste")
        
        # 3. Tentar ação de braço sem estado correto
        print("\n3️⃣ Tentando ação de braço SEM estado correto...")
        self.safe_arm_action(32, "Right Hand on Mouth")
        
        # 4. Instruções para o usuário
        print("\n4️⃣ INSTRUÇÕES PARA TESTE CORRETO:")
        print("   Para testar locomoção:")
        print("   - Coloque robô em Main Operation Control (R1+X)")
        print("   - Aguarde estabilização")
        print("   - Execute novamente este teste")
        print("")
        print("   Para testar braços:")
        print("   - Coloque robô em AI Mode")
        print("   - Aguarde estabilização")
        print("   - Execute novamente este teste")
        
        # 5. Verificar estado novamente
        print("\n5️⃣ Verificação final de estado...")
        self.check_robot_state()
    
    def run_example(self):
        """Executa o exemplo completo."""
        print("🔍 EXEMPLO DE VERIFICAÇÃO DE ESTADO DO G1")
        print("=" * 60)
        print("Este exemplo demonstra a prática CORRETA de verificar")
        print("o estado do robô antes de executar qualquer comando.")
        print("=" * 60)
        
        if not self.initialize_sdk():
            return False
        
        self.demonstrate_state_verification()
        
        print("\n🎯 RESUMO DA PRÁTICA CORRETA:")
        print("✅ SEMPRE verificar estado antes de qualquer comando")
        print("✅ Para locomoção: modo 'control'")
        print("✅ Para braços: modo 'ai'")
        print("✅ Se estado incorreto: NÃO executar comando")
        print("✅ Implementar verificação em TODOS os testes")
        
        return True

def main():
    """Função principal."""
    example = G1StateVerificationExample()
    example.run_example()

if __name__ == "__main__":
    main()
