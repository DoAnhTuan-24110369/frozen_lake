from collections import deque
import heapq
from environment import actions, goal_test, count_dust
from .utils import Node, child_node, solution

def breadth_first_search_2(initial_state):
    node = Node(initial_state)
    if goal_test(node.state): return solution(node)
    frontier = deque([node])
    explored = []

    while frontier:
        node = frontier.popleft()
        explored.append(node.state)

        for action in actions(node.state):
            child = child_node(node, action)
            in_explored = any(s == child.state for s in explored)
            in_frontier = any(n.state == child.state for n in frontier)

            if not in_explored and not in_frontier:
                if goal_test(child.state): return solution(child)
                frontier.append(child)
    return None

def depth_first_search_2(initial_state):
    node = Node(initial_state)
    if goal_test(node.state): return solution(node)
    frontier = deque([node])
    explored = []

    while frontier:
        node = frontier.pop()
        explored.append(node.state)

        for action in actions(node.state):
            child = child_node(node, action)
            in_explored = any(s == child.state for s in explored)
            in_frontier = any(n.state == child.state for n in frontier)

            if not in_explored and not in_frontier:
                if goal_test(child.state): return solution(child)
                frontier.append(child)
    return None

def uniform_cost_search(initial_state):
    node = Node(initial_state)
    node.cost = count_dust(node.state) 
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
            child.cost = node.cost + count_dust(child.state)

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