"""
Partial state update block. 

Here the partial state update blocks are configurated by setting
- policies
- variables

for each state update block individually
"""
from .parts.polimechs.liquidity_provision import *
from .parts.polimechs.arbitrage import *
from .parts.polimechs.accounting import *

partial_state_update_block = [
     {
        # main policy is to provide liquidity
        'policies': {
            'liquidity_provision': p_liquidity_provision,
            'accounting': p_accounting
        },
        'variables': {
            'agents': s_liquidity_provision,
            'state': s_accounting
        }
     }, 
     {
        # other policy is to seek for arbitrage 
        'policies': {
            'arbitrage': p_arbitrage
        },
        'variables': {
            'agents': s_arbitrage
        }
     }
 
]
