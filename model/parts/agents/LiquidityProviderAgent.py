import logging
log = logging.getLogger('marketagents')

from enforce_typing import enforce_types # type: ignore[import]
import random
from typing import Tuple, Optional
from .BaseAgent import BaseAgent
from .PoolAgent import PoolAgent

from .web3engine.uniswappool import TokenAmount, Pair
# from web3engine import bfactory, bpool, btoken, datatoken, dtfactory
# from web3tools.web3util import toBase18
from .util import constants
                    
@enforce_types
class LiquidityProviderAgent(BaseAgent):
    """Provides and removes liquidity"""
    
    def __init__(self, name: str, USD: float, ETH: float):
        super().__init__(name, USD, ETH)
        self.liquidityToken = {}
        self._s_since_lp = 0
        self._s_between_lp = 4 * constants.S_PER_MIN #magic number
        
    def takeStep(self, state, pool_agents):
        self._s_since_lp += state.ss.time_step
        if self._doLPAction(state):
            self._s_since_lp = 0
            tokenAmountA = TokenAmount(state.tokenA, 2000 )
            tokenAmountB = TokenAmount(state.tokenB, 1 )
            
            print("LP agent provides with: ", tokenAmountA, tokenAmountB)
            self._provide(state, pool_agents, tokenAmountA, tokenAmountB)

    def _doLPAction(self, state):
        return self._s_since_lp >= self._s_between_lp

    def _provide(self, state, pool_agents, tokenAmountA, tokenAmountB) -> PoolAgent:
        print("LP agent provides liquidity at step: ", state.tick)

        pool_agent = random.choice(list(pool_agents.values()))
        liquidityMinted = pool_agent.takeLiquidity(tokenAmountA, tokenAmountB)
        self.liquidityToken[pool_agent.name] = liquidityMinted
        
        # adjust balances of agent wallet
        self.payUSD(tokenAmountA.amount)
        self.payETH(tokenAmountB.amount)

        # adjust the new pool balance and liquidity
        pair = pool_agent._pool.pair
        new_amount0 = pair.token0.amount + tokenAmountA.amount
        new_amount1 = pair.token1.amount + tokenAmountB.amount
        
        new_pair= Pair(TokenAmount(pair.token0.token, new_amount0), TokenAmount(pair.token1.token, new_amount1))
        
        # should we do this?
        new_pair.txCount = pair.txCount + 1
        
        new_pair.liquidityToken = TokenAmount(pair.liquidityToken.token, pair.liquidityToken.amount + liquidityMinted.amount) 
        pool_agent._pool.pair = new_pair

        return pool_agent


        
            
