"""
Conector de rede para comunicação com G1 Tobias no sistema t031a5.
MÉTODO TESTADO E FUNCIONANDO: ping eth0 192.168.123.161
"""

import logging
import subprocess
import socket
import asyncio
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class G1NetworkConnector:
    """Conector de rede para G1 - MÉTODO TESTADO."""
    
    def __init__(self, config: dict):
        self.g1_ip = config.get("g1_ip", "192.168.123.161")
        self.jetson_ip = config.get("jetson_ip", "192.168.123.164")
        self.interface = config.get("interface", "eth0")
        self.ping_timeout = config.get("ping_timeout", 5)
        self.enabled = config.get("enabled", True)
        
        logger.info(f"G1NetworkConnector inicializado: {self.jetson_ip} → {self.g1_ip} via {self.interface}")
    
    async def test_g1_connectivity(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Testa conectividade com G1 Tobias.
        MÉTODO TESTADO: ping -c 3 192.168.123.161 funcionando
        
        Returns:
            Tuple[bool, dict]: (sucesso, dados_conectividade)
        """
        if not self.enabled:
            logger.warning("G1Network desabilitado")
            return False, {}
        
        try:
            start_time = datetime.now()
            
            # MÉTODO TESTADO: Ping para G1 com 3 packets
            logger.info(f"🌐 Testando conectividade G1: {self.g1_ip}")
            
            process = await asyncio.create_subprocess_exec(
                "ping", "-c", "3", self.g1_ip,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=self.ping_timeout + 5
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            if process.returncode == 0:
                # Analisar saída do ping (método testado funcionando)
                ping_output = stdout.decode()
                
                # Extrair estatísticas
                packet_loss = "unknown"
                avg_time = "unknown"
                
                for line in ping_output.split('\n'):
                    if 'packets transmitted' in line:
                        if '0% packet loss' in line:
                            packet_loss = "0%"
                        elif 'packet loss' in line:
                            # Extrair percentual de perda
                            parts = line.split('packet loss')[0].split()
                            if parts:
                                packet_loss = parts[-1]
                    
                    if 'rtt min/avg/max' in line:
                        # Extrair tempo médio
                        parts = line.split('=')
                        if len(parts) > 1:
                            times = parts[1].split('/')
                            if len(times) >= 2:
                                avg_time = times[1] + "ms"
                
                connectivity_data = {
                    "status": "connected",
                    "g1_ip": self.g1_ip,
                    "jetson_ip": self.jetson_ip,
                    "interface": self.interface,
                    "packet_loss": packet_loss,
                    "avg_ping_time": avg_time,
                    "test_duration": duration,
                    "timestamp": start_time,
                    "ping_output": ping_output,
                    "method": "ping_eth0_192.168.123.161_TESTADO"
                }
                
                logger.info(f"✅ G1 conectividade OK: {packet_loss} perda, {avg_time} latência")
                return True, connectivity_data
            
            else:
                # Ping falhou
                error_output = stderr.decode() if stderr else "Unknown error"
                
                connectivity_data = {
                    "status": "disconnected",
                    "g1_ip": self.g1_ip,
                    "error": error_output,
                    "test_duration": duration,
                    "timestamp": start_time,
                    "method": "ping_eth0_TESTADO"
                }
                
                logger.error(f"❌ G1 não responde: {error_output}")
                return False, connectivity_data
                
        except asyncio.TimeoutError:
            logger.error(f"❌ Timeout na conectividade G1 ({self.ping_timeout}s)")
            return False, {"status": "timeout", "error": "Ping timeout"}
        except Exception as e:
            logger.error(f"❌ Erro na conectividade G1: {e}")
            return False, {"status": "error", "error": str(e)}
    
    async def check_interface_status(self) -> Tuple[bool, Dict[str, Any]]:
        """Verifica status da interface eth0."""
        try:
            logger.info(f"🔍 Verificando interface {self.interface}...")
            
            process = await asyncio.create_subprocess_exec(
                "ip", "addr", "show", self.interface,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                output = stdout.decode()
                
                # Verificar se o IP da Jetson está configurado
                if self.jetson_ip in output:
                    interface_data = {
                        "status": "configured",
                        "interface": self.interface,
                        "jetson_ip": self.jetson_ip,
                        "output": output,
                        "method": "ip_addr_show_eth0_TESTADO"
                    }
                    
                    logger.info(f"✅ Interface {self.interface} configurada: {self.jetson_ip}")
                    return True, interface_data
                else:
                    logger.warning(f"⚠️ Interface {self.interface} sem IP esperado")
                    return False, {"status": "misconfigured", "expected_ip": self.jetson_ip}
            else:
                error_output = stderr.decode() if stderr else "Unknown error"
                logger.error(f"❌ Erro na interface {self.interface}: {error_output}")
                return False, {"status": "error", "error": error_output}
                
        except Exception as e:
            logger.error(f"Erro ao verificar interface: {e}")
            return False, {"status": "exception", "error": str(e)}
    
    async def comprehensive_network_test(self) -> Tuple[bool, Dict[str, Any]]:
        """Teste abrangente de rede (interface + conectividade)."""
        try:
            logger.info("🌐 Executando teste abrangente de rede...")
            
            # 1. Verificar interface
            interface_ok, interface_data = await self.check_interface_status()
            
            # 2. Testar conectividade G1
            g1_ok, g1_data = await self.test_g1_connectivity()
            
            # Compilar resultados
            comprehensive_data = {
                "overall_status": "healthy" if (interface_ok and g1_ok) else "degraded",
                "interface_test": interface_data,
                "g1_connectivity_test": g1_data,
                "timestamp": datetime.now(),
                "method": "comprehensive_network_TESTADO"
            }
            
            overall_success = interface_ok and g1_ok
            
            if overall_success:
                logger.info("✅ Rede G1 completamente funcional")
            else:
                logger.warning("⚠️ Rede G1 com problemas")
            
            return overall_success, comprehensive_data
            
        except Exception as e:
            logger.error(f"Erro no teste abrangente: {e}")
            return False, {"status": "exception", "error": str(e)}
    
    async def quick_ping(self) -> bool:
        """Ping rápido para verificação básica."""
        try:
            process = await asyncio.create_subprocess_exec(
                "ping", "-c", "1", self.g1_ip,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            
            await asyncio.wait_for(process.communicate(), timeout=3)
            return process.returncode == 0
            
        except:
            return False
