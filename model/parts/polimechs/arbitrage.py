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

    for label, agent in list(trade_agents.items()):
        p = agent.takeStep(state, pool_agents)
        if p is not None:
            pool_agent = p
            for k,v in pool_agents.items():
                print(v)
                if pool_agent.name == v.name:
                    pool_agent_delta[k] = pool_agent
        agent_delta[label] = agent

    return {'agent_delta': agent_delta,
            'pool_agent_delta':  pool_agent_delta}

def s_arbitrage(params, substep, state_history, prev_state, policy_input):
    updated_agents = prev_state['agents'].copy()
    for label, delta in list(policy_input['agent_delta'].items()):
        updated_agents[label] = delta
    for label, delta in list(policy_input['pool_agent_delta'].items()):
        updated_agents[label] = delta
        
    return ('agents', updated_agents)