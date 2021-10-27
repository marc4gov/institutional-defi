import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def make_df(experiment, pool=True, pool_agent='White Pool', agent='Trader'):
  agents_df = experiment.agents
  ldf = pd.concat([agents_df,experiment.timestep], axis=1)
  pdf = ldf.agents.apply(pd.Series)

  if pool:
    for column in pdf:
      df2 = pd.DataFrame([vars(f) for f in pdf[pool_agent]])
      df3 = pd.DataFrame([vars(f) for f in df2._pool])
      df4 = pd.DataFrame([vars(f) for f in df3.pair])
      df5 = pd.DataFrame([vars(f) for f in df4.token0])
      df6 = pd.DataFrame([vars(f) for f in df4.token1])
    return pd.concat([df5.amount, df6.amount, experiment.timestep], axis=1, keys = ['USD', 'ETH', 'Timestep'])
  else:
    for column in pdf:
      df2 = pd.DataFrame([vars(f) for f in pdf[agent]])
      df3 = pd.DataFrame([vars(f) for f in df2._wallet])
    return pd.concat([df3._USD, df3._ETH, experiment.timestep], axis=1, keys = ['USD', 'ETH', 'Timestep'])


def pool_plot(experiment, pool='White Pool') -> pd.DataFrame:
    """
For any pool 
    """
    df = experiment
    agents_df = df.agents
    ldf = pd.concat([agents_df,df.timestep], axis=1)
    pdf = ldf.agents.apply(pd.Series)

    for column in pdf:
        df2 = pd.DataFrame([vars(f) for f in pdf[pool]])
        df3 = pd.DataFrame([vars(f) for f in df2._pool])
        df4 = pd.DataFrame([vars(f) for f in df3.pair])
        df5 = pd.DataFrame([vars(f) for f in df4.token0])
        df6 = pd.DataFrame([vars(f) for f in df4.token1])
    edf = pd.concat([df5.amount, df6.amount, df.timestep], axis=1, keys = ['USD', 'ETH', 'Timestep'])
    # edf.head(10)
    # edf.plot(x = 'Timestep', y = 'USD' )
    edf.plot(x = 'Timestep', y = 'ETH' )
        

    plt.figure(figsize=(20,6))
    plt.subplot(141)
    plt.plot(edf["Timestep"],edf["USD"],label=pool)
    plt.xlabel('Timestep')
    plt.ylabel('Reserves')
    plt.legend()
    plt.title('Asset USD')

    plt.subplot(142)
    plt.plot(edf["Timestep"],edf["ETH"],label=pool)
    plt.xlabel('Timestep')
    plt.ylabel('Reserves')
    plt.legend()
    plt.title('Asset ETH')

    plt.subplot(143)
    plt.plot(edf["Timestep"] * edf["ETH"],label=pool)
    plt.xlabel('Timestep')
    plt.ylabel('k')
    plt.legend()
    plt.title('k' + ' for ' + pool)
       
    plt.show()
    return edf

def agent_plot(experiment, agent='Trader'):
    """
For any agent 
    """
    df = experiment
    agents_df = df.agents
    ldf = pd.concat([agents_df,df.timestep], axis=1)
    pdf = ldf.agents.apply(pd.Series)

    for column in pdf:
        df2 = pd.DataFrame([vars(f) for f in pdf[agent]])
        df3 = pd.DataFrame([vars(f) for f in df2._wallet])
    edf = pd.concat([df3._USD, df3._ETH, df.timestep], axis=1, keys = ['USD', 'ETH', 'Timestep'])
        

    plt.figure(figsize=(20,6))
    plt.subplot(141)
    plt.plot(edf["Timestep"],edf["USD"],label=agent)
    plt.xlabel('Timestep')
    plt.ylabel('Reserves')
    plt.legend()
    plt.title('Asset USD')

    plt.subplot(142)
    plt.plot(edf["Timestep"],edf["ETH"],label=agent)
    plt.xlabel('Timestep')
    plt.ylabel('Reserves')
    plt.legend()
    plt.title('Asset ETH')
       
    plt.show()


def monte_carlo_plot(dfs, pool=True, pool_agent='White Pool', agent='Trader', asset="USD"):
  fig, ax = plt.subplots()
  edfs = []
  for df in dfs:
    edf = make_df(df, pool=pool, pool_agent=pool_agent, agent=agent)
    edfs.append(edf)
  x = pd.Series(edf["Timestep"]).values
  for ed in edfs:
    ax.plot(x, pd.Series(ed[asset]).values) 
  plt.xlabel('Timestep')
  plt.ylabel(asset)
  plt.legend()
  if pool:
    plt.title('Reserve ' + asset + ' for ' + pool_agent)
  else:
    plt.title('Volume ' + asset + ' for ' + agent)
  plt.show()