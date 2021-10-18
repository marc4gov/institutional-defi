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
    """Provides and burns liquidity"""
    
    def __init__(self, name: str, USD: float, ETH: float):
        super().__init__(name, USD, ETH)
        self.liquidityToken = {}
        self.lpDone = False
        self.lpResult = (None, None)

        self._s_since_lp = 0
        self._s_between_lp = 4 * constants.S_PER_MIN #magic number
        self._s_since_burn = 0
        self._s_between_burn = 4 * constants.S_PER_MIN #magic number
        
    def takeStep(self, state, pool_agents):
        self._s_since_lp += state.ss.time_step
        if self._doLPAction(state):
            self.lpDone = True
            self._s_since_lp = 0
            tokenAmountA = TokenAmount(state.tokenA, 2000 )
            tokenAmountB = TokenAmount(state.tokenB, 1 )
            
            # print("LP agent provides with: ", tokenAmountA, tokenAmountB)
            self.lpResult = self._provide(state, pool_agents, tokenAmountA, tokenAmountB)
        if self._doBurnAction(state):
            self.burnDone = True
            self._s_since_burn = 0
            
            # print("LP agent provides with: ", tokenAmountA, tokenAmountB)
            self.lpResult = self._provide(state, pool_agents, tokenAmountA, tokenAmountB)

    def _doLPAction(self, state):
        return self._s_since_lp >= self._s_between_lp

    def _doBurnAction(self, state):
        return self._s_since_burn >= self._s_between_burn

    def _provide(self, state, pool_agents, tokenAmountA, tokenAmountB) -> Tuple[PoolAgent, float]:
        # print("LP agent provides liquidity at step: ", state.tick)

        pool_agent = random.choice(list(pool_agents.values()))
        liquidityMinted = pool_agent.takeLiquidity(tokenAmountA, tokenAmountB)
        self.liquidityToken[pool_agent.name] = liquidityMinted
        
        volume = tokenAmountA.amount
        # adjust balances of agent wallet
        self.payUSD(volume)
        self.payETH(tokenAmountB.amount)

        # # adjust the new pool balance and liquidity
        # pair = pool_agent._pool.pair
        # new_amount0 = pair.token0.amount + tokenAmountA.amount
        # new_amount1 = pair.token1.amount + tokenAmountB.amount
        
        # new_pair= Pair(TokenAmount(pair.token0.token, new_amount0), TokenAmount(pair.token1.token, new_amount1))
        
        # # should we do this?
        # new_pair.txCount = pair.txCount + 1
        
        # new_pair.liquidityToken = TokenAmount(pair.liquidityToken.token, pair.liquidityToken.amount + liquidityMinted.amount) 
        pool_agent._pool.pair = self._adjustPoolBalance(pool_agent, tokenAmountA, tokenAmountB, liquidityMinted)

        return (pool_agent, liquidityMinted.amount)

    def _burn(self, state, pool_agents, liquidityAmount) -> Tuple[PoolAgent, float]:
        print("LP agent burns liquidity at step: ", state.tick)

        pool_agent = random.choice(list(pool_agents.values()))
        
        pair = pool_agent._pool.pair
        pool_agent_liquidity = pair.liquidityToken

        volume = liquidityAmount.amount
        share = volume/pool_agent_liquidity.amount
        usd_share = share * pair.token0.amount
        eth_share = share * pair.token1.amount
        # adjust balances of agent wallet
        self.receiveUSD(usd_share)
        self.receiveETH(eth_share)

        # # adjust the new pool balance and liquidity
        # pair = pool_agent._pool.pair
        # new_amount0 = pair.token0.amount - usd_share
        # new_amount1 = pair.token1.amount - eth_share
        
        # new_pair= Pair(TokenAmount(pair.token0.token, new_amount0), TokenAmount(pair.token1.token, new_amount1))
        
        # # should we do this?
        # new_pair.txCount = pair.txCount + 1
        
        # new_pair.liquidityToken = TokenAmount(pair.liquidityToken.token, pair.liquidityToken.amount - liquidityAmount.amount) 
        # pool_agent._pool.pair = new_pair
        pool_agent._pool.pair = self._adjustPoolBalance(pool_agent, TokenAmount(pair.token0.token, - usd_share), TokenAmount(pair.token1.token, - eth_share), - liquidityAmount)
        return (pool_agent, liquidityAmount.amount)

    def _adjustPoolBalance(pool_agent: PoolAgent, tokenAmountA, tokenAmountB, liquidityAmount, burn=False) -> Pair:
        # adjust the new pool balance and liquidity
        pair = pool_agent._pool.pair
        new_amount0 = pair.token0.amount + tokenAmountA.amount
        new_amount1 = pair.token1.amount + tokenAmountB.amount
        
        new_pair= Pair(TokenAmount(pair.token0.token, new_amount0), TokenAmount(pair.token1.token, new_amount1))
        
        # should we do this?
        new_pair.txCount = pair.txCount + 1
        
        new_pair.liquidityToken = TokenAmount(pair.liquidityToken.token, pair.liquidityToken.amount + liquidityAmount.amount) 
        return new_pair

        
            
