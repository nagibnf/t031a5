#!/usr/bin/env python3
"""
Teste Simples: Juntas em Modo Debugging
=======================================

Este teste assume que o robô já está em modo debugging
e testa apenas o controle das juntas.
"""

import time
import sys
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient
from unitree_sdk2py.comm.motion_switcher.motion_switcher_client import MotionSwitcherClient

class G1JointsDebugTest:
    """Teste simples das juntas em modo debugging."""
    
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
                return current_mode, current_form
            else:
                print(f"❌ Erro ao verificar estado: {status}, {result}")
                return None, None
                
        except Exception as e:
            print(f"❌ Erro na verificação de estado: {e}")
            return None, None
    
    def test_joints_in_debug_mode(self):
        """Testa as juntas em modo debugging."""
        print("\n🦴 TESTE: JUNTAS EM MODO DEBUGGING")
        print("=" * 50)
        print("🎯 Testando controle das juntas")
        print("👀 OBSERVE se as juntas se movem independentemente")
        
        # Verificar estado atual
        current_mode, current_form = self.check_robot_state()
        print(f"🤖 Robô está em modo: {current_mode}, form: {current_form}")
        
        # Teste 1: Verificar métodos disponíveis
        print("\n1️⃣ TESTE: Verificar métodos disponíveis")
        print("   🔍 Verificando métodos do LocoClient...")
        
        try:
            methods = [method for method in dir(self.loco_client) if not method.startswith('_')]
            print(f"   📋 Métodos disponíveis: {methods}")
            
            # Procurar por métodos relacionados a juntas
            joint_methods = [m for m in methods if 'joint' in m.lower() or 'waist' in m.lower()]
            print(f"   🔧 Métodos de juntas: {joint_methods}")
            
        except Exception as e:
            print(f"   ❌ Erro ao verificar métodos: {e}")
        
        # Teste 2: Tentar SetTaskId para WAIST_YAW
        print("\n2️⃣ TESTE: SetTaskId para WAIST_YAW (ID 12)")
        print("   👀 Observe se o quadril se move...")
        input("   ⏸️  Pressione ENTER para testar WAIST_YAW...")
        
        try:
            result = self.loco_client.SetTaskId(12)  # WAIST_YAW
            if result == 0:
                print("   ✅ TaskId 12 (WAIST_YAW) definido")
                time.sleep(3)
                print("   👀 O quadril se moveu? (s/n): ", end="")
                response = input().lower()
                if response in ['s', 'sim', 'y', 'yes']:
                    print("   🎉 WAIST_YAW funcionou!")
                else:
                    print("   ❌ WAIST_YAW não funcionou")
            else:
                print(f"   ❌ Erro no TaskId 12: {result}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # Teste 3: Tentar outros TaskIds
        print("\n3️⃣ TESTE: Outros TaskIds")
        print("   👀 Observe se há mudanças...")
        input("   ⏸️  Pressione ENTER para testar outros TaskIds...")
        
        try:
            for task_id in [1, 2, 3, 4, 5]:
                print(f"   🔧 Testando TaskId: {task_id}")
                result = self.loco_client.SetTaskId(task_id)
                if result == 0:
                    print(f"   ✅ TaskId {task_id} definido")
                    time.sleep(2)
                    print(f"   👀 Houve mudança com TaskId {task_id}? (s/n): ", end="")
                    response = input().lower()
                    if response in ['s', 'sim', 'y', 'yes']:
                        print(f"   🎉 TaskId {task_id} causou mudança!")
                    else:
                        print(f"   ❌ TaskId {task_id} não causou mudança")
                else:
                    print(f"   ❌ Erro no TaskId {task_id}: {result}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # Teste 4: Tentar SetBalanceMode
        print("\n4️⃣ TESTE: SetBalanceMode")
        print("   👀 Observe se há mudança no controle...")
        input("   ⏸️  Pressione ENTER para testar SetBalanceMode...")
        
        try:
            for mode in [0, 1, 2]:
                print(f"   🔧 Testando BalanceMode: {mode}")
                result = self.loco_client.SetBalanceMode(mode)
                if result == 0:
                    print(f"   ✅ BalanceMode {mode} definido")
                    time.sleep(2)
                    print(f"   👀 Houve mudança com BalanceMode {mode}? (s/n): ", end="")
                    response = input().lower()
                    if response in ['s', 'sim', 'y', 'yes']:
                        print(f"   🎉 BalanceMode {mode} causou mudança!")
                    else:
                        print(f"   ❌ BalanceMode {mode} não causou mudança")
                else:
                    print(f"   ❌ Erro no BalanceMode {mode}: {result}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # Resumo final
        print("\n📊 RESUMO DO TESTE:")
        print("=" * 30)
        print("🤔 É possível controlar juntas em modo debugging?")
        print("   Baseado nos testes acima...")
        
        final_response = input("   RESPOSTA FINAL (s/n): ").lower()
        if final_response in ['s', 'sim', 'y', 'yes']:
            print("   🎉 CONCLUSÃO: JUNTAS PODEM SER CONTROLADAS!")
        else:
            print("   ❌ CONCLUSÃO: JUNTAS NÃO PODEM SER CONTROLADAS!")
        
        return True
    
    def run_test(self):
        """Executa o teste completo."""
        print("🦴 TESTE: JUNTAS EM MODO DEBUGGING")
        print("=" * 60)
        print("Este teste assume que o robô já está em modo debugging")
        print("e testa apenas o controle das juntas.")
        print("=" * 60)
        
        if not self.initialize_sdk():
            return False
        
        return self.test_joints_in_debug_mode()

def main():
    """Função principal."""
    print("🦴 TESTE: JUNTAS EM MODO DEBUGGING")
    print("=" * 60)
    print("⚠️  ATENÇÃO: Coloque o robô em modo debugging primeiro!")
    print("⚠️  Pressione Ctrl+C para interromper a qualquer momento!")
    print("=" * 60)
    
    # Confirmação do usuário
    try:
        response = input("\n🤔 O robô está em modo debugging? (s/N): ").lower()
        if response not in ['s', 'sim', 'y', 'yes']:
            print("❌ Coloque o robô em modo debugging primeiro!")
            return
    except KeyboardInterrupt:
        print("\n❌ Teste cancelado")
        return
    
    # Executar teste
    tester = G1JointsDebugTest()
    success = tester.run_test()
    
    if success:
        print("\n🎉 TESTE CONCLUÍDO!")
        print("📋 Agora sabemos se é possível controlar juntas em modo debugging!")
    else:
        print("\n❌ Teste falhou ou foi interrompido")

if __name__ == "__main__":
    main()
