import logging
log = logging.getLogger('wallet')

from enforce_typing import enforce_types # type: ignore[import]
import typing

# from web3engine import bpool, datatoken, globaltokens
from util import constants 
from util.strutil import asCurrency
# from web3tools import web3util, web3wallet
# from web3tools.web3util import fromBase18, toBase18

@enforce_types
class AgentWallet:
    """An AgentWallet holds balances of USD and other assets for a given Agent.

    """

    def __init__(self, USD:float=0.0, ETH:float=0.0):
        
        #USDC
        self._USD = USD
        self._ETH = ETH
        
    #=================================================================== 
    #USD-related   
    def USD(self) -> float:
        return self._USD
        
    def depositUSD(self, amt: float) -> None:
        assert amt >= 0.0
        self._USD += amt
        
    def withdrawUSD(self, amt: float) -> None:
        assert amt >= 0.0
        if amt > 0.0 and self._USD > 0.0:
            tol = 1e-12
            if (1.0 - tol) <= amt/self._USD <= (1.0 + tol):
                self._USD = amt #avoid floating point roundoff
        if amt > self._USD:
            amt = round(amt, 12)
        if amt > self._USD:
            raise ValueError("USD withdraw amount (%s) exceeds holdings (%s)"
                             % (amt, self._USD))
        self._USD -= amt

    #=================================================================== 
    #ETH-related   
    def ETH(self) -> float:
        return self._ETH
        
    def depositETH(self, amt: float) -> None:
        assert amt >= 0.0
        self._ETH += amt
        
    def withdrawETH(self, amt: float) -> None:
        assert amt >= 0.0
        if amt > 0.0 and self._ETH > 0.0:
            tol = 1e-12
            if (1.0 - tol) <= amt/self._ETH <= (1.0 + tol):
                self._ETH = amt #avoid floating point roundoff
        if amt > self._ETH:
            amt = round(amt, 12)
        if amt > self._ETH:
            raise ValueError("USD withdraw amount (%s) exceeds holdings (%s)"
                             % (amt, self._ETH))
        self._ETH -= amt

        
        
    def UNI(self, pool:bpool.UNIPool) -> float:
        return fromBase18(self._UNI_base(pool))
    
    def _UNI_base(self, pool:unipool.UNIPool) -> int:
        return pool.balanceOf_base(self._id)
                
    def stakeOCEAN(self, OCEAN_stake:float, pool:bpool.BPool):
        OCEAN = globaltokens.OCEANtoken()
        OCEAN.approve(pool.address, toBase18(OCEAN_stake),
                      from_wallet=self._web3wallet)
        pool.joinswapExternAmountIn(
            tokenIn_address=globaltokens.OCEAN_address(),
            tokenAmountIn_base=toBase18(OCEAN_stake),
            minPoolAmountOut_base=toBase18(0.0),
            from_wallet=self._web3wallet)
        self._cached_OCEAN_base = None #reset due to write action
        
    def unstakeOCEAN(self, BPT_unstake:float, pool:bpool.BPool):
        pool.exitswapPoolAmountIn(
            tokenOut_address=globaltokens.OCEAN_address(),
            poolAmountIn_base=toBase18(BPT_unstake),
            minAmountOut_base=toBase18(0.0),
            from_wallet=self._web3wallet)
        self._cached_OCEAN_base = None #reset due to write action

        
        
    #===================================================================
    def __str__(self) -> str:
        s = []
        s += ["AgentWallet={\n"]
        s += ['USD=%s' % asCurrency(self.USD())]
        s += ['; ETH=%.6f' % self.ETH()]
        s += [" /AgentWallet}"]
        return "".join(s)

