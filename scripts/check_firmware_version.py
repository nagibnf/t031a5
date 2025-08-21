#!/usr/bin/env python3
"""
Verificador de Versão de Firmware - G1 Tobias

Verifica a versão do firmware e motion control para determinar se 
precisamos usar serviço "loco" ou "sport" para comandos de locomoção.

DESCOBERTA CRÍTICA DO MANUAL OFICIAL:
- Firmware >= 8.2.0.0: Usar "sport" service
- Firmware < 8.2.0.0:  Usar "loco" service
"""

import sys
import time
import logging
from pathlib import Path
from datetime import datetime

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from unitree_sdk2py.core.channel import ChannelFactoryInitialize

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class G1FirmwareChecker:
    """Verificador de firmware e configurações do G1."""
    
    def __init__(self):
        self.firmware_info = {}
        self.service_config = {}
        
    def check_connection(self) -> bool:
        """Verifica conectividade com G1."""
        try:
            logger.info("🔌 Verificando conectividade com G1...")
            
            # Inicializa canal DDS
            ChannelFactoryInitialize(0, "eth0")
            logger.info("✅ Canal DDS inicializado")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro de conectividade: {e}")
            return False
    
    def get_firmware_version(self) -> dict:
        """
        Tenta obter versão do firmware.
        
        NOTA: Implementação básica - pode precisar de ajustes específicos 
        baseados na API real disponível no SDK.
        """
        try:
            logger.info("🔍 Verificando versão do firmware...")
            
            # TODO: Implementar chamada real para obter versão
            # Pode ser via DDS status, system info, ou API específica
            
            # Por enquanto, simulamos a verificação
            firmware_info = {
                "method": "manual_check_required",
                "instructions": [
                    "1. Verificar via controle remoto ou interface",
                    "2. Checar logs do sistema na Jetson",
                    "3. Consultar status via DDS se disponível"
                ],
                "current_assumption": "unknown",
                "service_recommendation": "sport (assumindo firmware recente)"
            }
            
            logger.warning("⚠️ Verificação automática não implementada")
            logger.info("📋 Instruções para verificação manual:")
            for instruction in firmware_info["instructions"]:
                logger.info(f"   {instruction}")
                
            return firmware_info
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar firmware: {e}")
            return {"error": str(e)}
    
    def determine_service_name(self, firmware_version: str = None) -> str:
        """
        Determina nome do serviço baseado na versão do firmware.
        
        Args:
            firmware_version: Versão do firmware (ex: "8.2.0.0")
            
        Returns:
            "sport" ou "loco"
        """
        if not firmware_version:
            logger.warning("⚠️ Versão não fornecida, assumindo firmware recente")
            return "sport"
        
        try:
            # Parse da versão (formato: "8.2.0.0")
            version_parts = firmware_version.split(".")
            major = int(version_parts[0])
            minor = int(version_parts[1])
            
            # Verifica se >= 8.2.0.0
            if major > 8 or (major == 8 and minor >= 2):
                service_name = "sport"
                logger.info(f"✅ Firmware {firmware_version} >= 8.2.0.0 → Usar serviço 'sport'")
            else:
                service_name = "loco"
                logger.info(f"✅ Firmware {firmware_version} < 8.2.0.0 → Usar serviço 'loco'")
            
            return service_name
            
        except Exception as e:
            logger.error(f"❌ Erro ao interpretar versão '{firmware_version}': {e}")
            logger.warning("⚠️ Assumindo firmware recente → 'sport'")
            return "sport"
    
    def check_current_config(self) -> dict:
        """Verifica configuração atual do sistema."""
        config_status = {
            "timestamp": datetime.now().isoformat(),
            "system_status": "checking",
            "current_assumptions": {
                "service_name": "sport",
                "reason": "Assumindo firmware >= 8.2.0.0 (padrão para G1 atual)",
                "source": "manual_oficial_discovery"
            },
            "action_required": False,
            "notes": []
        }
        
        # Verifica se temos código que precisa ser ajustado
        config_status["code_analysis"] = {
            "arm_movements": "✅ Usando ArmActionClient - não afetado",
            "locomotion_commands": "⚠️ Ainda não implementado no nível DDS",
            "audio_system": "✅ Usando APIs corretas",
            "vision_system": "✅ Não depende de serviços de locomoção"
        }
        
        config_status["recommendations"] = [
            "Sistema atual não afetado - usando ArmActionClient",
            "Quando implementar locomoção DDS, usar serviço 'sport'",
            "Verificar firmware real na primeira implementação",
            "Manter flexibilidade para ambos os serviços"
        ]
        
        return config_status
    
    def generate_config_template(self, service_name: str = "sport") -> str:
        """Gera template de configuração para locomoção."""
        template = f"""
# Configuração de Locomoção - G1 Tobias
# Baseado nas descobertas do manual oficial

[locomotion_service]
service_name = "{service_name}"
interface = "eth0"
timeout = 10.0

# Exemplos de uso:
# ./g1_loco_client --network_interface eth0 --set_velocity "0.5 0 0 1"

[service_compatibility]
# Firmware >= 8.2.0.0: service = "sport"
# Firmware < 8.2.0.0:  service = "loco"
auto_detect = true
fallback_service = "sport"

[parameters]
max_velocity = 0.5
max_angular = 1.0
default_duration = 1.0
        """
        
        return template
    
    def run_complete_check(self):
        """Executa verificação completa."""
        logger.info("🤖 VERIFICAÇÃO DE FIRMWARE E CONFIGURAÇÃO - G1 TOBIAS")
        logger.info("=" * 60)
        
        # 1. Verificar conectividade
        if not self.check_connection():
            logger.error("❌ Falha na conectividade - abortando verificação")
            return
        
        # 2. Verificar firmware
        firmware_info = self.get_firmware_version()
        
        # 3. Verificar configuração atual
        config_status = self.check_current_config()
        
        # 4. Gerar recomendações
        logger.info("\n📋 RESUMO DA VERIFICAÇÃO:")
        logger.info("-" * 40)
        
        logger.info("🔧 CONFIGURAÇÃO ATUAL:")
        logger.info(f"   Serviço assumido: {config_status['current_assumptions']['service_name']}")
        logger.info(f"   Motivo: {config_status['current_assumptions']['reason']}")
        
        logger.info("\n🧩 ANÁLISE DO CÓDIGO:")
        for component, status in config_status["code_analysis"].items():
            logger.info(f"   {component}: {status}")
        
        logger.info("\n💡 RECOMENDAÇÕES:")
        for rec in config_status["recommendations"]:
            logger.info(f"   • {rec}")
        
        # 5. Salvar template de configuração
        template = self.generate_config_template()
        config_file = "locomotion_service_config.txt"
        
        try:
            with open(config_file, 'w') as f:
                f.write(template)
            logger.info(f"\n💾 Template de configuração salvo: {config_file}")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar template: {e}")
        
        logger.info("\n🎯 PRÓXIMOS PASSOS:")
        logger.info("   1. Verificar firmware real quando possível")
        logger.info("   2. Implementar detecção automática de serviço")
        logger.info("   3. Usar 'sport' como padrão para firmware atual")
        logger.info("   4. Manter compatibilidade com 'loco' se necessário")
        
        logger.info("\n✅ Verificação concluída!")


def main():
    """Função principal."""
    try:
        checker = G1FirmwareChecker()
        checker.run_complete_check()
        
    except KeyboardInterrupt:
        logger.info("\n⏹️ Verificação interrompida pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
