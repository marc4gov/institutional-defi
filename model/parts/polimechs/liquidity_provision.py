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
        # print(agent)
        agent.takeStep(state, pool_agents)
        # providing liquidity
        if agent.lpDone:
            pool_agent = agent.lpResult[0]
            state_delta[pool_agent.name] = float(agent.lpResult[1])
                    # print(state_delta)
        agent_delta[label] = agent
        agent.lpDone = False
        agent.lpResult = (None, None)
        # burning liquidity tokens
        if agent.burnDone:
            pool_agent = agent.burnResult[0]
            state_delta[pool_agent.name] = - float(agent.burnResult[1])
                    # print(state_delta)
        agent_delta[label] = agent
        agent.burnDone = False
        agent.burnResult = (None, None)


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
    wlm = updated_state._total_Liq_minted_White
    glm = updated_state._total_Liq_minted_Grey
    wls = updated_state._total_Liq_supply_White
    gls = updated_state._total_Liq_supply_Grey
    
    for label, delta in list(policy_input['state_delta'].items()):
        if 'White' in label:
            updated_state._total_Liq_minted_White = wlm + delta
            updated_state._total_Liq_supply_White = wls + delta
            # print("Updates state liq White: ", updated_state._total_Liq_minted_White)
        else:
            updated_state._total_Liq_minted_Grey = glm + delta
            updated_state._total_Liq_supply_Grey = gls + delta

            # print("Updates state volume Grey: ", updated_state.grey_pool_volume_USD)
    return('state', updated_state)