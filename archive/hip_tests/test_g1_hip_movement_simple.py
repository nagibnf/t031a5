#!/usr/bin/env python3
"""
Teste Simples: O G1 Consegue Mover o Quadril?
=============================================

Este teste verifica se o robô G1 consegue mover o quadril ou não.
Teste direto e simples para confirmar a capacidade de movimento do quadril.
"""

import time
import sys
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient
from unitree_sdk2py.g1.arm.g1_arm_action_client import G1ArmActionClient
from unitree_sdk2py.comm.motion_switcher.motion_switcher_client import MotionSwitcherClient

class G1HipMovementSimpleTest:
    """Teste simples de movimento do quadril."""
    
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
    
    def test_hip_movement_simple(self):
        """Teste simples: o robô consegue mover o quadril?"""
        print("\n🦴 TESTE SIMPLES: O G1 CONSEGUE MOVER O QUADRIL?")
        print("=" * 50)
        
        # Verificar estado atual
        current_mode = self.check_robot_state()
        print(f"🤖 Robô está em modo: {current_mode}")
        
        print("\n🎯 Vamos testar se o quadril se move...")
        print("👀 OBSERVE o robô durante os testes!")
        
        # Teste 1: Squat (agachar) - deve mover o quadril
        print("\n1️⃣ TESTE: Squat (Agachar)")
        print("   👀 Observe se o quadril se move para baixo...")
        input("   ⏸️  Pressione ENTER para executar Squat...")
        
        try:
            result = self.loco_client.SetFsmId(2)  # Squat
            if result == 0:
                print("   ✅ Squat executado")
                time.sleep(5)  # Aguardar movimento
                print("   👀 O quadril se moveu? (s/n): ", end="")
                response = input().lower()
                if response in ['s', 'sim', 'y', 'yes']:
                    print("   🎉 QUADRIL SE MOVEU!")
                else:
                    print("   ❌ Quadril não se moveu")
            else:
                print(f"   ❌ Erro no Squat: {result}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # Teste 2: Seat (sentar) - deve mover o quadril
        print("\n2️⃣ TESTE: Seat (Sentar)")
        print("   👀 Observe se o quadril se move para baixo...")
        input("   ⏸️  Pressione ENTER para executar Seat...")
        
        try:
            result = self.loco_client.SetFsmId(3)  # Seat
            if result == 0:
                print("   ✅ Seat executado")
                time.sleep(5)  # Aguardar movimento
                print("   👀 O quadril se moveu? (s/n): ", end="")
                response = input().lower()
                if response in ['s', 'sim', 'y', 'yes']:
                    print("   🎉 QUADRIL SE MOVEU!")
                else:
                    print("   ❌ Quadril não se moveu")
            else:
                print(f"   ❌ Erro no Seat: {result}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # Teste 3: Get Ready (voltar ao normal)
        print("\n3️⃣ TESTE: Get Ready (Voltar ao normal)")
        print("   👀 Observe se o quadril volta à posição normal...")
        input("   ⏸️  Pressione ENTER para executar Get Ready...")
        
        try:
            result = self.loco_client.SetFsmId(4)  # Get Ready
            if result == 0:
                print("   ✅ Get Ready executado")
                time.sleep(5)  # Aguardar movimento
                print("   👀 O quadril voltou ao normal? (s/n): ", end="")
                response = input().lower()
                if response in ['s', 'sim', 'y', 'yes']:
                    print("   🎉 QUADRIL VOLTOU AO NORMAL!")
                else:
                    print("   ❌ Quadril não voltou ao normal")
            else:
                print(f"   ❌ Erro no Get Ready: {result}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # Teste 4: Ação de braço que pode mover torso
        print("\n4️⃣ TESTE: Ação de Braço (Right Hand on Heart)")
        print("   👀 Observe se o torso/quadril se move...")
        input("   ⏸️  Pressione ENTER para executar ação...")
        
        try:
            result = self.arm_client.ExecuteAction(33)  # Right Hand on Heart
            if result == 0:
                print("   ✅ Ação executada")
                time.sleep(3)  # Aguardar movimento
                print("   👀 O torso/quadril se moveu? (s/n): ", end="")
                response = input().lower()
                if response in ['s', 'sim', 'y', 'yes']:
                    print("   🎉 TORSO/QUADRIL SE MOVEU!")
                else:
                    print("   ❌ Torso/quadril não se moveu")
                
                # Relaxar braços
                self.arm_client.ExecuteAction(99)
                time.sleep(2)
            else:
                print(f"   ❌ Erro na ação: {result}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # Resumo final
        print("\n📊 RESUMO DO TESTE:")
        print("=" * 30)
        print("🤔 O robô G1 consegue mover o quadril?")
        print("   Baseado nos testes acima...")
        
        final_response = input("   RESPOSTA FINAL (s/n): ").lower()
        if final_response in ['s', 'sim', 'y', 'yes']:
            print("   🎉 CONCLUSÃO: O G1 CONSEGUE MOVER O QUADRIL!")
        else:
            print("   ❌ CONCLUSÃO: O G1 NÃO CONSEGUE MOVER O QUADRIL!")
        
        return True
    
    def run_test(self):
        """Executa o teste completo."""
        print("🦴 TESTE SIMPLES: MOVIMENTO DO QUADRIL G1")
        print("=" * 60)
        print("Este teste verifica se o robô consegue mover o quadril")
        print("ou se ele não move o quadril.")
        print("=" * 60)
        
        if not self.initialize_sdk():
            return False
        
        return self.test_hip_movement_simple()

def main():
    """Função principal."""
    print("🦴 TESTE SIMPLES: O G1 CONSEGUE MOVER O QUADRIL?")
    print("=" * 60)
    print("⚠️  ATENÇÃO: Observe o robô durante os testes!")
    print("⚠️  Pressione Ctrl+C para interromper a qualquer momento!")
    print("=" * 60)
    
    # Confirmação do usuário
    try:
        response = input("\n🤔 Deseja continuar com o teste simples? (s/N): ").lower()
        if response not in ['s', 'sim', 'y', 'yes']:
            print("❌ Teste cancelado pelo usuário")
            return
    except KeyboardInterrupt:
        print("\n❌ Teste cancelado")
        return
    
    # Executar teste
    tester = G1HipMovementSimpleTest()
    success = tester.run_test()
    
    if success:
        print("\n🎉 TESTE SIMPLES CONCLUÍDO!")
        print("📋 Agora sabemos se o G1 consegue mover o quadril ou não!")
    else:
        print("\n❌ Teste falhou ou foi interrompido")

if __name__ == "__main__":
    main()
