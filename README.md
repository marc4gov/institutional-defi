Dimensions to test
We want to understand the interdependencies between a whitelisted and a grey pool to help demystify the gap between traditional finance and DeFi
1)	How long the pools take for price alignment when an external price change occurred.
2)	Comparison of slippage
3)	Development of pool TVL
4)	Trading volume development

Preferably we should observe with Monte Carlo simulations as we are modelling under uncertainty, and random selection of only 1 observation is not meaningful. We want to observe with some level of confidence by using many time steps and several monte carlo runs.

For each dimension, design experiment notebook and plot dimensions with expectations to the outcome
1)	Simulation test case 1 – equilibrium simulation
a.	We start with the 2 pools with unaligned randomly selected prices and perform successive trades as outlined by the default trade agent policies for each pool: buy ETH at the cheaper pool, sell same amount ETH at the higher priced pool. Repeat this until price alignment.
b.	After each trade, observe the prices in the respective pools. They should hopefully approach one another. The plot should show price development in each pool over time to illustrate how the price of ETH expressed in USD aligns across the 2 pools.
2)	Simulation test case 2 - slippage
a.	Set slippage tolerance to infinite, ie no slippage tolerance max. In both pools we then perform a swap from token USD to ETH in parallel inside the 2 pools to check how strong the trades influence the price of ETH in the respective pool and swap back. This allows to compare the slippage of the respective pools.
b.	Plot should show slippage percentage per tradesize, I imagine a plot with slippage on one axis and trade size on second axis at different liquidity depths, so perhaps a plot for how the trades develop in a pool with total reserves below USD 100m, between USD 100-500m and above USD 500m value.
3)	Simulation test case 3 – Liquidity provision impact
a.	Reset liquidity return requirement and simply add liquidity of USD 10m/50m/100m mimicking a “whale” that enters without splitting trades, ie an institutional player into the white pool while keeping the other pool steady, do same in grey afterwards with white pool steady. Prior to injection of liquidity, both pools are aligned beforehand, and the simulation should show how this affect pricing in given the trading patterns, I would imagine a “whale” entering would significantly affect pricing in the pool she enters and that will lead to some aggressive trading, where we should observe trading levels vs “as is” in simulation test case 1.
4)	Simulation test case 4 – TVL impact
a.	White pool becomes successful and increases to say 10X TVL of grey pool, the trades that can be managed with same slippage wil then be 10x bigger than grey pool. With the slippage tolerance set at standard, what does that look like in terms of “marketshare”, assuming grey pool can only handle much smaller trades. I imagine the white pool will dominate so eg if you enter with an institutional setup that is 10x bigger than DeFi normal, does that mean institutional trading will conquer? What will it take for the white pool to dominate the grey pool, can we somehow define the edge cases that can show the trade-off between cost/burden of KYC in terms of better prices/liquidity in white pool in terms of market development?
b.	Repeat experiment with TVL increased in 1 pool to only 2X and again with 100X, what is the impact of the other with the above experiments, what observations can be made, when either white or grey pool changes less or more dramatically and what sensitivities can we make based on size of pool, likely less slippage and impairment loss when more liquid / deep, but what else can we observe?
5)	Simulation test case 5 – Trade frequency impact
a.	If we change the trade frequency in either pool to 10X or 0.5X default pattern, what is the impact of the other with the above 4 experiments, what observations can be made, when either white or grey pool changes less dramatically and what sensitivities can we make based on size of pool.
6)	Simulation test case 6 – ETH price volatility impact
a.	Say, do to a bug in a trader’s algorithm, there is a massive selling or buying and ETH price increases/decreases 20 pct over, say, 1 hour, how will the pools adjust in this time window and how will slippage, TVL, share of agents involved and trading volume etc as above behave in that scenario.
7)	Simulation test case 7 – Fee impact
a.	Simulate all the above but set trading fee to zero, default and 1 pct to analyze how the pools develop based on trading fee sensitivity
