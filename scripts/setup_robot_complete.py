#!/usr/bin/env python3
"""
Setup Automatizado Completo do Robô G1 (Tobias)
Sistema t031a5 - Configuração Inicial Inteligente

Este script configura completamente o robô desde o zero,
incluindo personalidade, voz, rede, e todas as configurações necessárias.
"""

import os
import sys
import json
import time
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
import platform
import socket

# Cores para output colorido
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def colored_print(message: str, color: str = Colors.OKBLUE, end: str = '\n'):
    """Imprime mensagem colorida."""
    print(f"{color}{message}{Colors.ENDC}", end=end)

def print_header(title: str):
    """Imprime cabeçalho formatado."""
    print()
    colored_print("=" * 60, Colors.HEADER)
    colored_print(f"🤖 {title}", Colors.HEADER + Colors.BOLD)
    colored_print("=" * 60, Colors.HEADER)
    print()

def print_step(step: str, description: str):
    """Imprime etapa do processo."""
    colored_print(f"📋 {step}", Colors.OKCYAN + Colors.BOLD)
    colored_print(f"   {description}", Colors.OKBLUE)

def print_success(message: str):
    """Imprime mensagem de sucesso."""
    colored_print(f"✅ {message}", Colors.OKGREEN)

def print_warning(message: str):
    """Imprime mensagem de aviso."""
    colored_print(f"⚠️  {message}", Colors.WARNING)

def print_error(message: str):
    """Imprime mensagem de erro."""
    colored_print(f"❌ {message}", Colors.FAIL)

def print_info(message: str):
    """Imprime informação."""
    colored_print(f"ℹ️  {message}", Colors.OKBLUE)


class RobotSetupWizard:
    """Assistente de configuração completa do robô."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.config_dir = self.project_root / "config"
        self.scripts_dir = self.project_root / "scripts"
        self.src_dir = self.project_root / "src"
        
        # Configuração coletada
        self.robot_config = {}
        self.network_config = {}
        self.personality_config = {}
        self.voice_config = {}
        self.hardware_config = {}
        
        # Detecção de ambiente
        self.is_jetson = self._detect_jetson()
        self.is_mac = platform.system() == "Darwin"
        self.is_linux = platform.system() == "Linux"
        
    def _detect_jetson(self) -> bool:
        """Detecta se está rodando em Jetson."""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                return 'tegra' in cpuinfo.lower() or 'jetson' in cpuinfo.lower()
        except:
            return False
    
    def run_complete_setup(self):
        """Executa setup completo do robô."""
        try:
            print_header("SETUP COMPLETO DO ROBÔ G1 (TOBIAS)")
            print_info("Este assistente irá configurar completamente o seu robô")
            print_info("Tempo estimado: 10-15 minutos")
            print()
            
            if not self._confirm_start():
                return False
            
            # Etapas do setup
            self._step_1_system_check()
            self._step_2_network_config()
            self._step_3_robot_identity()
            self._step_4_personality_config()
            self._step_5_voice_config()
            self._step_6_hardware_config()
            self._step_7_generate_configs()
            self._step_8_install_dependencies()
            self._step_9_setup_services()
            self._step_10_final_tests()
            
            self._show_setup_summary()
            
            print_header("SETUP CONCLUÍDO COM SUCESSO!")
            print_success("Robô G1 configurado e pronto para uso")
            print_info("Use 'python3 -m t031a5.cli' para iniciar o sistema")
            
            return True
            
        except KeyboardInterrupt:
            print_warning("\nSetup cancelado pelo usuário")
            return False
        except Exception as e:
            print_error(f"Erro durante setup: {e}")
            return False
    
    def _confirm_start(self) -> bool:
        """Confirma início do setup."""
        print_info("Informações do sistema:")
        print(f"  🖥️  Plataforma: {platform.system()} {platform.release()}")
        print(f"  🤖 Jetson detectado: {'Sim' if self.is_jetson else 'Não'}")
        print(f"  📁 Diretório do projeto: {self.project_root}")
        print()
        
        response = input("Deseja continuar com o setup? (s/N): ").strip().lower()
        return response in ['s', 'sim', 'y', 'yes']
    
    def _step_1_system_check(self):
        """Verifica sistema e dependências."""
        print_step("ETAPA 1", "Verificação do Sistema")
        
        # Verifica Python
        python_version = sys.version_info
        if python_version.major == 3 and python_version.minor >= 8:
            print_success(f"Python {python_version.major}.{python_version.minor} ✓")
        else:
            print_error(f"Python 3.8+ necessário (atual: {python_version.major}.{python_version.minor})")
            raise RuntimeError("Versão do Python incompatível")
        
        # Verifica estrutura do projeto
        required_dirs = [self.config_dir, self.scripts_dir, self.src_dir]
        for dir_path in required_dirs:
            if dir_path.exists():
                print_success(f"Diretório {dir_path.name} ✓")
            else:
                print_error(f"Diretório {dir_path.name} não encontrado")
                raise RuntimeError(f"Estrutura do projeto incompleta: {dir_path}")
        
        # Verifica espaço em disco
        total, used, free = shutil.disk_usage(self.project_root)
        free_gb = free // (1024**3)
        if free_gb >= 2:
            print_success(f"Espaço em disco: {free_gb}GB livres ✓")
        else:
            print_warning(f"Pouco espaço em disco: {free_gb}GB")
        
        print_success("Verificação do sistema concluída")
    
    def _step_2_network_config(self):
        """Configura rede e conectividade."""
        print_step("ETAPA 2", "Configuração de Rede")
        
        # Detecta interfaces de rede
        interfaces = self._get_network_interfaces()
        print_info(f"Interfaces detectadas: {', '.join(interfaces)}")
        
        if self.is_jetson:
            # Na Jetson, sempre usar eth0 para G1
            if 'eth0' in interfaces:
                self.network_config['g1_interface'] = 'eth0'
                print_success("Interface G1: eth0 (padrão Jetson)")
            else:
                print_warning("Interface eth0 não encontrada - usando padrão")
                self.network_config['g1_interface'] = 'eth0'
        else:
            # No Mac/Linux, perguntar ou usar padrão
            self.network_config['g1_interface'] = 'eth0'
            print_info("Interface G1: eth0 (modo desenvolvimento)")
        
        # Configuração de IPs
        self.network_config['g1_ip'] = '192.168.123.161'
        self.network_config['jetson_ip'] = '192.168.123.164'
        self.network_config['websim_port'] = 8080
        
        # Teste de conectividade (se em produção)
        if self.is_jetson:
            self._test_network_connectivity()
        
        print_success("Configuração de rede concluída")
    
    def _step_3_robot_identity(self):
        """Configura identidade do robô."""
        print_step("ETAPA 3", "Identidade do Robô")
        
        print_info("Configure a identidade básica do robô:")
        
        # Nome do robô
        default_name = "Tobias"
        robot_name = input(f"Nome do robô [{default_name}]: ").strip()
        self.robot_config['name'] = robot_name if robot_name else default_name
        
        # Modelo
        self.robot_config['model'] = "G1"
        self.robot_config['system'] = "t031a5"
        
        # Localização
        default_location = "Estúdio"
        location = input(f"Localização [{default_location}]: ").strip()
        self.robot_config['location'] = location if location else default_location
        
        # Operador padrão
        default_operator = "Operador"
        operator = input(f"Nome do operador [{default_operator}]: ").strip()
        self.robot_config['operator'] = operator if operator else default_operator
        
        print_success(f"Robô configurado: {self.robot_config['name']} (G1)")
    
    def _step_4_personality_config(self):
        """Configura personalidade do robô."""
        print_step("ETAPA 4", "Personalidade e Comportamento")
        
        print_info("Defina a personalidade do robô:")
        
        # Personalidades pré-definidas
        personalities = {
            '1': {
                'name': 'Amigável Profissional',
                'description': 'Educado, prestativo, focado em tarefas',
                'traits': ['helpful', 'professional', 'focused'],
                'greeting_style': 'formal',
                'interaction_level': 'medium'
            },
            '2': {
                'name': 'Companheiro Casual', 
                'description': 'Descontraído, divertido, sociável',
                'traits': ['friendly', 'humorous', 'social'],
                'greeting_style': 'casual',
                'interaction_level': 'high'
            },
            '3': {
                'name': 'Assistente Técnico',
                'description': 'Preciso, informativo, eficiente',
                'traits': ['precise', 'informative', 'efficient'],
                'greeting_style': 'brief',
                'interaction_level': 'low'
            },
            '4': {
                'name': 'Personalizado',
                'description': 'Configurar manualmente',
                'traits': [],
                'greeting_style': 'custom',
                'interaction_level': 'custom'
            }
        }
        
        print_info("Escolha uma personalidade:")
        for key, personality in personalities.items():
            print(f"  {key}. {personality['name']} - {personality['description']}")
        
        choice = input("Escolha [1-4]: ").strip()
        
        if choice in personalities:
            selected = personalities[choice]
            if choice == '4':
                # Personalidade customizada
                self.personality_config = self._create_custom_personality()
            else:
                self.personality_config = selected.copy()
        else:
            # Padrão se escolha inválida
            self.personality_config = personalities['1'].copy()
        
        # Configurações adicionais
        self._configure_interaction_settings()
        
        print_success(f"Personalidade configurada: {self.personality_config['name']}")
    
    def _step_5_voice_config(self):
        """Configura sistema de voz."""
        print_step("ETAPA 5", "Sistema de Voz")
        
        print_info("Configure o sistema de voz:")
        
        # TTS Provider
        tts_providers = {
            '1': {
                'name': 'G1 Nativo',
                'provider': 'g1_native',
                'description': 'TTS integrado do robô (apenas inglês)',
                'languages': ['en'],
                'quality': 'medium',
                'latency': 'low'
            },
            '2': {
                'name': 'ElevenLabs',
                'provider': 'elevenlabs',
                'description': 'TTS premium com vozes realistas',
                'languages': ['en', 'pt', 'es', 'fr'],
                'quality': 'high',
                'latency': 'medium'
            },
            '3': {
                'name': 'Anker Bluetooth',
                'provider': 'bluetooth_anker',
                'description': 'Caixa Anker via Bluetooth (áudio principal)',
                'languages': ['all'],
                'quality': 'high',
                'latency': 'low'
            },
            '4': {
                'name': 'Sistema Híbrido',
                'provider': 'hybrid',
                'description': 'G1 para alertas + Anker para conversas',
                'languages': ['all'],
                'quality': 'high',
                'latency': 'optimized'
            }
        }
        
        print_info("Escolha o sistema de TTS:")
        for key, provider in tts_providers.items():
            print(f"  {key}. {provider['name']} - {provider['description']}")
        
        tts_choice = input("Escolha [1-4]: ").strip()
        selected_tts = tts_providers.get(tts_choice, tts_providers['4'])
        
        self.voice_config['tts_provider'] = selected_tts['provider']
        self.voice_config['tts_quality'] = selected_tts['quality']
        
        # Configurações específicas
        if selected_tts['provider'] == 'elevenlabs':
            self._configure_elevenlabs()
        elif selected_tts['provider'] == 'hybrid':
            self._configure_hybrid_audio()
        
        # Volume padrão
        default_volume = "80"
        volume = input(f"Volume padrão (0-100) [{default_volume}]: ").strip()
        try:
            self.voice_config['default_volume'] = int(volume) if volume else 80
        except ValueError:
            self.voice_config['default_volume'] = 80
        
        # Idioma principal
        if 'pt' in selected_tts['languages'] or selected_tts['provider'] == 'hybrid':
            lang_choice = input("Idioma principal [en/pt]: ").strip().lower()
            self.voice_config['primary_language'] = lang_choice if lang_choice in ['en', 'pt'] else 'en'
        else:
            self.voice_config['primary_language'] = 'en'
        
        print_success(f"Sistema de voz configurado: {selected_tts['name']}")
    
    def _step_6_hardware_config(self):
        """Configura hardware e sensores."""
        print_step("ETAPA 6", "Configuração de Hardware")
        
        print_info("Configure os sensores e hardware:")
        
        # Câmera principal
        camera_options = {
            '1': {
                'name': 'Logitech HD Pro C920',
                'type': 'usb_camera',
                'resolution': '640x480',
                'fps': 30,
                'temporary': True
            },
            '2': {
                'name': 'Intel RealSense D455',
                'type': 'realsense_d455',
                'resolution': '1280x720',
                'fps': 30,
                'features': ['rgb', 'depth', 'imu']
            },
            '3': {
                'name': 'Sistema Dual',
                'type': 'dual_camera',
                'primary': 'realsense_d455',
                'secondary': 'logitech_c920'
            }
        }
        
        print_info("Escolha a configuração de câmera:")
        for key, camera in camera_options.items():
            status = " (TEMPORÁRIA)" if camera.get('temporary') else ""
            print(f"  {key}. {camera['name']}{status}")
        
        camera_choice = input("Escolha [1-3]: ").strip()
        selected_camera = camera_options.get(camera_choice, camera_options['1'])
        
        self.hardware_config['camera'] = selected_camera
        
        # Motor 2DOF para RealSense
        if selected_camera['type'] in ['realsense_d455', 'dual_camera']:
            self.hardware_config['head_motor'] = {
                'type': '2dof_servo',
                'pan_range': [-90, 90],
                'tilt_range': [-30, 30],
                'enabled': True
            }
        
        # Configurações de áudio
        self.hardware_config['audio'] = {
            'microphone': 'dji_mic_2',
            'speaker_main': 'anker_soundcore',
            'speaker_alerts': 'g1_native',
            'bluetooth_auto_connect': True
        }
        
        # Sensores adicionais
        additional_sensors = input("Ativar sensores Arduino? (GPS, Temp/Humid) [s/N]: ").strip().lower()
        if additional_sensors in ['s', 'sim', 'y', 'yes']:
            self.hardware_config['arduino_sensors'] = {
                'gps': {'enabled': True, 'port': '/dev/ttyUSB0'},
                'temperature_humidity': {'enabled': True, 'sensor': 'DHT22'},
                'light_sensor': {'enabled': True, 'sensor': 'LDR'}
            }
        
        print_success("Configuração de hardware concluída")
    
    def _step_7_generate_configs(self):
        """Gera arquivos de configuração."""
        print_step("ETAPA 7", "Geração de Arquivos de Configuração")
        
        # Cria configuração principal
        main_config = {
            'robot': self.robot_config,
            'network': self.network_config,
            'personality': self.personality_config,
            'voice': self.voice_config,
            'hardware': self.hardware_config,
            'system': {
                'version': '1.0.0',
                'created': time.time(),
                'platform': platform.system(),
                'is_jetson': self.is_jetson,
                'update_frequency': 10.0,
                'log_level': 'INFO',
                'auto_start': True
            },
            'safety': {
                'enable_emergency_stop': True,
                'max_operation_time': 7200,  # 2 horas
                'battery_warning_level': 25.0,
                'battery_critical_level': 15.0,
                'max_speed': 0.5,
                'auto_recovery': True
            },
            'effects': {
                'enable_effects': True,
                'effects_volume': 0.8,
                'context_detection': True,
                'cooldown_enabled': True
            },
            'websim': {
                'enable': True,
                'port': self.network_config['websim_port'],
                'mobile_optimized': True,
                'streaming_enabled': True
            }
        }
        
        # Salva configuração principal
        config_file = self.config_dir / f"g1_{self.robot_config['name'].lower()}_production.json5"
        self._save_config(config_file, main_config)
        print_success(f"Configuração principal salva: {config_file.name}")
        
        # Cria configuração de desenvolvimento
        dev_config = main_config.copy()
        dev_config['system']['log_level'] = 'DEBUG'
        dev_config['network']['g1_interface'] = 'mock'
        dev_config['robot']['mock_mode'] = True
        
        dev_config_file = self.config_dir / f"g1_{self.robot_config['name'].lower()}_development.json5"
        self._save_config(dev_config_file, dev_config)
        print_success(f"Configuração de desenvolvimento salva: {dev_config_file.name}")
        
        # Cria script de inicialização
        self._create_startup_script()
        
        print_success("Arquivos de configuração gerados com sucesso")
    
    def _step_8_install_dependencies(self):
        """Instala dependências necessárias."""
        print_step("ETAPA 8", "Instalação de Dependências")
        
        if not self.is_jetson:
            print_info("Modo desenvolvimento - dependências opcionais")
            return
        
        print_info("Instalando dependências do sistema...")
        
        # Lista de pacotes essenciais
        system_packages = [
            'python3-pip',
            'python3-dev',
            'python3-venv',
            'git',
            'curl',
            'bluetooth',
            'bluez',
            'pulseaudio',
            'alsa-utils'
        ]
        
        try:
            # Atualiza lista de pacotes
            subprocess.run(['sudo', 'apt', 'update'], check=True, capture_output=True)
            print_success("Lista de pacotes atualizada")
            
            # Instala pacotes
            subprocess.run(['sudo', 'apt', 'install', '-y'] + system_packages, 
                         check=True, capture_output=True)
            print_success("Pacotes do sistema instalados")
            
        except subprocess.CalledProcessError as e:
            print_warning(f"Falha na instalação de pacotes: {e}")
        
        # Instala dependências Python
        self._install_python_dependencies()
        
        print_success("Dependências instaladas")
    
    def _step_9_setup_services(self):
        """Configura serviços do sistema."""
        print_step("ETAPA 9", "Configuração de Serviços")
        
        if not self.is_jetson:
            print_info("Modo desenvolvimento - serviços não configurados")
            return
        
        # Configura serviço systemd
        service_content = self._generate_systemd_service()
        service_file = Path('/etc/systemd/system/t031a5-robot.service')
        
        try:
            with open('/tmp/t031a5-robot.service', 'w') as f:
                f.write(service_content)
            
            subprocess.run(['sudo', 'mv', '/tmp/t031a5-robot.service', str(service_file)], check=True)
            subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
            subprocess.run(['sudo', 'systemctl', 'enable', 't031a5-robot'], check=True)
            
            print_success("Serviço systemd configurado")
            
        except Exception as e:
            print_warning(f"Falha na configuração do serviço: {e}")
        
        # Configura Bluetooth
        self._setup_bluetooth()
        
        print_success("Serviços configurados")
    
    def _step_10_final_tests(self):
        """Executa testes finais."""
        print_step("ETAPA 10", "Testes Finais")
        
        print_info("Executando testes de validação...")
        
        # Teste 1: Configuração válida
        try:
            config_file = self.config_dir / f"g1_{self.robot_config['name'].lower()}_production.json5"
            with open(config_file, 'r') as f:
                config = json.load(f)
            print_success("✓ Configuração válida")
        except Exception as e:
            print_error(f"✗ Erro na configuração: {e}")
        
        # Teste 2: Importação do módulo
        try:
            sys.path.insert(0, str(self.src_dir))
            import t031a5
            print_success("✓ Módulo t031a5 importável")
        except Exception as e:
            print_warning(f"✗ Erro na importação: {e}")
        
        # Teste 3: Conectividade (se Jetson)
        if self.is_jetson:
            self._test_final_connectivity()
        
        print_success("Testes finais concluídos")
    
    # ==================== MÉTODOS AUXILIARES ====================
    
    def _get_network_interfaces(self) -> List[str]:
        """Obtém lista de interfaces de rede."""
        try:
            result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True)
            interfaces = []
            for line in result.stdout.split('\n'):
                if ': ' in line and not line.startswith(' '):
                    interface = line.split(': ')[1].split('@')[0]
                    if interface != 'lo':  # Ignora loopback
                        interfaces.append(interface)
            return interfaces
        except:
            return ['eth0', 'wlan0']  # Padrão se falhar
    
    def _test_network_connectivity(self):
        """Testa conectividade de rede."""
        try:
            # Ping para G1
            result = subprocess.run(['ping', '-c', '1', self.network_config['g1_ip']], 
                                  capture_output=True)
            if result.returncode == 0:
                print_success(f"Conectividade com G1 ({self.network_config['g1_ip']}) ✓")
            else:
                print_warning(f"G1 não alcançável em {self.network_config['g1_ip']}")
        except Exception as e:
            print_warning(f"Teste de conectividade falhou: {e}")
    
    def _create_custom_personality(self) -> Dict[str, Any]:
        """Cria personalidade customizada."""
        print_info("Configuração de personalidade customizada:")
        
        name = input("Nome da personalidade: ").strip()
        if not name:
            name = "Personalizada"
        
        # Traits
        print_info("Escolha características (separadas por vírgula):")
        print("  Exemplos: friendly, professional, humorous, precise, social, quiet")
        traits_input = input("Características: ").strip()
        traits = [t.strip() for t in traits_input.split(',') if t.strip()]
        
        # Estilo de cumprimento
        greeting_styles = {'1': 'formal', '2': 'casual', '3': 'brief'}
        print_info("Estilo de cumprimento: 1=Formal, 2=Casual, 3=Breve")
        greeting_choice = input("Escolha [1-3]: ").strip()
        greeting_style = greeting_styles.get(greeting_choice, 'casual')
        
        # Nível de interação
        interaction_levels = {'1': 'low', '2': 'medium', '3': 'high'}
        print_info("Nível de interação: 1=Baixo, 2=Médio, 3=Alto")
        interaction_choice = input("Escolha [1-3]: ").strip()
        interaction_level = interaction_levels.get(interaction_choice, 'medium')
        
        return {
            'name': name,
            'description': f'Personalidade customizada: {name}',
            'traits': traits,
            'greeting_style': greeting_style,
            'interaction_level': interaction_level
        }
    
    def _configure_interaction_settings(self):
        """Configura configurações de interação."""
        # Conversação contínua
        continuous = input("Ativar escuta conversacional contínua? [s/N]: ").strip().lower()
        self.personality_config['continuous_listening'] = continuous in ['s', 'sim', 'y', 'yes']
        
        # Comentários contextuais
        contextual = input("Ativar comentários sobre ambiente/pessoas? [s/N]: ").strip().lower()
        self.personality_config['contextual_comments'] = contextual in ['s', 'sim', 'y', 'yes']
        
        # Frequência de atualização
        try:
            freq = input("Frequência de atualização (Hz) [10]: ").strip()
            self.personality_config['update_frequency'] = float(freq) if freq else 10.0
        except ValueError:
            self.personality_config['update_frequency'] = 10.0
    
    def _configure_elevenlabs(self):
        """Configura ElevenLabs TTS."""
        print_info("Configuração ElevenLabs:")
        print_warning("Você precisará adicionar a API key no arquivo .env")
        
        # Voice ID
        voice_id = input("Voice ID ElevenLabs [padrão]: ").strip()
        self.voice_config['elevenlabs_voice_id'] = voice_id if voice_id else 'default'
        
        # Modelo
        model = input("Modelo [eleven_multilingual_v2]: ").strip()
        self.voice_config['elevenlabs_model'] = model if model else 'eleven_multilingual_v2'
    
    def _configure_hybrid_audio(self):
        """Configura sistema híbrido de áudio."""
        print_info("Sistema Híbrido configurado:")
        print("  - G1 TTS: Alertas do sistema em inglês")
        print("  - Anker Bluetooth: Conversas e efeitos sonoros")
        
        self.voice_config['hybrid_config'] = {
            'alerts_provider': 'g1_native',
            'conversation_provider': 'bluetooth_anker',
            'effects_provider': 'bluetooth_anker',
            'auto_switch': True
        }
    
    def _save_config(self, file_path: Path, config: Dict[str, Any]):
        """Salva configuração em arquivo JSON5."""
        # JSON5 não está disponível por padrão, usar JSON normal
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def _create_startup_script(self):
        """Cria script de inicialização."""
        startup_script = f"""#!/bin/bash
# Script de Inicialização do Robô {self.robot_config['name']} (G1)
# Sistema t031a5 - Gerado automaticamente

set -e

echo "🤖 Iniciando robô {self.robot_config['name']}..."

# Diretório do projeto
PROJECT_ROOT="{self.project_root}"
cd "$PROJECT_ROOT"

# Ativa ambiente virtual se existir
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Ambiente virtual ativado"
fi

# Configura PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"

# Configura interface de rede
export G1_INTERFACE="{self.network_config['g1_interface']}"

# Verifica configuração
CONFIG_FILE="config/g1_{self.robot_config['name'].lower()}_production.json5"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Arquivo de configuração não encontrado: $CONFIG_FILE"
    exit 1
fi

echo "✅ Configuração encontrada: $CONFIG_FILE"

# Inicia sistema
echo "🚀 Iniciando sistema t031a5..."
python3 -m t031a5.cli --config "$CONFIG_FILE" --robot-name "{self.robot_config['name']}"

echo "🛑 Sistema finalizado"
"""
        
        script_file = self.scripts_dir / f"start_{self.robot_config['name'].lower()}.sh"
        with open(script_file, 'w') as f:
            f.write(startup_script)
        
        # Torna executável
        script_file.chmod(0o755)
        print_success(f"Script de inicialização criado: {script_file.name}")
    
    def _install_python_dependencies(self):
        """Instala dependências Python."""
        requirements = [
            'asyncio',
            'websockets',
            'aiohttp',
            'numpy',
            'opencv-python',
            'pyaudio',
            'pynmea2',
            'pyserial',
            'bluetooth-python' if self.is_linux else None,
            'face-recognition' if self.is_jetson else None,
        ]
        
        # Remove None values
        requirements = [req for req in requirements if req]
        
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + requirements, 
                         check=True, capture_output=True)
            print_success("Dependências Python instaladas")
        except subprocess.CalledProcessError as e:
            print_warning(f"Algumas dependências falharam: {e}")
    
    def _generate_systemd_service(self) -> str:
        """Gera arquivo de serviço systemd."""
        return f"""[Unit]
Description=Robô {self.robot_config['name']} (G1) - Sistema t031a5
After=network.target bluetooth.target
Wants=network.target bluetooth.target

[Service]
Type=simple
User=unitree
Group=unitree
WorkingDirectory={self.project_root}
Environment=PYTHONPATH={self.project_root}/src
Environment=G1_INTERFACE={self.network_config['g1_interface']}
ExecStart={self.project_root}/scripts/start_{self.robot_config['name'].lower()}.sh
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
    
    def _setup_bluetooth(self):
        """Configura Bluetooth."""
        try:
            # Habilita Bluetooth
            subprocess.run(['sudo', 'systemctl', 'enable', 'bluetooth'], check=True)
            subprocess.run(['sudo', 'systemctl', 'start', 'bluetooth'], check=True)
            print_success("Bluetooth habilitado")
            
            # TODO: Adicionar pareamento automático da Anker Soundcore
            print_info("Lembre-se de parear manualmente a Anker Soundcore")
            
        except Exception as e:
            print_warning(f"Configuração Bluetooth falhou: {e}")
    
    def _test_final_connectivity(self):
        """Testa conectividade final."""
        # Ping para G1
        try:
            result = subprocess.run(['ping', '-c', '1', '-W', '2', self.network_config['g1_ip']], 
                                  capture_output=True)
            if result.returncode == 0:
                print_success("✓ Conectividade com G1")
            else:
                print_warning("✗ G1 não alcançável")
        except:
            print_warning("✗ Teste de conectividade falhou")
    
    def _show_setup_summary(self):
        """Mostra resumo da configuração."""
        print_header("RESUMO DA CONFIGURAÇÃO")
        
        print_info("🤖 ROBÔ:")
        print(f"   Nome: {self.robot_config['name']}")
        print(f"   Modelo: {self.robot_config['model']}")
        print(f"   Localização: {self.robot_config['location']}")
        print(f"   Operador: {self.robot_config['operator']}")
        
        print_info("🌐 REDE:")
        print(f"   Interface G1: {self.network_config['g1_interface']}")
        print(f"   IP G1: {self.network_config['g1_ip']}")
        print(f"   IP Jetson: {self.network_config['jetson_ip']}")
        print(f"   Porta WebSim: {self.network_config['websim_port']}")
        
        print_info("🎭 PERSONALIDADE:")
        print(f"   Tipo: {self.personality_config['name']}")
        print(f"   Estilo: {self.personality_config['greeting_style']}")
        print(f"   Interação: {self.personality_config['interaction_level']}")
        print(f"   Escuta contínua: {self.personality_config.get('continuous_listening', False)}")
        
        print_info("🗣️ VOZ:")
        print(f"   Provider: {self.voice_config['tts_provider']}")
        print(f"   Volume: {self.voice_config['default_volume']}%")
        print(f"   Idioma: {self.voice_config['primary_language']}")
        
        print_info("🔧 HARDWARE:")
        print(f"   Câmera: {self.hardware_config['camera']['name']}")
        print(f"   Áudio: {self.hardware_config['audio']['speaker_main']}")
        if 'arduino_sensors' in self.hardware_config:
            print(f"   Sensores Arduino: Ativados")
        
        print_info("📁 ARQUIVOS CRIADOS:")
        config_file = f"g1_{self.robot_config['name'].lower()}_production.json5"
        script_file = f"start_{self.robot_config['name'].lower()}.sh"
        print(f"   Configuração: config/{config_file}")
        print(f"   Script: scripts/{script_file}")
        
        if self.is_jetson:
            print(f"   Serviço: /etc/systemd/system/t031a5-robot.service")


def main():
    """Função principal."""
    try:
        wizard = RobotSetupWizard()
        success = wizard.run_complete_setup()
        
        if success:
            print()
            print_header("PRÓXIMOS PASSOS")
            print_info("1. Verifique o arquivo .env com credenciais necessárias")
            print_info("2. Teste a configuração: python3 -m t031a5.cli --test")
            print_info("3. Acesse a interface: http://IP:8080")
            print_info("4. Em produção: sudo systemctl start t031a5-robot")
            print()
            colored_print("🎉 Robô pronto para uso!", Colors.OKGREEN + Colors.BOLD)
        else:
            print_error("Setup não foi concluído")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print_warning("\nSetup cancelado")
        sys.exit(130)
    except Exception as e:
        print_error(f"Erro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
