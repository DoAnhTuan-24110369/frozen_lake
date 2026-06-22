import random
import math
from environment import actions, goal_test, count_gift, heuristic_cost
from .utils import Node, child_node, solution

def simple_hill_climbing(initial_state):
    current_node = Node(initial_state)
    current_node.cost = count_gift(current_node.state)
    
    while True:
        if goal_test(current_node.state): return solution(current_node)
        
        better_neighbor_found = False
        for action in actions(current_node.state):
            child = child_node(current_node, action)
            child.cost = count_gift(child.state)
            
            if child.cost < current_node.cost:
                current_node = child
                better_neighbor_found = True
                break 
                
        if not better_neighbor_found:
            return "LOCAL_MINIMUM"

def local_beam_search(initial_state, k=2):
    start_node = Node(initial_state)
    start_node.cost = count_gift(start_node.state)
    if goal_test(start_node.state): return solution(start_node)
        
    current_nodes = [start_node]
    max_iter = 100 
    
    for _ in range(1, max_iter + 1):
        neighbor_nodes = []
        for node in current_nodes:
            for action in actions(node.state):
                child = child_node(node, action)
                child.cost = count_gift(child.state)
                neighbor_nodes.append(child)
                
        if not neighbor_nodes: return "LOCAL_MINIMUM"
            
        for neighbor in neighbor_nodes:
            if goal_test(neighbor.state): return solution(neighbor)
                
        neighbor_nodes.sort(key=lambda x: (x.cost, x.name))
        current_nodes = neighbor_nodes[:k] 
        
    return "LOCAL_MINIMUM"

def simulated_annealing(initial_state, T0=100, Tmin=1, alpha=0.95):
    current_node = Node(initial_state)
    current_node.cost = heuristic_cost(current_node.state) 
    T = T0
    
    while T > Tmin:
        if goal_test(current_node.state): return solution(current_node)
        
        possible_actions = actions(current_node.state)
        if not possible_actions: break 
            
        action = random.choice(possible_actions)
        next_node = child_node(current_node, action)
        next_node.cost = heuristic_cost(next_node.state)
        
        delta = next_node.cost - current_node.cost
        
        if delta < 0:
            current_node = next_node
        else:
            p = math.exp(-delta / T)
            if random.random() < p: current_node = next_node
        
        T = alpha * T
        
    return "LOCAL_MINIMUM"