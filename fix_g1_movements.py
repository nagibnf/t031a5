#!/usr/bin/env python3
"""
CORREÇÃO COMPLETA - Sistema de Movimentos G1
Baseado no exemplo oficial do SDK
"""

import time
import sys
from pathlib import Path

# Imports do SDK oficial
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.arm.g1_arm_action_client import G1ArmActionClient
from unitree_sdk2py.g1.arm.g1_arm_action_client import action_map

class G1MovementSystem:
    """Sistema de movimentos G1 corrigido - usando API oficial."""
    
    def __init__(self, interface="eth0"):
        self.interface = interface
        self.client = None
        
        # Mapeamento CORRETO dos movimentos
        self.available_movements = {
            "release_arm": "release arm",
            "two_hand_kiss": "two-hand kiss", 
            "left_kiss": "left kiss",
            "right_kiss": "right kiss",
            "hands_up": "hands up",
            "clap": "clap",
            "high_five": "high five", 
            "hug": "hug",
            "heart": "heart",
            "right_heart": "right heart",
            "reject": "reject",
            "right_hand_up": "right hand up",
            "ultraman_ray": "x-ray",  # x-ray é o ultraman ray
            "face_wave": "face wave",
            "high_wave": "high wave", 
            "shake_hand": "shake hand"
        }
    
    def initialize(self) -> bool:
        """Inicializa sistema usando API oficial."""
        try:
            print(f"🔧 Inicializando canal DDS com interface {self.interface}...")
            ChannelFactoryInitialize(0, self.interface)
            
            print("🔧 Criando G1ArmActionClient...")
            self.client = G1ArmActionClient()
            self.client.SetTimeout(10.0)
            self.client.Init()
            
            print("✅ Sistema inicializado com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            return False
    
    def execute_movement(self, movement_name: str) -> bool:
        """Executa movimento usando API oficial."""
        try:
            if movement_name not in self.available_movements:
                print(f"❌ Movimento '{movement_name}' não disponível")
                return False
            
            action_name = self.available_movements[movement_name]
            action_id = action_map.get(action_name)
            
            if action_id is None:
                print(f"❌ ID não encontrado para '{action_name}'")
                return False
            
            print(f"🤚 Executando '{movement_name}' (ID: {action_id})...")
            result = self.client.ExecuteAction(action_id)
            
            success = result == 0
            print(f"{'✅' if success else '❌'} Movimento: {movement_name}")
            return success
            
        except Exception as e:
            print(f"❌ Erro executando movimento: {e}")
            return False
    
    def list_movements(self):
        """Lista todos os movimentos disponíveis."""
        print("\n📋 MOVIMENTOS DISPONÍVEIS:")
        for key, name in self.available_movements.items():
            action_id = action_map.get(name, "N/A")
            print(f"  {key:15} -> '{name}' (ID: {action_id})")
    
    def test_all_movements(self):
        """Testa todos os movimentos sequencialmente."""
        print("\n🎯 TESTANDO TODOS OS MOVIMENTOS...")
        
        for movement_key in self.available_movements.keys():
            print(f"\n--- Testando {movement_key} ---")
            
            # Sempre relaxar antes
            self.execute_movement("release_arm")
            time.sleep(1)
            
            # Executar movimento
            success = self.execute_movement(movement_key)
            time.sleep(3)  # Aguardar movimento completar
            
            # Relaxar depois
            self.execute_movement("release_arm") 
            time.sleep(1)
            
            input(f"Movimento {movement_key}: {'✅' if success else '❌'}. Pressione Enter para continuar...")

def main():
    """Função principal."""
    print("🎯 SISTEMA DE MOVIMENTOS G1 - VERSÃO CORRIGIDA")
    print("=" * 60)
    
    # Criar sistema
    movement_system = G1MovementSystem("eth0")
    
    # Inicializar
    if not movement_system.initialize():
        print("❌ Falha na inicialização")
        return
    
    # Listar movimentos
    movement_system.list_movements()
    
    print(f"\n🎯 OPÇÕES:")
    print("1. Testar movimento específico")
    print("2. Testar TODOS os movimentos")
    print("3. Sair")
    
    while True:
        choice = input("\nEscolha (1/2/3): ").strip()
        
        if choice == "1":
            movement = input("Nome do movimento: ").strip()
            movement_system.execute_movement(movement)
            time.sleep(2)
            movement_system.execute_movement("release_arm")
            
        elif choice == "2":
            confirm = input("Testar TODOS os movimentos? (y/N): ")
            if confirm.lower() == 'y':
                movement_system.test_all_movements()
                
        elif choice == "3":
            print("👋 Saindo...")
            movement_system.execute_movement("release_arm")
            break
        else:
            print("❌ Opção inválida")

if __name__ == "__main__":
    main()
