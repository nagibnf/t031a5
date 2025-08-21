"""
Sistema de Efeitos Sonoros Contextuais para G1 Tobias
Reproduz áudios pré-gravados baseados em contexto e situações
"""

import asyncio
import logging
import os
import random
import time
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class ContextType(Enum):
    """Tipos de contexto para efeitos sonoros."""
    # Pessoas e relacionamentos
    BEAUTIFUL_WOMAN = "beautiful_woman"
    HANDSOME_MAN = "handsome_man"
    CHILDREN = "children"
    ELDERLY = "elderly"
    
    # Despedidas e cumprimentos
    GOODBYE = "goodbye"
    HELLO = "hello"
    INTRODUCTION = "introduction"
    
    # Emoções e reações
    SURPRISE = "surprise"
    APPROVAL = "approval"
    EXCITEMENT = "excitement"
    THINKING = "thinking"
    CONFUSION = "confusion"
    
    # Situações especiais
    COMPLIMENT_RECEIVED = "compliment_received"
    JOKE = "joke"
    MUSIC_DETECTED = "music_detected"
    FOOD_MENTIONED = "food_mentioned"
    
    # Estados do robô
    STARTUP = "startup"
    SHUTDOWN = "shutdown"
    ERROR = "error"
    SUCCESS = "success"


@dataclass
class SoundEffect:
    """Efeito sonoro configurado."""
    name: str
    file_path: str
    context: ContextType
    duration: float
    volume: float = 1.0
    cooldown: float = 30.0  # Segundos antes de poder tocar novamente
    priority: int = 1       # 1=baixa, 5=alta
    enabled: bool = True


@dataclass
class ContextRule:
    """Regra para detecção de contexto."""
    context: ContextType
    keywords: List[str]
    vision_tags: List[str]
    probability_threshold: float = 0.7
    max_frequency: int = 3  # Máximo por sessão


class EffectsManager:
    """Gerenciador de efeitos sonoros contextuais."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o gerenciador de efeitos.
        
        Args:
            config: Configuração do sistema
        """
        self.config = config.get("effects", {})
        self.name = "EffectsManager"
        
        # Caminhos
        self.effects_dir = Path(config.get("audio_base_dir", "audio")) / "effects"
        self.effects_dir.mkdir(parents=True, exist_ok=True)
        
        # Estado
        self.is_initialized = False
        self.effects: Dict[str, SoundEffect] = {}
        self.context_rules: Dict[ContextType, ContextRule] = {}
        self.last_played: Dict[str, float] = {}
        self.session_counts: Dict[ContextType, int] = {}
        
        # Player de áudio (será injetado)
        self.audio_player: Optional[Callable] = None
        
        # Estatísticas
        self.total_played = 0
        self.effects_history: List[Dict[str, Any]] = []
        self.max_history = config.get("max_effects_history", 100)
        
        # Configurações
        self.global_volume = config.get("effects_volume", 0.8)
        self.enable_effects = config.get("enable_effects", True)
        self.max_effect_duration = config.get("max_effect_duration", 10.0)
        
        logger.debug("EffectsManager configurado")
    
    async def initialize(self) -> bool:
        """
        Inicializa o sistema de efeitos.
        
        Returns:
            True se a inicialização foi bem-sucedida
        """
        try:
            logger.info("Inicializando EffectsManager...")
            
            # Configura efeitos padrão
            await self._setup_default_effects()
            
            # Configura regras de contexto
            await self._setup_context_rules()
            
            # Escaneia diretório de efeitos
            await self._scan_effects_directory()
            
            # Reset estatísticas
            self.session_counts.clear()
            self.last_played.clear()
            
            self.is_initialized = True
            
            logger.info(f"EffectsManager inicializado com {len(self.effects)} efeitos")
            return True
            
        except Exception as e:
            logger.error(f"Erro na inicialização do EffectsManager: {e}")
            return False
    
    async def _setup_default_effects(self):
        """Configura efeitos padrão do sistema."""
        default_effects = [
            # Mulher bonita - Carl Whisper
            SoundEffect(
                name="carl_whisper",
                file_path="carl_whisper_10s.wav",
                context=ContextType.BEAUTIFUL_WOMAN,
                duration=10.0,
                volume=0.7,
                cooldown=60.0,
                priority=3
            ),
            
            # Despedida - Terminator
            SoundEffect(
                name="hasta_la_vista",
                file_path="hasta_la_vista_baby.wav", 
                context=ContextType.GOODBYE,
                duration=3.0,
                volume=0.8,
                cooldown=30.0,
                priority=4
            ),
            
            # Surpresa
            SoundEffect(
                name="surprise_effect",
                file_path="surprise_effect.wav",
                context=ContextType.SURPRISE,
                duration=2.0,
                volume=0.6,
                cooldown=20.0,
                priority=2
            ),
            
            # Aprovação/Elogio
            SoundEffect(
                name="nice_compliment",
                file_path="nice_compliment.wav",
                context=ContextType.APPROVAL,
                duration=3.0,
                volume=0.7,
                cooldown=25.0,
                priority=2
            ),
            
            # Empolgação
            SoundEffect(
                name="excited_reaction",
                file_path="excited_reaction.wav",
                context=ContextType.EXCITEMENT,
                duration=4.0,
                volume=0.8,
                cooldown=30.0,
                priority=3
            ),
            
            # Pensando
            SoundEffect(
                name="thinking_hmm",
                file_path="thinking_hmm.wav",
                context=ContextType.THINKING,
                duration=2.5,
                volume=0.5,
                cooldown=15.0,
                priority=1
            ),
            
            # Startup
            SoundEffect(
                name="system_startup",
                file_path="system_startup.wav",
                context=ContextType.STARTUP,
                duration=5.0,
                volume=0.9,
                cooldown=300.0,  # 5 minutos
                priority=5
            ),
            
            # Piada/Risos
            SoundEffect(
                name="evil_laugh",
                file_path="evil-laugh-89423.wav",  # Já existe
                context=ContextType.JOKE,
                duration=3.0,
                volume=0.6,
                cooldown=45.0,
                priority=2
            )
        ]
        
        for effect in default_effects:
            self.effects[effect.name] = effect
    
    async def _setup_context_rules(self):
        """Configura regras para detecção de contexto."""
        rules = [
            # Mulher bonita
            ContextRule(
                context=ContextType.BEAUTIFUL_WOMAN,
                keywords=["beautiful", "pretty", "gorgeous", "stunning", "attractive", "bonita", "linda"],
                vision_tags=["woman", "female", "face", "smile", "beauty"],
                probability_threshold=0.3,
                max_frequency=2
            ),
            
            # Despedida
            ContextRule(
                context=ContextType.GOODBYE,
                keywords=["goodbye", "bye", "farewell", "see you", "tchau", "adeus", "até logo"],
                vision_tags=["leaving", "exit", "wave"],
                probability_threshold=0.7,
                max_frequency=5
            ),
            
            # Surpresa
            ContextRule(
                context=ContextType.SURPRISE,
                keywords=["wow", "amazing", "incredible", "surprise", "unexpected", "nossa", "incrível"],
                vision_tags=["surprised_expression", "open_mouth", "wide_eyes"],
                probability_threshold=0.6,
                max_frequency=4
            ),
            
            # Aprovação
            ContextRule(
                context=ContextType.APPROVAL,
                keywords=["good", "great", "excellent", "perfect", "nice", "bom", "ótimo", "perfeito"],
                vision_tags=["thumbs_up", "smile", "nodding"],
                probability_threshold=0.6,
                max_frequency=3
            ),
            
            # Empolgação
            ContextRule(
                context=ContextType.EXCITEMENT,
                keywords=["excited", "awesome", "fantastic", "amazing", "empolgado", "fantástico"],
                vision_tags=["excited_expression", "jumping", "celebration"],
                probability_threshold=0.7,
                max_frequency=3
            ),
            
            # Pensamento
            ContextRule(
                context=ContextType.THINKING,
                keywords=["think", "hmm", "consider", "maybe", "perhaps", "pensar", "talvez"],
                vision_tags=["thinking_pose", "hand_on_chin", "contemplating"],
                probability_threshold=0.2,
                max_frequency=5
            ),
            
            # Piada
            ContextRule(
                context=ContextType.JOKE,
                keywords=["funny", "joke", "laugh", "haha", "lol", "piada", "engraçado", "risos"],
                vision_tags=["laughing", "smiling", "humor"],
                probability_threshold=0.6,
                max_frequency=3
            )
        ]
        
        for rule in rules:
            self.context_rules[rule.context] = rule
    
    async def _scan_effects_directory(self):
        """Escaneia diretório de efeitos em busca de arquivos."""
        try:
            if not self.effects_dir.exists():
                logger.warning(f"Diretório de efeitos não encontrado: {self.effects_dir}")
                return
            
            # Formatos suportados
            supported_formats = {".wav", ".mp3", ".ogg", ".m4a"}
            
            found_files = []
            for ext in supported_formats:
                found_files.extend(self.effects_dir.glob(f"*{ext}"))
            
            logger.info(f"Encontrados {len(found_files)} arquivos de áudio em {self.effects_dir}")
            
            # Verifica se arquivos dos efeitos padrão existem
            missing_files = []
            for effect in self.effects.values():
                full_path = self.effects_dir / effect.file_path
                if not full_path.exists():
                    missing_files.append(effect.file_path)
                    effect.enabled = False
                else:
                    effect.enabled = True
            
            if missing_files:
                logger.warning(f"Arquivos de efeito não encontrados: {missing_files}")
                logger.info("Para instalar efeitos sonoros, coloque arquivos .wav na pasta audio/effects/")
                
        except Exception as e:
            logger.error(f"Erro ao escanear diretório de efeitos: {e}")
    
    async def play_context_effect(self, context: ContextType, 
                                 additional_data: Dict[str, Any] = None) -> bool:
        """
        Reproduz efeito baseado no contexto.
        
        Args:
            context: Tipo de contexto
            additional_data: Dados adicionais para decisão
            
        Returns:
            True se efeito foi reproduzido
        """
        try:
            if not self.enable_effects or not self.is_initialized:
                return False
            
            # Verifica limite de frequência
            if not self._check_frequency_limit(context):
                logger.debug(f"Limite de frequência atingido para contexto: {context.value}")
                return False
            
            # Encontra efeitos para o contexto
            available_effects = [
                effect for effect in self.effects.values()
                if effect.context == context and effect.enabled
            ]
            
            if not available_effects:
                logger.debug(f"Nenhum efeito disponível para contexto: {context.value}")
                return False
            
            # Filtra por cooldown
            now = time.time()
            ready_effects = [
                effect for effect in available_effects
                if (effect.name not in self.last_played or 
                    now - self.last_played[effect.name] >= effect.cooldown)
            ]
            
            if not ready_effects:
                logger.debug(f"Todos os efeitos para {context.value} estão em cooldown")
                return False
            
            # Seleciona efeito por prioridade (com algum random)
            ready_effects.sort(key=lambda e: e.priority, reverse=True)
            
            # 70% chance de pegar o de maior prioridade, 30% chance aleatória
            if random.random() < 0.7 and ready_effects:
                selected_effect = ready_effects[0]
            else:
                selected_effect = random.choice(ready_effects)
            
            # Reproduz efeito
            success = await self._play_effect(selected_effect)
            
            if success:
                # Atualiza contadores
                self.last_played[selected_effect.name] = now
                self.session_counts[context] = self.session_counts.get(context, 0) + 1
                self.total_played += 1
                
                # Adiciona ao histórico
                self._add_to_history(selected_effect, context, additional_data)
                
                logger.info(f"Efeito reproduzido: {selected_effect.name} para contexto {context.value}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao reproduzir efeito contextual: {e}")
            return False
    
    async def play_specific_effect(self, effect_name: str) -> bool:
        """
        Reproduz efeito específico por nome.
        
        Args:
            effect_name: Nome do efeito
            
        Returns:
            True se efeito foi reproduzido
        """
        try:
            if not self.enable_effects or not self.is_initialized:
                return False
            
            if effect_name not in self.effects:
                logger.warning(f"Efeito não encontrado: {effect_name}")
                return False
            
            effect = self.effects[effect_name]
            
            if not effect.enabled:
                logger.warning(f"Efeito desabilitado: {effect_name}")
                return False
            
            # Verifica cooldown
            now = time.time()
            if (effect_name in self.last_played and 
                now - self.last_played[effect_name] < effect.cooldown):
                logger.debug(f"Efeito {effect_name} em cooldown")
                return False
            
            success = await self._play_effect(effect)
            
            if success:
                self.last_played[effect_name] = now
                self.total_played += 1
                self._add_to_history(effect, None, {"manual": True})
                
                logger.info(f"Efeito manual reproduzido: {effect_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao reproduzir efeito específico: {e}")
            return False
    
    async def _play_effect(self, effect: SoundEffect) -> bool:
        """Reproduz um efeito sonoro."""
        try:
            if not self.audio_player:
                logger.warning("Player de áudio não configurado")
                return False
            
            file_path = self.effects_dir / effect.file_path
            
            if not file_path.exists():
                logger.error(f"Arquivo de efeito não encontrado: {file_path}")
                return False
            
            # Calcula volume final
            final_volume = min(1.0, effect.volume * self.global_volume)
            
            # Chama player de áudio
            success = await self.audio_player(
                str(file_path),
                volume=final_volume,
                duration=effect.duration
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao reproduzir efeito: {e}")
            return False
    
    def _check_frequency_limit(self, context: ContextType) -> bool:
        """Verifica se contexto não excedeu limite de frequência."""
        if context not in self.context_rules:
            return True
        
        rule = self.context_rules[context]
        current_count = self.session_counts.get(context, 0)
        
        return current_count < rule.max_frequency
    
    def _add_to_history(self, effect: SoundEffect, context: Optional[ContextType], 
                       additional_data: Optional[Dict[str, Any]]):
        """Adiciona efeito ao histórico."""
        try:
            entry = {
                "timestamp": time.time(),
                "effect_name": effect.name,
                "context": context.value if context else None,
                "duration": effect.duration,
                "volume": effect.volume,
                "additional_data": additional_data or {}
            }
            
            self.effects_history.append(entry)
            
            # Limita histórico
            if len(self.effects_history) > self.max_history:
                self.effects_history.pop(0)
                
        except Exception as e:
            logger.error(f"Erro ao adicionar ao histórico: {e}")
    
    async def analyze_text_for_context(self, text: str) -> List[ContextType]:
        """
        Analisa texto em busca de contextos relevantes.
        
        Args:
            text: Texto para analisar
            
        Returns:
            Lista de contextos detectados
        """
        try:
            detected_contexts = []
            text_lower = text.lower()
            
            for context, rule in self.context_rules.items():
                # Verifica keywords
                matches = sum(1 for keyword in rule.keywords if keyword in text_lower)
                
                if matches > 0:
                    # Calcula score simples baseado em matches
                    score = matches / len(rule.keywords)
                    
                    if score >= rule.probability_threshold:
                        detected_contexts.append(context)
            
            return detected_contexts
            
        except Exception as e:
            logger.error(f"Erro na análise de texto: {e}")
            return []
    
    async def analyze_vision_for_context(self, vision_data: Dict[str, Any]) -> List[ContextType]:
        """
        Analisa dados de visão para contextos.
        
        Args:
            vision_data: Dados da análise de visão
            
        Returns:
            Lista de contextos detectados
        """
        try:
            detected_contexts = []
            
            # Extrai tags e descrições
            tags = vision_data.get("tags", [])
            description = vision_data.get("description", "").lower()
            
            for context, rule in self.context_rules.items():
                # Verifica vision_tags
                tag_matches = sum(1 for tag in rule.vision_tags if tag in tags or tag in description)
                
                if tag_matches > 0:
                    score = tag_matches / len(rule.vision_tags)
                    
                    if score >= rule.probability_threshold:
                        detected_contexts.append(context)
            
            return detected_contexts
            
        except Exception as e:
            logger.error(f"Erro na análise de visão: {e}")
            return []
    
    def set_audio_player(self, player_func: Callable):
        """Define função para reproduzir áudio."""
        self.audio_player = player_func
        logger.info("Player de áudio configurado")
    
    def get_available_effects(self) -> Dict[str, Dict[str, Any]]:
        """Retorna lista de efeitos disponíveis."""
        return {
            name: {
                "context": effect.context.value,
                "duration": effect.duration,
                "enabled": effect.enabled,
                "file_path": effect.file_path,
                "priority": effect.priority,
                "cooldown": effect.cooldown
            }
            for name, effect in self.effects.items()
        }
    
    def get_context_rules(self) -> Dict[str, Dict[str, Any]]:
        """Retorna regras de contexto."""
        return {
            context.value: {
                "keywords": rule.keywords,
                "vision_tags": rule.vision_tags,
                "probability_threshold": rule.probability_threshold,
                "max_frequency": rule.max_frequency,
                "current_count": self.session_counts.get(context, 0)
            }
            for context, rule in self.context_rules.items()
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Retorna status do sistema de efeitos."""
        enabled_effects = len([e for e in self.effects.values() if e.enabled])
        
        return {
            "initialized": self.is_initialized,
            "enabled": self.enable_effects,
            "total_effects": len(self.effects),
            "enabled_effects": enabled_effects,
            "total_played": self.total_played,
            "effects_directory": str(self.effects_dir),
            "global_volume": self.global_volume,
            "session_counts": {k.value: v for k, v in self.session_counts.items()},
            "recent_history": len([h for h in self.effects_history if time.time() - h["timestamp"] < 300])
        }
    
    async def reset_session_counters(self):
        """Reset contadores da sessão."""
        self.session_counts.clear()
        logger.info("Contadores de sessão resetados")
    
    async def stop(self) -> bool:
        """Para o sistema de efeitos."""
        try:
            logger.info("Parando EffectsManager...")
            
            self.is_initialized = False
            self.audio_player = None
            
            logger.info("EffectsManager parado")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao parar EffectsManager: {e}")
            return False
