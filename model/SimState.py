import logging
log = logging.getLogger('simstate')

from enforce_typing import enforce_types # type: ignore[import]
from typing import Set
import requests

from .SimStrategy import SimStrategy
from .parts.agents.util import mathutil, valuation
from .parts.agents.util.mathutil import Range
from .parts.agents.util.constants import *
from .parts.agents.web3engine.uniswappool import Token
from .Kpis import KPIs

@enforce_types
class SimState(object):
    
    def __init__(self, ss: SimStrategy):
        log.debug("init:begin")
        
        #main
        self.ss = ss
        self.tick = 0

        self.tokenA = None
        self.tokenB = None
        self.white_pool_volume_USD: float = 0.0
        self.grey_pool_volume_USD: float = 0.0
        self._total_Liq_minted_White: float = 0.0
        self._total_Liq_minted_Grey: float = 0.0
        self._total_Liq_supply_White: float = 0.0
        self._total_Liq_supply_Grey: float = 0.0
        self._total_Liq_burned_White: float = 0.0
        self._total_Liq_burned_Grey: float = 0.0

        #used to manage names
        self._next_free_marketplace_number = 0

        #used to add agents
        self._marketplace_tick_previous_add = 0

        #<<Note many magic numbers below, for simplicity>>
        #note: KPIs class also has some magic number

        self._percent_burn: float = 0.05 #to burning, vs to DAO #magic number

        self._speculation_valuation = 5e6 #in USD #magic number
        self._percent_increase_speculation_valuation_per_s = 0.10 / S_PER_YEAR # ""

        # #track certain metrics over time, so that we don't have to load
        self.kpis = KPIs(self.ss.time_step)

        log.debug("init: end")
            
    def takeStep(self, agents) -> None:
        """This happens once per tick"""
        self.tick += 1
        #update global state values: revenue, valuation
        self.kpis.takeStep(self, agents)

        #update global state values: other
        self._speculation_valuation *= (1.0 + self._percent_increase_speculation_valuation_per_s * self.ss.time_step)

    
    def percentToBurn(self) -> float:
        return self._percent_burn
    
    def tokenPrice(self, token:Token) -> float:
        r0 = requests.get("https://min-api.cryptocompare.com/data/price?fsym=" + token.symbol + "&tsyms=USD")
        return r0.json()['USD']

    #==============================================================
    def OCEANprice(self) -> float:
        """Estimated price of $OCEAN token, in USD"""
        price = valuation.OCEANprice(self.overallValuation(),
                                     self.OCEANsupply())
        assert price > 0.0
        return price
    
    #==============================================================
    def overallValuation(self) -> float: #in USD
        v = self.fundamentalsValuation() + \
            self.speculationValuation()
        assert v > 0.0
        return v
    
    def fundamentalsValuation(self) -> float: #in USD
        return self.kpis.valuationPS(30.0) #based on P/S=30                     #magic number
    
    def speculationValuation(self) -> float: #in USD
        return self._speculation_valuation
        
    #==============================================================
    def OCEANsupply(self) -> float:
        """Current OCEAN token supply"""
        return self.initialOCEAN() \
            + self.totalOCEANminted() \
            - self.totalOCEANburned()
        
    def initialOCEAN(self) -> float:
        return INIT_OCEAN_SUPPLY
        
    def totalOCEANminted(self) -> float:
        return self._total_OCEAN_minted
        
    def totalOCEANburned(self) -> float:
        return self._total_OCEAN_burned
        
    def totalOCEANburnedUSD(self) -> float:
        return self._total_OCEAN_burned_USD
    
    def getAgent(self, agents, name):
        return agents[name]


def funcOne():
    return 1.0

