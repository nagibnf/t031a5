"""
Engine de Conversação Multimodal para G1.

Integra visão, áudio, fala e gestos de forma sincronizada para uma experiência
de conversação natural e expressiva.
"""

import asyncio
import logging
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..inputs.base import InputData
from ..actions.base import ActionRequest, ActionResult
from ..llm.provider import LLMProvider, LLMRequest, LLMResponse
from ..fuser.base import FusedData


class ConversationState(Enum):
    """Estados da conversação."""
    IDLE = "idle"
    LISTENING = "listening" 
    PROCESSING = "processing"
    SPEAKING = "speaking"
    GESTURE = "gesture"
    THINKING = "thinking"


class EmotionLevel(Enum):
    """Níveis de emoção."""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    CONFUSED = "confused"
    FOCUSED = "focused"
    SURPRISED = "surprised"
    THINKING = "thinking"


@dataclass
class ConversationContext:
    """Contexto da conversação."""
    user_name: Optional[str] = None
    conversation_history: List[Dict[str, Any]] = None
    current_emotion: EmotionLevel = EmotionLevel.NEUTRAL
    detected_objects: List[str] = None
    detected_faces: List[str] = None
    environment_context: Dict[str, Any] = None
    last_interaction: Optional[datetime] = None
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []
        if self.detected_objects is None:
            self.detected_objects = []
        if self.detected_faces is None:
            self.detected_faces = []
        if self.environment_context is None:
            self.environment_context = {}


@dataclass
class ConversationResponse:
    """Resposta da conversação."""
    text: str
    emotion: EmotionLevel
    gestures: List[str]
    audio_cues: List[str]
    look_at: Optional[Tuple[float, float]] = None  # Direção para olhar (x, y)
    confidence: float = 1.0


class ConversationEngine:
    """
    Engine principal de conversação multimodal.
    
    Integra:
    - Visão computacional para contexto visual
    - Processamento de áudio para escuta
    - LLM para inteligência conversacional
    - Síntese de fala para resposta
    - Gestos e expressões para comunicação não-verbal
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"t031a5.conversation.engine")
        
        # Estado da conversação
        self.state = ConversationState.IDLE
        self.context = ConversationContext()
        
        # Componentes
        self.llm_provider: Optional[LLMProvider] = None
        self.input_plugins: Dict[str, Any] = {}
        self.action_plugins: Dict[str, Any] = {}
        
        # Configurações
        self.enable_vision_context = config.get("enable_vision_context", True)
        self.enable_gesture_sync = config.get("enable_gesture_sync", True)
        self.enable_emotion_detection = config.get("enable_emotion_detection", True)
        self.conversation_timeout = config.get("conversation_timeout", 30.0)
        self.response_delay = config.get("response_delay", 0.5)
        
        # Sistema de gestos sincronizados integrado com biblioteca completa G1
        from ..actions.g1_movement_mapping import G1MovementLibrary, G1MovementType
        self.movement_library = G1MovementLibrary
        self.movement_type = G1MovementType
        
        self.gesture_mapping = {
            # GESTOS DE SAUDAÇÃO
            "greeting": [26, 18],  # wave_above_head + high_five_opt
            "farewell": [25, 11],  # wave_under_head + blow_kiss_with_both_hands_50hz
            "welcome": [19, 27],   # hug_opt + shake_hand_opt
            
            # GESTOS DE COMUNICAÇÃO
            "pointing": [31],      # extend_right_arm_forward
            "explanation": [35, 15], # emphasize + both_hands_up
            "thinking": [32],      # right_hand_on_mouth
            "agreement": [15, 17], # both_hands_up + clamp
            "disagreement": [22],  # refuse
            "attention": [31, 35], # extend_right_arm_forward + emphasize
            
            # GESTOS EMOCIONAIS
            "excitement": [15, 24], # both_hands_up + ultraman_ray
            "love": [33, 13],      # right_hand_on_heart + blow_kiss_with_right_hand
            "celebration": [15, 24], # both_hands_up + ultraman_ray
            "confusion": [32, 22], # right_hand_on_mouth + refuse
            "surprise": [23, 15],  # right_hand_up + both_hands_up
            
            # GESTOS ESPECÍFICOS
            "applause": [17],      # clamp
            "kiss": [13],         # blow_kiss_with_right_hand
            "heart": [33],        # right_hand_on_heart
            "reject": [22],       # refuse
            "wave": [26],         # wave_above_head
            "relax": [99],        # release_arm
            
            # MOVIMENTOS DE LOCOMOÇÃO BÁSICOS
            "move_forward": ["move_forward"],
            "move_backward": ["move_backward"], 
            "move_left": ["move_left"],
            "move_right": ["move_right"],
            "turn_left": ["rotate_left_medium"],
            "turn_right": ["rotate_right_medium"],
            "stop": ["stop_movement"],
            
            # PADRÕES COMPLEXOS
            "dance": ["circular_movement"],
            "spin": ["rotate_left_fast", "rotate_right_fast"],
            "balance": ["balance_mode_1"]
        }
        
        # Contexto visual
        self.visual_keywords = {
            "person": ["pessoa", "você", "alguém"],
            "object": ["isso", "aquilo", "objeto"],
            "location": ["aqui", "ali", "lugar"],
            "movement": ["movimento", "mexendo", "se movendo"]
        }
        
        # Métricas
        self.conversations_count = 0
        self.total_response_time = 0.0
        self.emotion_changes = 0
        self.gestures_performed = 0
        
    async def initialize(self, llm_provider: LLMProvider, input_plugins: Dict[str, Any], action_plugins: Dict[str, Any]) -> bool:
        """Inicializa o engine de conversação."""
        try:
            self.logger.info("Inicializando Conversation Engine...")
            
            # Configura componentes
            self.llm_provider = llm_provider
            self.input_plugins = input_plugins
            self.action_plugins = action_plugins
            
            # Inicializa contexto
            await self._initialize_context()
            
            self.logger.info("Conversation Engine inicializado com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na inicialização do Conversation Engine: {e}")
            return False
    
    async def _initialize_context(self):
        """Inicializa o contexto conversacional."""
        self.context.last_interaction = datetime.now()
        
        # Configura personalidade base
        system_prompt = """
        Você é um assistente robótico G1 inteligente e expressivo. 
        
        Características:
        - Conversação natural e empática
        - Usa informações visuais do ambiente
        - Expressa emoções através de gestos e voz
        - Mantém contexto da conversa
        - É proativo e engajado
        
        Sempre considere:
        - O que você está vendo no ambiente
        - O estado emocional da conversa
        - Gestos apropriados para suas respostas
        - Tom de voz adequado
        """
        
        self.base_system_prompt = system_prompt
    
    async def process_conversation_cycle(self, inputs: Dict[str, InputData]) -> Optional[ConversationResponse]:
        """
        Processa um ciclo completo de conversação.
        
        1. Analisa inputs (visão, áudio, sensores)
        2. Atualiza contexto conversacional
        3. Gera resposta inteligente via LLM
        4. Planeja gestos e expressões
        5. Retorna resposta coordenada
        """
        try:
            start_time = time.time()
            self.logger.debug(f"🎤 INÍCIO CONVERSAÇÃO: {len(inputs)} inputs recebidos")
            
            # 1. Análise de inputs
            self.logger.debug("🔍 Analisando inputs...")
            conversation_data = await self._analyze_inputs(inputs)
            
            if not conversation_data:
                self.logger.debug("❌ Nenhum dado conversacional extraído")
                return None
            
            self.logger.debug(f"✅ Dados conversacionais: {conversation_data}")
            
            # 2. Atualização de contexto
            self.logger.debug("📝 Atualizando contexto...")
            await self._update_context(conversation_data, inputs)
            
            # 3. Verificar se precisa responder
            self.logger.debug("🤔 Verificando se deve responder...")
            should_respond = await self._should_respond(conversation_data)
            if not should_respond:
                self.logger.debug("❌ Não deve responder agora")
                return None
            
            self.logger.debug("✅ Deve responder - gerando resposta...")
            
            # 4. Gerar resposta via LLM
            self.state = ConversationState.PROCESSING
            self.logger.debug("🧠 Gerando resposta via LLM...")
            llm_response = await self._generate_llm_response(conversation_data)
            
            if not llm_response:
                self.logger.debug("❌ LLM não retornou resposta")
                return None
            
            self.logger.debug(f"✅ LLM resposta: {llm_response.content[:50]}...")
            
            # 5. Planejar resposta multimodal
            self.logger.debug("🎭 Planejando resposta multimodal...")
            response = await self._plan_multimodal_response(llm_response, conversation_data)
            
            # 6. Atualizar métricas
            response_time = time.time() - start_time
            self.total_response_time += response_time
            self.conversations_count += 1
            
            self.logger.info(f"✅ Resposta gerada em {response_time:.2f}s: {response.text[:50]}...")
            
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Erro no ciclo de conversação: {e}")
            self.state = ConversationState.IDLE
            return None
    
    async def _analyze_inputs(self, inputs: Dict[str, InputData]) -> Optional[Dict[str, Any]]:
        """Analisa todos os inputs para extrair informações conversacionais."""
        conversation_data = {
            "voice_input": None,
            "visual_context": {},
            "user_detected": False,
            "interaction_type": "passive",
            "urgency": 0.0
        }
        
        # Análise de voz
        if "G1Voice" in inputs and inputs["G1Voice"]:
            voice_data = inputs["G1Voice"].data
            # Suporta tanto formato mock quanto real
            speech_detected = voice_data.get("speech_detected") or voice_data.get("is_speech", False)
            transcript = voice_data.get("transcription") or voice_data.get("transcript") or voice_data.get("text", "")
            
            if speech_detected and transcript:
                conversation_data["voice_input"] = transcript
                conversation_data["interaction_type"] = "active"
                conversation_data["urgency"] = voice_data.get("confidence", 0.0)
        
        # Análise visual
        if "G1Vision" in inputs and inputs["G1Vision"]:
            vision_data = inputs["G1Vision"].data
            
            # Suporta tanto formato mock quanto real
            objects = vision_data.get("objects_detected", []) or vision_data.get("objects", [])
            faces = vision_data.get("faces_detected", []) or vision_data.get("faces", [])
            
            conversation_data["visual_context"] = {
                "objects": objects,
                "faces": faces,
                "scene_analysis": vision_data.get("scene_analysis", {}),
                "scene_description": vision_data.get("scene_description", ""),
                "motion_detected": vision_data.get("motion_detected", False)
            }
            
            # Detectar presença humana
            if faces or any(obj.get("type") == "person" for obj in objects):
                conversation_data["user_detected"] = True
                if conversation_data["interaction_type"] == "passive":
                    conversation_data["interaction_type"] = "visual"
        
        # Análise de estado do robô
        if "G1State" in inputs and inputs["G1State"]:
            state_data = inputs["G1State"].data
            robot_state = state_data.get("robot_state", {})
            
            # Verificar se precisa de atenção
            if robot_state.get("battery_percentage", 100) < 20:
                conversation_data["urgency"] = max(conversation_data["urgency"], 0.8)
            
            if robot_state.get("safety_status") != "safe":
                conversation_data["urgency"] = 1.0
        
        return conversation_data if conversation_data["voice_input"] or conversation_data["user_detected"] else None
    
    async def _update_context(self, conversation_data: Dict[str, Any], inputs: Dict[str, InputData]):
        """Atualiza o contexto conversacional."""
        
        # Atualizar histórico de conversa
        if conversation_data.get("voice_input"):
            self.context.conversation_history.append({
                "timestamp": datetime.now(),
                "type": "user_input",
                "content": conversation_data["voice_input"],
                "visual_context": conversation_data.get("visual_context", {})
            })
        
        # Atualizar contexto visual
        visual_ctx = conversation_data.get("visual_context", {})
        if visual_ctx.get("objects"):
            self.context.detected_objects = [obj.get("type", "unknown") for obj in visual_ctx["objects"]]
        
        if visual_ctx.get("faces"):
            self.context.detected_faces = [f"person_{i}" for i in range(len(visual_ctx["faces"]))]
        
        # Atualizar ambiente
        self.context.environment_context = {
            "motion_detected": visual_ctx.get("motion_detected", False),
            "interaction_type": conversation_data.get("interaction_type", "passive"),
            "urgency": conversation_data.get("urgency", 0.0)
        }
        
        self.context.last_interaction = datetime.now()
    
    async def _should_respond(self, conversation_data: Dict[str, Any]) -> bool:
        """Determina se deve gerar uma resposta."""
        
        # Sempre responder a input de voz
        if conversation_data.get("voice_input"):
            return True
        
        # Responder se há urgência
        if conversation_data.get("urgency", 0.0) > 0.7:
            return True
        
        # Responder a interações visuais se configurado
        if (conversation_data.get("user_detected") and 
            conversation_data.get("interaction_type") == "visual" and
            self.enable_vision_context):
            
            # Evitar responder muito frequentemente
            if self.context.last_interaction:
                time_since_last = (datetime.now() - self.context.last_interaction).total_seconds()
                return time_since_last > 5.0  # Mínimo 5 segundos entre respostas visuais
        
        return False
    
    async def _generate_llm_response(self, conversation_data: Dict[str, Any]) -> Optional[LLMResponse]:
        """Gera resposta via LLM com contexto completo."""
        try:
            # Preparar contexto
            context_parts = [self.base_system_prompt]
            
            # Adicionar contexto visual
            if self.enable_vision_context:
                visual_context = self._format_visual_context(conversation_data.get("visual_context", {}))
                if visual_context:
                    context_parts.append(f"Contexto Visual: {visual_context}")
            
            # Adicionar histórico recente
            recent_history = self._format_conversation_history()
            if recent_history:
                context_parts.append(f"Histórico Recente: {recent_history}")
            
            # Adicionar situação atual
            current_situation = self._format_current_situation(conversation_data)
            context_parts.append(f"Situação Atual: {current_situation}")
            
            # Preparar dados fusionados
            fused_data = FusedData(
                fusion_type="conversation",
                timestamp=datetime.now(),
                data={
                    "content": "\n\n".join(context_parts),
                    "conversation_context": self.context.__dict__,
                    "visual_context": conversation_data.get("visual_context", {}),
                    "interaction_type": conversation_data.get("interaction_type", "passive")
                },
                confidence=conversation_data.get("urgency", 0.5),
                source_inputs=["conversation_engine"],
                fusion_metadata={
                    "conversation_turn": len(self.context.conversation_history),
                    "response_type": "conversational"
                }
            )
            
            # Gerar resposta usando interface correta do LLMProvider
            return await self.llm_provider.process(fused_data, "\n\n".join(context_parts))
            
        except Exception as e:
            self.logger.error(f"Erro na geração de resposta LLM: {e}")
            return None
    
    def _format_visual_context(self, visual_context: Dict[str, Any]) -> str:
        """Formata contexto visual para o LLM."""
        parts = []
        
        if visual_context.get("objects"):
            objects = [obj.get("type", "objeto") for obj in visual_context["objects"]]
            parts.append(f"Objetos visíveis: {', '.join(objects)}")
        
        if visual_context.get("faces"):
            faces_count = len(visual_context["faces"])
            parts.append(f"Pessoas detectadas: {faces_count}")
        
        if visual_context.get("motion_detected"):
            parts.append("Movimento detectado no ambiente")
        
        scene = visual_context.get("scene_analysis", {})
        if scene:
            if scene.get("brightness"):
                parts.append(f"Iluminação: {scene['brightness']}")
            if scene.get("activity_level"):
                parts.append(f"Atividade: {scene['activity_level']}")
        
        return "; ".join(parts) if parts else ""
    
    def _format_conversation_history(self, max_entries: int = 5) -> str:
        """Formata histórico de conversa recente."""
        if not self.context.conversation_history:
            return ""
        
        recent = self.context.conversation_history[-max_entries:]
        formatted = []
        
        for entry in recent:
            timestamp = entry["timestamp"].strftime("%H:%M")
            content = entry["content"]
            entry_type = entry["type"]
            
            if entry_type == "user_input":
                formatted.append(f"[{timestamp}] Usuário: {content}")
            elif entry_type == "bot_response":
                formatted.append(f"[{timestamp}] G1: {content}")
        
        return "\n".join(formatted)
    
    def _format_current_situation(self, conversation_data: Dict[str, Any]) -> str:
        """Formata situação atual."""
        parts = []
        
        # Input do usuário
        if conversation_data.get("voice_input"):
            parts.append(f"Usuário disse: '{conversation_data['voice_input']}'")
        
        # Tipo de interação
        interaction_type = conversation_data.get("interaction_type", "passive")
        if interaction_type == "visual":
            parts.append("Usuário está presente mas não falou")
        elif interaction_type == "active":
            parts.append("Usuário está interagindo ativamente")
        
        # Urgência
        urgency = conversation_data.get("urgency", 0.0)
        if urgency > 0.7:
            parts.append("Situação requer atenção imediata")
        elif urgency > 0.3:
            parts.append("Situação merece atenção")
        
        return "; ".join(parts) if parts else "Situação normal"
    
    async def _plan_multimodal_response(self, llm_response: LLMResponse, conversation_data: Dict[str, Any]) -> ConversationResponse:
        """Planeja resposta multimodal coordenada."""
        
        response_text = llm_response.content
        
        # Detectar emoção da resposta
        emotion = self._detect_response_emotion(response_text, conversation_data)
        
        # Planejar gestos
        gestures = self._plan_gestures(response_text, emotion, conversation_data)
        
        # Planejar áudio
        audio_cues = self._plan_audio_cues(response_text, emotion)
        
        # Determinar direção do olhar
        look_at = self._plan_gaze_direction(conversation_data)
        
        # Atualizar histórico
        self.context.conversation_history.append({
            "timestamp": datetime.now(),
            "type": "bot_response",
            "content": response_text,
            "emotion": emotion.value,
            "gestures": gestures
        })
        
        # Atualizar emoção atual
        if emotion != self.context.current_emotion:
            self.context.current_emotion = emotion
            self.emotion_changes += 1
        
        return ConversationResponse(
            text=response_text,
            emotion=emotion,
            gestures=gestures,
            audio_cues=audio_cues,
            look_at=look_at,
            confidence=llm_response.metadata.get("confidence", 0.8)
        )
    
    def _detect_response_emotion(self, text: str, conversation_data: Dict[str, Any]) -> EmotionLevel:
        """Detecta emoção apropriada para a resposta."""
        text_lower = text.lower()
        
        # Palavras-chave emocionais
        if any(word in text_lower for word in ["feliz", "ótimo", "excelente", "fantástico", "maravilhoso"]):
            return EmotionLevel.HAPPY
        
        if any(word in text_lower for word in ["interessante", "incrível", "uau", "nossa"]):
            return EmotionLevel.EXCITED
        
        if any(word in text_lower for word in ["hmm", "deixe-me pensar", "não tenho certeza"]):
            return EmotionLevel.THINKING
        
        if any(word in text_lower for word in ["não entendi", "confuso", "perdão"]):
            return EmotionLevel.CONFUSED
        
        if any(word in text_lower for word in ["observando", "vejo", "analisando"]):
            return EmotionLevel.FOCUSED
        
        # Baseado no contexto
        urgency = conversation_data.get("urgency", 0.0)
        if urgency > 0.7:
            return EmotionLevel.FOCUSED
        
        return EmotionLevel.NEUTRAL
    
    def _plan_gestures(self, text: str, emotion: EmotionLevel, conversation_data: Dict[str, Any]) -> List[str]:
        """Planeja gestos apropriados."""
        if not self.enable_gesture_sync:
            return []
        
        gestures = []
        text_lower = text.lower()
        
        # Gestos baseados no conteúdo
        if any(word in text_lower for word in ["olá", "oi", "saudações", "bem-vindo"]):
            gestures.extend(self.gesture_mapping.get("greeting", []))
        
        elif any(word in text_lower for word in ["isso", "aquilo", "ali", "aqui"]):
            gestures.extend(self.gesture_mapping.get("pointing", []))
        
        elif any(word in text_lower for word in ["explicar", "mostrar", "demonstrar"]):
            gestures.extend(self.gesture_mapping.get("explanation", []))
        
        elif any(word in text_lower for word in ["pensar", "considerar", "analisar"]):
            gestures.extend(self.gesture_mapping.get("thinking", []))
        
        elif any(word in text_lower for word in ["sim", "correto", "exato", "concordo"]):
            gestures.extend(self.gesture_mapping.get("agreement", []))
        
        elif any(word in text_lower for word in ["não", "incorreto", "discordo"]):
            gestures.extend(self.gesture_mapping.get("disagreement", []))
        
        # Gestos baseados na emoção
        if emotion == EmotionLevel.HAPPY:
            gestures.extend(self.gesture_mapping.get("excitement", []))
        elif emotion == EmotionLevel.CONFUSED:
            gestures.extend(self.gesture_mapping.get("confusion", []))
        
        # Remover duplicatas e limitar
        return list(dict.fromkeys(gestures))[:3]  # Máximo 3 gestos
    
    def _plan_audio_cues(self, text: str, emotion: EmotionLevel) -> List[str]:
        """Planeja sinais de áudio."""
        audio_cues = []
        
        # Sons baseados na emoção
        if emotion == EmotionLevel.HAPPY:
            audio_cues.append("happy")
        elif emotion == EmotionLevel.EXCITED:
            audio_cues.append("excited")
        elif emotion == EmotionLevel.THINKING:
            audio_cues.append("notification")  # Som sutil de pensamento
        
        # Sons baseados no conteúdo
        if "sucesso" in text.lower() or "consegui" in text.lower():
            audio_cues.append("success")
        
        return audio_cues
    
    def _plan_gaze_direction(self, conversation_data: Dict[str, Any]) -> Optional[Tuple[float, float]]:
        """Planeja direção do olhar."""
        visual_context = conversation_data.get("visual_context", {})
        
        # Olhar para faces detectadas
        if visual_context.get("faces"):
            # Pegar primeira face detectada
            face = visual_context["faces"][0]
            if "center" in face:
                return (face["center"][0], face["center"][1])
        
        # Olhar para objetos mencionados
        if visual_context.get("objects"):
            obj = visual_context["objects"][0]
            if "center" in obj:
                return (obj["center"][0], obj["center"][1])
        
        return None  # Olhar neutro
    
    async def execute_response(self, response: ConversationResponse) -> bool:
        """Executa resposta multimodal de forma sincronizada."""
        try:
            self.logger.info(f"Executando resposta: {response.text[:50]}...")
            
            # Lista de tarefas a executar
            tasks = []
            
            # 1. Configurar emoção
            if "G1Emotion" in self.action_plugins:
                emotion_request = ActionRequest(
                    action_type="emotion",
                    action_name="set_emotion",
                    timestamp=datetime.now(),
                    data={
                        "emotion": response.emotion.value,
                        "intensity": 0.8,
                        "duration": len(response.text) * 0.1  # Duração baseada no texto
                    }
                )
                tasks.append(self._execute_action("G1Emotion", emotion_request))
            
            # 2. Executar gestos e movimentos
            if response.gestures:
                for gesture in response.gestures:
                    # Verificar se é um ID numérico (APENAS movimentos de braços, NÃO estados FSM)
                    if isinstance(gesture, int):
                        if "G1Arms" in self.action_plugins:
                            # Verificar se é um movimento de braços válido (não estado FSM)
                            arm_movement = self.movement_library.get_movement_by_id(gesture)
                            if (arm_movement and 
                                arm_movement.movement_type == self.movement_type.ARM_GESTURE):
                                
                                gesture_request = ActionRequest(
                                    action_type="arms",
                                    action_name="execute_movement",
                                    timestamp=datetime.now(),
                                    data={
                                        "movement_id": gesture,
                                        "movement_name": arm_movement.name,
                                        "duration": arm_movement.duration,
                                        "requires_relax": arm_movement.requires_relax
                                    }
                                )
                                tasks.append(self._execute_action("G1Arms", gesture_request))
                            else:
                                self.logger.warning(f"Ignorando estado FSM {gesture} em contexto conversacional")
                    
                    # Verificar se é um comando de locomoção (string) - APENAS locomoção, NÃO estados FSM
                    elif isinstance(gesture, str):
                        if "G1Movement" in self.action_plugins:
                            locomotion = self.movement_library.get_movement_by_name(gesture)
                            if (locomotion and 
                                locomotion.movement_type == self.movement_type.LOCOMOTION):
                                
                                locomotion_request = ActionRequest(
                                    action_type="movement",
                                    action_name="execute_locomotion",
                                    timestamp=datetime.now(),
                                    data={
                                        "command": gesture,
                                        "movement_name": locomotion.name,
                                        "duration": locomotion.duration
                                    }
                                )
                                tasks.append(self._execute_action("G1Movement", locomotion_request))
                        
                        # Fallback para gestos legados
                        elif "G1Arms" in self.action_plugins:
                            gesture_request = ActionRequest(
                                action_type="arms",
                                action_name="gesture",
                                timestamp=datetime.now(),
                                data={
                                    "gesture": gesture,
                                    "speed": 0.8,
                                    "hold_time": 2.0
                                }
                            )
                            tasks.append(self._execute_action("G1Arms", gesture_request))
            
            # 3. Reproduzir áudio
            if response.audio_cues and "G1Audio" in self.action_plugins:
                for audio_cue in response.audio_cues:
                    audio_request = ActionRequest(
                        action_type="audio",
                        action_name="play",
                        timestamp=datetime.now(),
                        data={
                            "sound": audio_cue,
                            "volume": 0.6
                        }
                    )
                    tasks.append(self._execute_action("G1Audio", audio_request))
            
            # 4. Falar
            if "G1Speech" in self.action_plugins:
                speech_request = ActionRequest(
                    action_type="speech",
                    action_name="speak",
                    timestamp=datetime.now(),
                    data={
                        "text": response.text,
                        "emotion": response.emotion.value,
                        "speed": 0.9,
                        "volume": 0.8
                    }
                )
                tasks.append(self._execute_action("G1Speech", speech_request))
            
            # 5. Ajustar olhar
            if response.look_at and "G1Movement" in self.action_plugins:
                look_request = ActionRequest(
                    action_type="movement",
                    action_name="look_at",
                    timestamp=datetime.now(),
                    data={
                        "x": response.look_at[0],
                        "y": response.look_at[1],
                        "speed": 0.5
                    }
                )
                tasks.append(self._execute_action("G1Movement", look_request))
            
            # Executar todas as ações
            self.state = ConversationState.SPEAKING
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Verificar resultados
            success_count = sum(1 for r in results if isinstance(r, ActionResult) and r.success)
            total_count = len(tasks)
            
            self.logger.info(f"Resposta executada: {success_count}/{total_count} ações bem-sucedidas")
            
            # Atualizar métricas
            self.gestures_performed += len(response.gestures)
            
            # Aguardar delay de resposta
            await asyncio.sleep(self.response_delay)
            
            self.state = ConversationState.IDLE
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Erro na execução da resposta: {e}")
            self.state = ConversationState.IDLE
            return False
    
    async def _execute_action(self, plugin_name: str, request: ActionRequest) -> ActionResult:
        """Executa uma ação específica."""
        try:
            plugin = self.action_plugins.get(plugin_name)
            if plugin:
                return await plugin.execute(request)
            else:
                self.logger.warning(f"Plugin {plugin_name} não disponível")
                return ActionResult(
                    action_type=request.action_type,
                    action_name=request.action_name,
                    timestamp=datetime.now(),
                    success=False,
                    data={"error": f"Plugin {plugin_name} não disponível"}
                )
        except Exception as e:
            self.logger.error(f"Erro ao executar ação {plugin_name}: {e}")
            return ActionResult(
                action_type=request.action_type,
                action_name=request.action_name,
                timestamp=datetime.now(),
                success=False,
                data={"error": str(e)}
            )
    
    async def get_status(self) -> Dict[str, Any]:
        """Retorna status do engine de conversação."""
        return {
            "state": self.state.value,
            "current_emotion": self.context.current_emotion.value,
            "conversations_count": self.conversations_count,
            "avg_response_time": (
                self.total_response_time / self.conversations_count 
                if self.conversations_count > 0 else 0.0
            ),
            "emotion_changes": self.emotion_changes,
            "gestures_performed": self.gestures_performed,
            "last_interaction": self.context.last_interaction.isoformat() if self.context.last_interaction else None,
            "conversation_history_length": len(self.context.conversation_history),
            "detected_objects": self.context.detected_objects,
            "detected_faces": self.context.detected_faces,
            "components_available": {
                "llm_provider": self.llm_provider is not None,
                "vision": "G1Vision" in self.input_plugins,
                "voice": "G1Voice" in self.input_plugins,
                "speech": "G1Speech" in self.action_plugins,
                "arms": "G1Arms" in self.action_plugins,
                "emotion": "G1Emotion" in self.action_plugins,
                "audio": "G1Audio" in self.action_plugins
            }
        }
    
    async def stop(self) -> bool:
        """Para o engine de conversação."""
        try:
            self.logger.info("Parando Conversation Engine...")
            self.state = ConversationState.IDLE
            return True
        except Exception as e:
            self.logger.error(f"Erro ao parar Conversation Engine: {e}")
            return False
