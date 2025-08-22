# -*- coding: utf-8 -*-
"""
G1 Movement Real Connector
Implementação real usando SDK LocoClient
TESTE 9: ✅ SUCESSO - Start() + Move() + StopMove()
"""

import asyncio
import logging
import sys
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class G1MovementRealConnector:
    """
    Connector real para movimentos de locomoção G1
    
    Usa SDK LocoClient para comandos físicos reais.
    SEQUÊNCIA VALIDADA: Start() → Move() → StopMove()
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.enabled = config.get("enabled", True)
        self.network_interface = config.get("network_interface", "eth0")
        self.timeout = config.get("timeout", 10.0)
        
        # Configurações de movimento
        self.default_velocity = config.get("default_velocity", 0.5)  # Validado no teste
        self.max_velocity = config.get("max_velocity", 1.0)
        self.default_duration = config.get("default_duration", 2.0)
        
        # Estado do connector
        self.is_initialized = False
        self.is_movement_active = False
        self.loco_client = None
        
        logger.info(f"G1MovementRealConnector inicializado: enabled={self.enabled}")
    
    async def initialize(self) -> bool:
        """
        Inicializa o connector G1 Movement real
        
        Returns:
            True se inicialização foi bem-sucedida
        """
        if not self.enabled:
            logger.warning("G1MovementRealConnector desabilitado")
            return False
        
        try:
            logger.info("Inicializando LocoClient...")
            
            # Adicionar SDK ao path
            sdk_path = Path(__file__).parent.parent.parent.parent / "unitree_sdk2_python"
            if str(sdk_path) not in sys.path:
                sys.path.insert(0, str(sdk_path))
            
            # Importar SDK G1
            from unitree_sdk2py.core.channel import ChannelFactoryInitialize
            from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient
            
            # Inicializar canal de comunicação
            ChannelFactoryInitialize(0, self.network_interface)
            
            # Criar e inicializar cliente LocoClient
            self.loco_client = LocoClient()
            self.loco_client.SetTimeout(self.timeout)
            self.loco_client.Init()
            
            self.is_initialized = True
            logger.info("✅ LocoClient inicializado com sucesso")
            return True
            
        except ImportError as e:
            logger.error(f"Erro ao importar SDK G1: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro na inicialização G1Movement: {e}")
            return False
    
    async def activate_movement_mode(self) -> bool:
        """
        Ativa modo de movimento - MÉTODO VALIDADO
        
        Returns:
            True se ativação foi bem-sucedida
        """
        if not self.is_initialized or not self.loco_client:
            logger.error("G1MovementRealConnector não inicializado")
            return False
        
        try:
            logger.info("Ativando modo movimento: Start()")
            
            # COMANDO VALIDADO NO TESTE 9
            self.loco_client.Start()  # SetFsmId(200)
            
            self.is_movement_active = True
            logger.info("✅ Modo movimento ativado")
            
            # Aguardar ativação
            await asyncio.sleep(1.0)
            return True
            
        except Exception as e:
            logger.error(f"Erro ao ativar modo movimento: {e}")
            return False
    
    async def move_forward(self, velocity: float = None, duration: float = None) -> bool:
        """
        Move robô para frente - MÉTODO VALIDADO
        
        Args:
            velocity: Velocidade em m/s (default: 0.5 validado)
            duration: Duração em segundos (default: 2.0)
            
        Returns:
            True se movimento foi executado com sucesso
        """
        velocity = velocity or self.default_velocity
        duration = duration or self.default_duration
        
        # Validar limites
        velocity = min(velocity, self.max_velocity)
        
        if not self.is_initialized or not self.loco_client:
            logger.error("G1MovementRealConnector não inicializado")
            return False
        
        try:
            # Ativar modo movimento se necessário
            if not self.is_movement_active:
                success = await self.activate_movement_mode()
                if not success:
                    return False
            
            logger.info(f"Executando movimento: velocity={velocity}, duration={duration}")
            
            # COMANDO VALIDADO NO TESTE 9
            self.loco_client.Move(velocity, 0, 0)  # Forward: x=velocity, y=0, rotation=0
            
            # Aguardar duração do movimento
            await asyncio.sleep(duration)
            
            # PARAR SEGURO (não Damp!)
            self.loco_client.StopMove()  # SetVelocity(0,0,0)
            
            logger.info("✅ Movimento forward executado e parado com segurança")
            return True
            
        except Exception as e:
            logger.error(f"Erro no movimento forward: {e}")
            return False
    
    async def move_lateral(self, velocity: float = None, duration: float = None) -> bool:
        """
        Move robô lateralmente
        
        Args:
            velocity: Velocidade lateral em m/s
            duration: Duração em segundos
            
        Returns:
            True se movimento foi executado com sucesso
        """
        velocity = velocity or self.default_velocity
        duration = duration or self.default_duration
        
        if not self.is_initialized or not self.loco_client:
            logger.error("G1MovementRealConnector não inicializado")
            return False
        
        try:
            # Ativar modo movimento se necessário
            if not self.is_movement_active:
                success = await self.activate_movement_mode()
                if not success:
                    return False
            
            logger.info(f"Executando movimento lateral: velocity={velocity}")
            
            self.loco_client.Move(0, velocity, 0)  # Lateral: x=0, y=velocity, rotation=0
            await asyncio.sleep(duration)
            self.loco_client.StopMove()
            
            logger.info("✅ Movimento lateral executado")
            return True
            
        except Exception as e:
            logger.error(f"Erro no movimento lateral: {e}")
            return False
    
    async def rotate(self, angular_velocity: float = None, duration: float = None) -> bool:
        """
        Rotaciona robô
        
        Args:
            angular_velocity: Velocidade angular em rad/s
            duration: Duração em segundos
            
        Returns:
            True se rotação foi executada com sucesso
        """
        angular_velocity = angular_velocity or 0.3  # Velocidade angular padrão
        duration = duration or self.default_duration
        
        if not self.is_initialized or not self.loco_client:
            logger.error("G1MovementRealConnector não inicializado")
            return False
        
        try:
            # Ativar modo movimento se necessário
            if not self.is_movement_active:
                success = await self.activate_movement_mode()
                if not success:
                    return False
            
            logger.info(f"Executando rotação: angular_velocity={angular_velocity}")
            
            self.loco_client.Move(0, 0, angular_velocity)  # Rotation: x=0, y=0, rotation=angular_velocity
            await asyncio.sleep(duration)
            self.loco_client.StopMove()
            
            logger.info("✅ Rotação executada")
            return True
            
        except Exception as e:
            logger.error(f"Erro na rotação: {e}")
            return False
    
    async def stop_movement(self) -> bool:
        """
        Para movimento de forma segura - MÉTODO VALIDADO
        
        Returns:
            True se parada foi executada com sucesso
        """
        if not self.is_initialized or not self.loco_client:
            logger.error("G1MovementRealConnector não inicializado")
            return False
        
        try:
            logger.info("Parando movimento com StopMove()")
            
            # MÉTODO SEGURO VALIDADO (não Damp!)
            self.loco_client.StopMove()  # SetVelocity(0,0,0)
            
            logger.info("✅ Movimento parado com segurança")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao parar movimento: {e}")
            return False
    
    async def cleanup(self):
        """Limpeza do connector"""
        if self.loco_client:
            try:
                # Parar movimento final
                await self.stop_movement()
            except:
                pass
        
        self.is_initialized = False
        self.is_movement_active = False
        self.loco_client = None
        logger.info("G1MovementRealConnector cleanup concluído")
