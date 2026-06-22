import heapq
from config import MAX_ITERATIONS
from environment import actions, goal_test, count_gift, heuristic_cost
from .utils import Node, child_node, solution

def greedy_search(initial_state):
    node = Node(initial_state)
    node.cost = count_gift(node.state) 
    if goal_test(node.state): return solution(node)

    frontier = []
    heapq.heappush(frontier, (node.cost, node.name, node))
    reached = []

    while frontier:
        current_cost, _, node = heapq.heappop(frontier)
        reached.append(node.state)

        if goal_test(node.state): return solution(node)

        for action in actions(node.state):
            child = child_node(node, action)
            child.cost = count_gift(child.state)

            in_reached = any(s == child.state for s in reached)
            in_frontier = any(f_node.state == child.state for _, _, f_node in frontier)

            if not in_reached and not in_frontier:
                heapq.heappush(frontier, (child.cost, child.name, child))
    return None

def a_star_search(initial_state):
    node = Node(initial_state)
    node.g = count_gift(node.state)
    node.h = heuristic_cost(node.state)
    node.cost = node.g + node.h 
    
    if goal_test(node.state): return solution(node)

    frontier = []
    heapq.heappush(frontier, (node.cost, node.name, node))
    reached = []

    while frontier:
        current_cost, _, node = heapq.heappop(frontier)
        reached.append(node.state)

        if goal_test(node.state): return solution(node)

        for action in actions(node.state):
            child = child_node(node, action)
            child.g = node.g + count_gift(child.state)
            child.h = heuristic_cost(child.state)
            child.cost = child.g + child.h

            in_reached = any(s == child.state for s in reached)
            in_frontier = False
            for i, (f_cost, f_name, f_node) in enumerate(frontier):
                if f_node.state == child.state:
                    in_frontier = True
                    if child.cost < f_cost:
                        frontier[i] = (child.cost, child.name, child)
                        heapq.heapify(frontier)
                    break

            if not in_reached and not in_frontier:
                heapq.heappush(frontier, (child.cost, child.name, child))
    return None

def bounded_a_star_search(initial_state, threshold_I):
    node = Node(initial_state)
    node.g = count_gift(node.state)
    node.h = heuristic_cost(node.state)
    node.cost = node.g + node.h 
    
    if goal_test(node.state): return solution(node), None

    frontier = []
    heapq.heappush(frontier, (node.cost, node.name, node))
    reached = []
    next_I = float('inf') 
    cutoff_occurred = False

    while frontier:
        current_cost, _, node = heapq.heappop(frontier)
        reached.append(node.state)

        if goal_test(node.state): return solution(node), None

        for action in actions(node.state):
            child = child_node(node, action)
            child.g = node.g + count_gift(child.state)
            child.h = heuristic_cost(child.state)
            child.cost = child.g + child.h

            if child.cost > threshold_I:
                cutoff_occurred = True
                if child.cost < next_I: next_I = child.cost
                continue 

            in_reached = any(s == child.state for s in reached)
            in_frontier = False
            for i, (f_cost, f_name, f_node) in enumerate(frontier):
                if f_node.state == child.state:
                    in_frontier = True
                    if child.cost < f_cost:
                        frontier[i] = (child.cost, child.name, child)
                        heapq.heapify(frontier)
                    break

            if not in_reached and not in_frontier:
                heapq.heappush(frontier, (child.cost, child.name, child))
                
    return ("CUTOFF", next_I) if cutoff_occurred else (None, None)

def ida_star_search(initial_state):
    threshold_I = count_gift(initial_state)
    for _ in range(MAX_ITERATIONS):
        Node.reset_counter()
        result_val, next_I = bounded_a_star_search(initial_state, threshold_I)
        
        if result_val != "CUTOFF" and result_val is not None:
            return result_val
        if result_val is None:
            return None
            
        if next_I == float('inf'): break
        threshold_I = next_I
    return None