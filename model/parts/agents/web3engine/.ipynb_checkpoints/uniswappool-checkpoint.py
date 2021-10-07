from enforce_typing import enforce_types # type: ignore[import]
import typing
import requests

# from web3tools import web3util, web3wallet
# from .btoken import BToken

class Token():
    def __init__(self, token_id: str, symbol: str, name: str):
        self.token_id = token_id
        self.symbol = symbol
        self.name = name

class Pair():
    def __init__(self, pid: str, token0: Token, token1: Token, reserve0: float, reserve1: float, 
                token0Price: float, token1Price: float, volumeUSD: float, txCount: int):
        self.pid = pid
        self.token0 = token0
        self.token1 = token1
        self.reserve0 = reserve0
        self.reserve1 = reserve1
        
        r0 = requests.get("https://min-api.cryptocompare.com/data/price?fsym=" + token0.symbol + "&tsyms=USD")
        res0USD = r0.json()['USD']
        r1 = requests.get("https://min-api.cryptocompare.com/data/price?fsym=" + token1.symbol + "&tsyms=USD")
        res1USD = r1.json()['USD']
        self.reserveUSD = res0 + res1
        self.token0Price = reserve0/reserve1
        self.token1Price = reserve1/reserve0
        self.volumeUSD = self.reserveUSD
        self.txCount = 1
        
class User():
    def __init__(self, uid: str, liquidityPositions: [LiquidityPosition], usdSwapped: int):
        self.uid = uid
        self.liquidityPositions = liquidityPositions
        self.usdSwapped = usdSwapped
        
class LiquidityPosition():
    def __init__(self, lid: str, user: User, pair: Pair, liquidityTokenBalance: int):
        self.uid = lid
        self.user = user
        self.pair = pair
        self.liquidityTokenBalance = liquidityTokenBalance
        
class Transaction():
    def __init__(self, transaction_id: str, timestamp: int, mints: [Mint], burns: [Burn], swaps: [Swap]):
        self.transaction_id = transaction_id
        self.timestamp = timestamp
        self.mints = mints
        self.burns = burns
        self.swaps = swaps

class Mint():
    def __init__(self, transaction: Transaction, timestamp: int, pair: Pair, to: User, liquidity: float,
                sender: User, amount0: float, amount1: float, feeTo: User, feeLiquidity: float):
        self.transaction = transaction
        self.timestamp = timestamp
        self.pair = pair
        self.to = to
        self.liquidity = liquidity
        self.sender = sender
        self.amount0 = amount0
        self.amount1 = amount1
        self.feeTo = feeTo
        self.feeLiquidity = feeLiquidity
        
class Burn():
    def __init__(self, transaction: Transaction, timestamp: int, pair: Pair, to: User, liquidity: float,
                sender: User, amount0: float, amount1: float, feeTo: User, feeLiquidity: float):
        self.transaction = transaction
        self.timestamp = timestamp
        self.pair = pair
        self.to = to
        self.liquidity = liquidity
        self.sender = sender
        self.amount0 = amount0
        self.amount1 = amount1
        self.feeTo = feeTo
        self.feeLiquidity = feeLiquidity

class Swap():
    def __init__(self, transaction: Transaction, timestamp: int, pair: Pair,
                sender: User, amount0In: float, amount1In: float, amount0Out: float, amount1Out: float, to: User):
        self.transaction = transaction
        self.timestamp = timestamp
        self.pair = pair
        self.sender = sender
        self.amount0In = amount0In
        self.amount1In = amount1In
        self.amount0Out = amount0Out
        self.amount1Out = amount1Out      
        self.to = to
        
        
@enforce_types
class UniswapPool():
    def __init__(self, name: str, pair: Pair):
        self.name = name
        self._wallet = AgentWallet.AgentWallet(0, 0)
        self.pair = pair
        self.swap_fee = 0.003

    def __str__(self):
        s = []
        s += ["UniswapPool:"]
        s += [f"  name={self.name}"]
        s += ["  swapFee = %.2f%%" % (swap_fee * 100.0)]
        cur_symbols = [self.pair.token0.symbol, self.pair.token1.symbol]
        s += [f"  currentTokens (as symbols) = {', '.join(cur_symbols)}"] 
        s += [f"  balances:"]
        s += [f"    {self.pair.token0.symbol}: {self.pair.reserve0}"]
        s += [f"    {self.pair.token1.symbol}: {self.pair.reserve1}"]
        return "\n".join(s)

        
    #==== Price Functions

    def getSpotPrice(self) -> (float, float):
        return (self.token0Price, self.token1Price)

    #==== Trading and Liquidity Functions

    def joinPool(
            self,
            poolAmountOut_base: int,
            maxAmountsIn_base: typing.List[int],
            from_wallet: web3wallet.Web3Wallet):
        """
        Join the pool, getting `poolAmountOut` pool tokens. This will pull some
        of each of the currently trading tokens in the pool, meaning you must 
        have called `approve` for each token for this pool. These values are
        limited by the array of `maxAmountsIn` in the order of the pool tokens.
        """
        func = self.f.joinPool(poolAmountOut_base, maxAmountsIn_base)
        return web3wallet.buildAndSendTx(func, from_wallet)

    def exitPool(
            self,
            poolAmountIn_base: int,
            minAmountsOut_base : typing.List[int],
            from_wallet: web3wallet.Web3Wallet):
        """
        Exit the pool, paying `poolAmountIn` pool tokens and getting some of 
        each of the currently trading tokens in return. These values are 
        limited by the array of `minAmountsOut` in the order of the pool tokens.
        """
        func = self.f.exitPool(poolAmountIn_base, minAmountsOut_base)
        return web3wallet.buildAndSendTx(func, from_wallet)
        
    def swapExactAmountIn(
            self,
            tokenIn_address: str,
            tokenAmountIn_base: int,
            tokenOut_address: str,
            minAmountOut_base: int,
            maxPrice_base: int,
            from_wallet: web3wallet.Web3Wallet):
        """
        Trades an exact `tokenAmountIn` of `tokenIn` taken from the caller by 
        the pool, in exchange for at least `minAmountOut` of `tokenOut` given 
        to the caller from the pool, with a maximum marginal price of 
        `maxPrice`.
        
        Returns `(tokenAmountOut`, `spotPriceAfter)`, where `tokenAmountOut` 
        is the amount of token that came out of the pool, and `spotPriceAfter`
        is the new marginal spot price, ie, the result of `getSpotPrice` after
        the call. (These values are what are limited by the arguments; you are 
        guaranteed `tokenAmountOut >= minAmountOut` and 
        `spotPriceAfter <= maxPrice)`.
        """
        func = self.f.swapExactAmountIn(
            tokenIn_address, tokenAmountIn_base,
            tokenOut_address, minAmountOut_base, maxPrice_base)
        return web3wallet.buildAndSendTx(func, from_wallet)
        
    def swapExactAmountOut(
            self,
            tokenIn_address: str,
            maxAmountIn_base: int,
            tokenOut_address: str,
            tokenAmountOut_base: int,
            maxPrice_base: int,
            from_wallet: web3wallet.Web3Wallet):
        func = self.f.swapExactAmountOut(
            tokenIn_address, maxAmountIn_base, tokenOut_address,
            tokenAmountOut_base, maxPrice_base)
        return web3wallet.buildAndSendTx(func, from_wallet)

    def joinswapExternAmountIn(
            self,
            tokenIn_address: str,
            tokenAmountIn_base: int,
            minPoolAmountOut_base: int,
            from_wallet: web3wallet.Web3Wallet):
        """
        Pay `tokenAmountIn` of token `tokenIn` to join the pool, getting
        `poolAmountOut` of the pool shares.
        """
        func = self.f.joinswapExternAmountIn(
            tokenIn_address, tokenAmountIn_base, minPoolAmountOut_base)
        return web3wallet.buildAndSendTx(func, from_wallet)
                  
    def joinswapPoolAmountOut(
            self,
            tokenIn_address: str,
            poolAmountOut_base: int,
            maxAmountIn_base: int,
            from_wallet: web3wallet.Web3Wallet):
        """
        Specify `poolAmountOut` pool shares that you want to get, and a token
        `tokenIn` to pay with. This costs `maxAmountIn` tokens (these went 
        into the pool).
        """
        func = self.f.joinswapPoolAmountOut(
            tokenIn_address, poolAmountOut_base, maxAmountIn_base)
        return web3wallet.buildAndSendTx(func, from_wallet)

    def exitswapPoolAmountIn(
            self,
            tokenOut_address: str,
            poolAmountIn_base: int,
            minAmountOut_base: int,
            from_wallet: web3wallet.Web3Wallet):
        """
        Pay `poolAmountIn` pool shares into the pool, getting `tokenAmountOut` 
        of the given token `tokenOut` out of the pool.
        """
        func = self.f.exitswapPoolAmountIn(
            tokenOut_address, poolAmountIn_base, minAmountOut_base)
        return web3wallet.buildAndSendTx(func, from_wallet)
        
    def exitswapExternAmountOut(
            self,
            tokenOut_address: str,
            tokenAmountOut_base: int,
            maxPoolAmountIn_base: int,
            from_wallet: web3wallet.Web3Wallet):
        """
        Specify `tokenAmountOut` of token `tokenOut` that you want to get out
        of the pool. This costs `poolAmountIn` pool shares (these went into 
        the pool).
        """
        func = self.f.exitswapExternAmountOut(
            tokenOut_address, tokenAmountOut_base, maxPoolAmountIn_base)
        return web3wallet.buildAndSendTx(func, from_wallet)
        

    #===== Calculators
    def calcSpotPrice_base(
            self,
            tokenBalanceIn_base: int,
            tokenWeightIn_base : int,
            tokenBalanceOut_base: int,
            tokenWeightOut_base : int,
            swapFee_base : int) -> int:
        """Returns spotPrice_base"""
        return self.f.calcSpotPrice(
            tokenBalanceIn_base, tokenWeightIn_base, tokenBalanceOut_base,
            tokenWeightOut_base, swapFee_base).call()

    def calcOutGivenIn_base(
            self,
            tokenBalanceIn_base: int,
            tokenWeightIn_base : int,
            tokenBalanceOut : int,
            tokenWeightOut_base : int,
            tokenAmountIn_base : int,
            swapFee_base : int) -> int:
        """Returns tokenAmountOut_base"""
        return self.f.calcOutGivenIn(
            tokenBalanceIn_base, tokenWeightIn_base, tokenBalanceOut, 
            tokenWeightOut_base, tokenAmountIn_base, swapFee_base).call()
                       
    def calcInGivenOut_base(
            self,
            tokenBalanceIn_base: int,
            tokenWeightIn_base : int,
            tokenBalanceOut_base : int,
            tokenWeightOut_base : int,
            tokenAmountOut_base: int,
            swapFee_base: int) -> int:
        """Returns tokenAmountIn_base"""
        return self.f.calcInGivenOut(
            tokenBalanceIn_base, tokenWeightIn_base, tokenBalanceOut_base,
            tokenWeightOut_base, tokenAmountOut_base, swapFee_base).call()
    
    def calcPoolOutGivenSingleIn_base(
            self,
            tokenBalanceIn_base: int,
            tokenWeightIn_base: int,
            poolSupply_base: int,
            totalWeight_base: int,
            tokenAmountIn_base: int,
            swapFee_base: int) -> int:
        """Returns poolAmountOut_base"""
        return self.f.calcPoolOutGivenSingleIn(
            tokenBalanceIn_base, tokenWeightIn_base, poolSupply_base,
            totalWeight_base, tokenAmountIn_base, swapFee_base).call()
    
    def calcSingleInGivenPoolOut_base(
            self,
            tokenBalanceIn_base: int,
            tokenWeightIn_base: int,
            poolSupply_base: int,
            totalWeight_base: int,
            poolAmountOut_base: int,
            swapFee_base: int) -> int:
        """Returns tokenAmountIn_base"""
        return self.f.calcSingleInGivenPoolOut(
            tokenBalanceIn_base, tokenWeightIn_base, poolSupply_base,
            totalWeight_base, poolAmountOut_base, swapFee_base).call()
    
    def calcSingleOutGivenPoolIn_base(
            self,
            tokenBalanceOut_base: int,
            tokenWeightOut_base: int,
            poolSupply_base: int,
            totalWeight_base: int,
            poolAmountIn_base: int,
            swapFee_base: int) -> int:
        """Returns tokenAmountOut_base"""
        return self.f.calcSingleOutGivenPoolIn(
            tokenBalanceOut_base, tokenWeightOut_base, poolSupply_base,
            totalWeight_base, poolAmountIn_base, swapFee_base).call()
            
    def calcPoolInGivenSingleOut(
            self,
            tokenBalanceOut_base: int,
            tokenWeightOut_base: int,
            poolSupply_base: int,
            totalWeight_base: int,
            tokenAmountOut_base: int,
            swapFee_base: int) -> int:
        """Returns poolAmountIn_base"""
        return self.f.calcPoolInGivenSingleOut(
            tokenBalanceOut_base, tokenWeightOut_base, poolSupply_base,
            totalWeight_base, tokenAmountOut_base, swapFee_base).call()
    
