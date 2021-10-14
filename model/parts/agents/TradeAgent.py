import logging
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
        
@enforce_types
class TradeAgent(BaseAgent):
    def __init__(self, name: str, USD: float, ETH: float):
        super().__init__(name, USD, ETH)
        self.tradeDone = False
        self.tradeResult = (None, None)
        self._s_since_trade = 0
        self._s_between_trade = 10 * constants.S_PER_MIN #magic number
        
    def takeStep(self, state, pool_agents) -> Tuple:
        self._s_since_trade += state.ss.time_step
    
        if self._doTrade(state):
            self.tradeDone = True
            self._s_since_trade = 0
            tokenAmount = TokenAmount(random.choice([state.tokenA, state.tokenB]), random.randint(1, 10) )
            print("Trader trades with: ", tokenAmount)
            self.tradeResult = self._trade(state, pool_agents, tokenAmount)
        return self.tradeResult

    def _doTrade(self, state) -> bool:
        return self._s_since_trade >= self._s_between_trade

    def _trade(self, state, pool_agents, tokenAmount: TokenAmount) -> Tuple[PoolAgent, float]:
        print("Trader does trade at step: ", state.tick)
        pool_agent = random.choice(list(pool_agents.values()))
        output, new_pair_tokens = pool_agent.takeSwap(tokenAmount)
        volume = 0.0
        # adjust balances of wallet
        if tokenAmount.token.symbol == 'USDC':
            volume = tokenAmount.amount
            self.payUSD(volume)
            self.receiveETH(output.amount)
        else:
            volume = output.amount
            self.receiveUSD(volume)
            self.payETH(tokenAmount.amount)
        new_pair = Pair(new_pair_tokens[0], new_pair_tokens[1])
        pool_agent._pool.pair = new_pair
        return (pool_agent, volume)


