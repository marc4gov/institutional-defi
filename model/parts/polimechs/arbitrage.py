from multiprocessing import pool


def p_arbitrage(params, substep, state_history, prev_state):
    """
    Do arbitrage.
    """
    agents = prev_state['agents']
    state = prev_state['state']

    trade_agents = {k: v for k, v in agents.items() if 'Trader' in v.name}
    pool_agents = {k: v for k, v in agents.items() if 'Pool' in v.name}
        
    agent_delta = {}
    pool_agent_delta = {}
    state_delta = {}

    for label, agent in list(trade_agents.items()):
        agent.takeStep(state, pool_agents)

        if agent.tradeDone:
            pool_agent = agent.tradeResult[0]
            if agent.tradeResult[1] != None:
                pool_agent_delta[pool_agent.name] = pool_agent
                state_delta[pool_agent.name] = float(agent.tradeResult[1])
                    # print('Volume: ', agent.tradeResult[1])
        agent_delta[label] = agent
        agent.tradeDone = False
        agent.tradeResult = (None, None)

    return {'agent_delta': agent_delta,
            'pool_agent_delta':  pool_agent_delta,
            'state_delta': state_delta }

def s_arbitrage(params, substep, state_history, prev_state, policy_input):
    updated_agents = prev_state['agents'].copy()
    for label, delta in list(policy_input['agent_delta'].items()):
        updated_agents[label] = delta
    for label, delta in list(policy_input['pool_agent_delta'].items()):
        updated_agents[label] = delta

    return ('agents', updated_agents)

def s_arbitrage_state(params, substep, state_history, prev_state, policy_input):
    updated_state = prev_state['state']
    wp = updated_state.white_pool_volume_USD
    gp = updated_state.grey_pool_volume_USD
    
    for label, delta in list(policy_input['state_delta'].items()):
        if 'White' in label:
            updated_state.white_pool_volume_USD = wp + delta
            # print("Updates state volume White: ", updated_state.white_pool_volume_USD)
        else:
            updated_state.grey_pool_volume_USD = gp + delta
            # print("Updates state volume Grey: ", updated_state.grey_pool_volume_USD)
    return('state', updated_state)