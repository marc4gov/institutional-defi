import logging
log = logging.getLogger('marketagents')

from enforce_typing import enforce_types # type: ignore[import]
import random

from .BaseAgent import BaseAgent
# from web3engine import bfactory, bpool, btoken, datatoken, dtfactory
# from web3tools.web3util import toBase18
from .util import constants
                    
@enforce_types
class LiquidityProviderAgent(BaseAgent):
    """Provides and removes liquidity"""
    
    def __init__(self, name: str, USD: float, ETH: float):
        super().__init__(name, USD, ETH)

        self._s_since_lp = 0
        self._s_between_lp = 4 * constants.S_PER_MIN #magic number
        
    def takeStep(self, state, pool_agents):
        self._s_since_lp += state.ss.time_step
        if self._doLPAction(state):
            self._s_since_lp = 0
            self._lpAction(state, pool_agents)

    def _doLPAction(self, state):
        return self._s_since_lp >= self._s_between_lp

    def _lpAction(self, state, pool_agents):
        print("LP agent provides liquidity at step: ", state.tick)


        # new_amount0 = pair.token0.token.amount + tokenAmount0.amount
        # new_amount1 = pair.token1.token.amount + tokenAmount1.amount
        
        # new_pair= Pair(TokenAmount(pair.token0.token, new_amount0), TokenAmount(pair.token1.token, new_amount1))
        
        # # should we do this?
        # new_pair.txCount = pair.txCount + 1
        
        # new_pair.liquidityToken = TokenAmount(pair.liquidityToken.token, pair.liquidityToken.amount + liquidity.amount) 
        # self._pool.pair = new_pair

        # pool_agents = state.agents.filterToPool().values()
        # assert pool_agents, "need pools to be able to provide liquidity"
        
        # pool = random.choice(list(pool_agents)).pool

        
            
