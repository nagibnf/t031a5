#!/usr/bin/env python3
"""
Teste Específico: WAIST_YAW (ID 12) - Rotação do Quadril G1
===========================================================

Este teste verifica especificamente a junta WAIST_YAW (ID 12) do G1.
Testa a rotação horizontal do quadril (esquerda/direita).
"""

import time
import sys
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient
from unitree_sdk2py.comm.motion_switcher.motion_switcher_client import MotionSwitcherClient

class G1WaistYawTest:
    """Teste específico da junta WAIST_YAW."""
    
    def __init__(self):
        self.interface = "en11"
        self.loco_client = None
        self.motion_switcher = None
        
    def initialize_sdk(self):
        """Inicializa o SDK."""
        try:
            print("🔧 Inicializando SDK...")
            ChannelFactoryInitialize(0, self.interface)
            
            self.loco_client = LocoClient()
            self.loco_client.SetTimeout(10.0)
            self.loco_client.Init()
            
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
    
    def test_waist_yaw_rotation(self):
        """Testa a rotação WAIST_YAW (ID 12)."""
        print("\n🦴 TESTE ESPECÍFICO: WAIST_YAW (ID 12)")
        print("=" * 50)
        print("🎯 Testando rotação horizontal do quadril")
        print("👀 OBSERVE se o robô gira o quadril para esquerda/direita")
        
        # Verificar estado atual
        current_mode = self.check_robot_state()
        print(f"🤖 Robô está em modo: {current_mode}")
        
        # Teste 1: Rotação para esquerda
        print("\n1️⃣ TESTE: Rotação para ESQUERDA")
        print("   👀 Observe se o quadril gira para a ESQUERDA...")
        input("   ⏸️  Pressione ENTER para testar rotação esquerda...")
        
        try:
            # Tentar rotação para esquerda (vyaw negativo)
            result = self.loco_client.SetVelocity(0.0, 0.0, -0.5)  # Rotação esquerda
            if result == 0:
                print("   ✅ Comando de rotação esquerda enviado")
                time.sleep(3)  # Aguardar movimento
                self.loco_client.StopMove()
                print("   👀 O quadril girou para a ESQUERDA? (s/n): ", end="")
                response = input().lower()
                if response in ['s', 'sim', 'y', 'yes']:
                    print("   🎉 WAIST_YAW FUNCIONOU - Rotação esquerda!")
                else:
                    print("   ❌ WAIST_YAW não funcionou - Rotação esquerda")
            else:
                print(f"   ❌ Erro na rotação esquerda: {result}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # Teste 2: Rotação para direita
        print("\n2️⃣ TESTE: Rotação para DIREITA")
        print("   👀 Observe se o quadril gira para a DIREITA...")
        input("   ⏸️  Pressione ENTER para testar rotação direita...")
        
        try:
            # Tentar rotação para direita (vyaw positivo)
            result = self.loco_client.SetVelocity(0.0, 0.0, 0.5)  # Rotação direita
            if result == 0:
                print("   ✅ Comando de rotação direita enviado")
                time.sleep(3)  # Aguardar movimento
                self.loco_client.StopMove()
                print("   👀 O quadril girou para a DIREITA? (s/n): ", end="")
                response = input().lower()
                if response in ['s', 'sim', 'y', 'yes']:
                    print("   🎉 WAIST_YAW FUNCIONOU - Rotação direita!")
                else:
                    print("   ❌ WAIST_YAW não funcionou - Rotação direita")
            else:
                print(f"   ❌ Erro na rotação direita: {result}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # Teste 3: Rotação sutil
        print("\n3️⃣ TESTE: Rotação SUTIL")
        print("   👀 Observe se o quadril faz rotação sutil...")
        input("   ⏸️  Pressione ENTER para testar rotação sutil...")
        
        try:
            # Tentar rotação sutil
            result = self.loco_client.SetVelocity(0.0, 0.0, 0.1)  # Rotação sutil
            if result == 0:
                print("   ✅ Comando de rotação sutil enviado")
                time.sleep(2)  # Aguardar movimento
                self.loco_client.StopMove()
                print("   👀 O quadril fez rotação SUTIL? (s/n): ", end="")
                response = input().lower()
                if response in ['s', 'sim', 'y', 'yes']:
                    print("   🎉 WAIST_YAW FUNCIONOU - Rotação sutil!")
                else:
                    print("   ❌ WAIST_YAW não funcionou - Rotação sutil")
            else:
                print(f"   ❌ Erro na rotação sutil: {result}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # Teste 4: Parar movimento
        print("\n4️⃣ TESTE: Parar Movimento")
        print("   👀 Observe se o quadril para de girar...")
        input("   ⏸️  Pressione ENTER para parar movimento...")
        
        try:
            result = self.loco_client.StopMove()
            if result == 0:
                print("   ✅ Comando de parar enviado")
                time.sleep(2)  # Aguardar parada
                print("   👀 O quadril PAROU de girar? (s/n): ", end="")
                response = input().lower()
                if response in ['s', 'sim', 'y', 'yes']:
                    print("   🎉 WAIST_YAW FUNCIONOU - Parou corretamente!")
                else:
                    print("   ❌ WAIST_YAW não parou corretamente")
            else:
                print(f"   ❌ Erro ao parar: {result}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # Resumo final
        print("\n📊 RESUMO DO TESTE WAIST_YAW:")
        print("=" * 40)
        print("🤔 A junta WAIST_YAW (ID 12) funciona?")
        print("   Baseado nos testes acima...")
        
        final_response = input("   RESPOSTA FINAL (s/n): ").lower()
        if final_response in ['s', 'sim', 'y', 'yes']:
            print("   🎉 CONCLUSÃO: WAIST_YAW FUNCIONA!")
            print("   ✅ O G1 consegue girar o quadril horizontalmente")
        else:
            print("   ❌ CONCLUSÃO: WAIST_YAW NÃO FUNCIONA!")
            print("   ❌ O G1 não consegue girar o quadril")
        
        return True
    
    def run_test(self):
        """Executa o teste completo."""
        print("🦴 TESTE ESPECÍFICO: WAIST_YAW (ID 12)")
        print("=" * 60)
        print("Este teste verifica especificamente a junta WAIST_YAW")
        print("do quadril do G1 (rotação horizontal).")
        print("=" * 60)
        
        if not self.initialize_sdk():
            return False
        
        return self.test_waist_yaw_rotation()

def main():
    """Função principal."""
    print("🦴 TESTE ESPECÍFICO: WAIST_YAW (ID 12)")
    print("=" * 60)
    print("⚠️  ATENÇÃO: Observe se o robô gira o quadril!")
    print("⚠️  Pressione Ctrl+C para interromper a qualquer momento!")
    print("=" * 60)
    
    # Confirmação do usuário
    try:
        response = input("\n🤔 Deseja testar a junta WAIST_YAW? (s/N): ").lower()
        if response not in ['s', 'sim', 'y', 'yes']:
            print("❌ Teste cancelado pelo usuário")
            return
    except KeyboardInterrupt:
        print("\n❌ Teste cancelado")
        return
    
    # Executar teste
    tester = G1WaistYawTest()
    success = tester.run_test()
    
    if success:
        print("\n🎉 TESTE WAIST_YAW CONCLUÍDO!")
        print("📋 Agora sabemos se a junta WAIST_YAW funciona!")
    else:
        print("\n❌ Teste falhou ou foi interrompido")

if __name__ == "__main__":
    main()
