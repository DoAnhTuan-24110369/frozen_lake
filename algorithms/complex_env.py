from collections import deque
from environment import actions, goal_test, nondeterministic_results, state_to_tuple_key
from .utils import BeliefNode, bs_goal_test, bs_to_str, bs_child_node, solution

def sensorless_bfs(initial_states):
    node = BeliefNode(initial_states)
    if bs_goal_test(node.states): return solution(node)

    frontier = deque([node])
    reached = [] 
    possible_actions = ["UP", "DOWN", "LEFT", "RIGHT"]

    while frontier:
        node = frontier.popleft()
        reached.append(bs_to_str(node.states))
        
        if bs_goal_test(node.states): return solution(node)

        for action in possible_actions:
            child = bs_child_node(node, action)
            child_str = bs_to_str(child.states)
            
            in_reached = child_str in reached
            in_frontier = any(bs_to_str(n.states) == child_str for n in frontier)

            if not in_reached and not in_frontier:
                frontier.append(child)
    return None

def partial_obs_bfs(initial_states):
    node = BeliefNode(initial_states)
    if bs_goal_test(node.states): return solution(node)

    frontier = deque([node])
    reached = []
    possible_actions = ["UP", "DOWN", "LEFT", "RIGHT"]

    while frontier:
        node = frontier.popleft()
        reached.append(bs_to_str(node.states))
        
        if bs_goal_test(node.states): return solution(node)

        for action in possible_actions:
            child = bs_child_node(node, action)
            child_str = bs_to_str(child.states)
            
            in_reached = child_str in reached
            in_frontier = any(bs_to_str(n.states) == child_str for n in frontier)

            if not in_reached and not in_frontier:
                frontier.append(child)
    return None

def and_or_graph_search(initial_state):
    return or_search(initial_state, [], 0)

def or_search(state, path, depth):
    if goal_test(state): return []
    if state in path: return "failure"
        
    for action in actions(state):
        result_states = nondeterministic_results(state, action)
        plan = and_search(result_states, path + [state], depth + 1)
        if plan != "failure": return [action, plan]
            
    return "failure"

def and_search(labeled_states, path, depth):
    plans = {}
    for label, s in labeled_states:
        plan_s = or_search(s, path, depth + 1)
        if plan_s == "failure": return "failure"
        plans[(label, state_to_tuple_key(s))] = plan_s
    return plans