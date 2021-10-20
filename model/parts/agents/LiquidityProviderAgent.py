import logging
log = logging.getLogger('marketagents')

from enforce_typing import enforce_types # type: ignore[import]
import random
from typing import Tuple, Optional
from .BaseAgent import BaseAgent
from .PoolAgent import PoolAgent

from .web3engine.uniswappool import Token, TokenAmount, Pair
# from web3engine import bfactory, bpool, btoken, datatoken, dtfactory
# from web3tools.web3util import toBase18
from .util import constants

from enum import Enum

class Policy(Enum):
    PROVIDE = 1
    BURN = 2
    DO_NOTHING = 3

@enforce_types
class LiquidityProviderAgent(BaseAgent):
    """Provides and burns liquidity"""
    
    def __init__(self, name: str, USD: float, ETH: float, white: Token, grey: Token):
        super().__init__(name, USD, ETH)
        self.liquidityToken = {'White Pool': TokenAmount(white, 0.0), 'Grey Pool': TokenAmount(grey, 0.0)}
        self.lpDone = False
        self.lpResult = (None, None)
        self.roi = random.randrange(10,20)/100
        self.treshold = 1000

        self._s_since_lp = 0
        self._s_between_lp = random.randrange(20, 30) #magic number
        
    def takeStep(self, state, pool_agents):
        self._s_since_lp += state.ss.time_step

        if self._doLPAction(state):
            self.lpDone = True
            self._s_since_lp = 0
    
            white_pool_agent = pool_agents['White Pool']
            grey_pool_agent = pool_agents['Grey Pool']
            
            (policy, tokenAmountA, pool_agent) = self._lpPolicy(state, white_pool_agent, grey_pool_agent)

            tokenAmountB = TokenAmount(pool_agent._pool.pair.token1.token, pool_agent._pool.pair.token0Price() * tokenAmountA.amount)
            if policy == Policy.PROVIDE:
                self.lpResult = self._provide(state, pool_agent, tokenAmountA, tokenAmountB)
            if policy == Policy.BURN:
                self.lpResult = self._burn(state, pool_agent, tokenAmountA)
            else:
                pass # DO_NOTHING


    def _doLPAction(self, state):
        return self._s_since_lp >= self._s_between_lp

    def _provide(self, state, pool_agent, tokenAmountA : TokenAmount, tokenAmountB: TokenAmount) -> Tuple[PoolAgent, float]:
        # print("LP agent provides liquidity at step: ", state.tick)

        # top up liquidity share
        liquidityMinted = pool_agent.takeLiquidity(tokenAmountA, tokenAmountB)
        self.liquidityToken[pool_agent.name].amount += liquidityMinted.amount
        
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

    def _burn(self, state, pool_agent, tokenAmountA) -> Tuple[PoolAgent, float]:
        print("LP agent burns liquidity at step: ", state.tick)
        
        pair = pool_agent._pool.pair
        pool_agent_liquidity = pair.liquidityToken
        pool_volume_usd = pair.token0.amount

        volume_to_burn = tokenAmountA.amount
        share = volume_to_burn/pool_volume_usd
        usd_share = share * pair.token0.amount
        eth_share = share * pair.token1.amount
        # adjust balances of agent wallet
        self.receiveUSD(usd_share)
        self.receiveETH(eth_share)

        # burn the liquidity tokens
        lAmount = share * pool_agent_liquidity.amount
        old_liquidity_amount = self.liquidityToken[pool_agent.name].amount
        new_liquidity_amount = old_liquidity_amount - lAmount
    
        self.liquidityToken[pool_agent.name].amount = new_liquidity_amount
        liquidityBurned= TokenAmount(pool_agent_liquidity.token, lAmount)
        # # adjust the new pool balance and liquidity
        # pair = pool_agent._pool.pair
        # new_amount0 = pair.token0.amount - usd_share
        # new_amount1 = pair.token1.amount - eth_share
        
        # new_pair= Pair(TokenAmount(pair.token0.token, new_amount0), TokenAmount(pair.token1.token, new_amount1))
        
        # # should we do this?
        # new_pair.txCount = pair.txCount + 1
        
        # new_pair.liquidityToken = TokenAmount(pair.liquidityToken.token, pair.liquidityToken.amount - liquidityAmount.amount) 
        # pool_agent._pool.pair = new_pair
        pool_agent._pool.pair = self._adjustPoolBalance(pool_agent, TokenAmount(pair.token0.token, - usd_share), TokenAmount(pair.token1.token, - eth_share), liquidityBurned, True)
        return (pool_agent, liquidityBurned.amount)

    def _adjustPoolBalance(self, pool_agent: PoolAgent, tokenAmountA, tokenAmountB, liquidityAmount, burn=False) -> Pair:
        # adjust the new pool balance and liquidity
        pair = pool_agent._pool.pair
        new_amount0 = pair.token0.amount + tokenAmountA.amount
        new_amount1 = pair.token1.amount + tokenAmountB.amount
        
        new_pair= Pair(TokenAmount(pair.token0.token, new_amount0), TokenAmount(pair.token1.token, new_amount1))
        
        # should we do this?
        new_pair.txCount = pair.txCount + 1
        if burn:
            new_pair.liquidityToken = TokenAmount(pair.liquidityToken.token, pair.liquidityToken.amount - liquidityAmount.amount)
        else:
            new_pair.liquidityToken = TokenAmount(pair.liquidityToken.token, pair.liquidityToken.amount + liquidityAmount.amount)
        
        return new_pair

    def _lpPolicy(self, state, white_pool_agent: PoolAgent, grey_pool_agent: PoolAgent) -> Tuple[Policy, TokenAmount, PoolAgent]:
        days_elapsed = state.tick/(state.ss.time_step * constants.S_PER_DAY)
        expected_fees_white_per_year = 365 * white_pool_agent._pool.swap_fee * state.white_pool_volume_USD/days_elapsed
        expected_fees_grey_per_year = 365 * grey_pool_agent._pool.swap_fee * state.grey_pool_volume_USD/days_elapsed
        my_volume_usd = self._wallet.USD()
        my_liquidity = self.liquidityToken

        roi_white = my_volume_usd/expected_fees_white_per_year if expected_fees_white_per_year != 0 else 0
        roi_grey = my_volume_usd/expected_fees_grey_per_year if expected_fees_grey_per_year != 0 else 0
        amount = TokenAmount(state.tokenA, my_volume_usd * random.randrange(15,20)/100)
        if max(roi_white, roi_grey) >= self.roi and my_volume_usd > self.treshold:
            if roi_white > roi_grey:
                return (Policy.PROVIDE, amount, white_pool_agent)
            else:
                return (Policy.PROVIDE, amount, grey_pool_agent)
        if min(roi_white, roi_grey) < self.roi:
            if roi_white < roi_grey and my_liquidity[white_pool_agent.name].amount < self._defineLiquidityTreshold(white_pool_agent, 0.80):
                return (Policy.BURN, amount, white_pool_agent)
            if roi_white >= roi_grey and my_liquidity[grey_pool_agent.name].amount < self._defineLiquidityTreshold(grey_pool_agent, 0.80):
                return (Policy.BURN, amount, grey_pool_agent)
        return (Policy.DO_NOTHING, amount, grey_pool_agent)

    def _defineLiquidityTreshold(self, pool_agent, percentage) -> float:
        pair = pool_agent._pool.pair
        pool_agent_liquidity = pair.liquidityToken
        pool_volume_usd = pair.token0.amount
        pool_share = self.liquidityToken[pool_agent.name]
        share_in_usd = pool_volume_usd * pool_share.amount/pool_agent_liquidity.amount
        return share_in_usd * percentage
        
        
        
