def p_arbitrage(params, substep, state_history, prev_state):
    """
    Do arbitrage.
    """
    agents = prev_state['agents']
    state = prev_state['state']

    trade_agents = {k: v for k, v in agents.items() if 'Trader' in v.name}
    pool_agents = {k: v for k, v in agents.items() if 'Pool' in v.name}
    
    agent_delta = {}

    for label, agent in list(trade_agents.items()):
        agent.takeStep(state, pool_agents)
        agent_delta[label] = agent

    return {'agent_delta': agent_delta }

def s_arbitrage(params, substep, state_history, prev_state, policy_input):
    updated_agents = prev_state['agents'].copy()
    for label, delta in list(policy_input['agent_delta'].items()):
        updated_agents[label] = delta
    return ('agents', updated_agents)