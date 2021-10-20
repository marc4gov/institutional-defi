"""
Model initial state.
"""

# Dependencies

import random
import uuid
import logging
log = logging.getLogger('simstate')

from enforce_typing import enforce_types # type: ignore[import]
from typing import Set

from .parts.agents.TradeAgent import TradeAgent
from .parts.agents.LiquidityProviderAgent import LiquidityProviderAgent
from .parts.agents.PoolAgent import PoolAgent

from .SimStrategy import SimStrategy
from .SimState import SimState, funcOne
from .parts.agents.util import mathutil, valuation
from .parts.agents.util.mathutil import Range
from .parts.agents.util.constants import *

from .parts.agents.web3engine.uniswappool import Token, TokenAmount, Pair, UniswapPool

import numpy as np
import names
from typing import Tuple, List, Dict
from itertools import cycle
from enum import Enum
import uuid

MAX_DAYS = 3660
OUTPUT_DIR = 'output_test'

ss = SimStrategy()
ss.setMaxTicks(MAX_DAYS * S_PER_DAY / ss.time_step + 1)
    
simState = SimState(ss)

# init agents
# initial_agents = AgentDict()
initial_agents = {}

# set op the Uniswap pools
tokenA = Token(uuid.uuid4(), 'USDC', 'USDC token')
tokenB = Token(uuid.uuid4(), 'ETH', 'Ethereum token')
simState.tokenA = tokenA
simState.tokenB = tokenB

white_pool_pair = Pair(TokenAmount(tokenA, 200000), TokenAmount(tokenB, 100))
grey_pool_pair = Pair(TokenAmount(tokenA, 3000000), TokenAmount(tokenB, 1500))

white_pool = UniswapPool('White pool', white_pool_pair)
grey_pool = UniswapPool('Grey pool', grey_pool_pair)

#Instantiate and connnect agent instances. "Wire up the circuit"
new_agents = list()

new_agents.append(PoolAgent(
    name = "White Pool", pool = white_pool))

new_agents.append(PoolAgent(
    name = "Grey Pool", pool = grey_pool))

for i in range(20):
    new_agents.append(TradeAgent(
        name = "Trader " + names.get_first_name(), USD=100000.0, ETH=500.0))
    i += 1

for i in range(10):
    new_agents.append(LiquidityProviderAgent(
        name = "Liquidity Provider " + names.get_first_name(), USD=200000.0, ETH=1000.0, white=white_pool_pair.liquidityToken.token, grey=grey_pool_pair.liquidityToken.token))
    i += 1

for agent in new_agents:
    initial_agents[agent.name] = agent
    print(agent)

from collections import defaultdict

initial_state = {
    'agents': initial_agents,
    'state': simState
}
