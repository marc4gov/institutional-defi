import logging

from model.SimState import SimState
log = logging.getLogger('marketagents')

from enforce_typing import enforce_types # type: ignore[import]
import random
from typing import Tuple, Optional
from .BaseAgent import BaseAgent
from .PoolAgent import PoolAgent
from .util import constants
# from util.constants import POOL_WEIGHT_DT, POOL_WEIGHT_OCEAN
from .web3engine.uniswappool import TokenAmount, Pair
from .web3tools.web3util import toBase18
from enum import Enum

class TradePolicy(Enum):
    TRADE_USD_ETH_USD = 1
    TRADE_ETH_USD_ETH = 2
    DO_NOTHING = 3

@enforce_types
class TradeAgent(BaseAgent):
    def __init__(self, name: str, USD: float, ETH: float):
        super().__init__(name, USD, ETH)
        self.tradeDone = False
        self.tradeResult = (None, None)
        self.slippage_tolerance = 0.5/100
        self.roi = random.randrange(2,5)/100
        self._s_since_trade = 0
        self._s_between_trade = random.randrange(10,15) # magic number
        
    def takeStep(self, state, pool_agents):
        self._s_since_trade += state.ss.time_step
    
        if self._doTrade(state):
            self.tradeDone = True
            self._s_since_trade = 0
    
            white_pool_agent = pool_agents['White Pool']
            grey_pool_agent = pool_agents['Grey Pool']
            
            (policy, tokenAmountA, pool_agent) = self._tradePolicy(state, white_pool_agent, grey_pool_agent)

            if policy == TradePolicy.TRADE_USD_ETH_USD:
                print("Trader trades with: ", tokenAmountA)
                self.lpResult = self._trade(state, pool_agent, tokenAmountA)
            if policy == TradePolicy.TRADE_ETH_USD_ETH:
                pass
            else:
                pass # DO_NOTHING

    def _doTrade(self, state) -> bool:
        return self._s_since_trade >= self._s_between_trade

    def _trade(self, state, pool_agent: PoolAgent, tokenAmount: TokenAmount) -> Tuple[PoolAgent, float]:
        # print("Trader does trade at step: ", state.tick)
        output, new_pair_tokens = pool_agent.takeSwap(tokenAmount)
        new_token0 = new_pair_tokens[0]
        new_token1 = new_pair_tokens[1]
        volume = 0.0
        # adjust balances of wallet
        if new_pair_tokens[0].token.symbol == state.tokenA.symbol:
            new_token0 = new_pair_tokens[0]
            new_token1 = new_pair_tokens[1]
            volume = tokenAmount.amount
            self.payUSD(volume)
            self.receiveETH(output.amount)
        else:
            new_token0 = new_pair_tokens[1]
            new_token1 = new_pair_tokens[0]
            volume = output.amount
            self.receiveUSD(volume)
            self.payETH(tokenAmount.amount)
        pool_agent._pool.pair.instantiate(new_token0, new_token1, pool_agent._pool.pair.liquidityToken)
        return (pool_agent, volume)

    def _tradePolicy(self, state: SimState, white_pool_agent: PoolAgent, grey_pool_agent: PoolAgent) -> Tuple[TradePolicy, TokenAmount, PoolAgent]:
        # trade direction USD -> ETH -> USD
        white_price_usd_to_eth = white_pool_agent._pool.pair.token0Price()
        print("white_price_usd_to_eth: ", white_price_usd_to_eth)
        grey_price_usd_to_eth = grey_pool_agent._pool.pair.token0Price()
        print("grey_price_usd_to_eth: ", grey_price_usd_to_eth)
        ratio = white_price_usd_to_eth/grey_price_usd_to_eth
        spread = 0.0
        if ratio > 1:
            spread = ratio - 1
        else:
            spread = 1 - ratio

        print("ratio: ", white_price_usd_to_eth/grey_price_usd_to_eth)
        
        # opportunity to swap ETH from white pool to ETH in grey pool
        if ratio <= 1 and spread >= 0.6/100: 
            trade_size = self.slippage_tolerance * 0.07 * white_pool_agent._pool.pair.reserve1().amount
            tradeAmount = TokenAmount(state.tokenB, trade_size)
            print("Trade token: ", tradeAmount)
            if self._wallet.ETH() < trade_size: return (TradePolicy.DO_NOTHING, tradeAmount, white_pool_agent) 
            (outputAmountA, slippageA) = self._getSlippage(white_pool_agent,tradeAmount)
            print("Slippage white: ", slippageA)
            if slippageA <= self.slippage_tolerance:
                (outputAmountB, slippageB) = self._getSlippage(grey_pool_agent, outputAmountA)
                profit = (outputAmountB.amount - trade_size)/trade_size
                print("Profit: ", profit)
                if profit >= self.roi:
                    return (TradePolicy.TRADE_USD_ETH_USD, tradeAmount, white_pool_agent)
            else:
                return (TradePolicy.DO_NOTHING, tradeAmount, white_pool_agent)
        # opportunity to swap ETH from grey pool to ETH in white pool
        if ratio > 1 and spread >= 0.6/100:
            trade_size = self.slippage_tolerance * 0.07 * grey_pool_agent._pool.pair.reserve1().amount
            tradeAmount = TokenAmount(state.tokenB, trade_size)
            print("Trade token: ", tradeAmount)
            if self._wallet.ETH() < trade_size: return (TradePolicy.DO_NOTHING, tradeAmount, grey_pool_agent) 
            (outputAmountA, slippageA) = self._getSlippage(grey_pool_agent,tradeAmount)
            print("Slippage grey: ", slippageA)
            if slippageA <= self.slippage_tolerance:
                (outputAmountB, slippageB) = self._getSlippage(white_pool_agent, outputAmountA)
                profit = (outputAmountB.amount - trade_size)/trade_size
                print("Profit: ", profit)
                if profit >= self.roi:
                    return (TradePolicy.TRADE_USD_ETH_USD, tradeAmount, grey_pool_agent)
            else:
                return (TradePolicy.DO_NOTHING, tradeAmount, grey_pool_agent)
        return (TradePolicy.DO_NOTHING, tradeAmount, grey_pool_agent)


    def _getSlippage(self, pool_agent: PoolAgent, inputAmount: TokenAmount) -> Tuple[TokenAmount, float]:
        slippage = 0.0
        pair = pool_agent._pool.pair
        token0 = pair.token0
        outputAmount, new_pair_tokens = pool_agent.takeSwap(inputAmount)
        new_pair = Pair(new_pair_tokens[0], new_pair_tokens[1])
        new_price_ratio = 0.0
        if inputAmount.token.symbol == token0.token.symbol:
            # USD
            old_price_ratio = pair.token1Price()
            if new_pair_tokens[0].token.symbol == token0.token.symbol:
                new_price_ratio = new_pair.token1Price()
            else:
                new_price_ratio = new_pair.token0Price()
            slippage = 1 - old_price_ratio/new_price_ratio if new_price_ratio != 0 else 1
        else:
            # ETH
            old_price_ratio = pair.token0Price()
            if new_pair_tokens[0].token.symbol == token0.token.symbol:
                new_price_ratio = new_pair.token0Price()
            else:
                new_price_ratio = new_pair.token1Price()
            print("old_price_ratio: ", old_price_ratio)
            print("new_price_ratio: ", new_price_ratio)        
            slippage = 1 - old_price_ratio/new_price_ratio if new_price_ratio != 0 else 1
        return (outputAmount, slippage)


