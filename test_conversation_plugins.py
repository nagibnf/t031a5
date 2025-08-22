#!/usr/bin/env python3
"""
Teste para verificar se ConversationEngine tem action_plugins corretos
"""

import asyncio
import sys
sys.path.append('src')
from t031a5.runtime.cortex import CortexRuntime
from pathlib import Path

async def test():
    print("🔍 Testando ConversationEngine action_plugins...")
    
    cortex = CortexRuntime(Path('config/g1_production.json5'))
    await cortex.initialize()
    
    if cortex.conversation_engine:
        print('✅ ConversationEngine existe')
        print('📋 Action plugins:', list(cortex.conversation_engine.action_plugins.keys()))
        print('📋 Input plugins:', list(cortex.conversation_engine.input_plugins.keys()))
        
        # Verificar se tem os plugins essenciais
        required_actions = ['G1Speech', 'G1Arms', 'G1Emotion', 'G1Movement']
        for action in required_actions:
            status = "✅" if action in cortex.conversation_engine.action_plugins else "❌"
            print(f'{status} {action}: {action in cortex.conversation_engine.action_plugins}')
            
    else:
        print('❌ ConversationEngine é None')
        
    # Verificar ActionOrchestrator
    if cortex.action_orchestrator:
        print('📋 ActionOrchestrator actions:', list(cortex.action_orchestrator.actions.keys()))
    else:
        print('❌ ActionOrchestrator é None')

if __name__ == "__main__":
    asyncio.run(test())
