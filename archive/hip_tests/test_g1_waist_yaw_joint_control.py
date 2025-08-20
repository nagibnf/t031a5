#!/usr/bin/env python3
"""
Teste Específico: WAIST_YAW (ID 12) - Controle de Junta
=======================================================

Este teste tenta controlar especificamente a junta WAIST_YAW (ID 12)
usando controle de juntas, não locomoção.
"""

import time
import sys
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient
from unitree_sdk2py.g1.arm.g1_arm_action_client import G1ArmActionClient
from unitree_sdk2py.comm.motion_switcher.motion_switcher_client import MotionSwitcherClient

class G1WaistYawJointControlTest:
    """Teste de controle específico da junta WAIST_YAW."""
    
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
    
    def check_robot_state(self):
        """Verifica o estado atual do robô."""
        try:
            status, result = self.motion_switcher.CheckMode()
            if status == 0 and result:
                current_mode = result.get('name', 'unknown')
                current_form = result.get('form', 'unknown')
                print(f"📊 Estado atual: {result}")
                return current_mode
            else:
                print(f"❌ Erro ao verificar estado: {status}, {result}")
                return None
                
        except Exception as e:
            print(f"❌ Erro na verificação de estado: {e}")
            return None
    
    def test_waist_yaw_joint_control(self):
        """Testa controle específico da junta WAIST_YAW."""
        print("\n🦴 TESTE: CONTROLE ESPECÍFICO WAIST_YAW (ID 12)")
        print("=" * 60)
        print("🎯 Tentando controlar APENAS a junta WAIST_YAW")
        print("👀 OBSERVE se APENAS o quadril gira (não as pernas)")
        
        # Verificar estado atual
        current_mode = self.check_robot_state()
        print(f"🤖 Robô está em modo: {current_mode}")
        
        # Teste 1: Tentar usar SetJoint para WAIST_YAW
        print("\n1️⃣ TESTE: SetJoint para WAIST_YAW (ID 12)")
        print("   👀 Observe se APENAS o quadril gira...")
        input("   ⏸️  Pressione ENTER para testar SetJoint...")
        
        try:
            # Tentar controlar especificamente a junta WAIST_YAW
            # WAIST_YAW = ID 12, tentar rotação de 0.2 radianos
            result = self.loco_client.SetJoint(12, 0.2)  # WAIST_YAW para direita
            if result == 0:
                print("   ✅ Comando SetJoint enviado para WAIST_YAW")
                time.sleep(3)  # Aguardar movimento
                print("   👀 APENAS o quadril girou? (s/n): ", end="")
                response = input().lower()
                if response in ['s', 'sim', 'y', 'yes']:
                    print("   🎉 WAIST_YAW FUNCIONOU - Controle específico!")
                else:
                    print("   ❌ WAIST_YAW não funcionou ou moveu pernas")
            else:
                print(f"   ❌ Erro no SetJoint: {result}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # Teste 2: Tentar usar SetJoint para rotação oposta
        print("\n2️⃣ TESTE: SetJoint WAIST_YAW oposto")
        print("   👀 Observe se APENAS o quadril gira para o lado oposto...")
        input("   ⏸️  Pressione ENTER para testar rotação oposta...")
        
        try:
            # Tentar rotação oposta
            result = self.loco_client.SetJoint(12, -0.2)  # WAIST_YAW para esquerda
            if result == 0:
                print("   ✅ Comando SetJoint oposto enviado")
                time.sleep(3)  # Aguardar movimento
                print("   👀 APENAS o quadril girou para o lado oposto? (s/n): ", end="")
                response = input().lower()
                if response in ['s', 'sim', 'y', 'yes']:
                    print("   🎉 WAIST_YAW FUNCIONOU - Rotação oposta!")
                else:
                    print("   ❌ WAIST_YAW não funcionou ou moveu pernas")
            else:
                print(f"   ❌ Erro no SetJoint oposto: {result}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # Teste 3: Tentar voltar à posição neutra
        print("\n3️⃣ TESTE: SetJoint WAIST_YAW neutro")
        print("   👀 Observe se APENAS o quadril volta ao centro...")
        input("   ⏸️  Pressione ENTER para voltar ao centro...")
        
        try:
            # Tentar voltar ao centro
            result = self.loco_client.SetJoint(12, 0.0)  # WAIST_YAW neutro
            if result == 0:
                print("   ✅ Comando SetJoint neutro enviado")
                time.sleep(3)  # Aguardar movimento
                print("   👀 APENAS o quadril voltou ao centro? (s/n): ", end="")
                response = input().lower()
                if response in ['s', 'sim', 'y', 'yes']:
                    print("   🎉 WAIST_YAW FUNCIONOU - Posição neutra!")
                else:
                    print("   ❌ WAIST_YAW não voltou ao centro ou moveu pernas")
            else:
                print(f"   ❌ Erro no SetJoint neutro: {result}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # Teste 4: Verificar se SetJoint existe
        print("\n4️⃣ TESTE: Verificar métodos disponíveis")
        print("   🔍 Verificando métodos do LocoClient...")
        
        try:
            # Listar métodos disponíveis
            methods = [method for method in dir(self.loco_client) if not method.startswith('_')]
            print(f"   📋 Métodos disponíveis: {methods}")
            
            if 'SetJoint' in methods:
                print("   ✅ SetJoint existe no LocoClient")
            else:
                print("   ❌ SetJoint NÃO existe no LocoClient")
                
            if 'SetWaistYaw' in methods:
                print("   ✅ SetWaistYaw existe no LocoClient")
            else:
                print("   ❌ SetWaistYaw NÃO existe no LocoClient")
                
        except Exception as e:
            print(f"   ❌ Erro ao verificar métodos: {e}")
        
        # Resumo final
        print("\n📊 RESUMO DO TESTE WAIST_YAW:")
        print("=" * 40)
        print("🤔 É possível controlar APENAS a junta WAIST_YAW?")
        print("   Baseado nos testes acima...")
        
        final_response = input("   RESPOSTA FINAL (s/n): ").lower()
        if final_response in ['s', 'sim', 'y', 'yes']:
            print("   🎉 CONCLUSÃO: WAIST_YAW PODE SER CONTROLADO!")
            print("   ✅ É possível mover apenas o quadril")
        else:
            print("   ❌ CONCLUSÃO: WAIST_YAW NÃO PODE SER CONTROLADO!")
            print("   ❌ Não é possível mover apenas o quadril")
        
        return True
    
    def run_test(self):
        """Executa o teste completo."""
        print("🦴 TESTE: CONTROLE ESPECÍFICO WAIST_YAW")
        print("=" * 60)
        print("Este teste tenta controlar APENAS a junta WAIST_YAW")
        print("sem mover as pernas do robô.")
        print("=" * 60)
        
        if not self.initialize_sdk():
            return False
        
        return self.test_waist_yaw_joint_control()

def main():
    """Função principal."""
    print("🦴 TESTE: CONTROLE ESPECÍFICO WAIST_YAW")
    print("=" * 60)
    print("⚠️  ATENÇÃO: Observe se APENAS o quadril gira!")
    print("⚠️  Pressione Ctrl+C para interromper a qualquer momento!")
    print("=" * 60)
    
    # Confirmação do usuário
    try:
        response = input("\n🤔 Deseja testar controle específico da WAIST_YAW? (s/N): ").lower()
        if response not in ['s', 'sim', 'y', 'yes']:
            print("❌ Teste cancelado pelo usuário")
            return
    except KeyboardInterrupt:
        print("\n❌ Teste cancelado")
        return
    
    # Executar teste
    tester = G1WaistYawJointControlTest()
    success = tester.run_test()
    
    if success:
        print("\n🎉 TESTE WAIST_YAW CONCLUÍDO!")
        print("📋 Agora sabemos se é possível controlar apenas o quadril!")
    else:
        print("\n❌ Teste falhou ou foi interrompido")

if __name__ == "__main__":
    main()
