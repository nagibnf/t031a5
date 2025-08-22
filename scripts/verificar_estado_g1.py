#!/usr/bin/env python3
"""
Verificação Automática do Estado G1 Tobias
SEMPRE executar antes de qualquer operação com o robô
"""

import sys
import subprocess
import logging
from pathlib import Path

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VerificadorEstadoG1:
    """Verifica automaticamente o estado do G1 e orienta o usuário."""
    
    def __init__(self):
        self.g1_ip = "192.168.123.161"
        self.estados_necessarios = {
            "POWER": "Robô ligado fisicamente",
            "DAMPING": "L2 + B (modo amortecimento)",
            "READY": "L2 + ↑ (modo pronto)", 
            "CONTROL": "R1 + X (modo controle SDK)"
        }
    
    def verificar_conectividade(self) -> bool:
        """Verifica se G1 está respondendo na rede - MÉTODO TESTADO."""
        logger.info("🌐 Verificando conectividade G1...")
        
        try:
            # Usar G1NetworkConnector testado
            from t031a5.connectors.g1_network import G1NetworkConnector
            
            network = G1NetworkConnector({
                "g1_ip": self.g1_ip,
                "jetson_ip": "192.168.123.164",
                "interface": "eth0",
                "enabled": True
            })
            
            # Teste rápido de conectividade (método testado)
            import asyncio
            success = asyncio.run(network.quick_ping())
            
            if success:
                logger.info(f"✅ G1 respondendo em {self.g1_ip} (método testado)")
                return True
            else:
                logger.error(f"❌ G1 não responde em {self.g1_ip}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro na conectividade: {e}")
            # Fallback para ping manual
            try:
                result = subprocess.run(
                    ["ping", "-c", "1", self.g1_ip], 
                    capture_output=True, 
                    timeout=5
                )
                return result.returncode == 0
            except:
                return False
    
    def verificar_modo_control(self) -> tuple[bool, str]:
        """Verifica se G1 está em modo CONTROL."""
        logger.info("🤖 Verificando modo CONTROL do G1...")
        
        try:
            from unitree_sdk2py.core.channel import ChannelFactoryInitialize
            from unitree_sdk2py.g1.arm.g1_arm_action_client import G1ArmActionClient
            
            # Inicializar canal
            ChannelFactoryInitialize(0, "eth0")
            
            # Criar cliente
            client = G1ArmActionClient()
            client.SetTimeout(10.0)
            client.Init()
            
            # Teste movimento básico (relaxar)
            result = client.ExecuteAction(99)
            
            if result == 0:
                logger.info("✅ G1 está em modo CONTROL - movimento OK")
                return True, "CONTROL_OK"
            else:
                logger.warning(f"⚠️ G1 não está em modo CONTROL - erro {result}")
                return False, f"MOVIMENTO_FALHOU_{result}"
                
        except Exception as e:
            logger.error(f"❌ Erro ao verificar modo CONTROL: {e}")
            return False, f"ERRO_SDK_{str(e)[:50]}"
    
    def orientar_ativacao(self) -> str:
        """Fornece orientações para ativação do G1."""
        orientacao = """
🤖 PROCEDIMENTO PARA ATIVAR G1 TOBIAS:

1. 🔌 POWER: Pressione botão físico para ligar
2. 🛡️ DAMPING: L2 + B (modo amortecimento - robô fica seguro)
3. 🟢 READY: L2 + ↑ (seta para cima - robô pronto)
4. 🎮 CONTROL: R1 + X (modo controle SDK - CRÍTICO!)

⚠️ IMPORTANTE:
- Robô deve estar DE PÉ ou SUSPENSO antes de ativar
- Sem modo CONTROL o SDK não funcionará
- Sempre confirme que chegou no modo CONTROL antes de usar

🔍 Após ativação, execute este script novamente para validar.
"""
        return orientacao
    
    def verificacao_completa(self) -> dict:
        """Executa verificação completa do estado G1."""
        logger.info("🔍 INICIANDO VERIFICAÇÃO COMPLETA DO G1...")
        logger.info("="*60)
        
        resultado = {
            "conectividade": False,
            "modo_control": False,
            "status_geral": "ERRO",
            "detalhes": "",
            "orientacao": ""
        }
        
        # 1. Verificar conectividade
        if not self.verificar_conectividade():
            resultado["detalhes"] = "G1 não responde na rede"
            resultado["orientacao"] = "Verificar se G1 está ligado e conectado na rede"
            return resultado
        
        resultado["conectividade"] = True
        
        # 2. Verificar modo CONTROL
        control_ok, detalhes = self.verificar_modo_control()
        resultado["modo_control"] = control_ok
        resultado["detalhes"] = detalhes
        
        if control_ok:
            resultado["status_geral"] = "PRONTO"
            resultado["orientacao"] = "G1 está pronto para uso!"
            logger.info("🎉 G1 ESTÁ PRONTO PARA OPERAÇÃO!")
        else:
            resultado["status_geral"] = "PRECISA_ATIVACAO"
            resultado["orientacao"] = self.orientar_ativacao()
            logger.warning("⚠️ G1 PRECISA SER ATIVADO EM MODO CONTROL")
            print(resultado["orientacao"])
        
        logger.info("="*60)
        return resultado

def main():
    """Função principal - executa verificação automática."""
    verificador = VerificadorEstadoG1()
    resultado = verificador.verificacao_completa()
    
    # Retorna código de saída para scripts
    if resultado["status_geral"] == "PRONTO":
        sys.exit(0)  # Sucesso
    else:
        sys.exit(1)  # Precisa ação do usuário

if __name__ == "__main__":
    main()
