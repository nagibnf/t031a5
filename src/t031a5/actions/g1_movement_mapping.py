"""
Mapeamento completo dos movimentos do G1 Tobias.

Contém todos os 20 movimentos de braços + estados FSM + locomoção confirmados
durante os testes extensivos realizados com o robô Unitree G1.

IMPORTANTE: Esta lista reflete os movimentos reais testados e funcionais.
IDs não listados retornam erro 7402 e devem ser evitados.
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


class G1MovementType(Enum):
    """Tipos de movimentos do G1."""
    ARM_GESTURE = "arm_gesture"
    FSM_STATE = "fsm_state"
    LOCOMOTION = "locomotion"


@dataclass
class G1Movement:
    """Representa um movimento do G1."""
    id: int
    name: str
    display_name: str
    description: str
    movement_type: G1MovementType
    duration: float = 3.0
    requires_relax: bool = True
    is_relax: bool = False
    tested: bool = True
    working: bool = True


class G1MovementLibrary:
    """Biblioteca completa de movimentos do G1."""
    
    # ============================================================================
    # 🤚 MOVIMENTOS DE BRAÇOS (20 CONFIRMADOS)
    # ============================================================================
    ARM_MOVEMENTS = {
        1: G1Movement(
            id=1,
            name="turn_back_wave",
            display_name="Vira e Acena",
            description="Vira para trás e acena",
            movement_type=G1MovementType.ARM_GESTURE,
            duration=4.0,
            requires_relax=True
        ),
        11: G1Movement(
            id=11,
            name="blow_kiss_with_both_hands_50hz",
            display_name="Beijo Duas Mãos",
            description="Beijo com duas mãos",
            movement_type=G1MovementType.ARM_GESTURE,
            duration=3.0,
            requires_relax=True
        ),
        12: G1Movement(
            id=12,
            name="blow_kiss_with_left_hand",
            display_name="Beijo Mão Esquerda",
            description="Beijo com mão esquerda",
            movement_type=G1MovementType.ARM_GESTURE,
            duration=3.0,
            requires_relax=True
        ),
        13: G1Movement(
            id=13,
            name="blow_kiss_with_right_hand",
            display_name="Beijo Mão Direita",
            description="Beijo com mão direita",
            movement_type=G1MovementType.ARM_GESTURE,
            duration=3.0,
            requires_relax=True
        ),
        15: G1Movement(
            id=15,
            name="both_hands_up",
            display_name="Mãos Para Cima",
            description="Duas mãos para cima",
            movement_type=G1MovementType.ARM_GESTURE,
            duration=3.0,
            requires_relax=True
        ),
        17: G1Movement(
            id=17,
            name="clamp",
            display_name="Aplaudir",
            description="Aplaudir",
            movement_type=G1MovementType.ARM_GESTURE,
            duration=3.0,
            requires_relax=True
        ),
        18: G1Movement(
            id=18,
            name="high_five_opt",
            display_name="Toca Aqui",
            description="Toca aqui / High Five",
            movement_type=G1MovementType.ARM_GESTURE,
            duration=3.0,
            requires_relax=True
        ),
        19: G1Movement(
            id=19,
            name="hug_opt",
            display_name="Abraçar",
            description="Abraçar",
            movement_type=G1MovementType.ARM_GESTURE,
            duration=3.0,
            requires_relax=True
        ),
        22: G1Movement(
            id=22,
            name="refuse",
            display_name="Recusar",
            description="Recusar / Negar",
            movement_type=G1MovementType.ARM_GESTURE,
            duration=3.0,
            requires_relax=True
        ),
        23: G1Movement(
            id=23,
            name="right_hand_up",
            display_name="Mão Direita Para Cima",
            description="Mão direita para cima",
            movement_type=G1MovementType.ARM_GESTURE,
            duration=3.0,
            requires_relax=True
        ),
        24: G1Movement(
            id=24,
            name="ultraman_ray",
            display_name="Raio do Ultraman",
            description="Raio do Ultraman",
            movement_type=G1MovementType.ARM_GESTURE,
            duration=3.0,
            requires_relax=True
        ),
        25: G1Movement(
            id=25,
            name="wave_under_head",
            display_name="Acenar Baixo",
            description="Acenar abaixo da cabeça",
            movement_type=G1MovementType.ARM_GESTURE,
            duration=3.0,
            requires_relax=True
        ),
        26: G1Movement(
            id=26,
            name="wave_above_head",
            display_name="Acenar Alto",
            description="Acenar acima da cabeça",
            movement_type=G1MovementType.ARM_GESTURE,
            duration=3.0,
            requires_relax=True
        ),
        27: G1Movement(
            id=27,
            name="shake_hand_opt",
            display_name="Apertar Mão",
            description="Apertar mão",
            movement_type=G1MovementType.ARM_GESTURE,
            duration=3.0,
            requires_relax=True
        ),
        31: G1Movement(
            id=31,
            name="extend_right_arm_forward",
            display_name="Apontar",
            description="Estender braço direito para frente",
            movement_type=G1MovementType.ARM_GESTURE,
            duration=3.0,
            requires_relax=True
        ),
        32: G1Movement(
            id=32,
            name="right_hand_on_mouth",
            display_name="Mão na Boca",
            description="Mão direita na boca",
            movement_type=G1MovementType.ARM_GESTURE,
            duration=3.0,
            requires_relax=True
        ),
        33: G1Movement(
            id=33,
            name="right_hand_on_heart",
            display_name="Mão no Coração",
            description="Mão direita no coração",
            movement_type=G1MovementType.ARM_GESTURE,
            duration=3.0,
            requires_relax=True
        ),
        34: G1Movement(
            id=34,
            name="both_hands_up_deviate_right",
            display_name="Mãos Para Cima Direita",
            description="Duas mãos para cima desviando direita",
            movement_type=G1MovementType.ARM_GESTURE,
            duration=3.0,
            requires_relax=True
        ),
        35: G1Movement(
            id=35,
            name="emphasize",
            display_name="Enfatizar",
            description="Enfatizar",
            movement_type=G1MovementType.ARM_GESTURE,
            duration=3.0,
            requires_relax=True
        ),
        99: G1Movement(
            id=99,
            name="release_arm",
            display_name="Relaxar Braços",
            description="Liberar braços (ESSENCIAL)",
            movement_type=G1MovementType.ARM_GESTURE,
            duration=1.0,
            requires_relax=False,
            is_relax=True
        )
    }
    
    # ============================================================================
    # 🚶 ESTADOS FSM (8 CONFIRMADOS)
    # ============================================================================
    FSM_STATES = {
        0: G1Movement(
            id=0,
            name="zero_torque",
            display_name="Torque Zero",
            description="Torque zero - estado seguro",
            movement_type=G1MovementType.FSM_STATE,
            duration=2.0,
            requires_relax=False
        ),
        1: G1Movement(
            id=1,
            name="damping",
            display_name="Amortecimento",
            description="Amortecimento - estado estável",
            movement_type=G1MovementType.FSM_STATE,
            duration=2.0,
            requires_relax=False
        ),
        2: G1Movement(
            id=2,
            name="squat",
            display_name="Agachar",
            description="Agachar - postura baixa",
            movement_type=G1MovementType.FSM_STATE,
            duration=3.0,
            requires_relax=False
        ),
        3: G1Movement(
            id=3,
            name="seat",
            display_name="Sentar",
            description="Sentar - postura sentada",
            movement_type=G1MovementType.FSM_STATE,
            duration=3.0,
            requires_relax=False
        ),
        4: G1Movement(
            id=4,
            name="get_ready",
            display_name="Preparar",
            description="Preparar - estado inicial",
            movement_type=G1MovementType.FSM_STATE,
            duration=2.0,
            requires_relax=False
        ),
        200: G1Movement(
            id=200,
            name="start",
            display_name="Iniciar",
            description="Iniciar - estado ativo",
            movement_type=G1MovementType.FSM_STATE,
            duration=2.0,
            requires_relax=False
        ),
        702: G1Movement(
            id=702,
            name="lie2standup",
            display_name="Deitar para Levantar",
            description="Deitar para levantar - transição",
            movement_type=G1MovementType.FSM_STATE,
            duration=5.0,
            requires_relax=False
        ),
        706: G1Movement(
            id=706,
            name="squat2standup",
            display_name="Agachar para Levantar",
            description="Agachar para levantar - transição",
            movement_type=G1MovementType.FSM_STATE,
            duration=4.0,
            requires_relax=False
        )
    }
    
    # ============================================================================
    # 🚶 COMANDOS DE LOCOMOÇÃO (4 CONFIRMADOS)
    # ============================================================================
    LOCOMOTION_COMMANDS = {
        "damp": G1Movement(
            id=-1,  # Comandos de locomoção não usam ID numérico
            name="damp",
            display_name="Amortecimento",
            description="Amortecimento - funciona em qualquer estado",
            movement_type=G1MovementType.LOCOMOTION,
            duration=2.0,
            requires_relax=False
        ),
        "sit": G1Movement(
            id=-1,
            name="sit",
            display_name="Sentar",
            description="Sentar - postura sentada",
            movement_type=G1MovementType.LOCOMOTION,
            duration=3.0,
            requires_relax=False
        ),
        "highstand": G1Movement(
            id=-1,
            name="highstand",
            display_name="Postura Alta",
            description="Postura alta - postura ereta",
            movement_type=G1MovementType.LOCOMOTION,
            duration=2.0,
            requires_relax=False
        ),
        "lowstand": G1Movement(
            id=-1,
            name="lowstand",
            display_name="Postura Baixa",
            description="Postura baixa - postura agachada",
            movement_type=G1MovementType.LOCOMOTION,
            duration=2.0,
            requires_relax=False
        )
    }
    
    # ============================================================================
    # 🎭 PADRÕES DE MOVIMENTOS (SEQUÊNCIAS)
    # ============================================================================
    MOVEMENT_PATTERNS = {
        "greeting": {
            "name": "Saudação",
            "description": "Sequência de saudação amigável",
            "movements": [26, 18],  # High Wave + High Five
            "total_duration": 6.0
        },
        "farewell": {
            "name": "Despedida", 
            "description": "Sequência de despedida carinhosa",
            "movements": [25, 11],  # Face Wave + Two Hand Kiss
            "total_duration": 6.0
        },
        "thinking": {
            "name": "Pensando",
            "description": "Gesto de reflexão",
            "movements": [32],  # Hand on Mouth
            "total_duration": 3.0
        },
        "agreement": {
            "name": "Concordando",
            "description": "Sequência de concordância",
            "movements": [15, 17],  # Hands Up + Clap
            "total_duration": 6.0
        },
        "celebration": {
            "name": "Celebração",
            "description": "Sequência de comemoração",
            "movements": [15, 24],  # Hands Up + Ultraman Ray
            "total_duration": 6.0
        },
        "love": {
            "name": "Amor",
            "description": "Sequência romântica",
            "movements": [33, 13],  # Hand on Heart + Right Kiss
            "total_duration": 6.0
        },
        "attention": {
            "name": "Atenção",
            "description": "Chamando atenção",
            "movements": [31, 35],  # Point Forward + Emphasize
            "total_duration": 6.0
        },
        "reject": {
            "name": "Rejeitar",
            "description": "Gesto de negação",
            "movements": [22],  # Refuse
            "total_duration": 3.0
        },
        "welcome": {
            "name": "Bem-vindo",
            "description": "Sequência de boas-vindas",
            "movements": [19, 27],  # Hug + Shake Hand
            "total_duration": 6.0
        }
    }
    
    # ============================================================================
    # ⚠️ MOVIMENTOS NÃO DISPONÍVEIS (RETORNAM ERRO 7402)
    # ============================================================================
    UNAVAILABLE_MOVEMENTS = [10, 14, 16, 20, 21, 28, 29, 30, 36, 37, 38, 39, 
                           40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50]
    
    @classmethod
    def get_all_arm_movements(cls) -> Dict[int, G1Movement]:
        """Retorna todos os movimentos de braços."""
        return cls.ARM_MOVEMENTS.copy()
    
    @classmethod
    def get_all_fsm_states(cls) -> Dict[int, G1Movement]:
        """Retorna todos os estados FSM."""
        return cls.FSM_STATES.copy()
    
    @classmethod 
    def get_all_locomotion(cls) -> Dict[str, G1Movement]:
        """Retorna todos os comandos de locomoção."""
        return cls.LOCOMOTION_COMMANDS.copy()
    
    @classmethod
    def get_movement_by_id(cls, movement_id: int) -> Optional[G1Movement]:
        """Retorna movimento por ID."""
        if movement_id in cls.ARM_MOVEMENTS:
            return cls.ARM_MOVEMENTS[movement_id]
        elif movement_id in cls.FSM_STATES:
            return cls.FSM_STATES[movement_id]
        return None
    
    @classmethod
    def get_movement_by_name(cls, name: str) -> Optional[G1Movement]:
        """Retorna movimento por nome."""
        # Busca em movimentos de braços
        for movement in cls.ARM_MOVEMENTS.values():
            if movement.name == name:
                return movement
        
        # Busca em estados FSM
        for movement in cls.FSM_STATES.values():
            if movement.name == name:
                return movement
        
        # Busca em locomoção
        if name in cls.LOCOMOTION_COMMANDS:
            return cls.LOCOMOTION_COMMANDS[name]
        
        return None
    
    @classmethod
    def get_pattern(cls, pattern_name: str) -> Optional[Dict[str, Any]]:
        """Retorna padrão de movimento por nome."""
        return cls.MOVEMENT_PATTERNS.get(pattern_name)
    
    @classmethod
    def is_available(cls, movement_id: int) -> bool:
        """Verifica se movimento está disponível."""
        return movement_id not in cls.UNAVAILABLE_MOVEMENTS
    
    @classmethod
    def get_working_movements(cls) -> List[int]:
        """Retorna lista de IDs dos movimentos funcionais."""
        working = list(cls.ARM_MOVEMENTS.keys()) + list(cls.FSM_STATES.keys())
        return sorted(working)
    
    @classmethod
    def get_statistics(cls) -> Dict[str, Any]:
        """Retorna estatísticas dos movimentos."""
        return {
            "arm_movements": len(cls.ARM_MOVEMENTS),
            "fsm_states": len(cls.FSM_STATES),
            "locomotion_commands": len(cls.LOCOMOTION_COMMANDS),
            "total_movements": len(cls.ARM_MOVEMENTS) + len(cls.FSM_STATES) + len(cls.LOCOMOTION_COMMANDS),
            "unavailable_movements": len(cls.UNAVAILABLE_MOVEMENTS),
            "movement_patterns": len(cls.MOVEMENT_PATTERNS),
            "success_rate": f"{len(cls.ARM_MOVEMENTS)}/{len(cls.ARM_MOVEMENTS) + len(cls.UNAVAILABLE_MOVEMENTS)} ({(len(cls.ARM_MOVEMENTS)/(len(cls.ARM_MOVEMENTS) + len(cls.UNAVAILABLE_MOVEMENTS)) * 100):.0f}%)"
        }


# ============================================================================
# 🎯 FUNÇÕES DE CONVENIÊNCIA
# ============================================================================

def get_random_gesture() -> G1Movement:
    """Retorna um gesto aleatório."""
    import random
    movements = list(G1MovementLibrary.ARM_MOVEMENTS.values())
    # Remove o movimento de relaxar da seleção aleatória
    movements = [m for m in movements if not m.is_relax]
    return random.choice(movements)


def create_movement_sequence(*movement_ids: int) -> List[G1Movement]:
    """Cria sequência de movimentos com relaxamento automático."""
    sequence = []
    for movement_id in movement_ids:
        movement = G1MovementLibrary.get_movement_by_id(movement_id)
        if movement:
            if sequence and movement.requires_relax:
                # Adiciona relaxamento entre movimentos
                relax = G1MovementLibrary.get_movement_by_id(99)
                if relax:
                    sequence.append(relax)
            sequence.append(movement)
    
    # Adiciona relaxamento final
    if sequence:
        relax = G1MovementLibrary.get_movement_by_id(99)
        if relax:
            sequence.append(relax)
    
    return sequence


def validate_movement_sequence(movement_ids: List[int]) -> List[str]:
    """Valida sequência de movimentos e retorna erros."""
    errors = []
    
    for movement_id in movement_ids:
        if movement_id in G1MovementLibrary.UNAVAILABLE_MOVEMENTS:
            errors.append(f"Movement ID {movement_id} is not available (returns error 7402)")
        elif not G1MovementLibrary.get_movement_by_id(movement_id):
            errors.append(f"Movement ID {movement_id} is not recognized")
    
    return errors


# ============================================================================
# 📊 INFORMAÇÕES DE DEBUG
# ============================================================================

if __name__ == "__main__":
    print("🤖 G1 MOVEMENT LIBRARY - ESTATÍSTICAS")
    print("=" * 50)
    
    stats = G1MovementLibrary.get_statistics()
    for key, value in stats.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    print("\n🤚 MOVIMENTOS DE BRAÇOS DISPONÍVEIS:")
    for movement_id, movement in G1MovementLibrary.ARM_MOVEMENTS.items():
        print(f"  ID {movement_id:2d}: {movement.display_name} - {movement.description}")
    
    print("\n🚶 ESTADOS FSM DISPONÍVEIS:")
    for state_id, state in G1MovementLibrary.FSM_STATES.items():
        print(f"  ID {state_id:3d}: {state.display_name} - {state.description}")
    
    print("\n🚶 COMANDOS DE LOCOMOÇÃO:")
    for cmd_name, cmd in G1MovementLibrary.LOCOMOTION_COMMANDS.items():
        print(f"  {cmd_name:9s}: {cmd.display_name} - {cmd.description}")
    
    print("\n🎭 PADRÕES DE MOVIMENTO:")
    for pattern_name, pattern in G1MovementLibrary.MOVEMENT_PATTERNS.items():
        print(f"  {pattern_name:11s}: {pattern['name']} - {pattern['description']}")
