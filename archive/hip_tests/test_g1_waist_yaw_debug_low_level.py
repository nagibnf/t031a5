#!/usr/bin/env python3
"""
Teste Baixo Nível: WAIST_YAW (ID 12) - Modo Debugging
=====================================================

Este teste tenta controlar a junta WAIST_YAW em baixo nível
usando o modo debugging do G1.
"""

import time
import sys
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient
from unitree_sdk2py.comm.motion_switcher.motion_switcher_client import MotionSwitcherClient

class G1WaistYawDebugTest:
    """Teste de baixo nível da junta WAIST_YAW em modo debugging."""
    
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
    
    def put_robot_in_debug_mode(self):
        """Tenta colocar o robô em modo debugging programaticamente."""
        print("\n🔧 COLOCANDO ROBÔ EM MODO DEBUGGING")
        print("=" * 50)
        
        # Verificar estado atual
        current_mode, current_form = self.check_robot_state()
        print(f"🤖 Estado atual: {current_mode}, {current_form}")
        
        # Tentar colocar em modo debugging usando FSM
        print("🔧 Tentando colocar em modo debugging...")
        
        try:
            # Tentar diferentes FSM IDs que podem ser debugging
            debug_fsm_ids = [5, 6, 7, 8, 9, 10]  # Possíveis IDs de debugging
            
            for fsm_id in debug_fsm_ids:
                print(f"   🔧 Tentando FSM ID: {fsm_id}")
                result = self.loco_client.SetFsmId(fsm_id)
                if result == 0:
                    print(f"   ✅ FSM ID {fsm_id} definido")
                    time.sleep(2)  # Aguardar mudança
                    
                    # Verificar novo estado
                    new_mode, new_form = self.check_robot_state()
                    print(f"   📊 Novo estado: {new_mode}, {new_form}")
                    
                    if new_mode == "debugging" or new_form == "debugging" or "debug" in str(new_mode).lower():
                        print("   🎉 Robô está em modo debugging!")
                        return True
                    else:
                        print(f"   ⚠️  FSM {fsm_id} não é debugging")
                else:
                    print(f"   ❌ Erro no FSM {fsm_id}: {result}")
            
            # Se não conseguiu com FSM, tentar outros métodos
            print("🔧 Tentando outros métodos para debugging...")
            
            # Tentar SetTaskId para debugging
            for task_id in [99, 100, 101, 102]:  # Possíveis task IDs de debugging
                print(f"   🔧 Tentando TaskId: {task_id}")
                result = self.loco_client.SetTaskId(task_id)
                if result == 0:
                    print(f"   ✅ TaskId {task_id} definido")
                    time.sleep(2)
                    
                    new_mode, new_form = self.check_robot_state()
                    print(f"   📊 Novo estado: {new_mode}, {new_form}")
                    
                    if new_mode == "debugging" or new_form == "debugging" or "debug" in str(new_mode).lower():
                        print("   🎉 Robô está em modo debugging!")
                        return True
                else:
                    print(f"   ❌ Erro no TaskId {task_id}: {result}")
            
            print("⚠️  Não foi possível colocar em modo debugging programaticamente")
            print("   Continuando com o estado atual...")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao tentar modo debugging: {e}")
            return True
    
    def test_waist_yaw_low_level(self):
        """Testa controle de baixo nível da junta WAIST_YAW."""
        print("\n🦴 TESTE BAIXO NÍVEL: WAIST_YAW (ID 12)")
        print("=" * 60)
        print("🎯 Testando controle de baixo nível da junta WAIST_YAW")
        print("👀 OBSERVE se o quadril se move independentemente")
        
        # Verificar estado atual
        current_mode, current_form = self.check_robot_state()
        print(f"🤖 Robô está em modo: {current_mode}, form: {current_form}")
        
        # Colocar em modo debugging
        if not self.put_robot_in_debug_mode():
            print("❌ Não foi possível colocar em modo debugging")
            return False
        
        # Teste 1: Verificar métodos disponíveis em modo debugging
        print("\n1️⃣ TESTE: Verificar métodos em modo debugging")
        print("   🔍 Verificando métodos do LocoClient...")
        
        try:
            methods = [method for method in dir(self.loco_client) if not method.startswith('_')]
            print(f"   📋 Métodos disponíveis: {methods}")
            
            # Procurar por métodos relacionados a juntas
            joint_methods = [m for m in methods if 'joint' in m.lower() or 'waist' in m.lower()]
            print(f"   🔧 Métodos de juntas: {joint_methods}")
            
        except Exception as e:
            print(f"   ❌ Erro ao verificar métodos: {e}")
        
        # Teste 2: Tentar ZeroTorque (pode liberar juntas)
        print("\n2️⃣ TESTE: ZeroTorque (liberar juntas)")
        print("   👀 Observe se as juntas ficam livres...")
        input("   ⏸️  Pressione ENTER para executar ZeroTorque...")
        
        try:
            result = self.loco_client.ZeroTorque()
            if result == 0:
                print("   ✅ ZeroTorque executado")
                time.sleep(3)  # Aguardar efeito
                print("   👀 As juntas ficaram livres? (s/n): ", end="")
                response = input().lower()
                if response in ['s', 'sim', 'y', 'yes']:
                    print("   🎉 Juntas liberadas!")
                else:
                    print("   ❌ Juntas não ficaram livres")
            else:
                print(f"   ❌ Erro no ZeroTorque: {result}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # Teste 3: Tentar SetTaskId (pode ser para controle de juntas)
        print("\n3️⃣ TESTE: SetTaskId (controle de tarefas)")
        print("   👀 Observe se há mudança no comportamento...")
        input("   ⏸️  Pressione ENTER para testar SetTaskId...")
        
        try:
            # Tentar diferentes task IDs
            for task_id in [1, 2, 3, 12]:  # Incluindo 12 (WAIST_YAW)
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
        
        # Teste 4: Tentar SetBalanceMode (pode afetar juntas)
        print("\n4️⃣ TESTE: SetBalanceMode (modo de equilíbrio)")
        print("   👀 Observe se há mudança no controle das juntas...")
        input("   ⏸️  Pressione ENTER para testar SetBalanceMode...")
        
        try:
            # Tentar diferentes modos de equilíbrio
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
        
        # Teste 5: Tentar voltar ao normal
        print("\n5️⃣ TESTE: Voltar ao modo normal")
        print("   👀 Observe se o robô volta ao comportamento normal...")
        input("   ⏸️  Pressione ENTER para voltar ao normal...")
        
        try:
            # Tentar voltar ao modo normal
            result = self.loco_client.SetFsmId(4)  # Get Ready
            if result == 0:
                print("   ✅ Modo normal restaurado")
                time.sleep(3)
                print("   👀 O robô voltou ao normal? (s/n): ", end="")
                response = input().lower()
                if response in ['s', 'sim', 'y', 'yes']:
                    print("   🎉 Robô voltou ao normal!")
                else:
                    print("   ❌ Robô não voltou ao normal")
            else:
                print(f"   ❌ Erro ao voltar ao normal: {result}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # Resumo final
        print("\n📊 RESUMO DO TESTE BAIXO NÍVEL:")
        print("=" * 50)
        print("🤔 É possível controlar WAIST_YAW em baixo nível?")
        print("   Baseado nos testes acima...")
        
        final_response = input("   RESPOSTA FINAL (s/n): ").lower()
        if final_response in ['s', 'sim', 'y', 'yes']:
            print("   🎉 CONCLUSÃO: WAIST_YAW PODE SER CONTROLADO EM BAIXO NÍVEL!")
        else:
            print("   ❌ CONCLUSÃO: WAIST_YAW NÃO PODE SER CONTROLADO EM BAIXO NÍVEL!")
        
        return True
    
    def run_test(self):
        """Executa o teste completo."""
        print("🦴 TESTE BAIXO NÍVEL: WAIST_YAW")
        print("=" * 60)
        print("Este teste tenta controlar WAIST_YAW em baixo nível")
        print("usando modo debugging do G1.")
        print("=" * 60)
        
        if not self.initialize_sdk():
            return False
        
        return self.test_waist_yaw_low_level()

def main():
    """Função principal."""
    print("🦴 TESTE BAIXO NÍVEL: WAIST_YAW")
    print("=" * 60)
    print("⚠️  ATENÇÃO: Este teste usa modo debugging!")
    print("⚠️  Pressione Ctrl+C para interromper a qualquer momento!")
    print("=" * 60)
    
    # Confirmação do usuário
    try:
        response = input("\n🤔 Deseja testar WAIST_YAW em baixo nível? (s/N): ").lower()
        if response not in ['s', 'sim', 'y', 'yes']:
            print("❌ Teste cancelado pelo usuário")
            return
    except KeyboardInterrupt:
        print("\n❌ Teste cancelado")
        return
    
    # Executar teste
    tester = G1WaistYawDebugTest()
    success = tester.run_test()
    
    if success:
        print("\n🎉 TESTE BAIXO NÍVEL CONCLUÍDO!")
        print("📋 Agora sabemos se é possível controlar WAIST_YAW em baixo nível!")
    else:
        print("\n❌ Teste falhou ou foi interrompido")

if __name__ == "__main__":
    main()
