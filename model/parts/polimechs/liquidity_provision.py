def p_liquidity_provision(params, substep, state_history, prev_state):
    """
    Provide liquidity.
    """
    agents = prev_state['agents']
    state = prev_state['state']

    lp_agents = {k: v for k, v in agents.items() if 'Liquidity Provider' in v.name}
    pool_agents = {k: v for k, v in agents.items() if 'Pool' in v.name}
 
    agent_delta = {}
    pool_agent_delta = {}
    state_delta = {}

    for label, agent in list(lp_agents.items()):
        print(agent)
        agent.takeStep(state, pool_agents)
        if agent.lpDone:
            pool_agent = agent.lpResult[0]
            for k,v in pool_agents.items():
                # print(v)
                if pool_agent.name == v.name:
                    pool_agent_delta[k] = pool_agent
                    state_delta[pool_agent.name] = agent.lpResult[1]
        agent_delta[label] = agent

    return {'agent_delta': agent_delta,
            'pool_agent_delta':  pool_agent_delta,
            'state_delta': state_delta }

def s_liquidity_provision(params, substep, state_history, prev_state, policy_input):
    updated_agents = prev_state['agents'].copy()
    for label, delta in list(policy_input['agent_delta'].items()):
        updated_agents[label] = delta
    for label, delta in list(policy_input['pool_agent_delta'].items()):
        updated_agents[label] = delta
    return ('agents', updated_agents)

def s_liquidity_provision_state(params, substep, state_history, prev_state, policy_input):
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