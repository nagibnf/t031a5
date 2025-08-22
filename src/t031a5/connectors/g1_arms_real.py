# -*- coding: utf-8 -*-
"""
G1 Arms Real Connector
Implementação real usando SDK G1ArmActionClient
TESTE 8: Conexão direta com hardware G1
"""

import asyncio
import logging
import sys
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

class G1ArmsRealConnector:
    """
    Connector real para movimentos de braços G1
    
    Usa SDK G1ArmActionClient para comandos físicos reais.
    MÉTODO VALIDADO: ExecuteAction() com action_map
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.enabled = config.get("enabled", True)
        self.network_interface = config.get("network_interface", "eth0")
        self.timeout = config.get("timeout", 10.0)
        
        # Estado do connector
        self.is_initialized = False
        self.arm_client = None
        
        # Mapeamento de gestos para action_map
        self.gesture_map = {
            "wave": "high wave",
            "clap": "clap", 
            "hello": "face wave",
            "shake_hand": "shake hand",
            "high_five": "high five",
            "hug": "hug",
            "heart": "heart",
            "hands_up": "hands up",
            "kiss": "right kiss",
            "release": "release arm"
        }
        
        logger.info(f"G1ArmsRealConnector inicializado: enabled={self.enabled}")
    
    async def initialize(self) -> bool:
        """
        Inicializa o connector G1 Arms real
        
        Returns:
            True se inicialização foi bem-sucedida
        """
        if not self.enabled:
            logger.warning("G1ArmsRealConnector desabilitado")
            return False
        
        try:
            logger.info("Inicializando G1ArmActionClient...")
            
            # Adicionar SDK ao path
            sdk_path = Path(__file__).parent.parent.parent.parent / "unitree_sdk2_python"
            if str(sdk_path) not in sys.path:
                sys.path.insert(0, str(sdk_path))
            
            # Importar SDK G1
            from unitree_sdk2py.core.channel import ChannelFactoryInitialize
            from unitree_sdk2py.g1.arm.g1_arm_action_client import G1ArmActionClient, action_map
            
            # Inicializar canal de comunicação
            ChannelFactoryInitialize(0, self.network_interface)
            
            # Criar e inicializar cliente G1
            self.arm_client = G1ArmActionClient()
            self.arm_client.SetTimeout(self.timeout)
            self.arm_client.Init()
            
            # Armazenar action_map para uso posterior
            self.action_map = action_map
            
            self.is_initialized = True
            logger.info("✅ G1ArmActionClient inicializado com sucesso")
            return True
            
        except ImportError as e:
            logger.error(f"Erro ao importar SDK G1: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro na inicialização G1Arms: {e}")
            return False
    
    async def execute_gesture(self, gesture_name: str, duration: float = 3.0) -> bool:
        """
        Executa gesto usando SDK real
        
        Args:
            gesture_name: Nome do gesto (wave, clap, hello, etc.)
            duration: Duração em segundos (para sleep)
            
        Returns:
            True se comando foi executado com sucesso
        """
        if not self.is_initialized or not self.arm_client:
            logger.error("G1ArmsRealConnector não inicializado")
            return False
        
        try:
            # Mapear gesto para action_map
            action_name = self.gesture_map.get(gesture_name, gesture_name)
            
            if action_name not in self.action_map:
                logger.error(f"Gesto não encontrado no action_map: {action_name}")
                available = list(self.action_map.keys())
                logger.info(f"Gestos disponíveis: {available}")
                return False
            
            logger.info(f"Executando gesto G1: {gesture_name} -> {action_name}")
            
            # EXECUTAR COMANDO REAL NO HARDWARE G1
            self.arm_client.ExecuteAction(self.action_map.get(action_name))
            
            logger.info(f"✅ Comando G1 enviado: {action_name}")
            
            # Aguardar execução (sem bloquear async)
            await asyncio.sleep(duration)
            
            # Comando release automático para alguns gestos
            if gesture_name in ["shake_hand", "high_five", "hug", "heart", "hands_up"]:
                logger.info("Enviando comando release automático...")
                self.arm_client.ExecuteAction(self.action_map.get("release arm"))
                await asyncio.sleep(1.0)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na execução do gesto {gesture_name}: {e}")
            return False
    
    async def release_arms(self) -> bool:
        """
        Libera os braços (posição relaxada)
        
        Returns:
            True se comando foi executado com sucesso
        """
        if not self.is_initialized or not self.arm_client:
            logger.error("G1ArmsRealConnector não inicializado")
            return False
        
        try:
            logger.info("Executando release arms...")
            self.arm_client.ExecuteAction(self.action_map.get("release arm"))
            logger.info("✅ Arms released")
            return True
            
        except Exception as e:
            logger.error(f"Erro no release arms: {e}")
            return False
    
    def get_available_gestures(self) -> List[str]:
        """
        Retorna lista de gestos disponíveis
        
        Returns:
            Lista de nomes de gestos
        """
        return list(self.gesture_map.keys())
    
    def get_available_actions(self) -> List[str]:
        """
        Retorna lista de ações do action_map
        
        Returns:
            Lista de ações SDK disponíveis
        """
        if hasattr(self, 'action_map'):
            return list(self.action_map.keys())
        return []
    
    async def cleanup(self):
        """Limpeza do connector"""
        if self.arm_client:
            try:
                # Release final
                await self.release_arms()
            except:
                pass
        
        self.is_initialized = False
        self.arm_client = None
        logger.info("G1ArmsRealConnector cleanup concluído")
