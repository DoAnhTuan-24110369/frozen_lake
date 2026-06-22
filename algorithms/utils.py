from environment import copy_matrix, goal_test, result, safe_apply_action

class Node:
    name_counter = 0

    @classmethod
    def reset_counter(cls):
        cls.name_counter = 0

    @classmethod
    def get_next_name(cls):
        n = cls.name_counter
        cls.name_counter += 1
        name = ""
        while True:
            name = chr(n % 26 + 65) + name
            n = n // 26 - 1
            if n < 0: break
        return name

    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.name = Node.get_next_name()
        self.cost = 0 if parent is None else parent.cost + 1

class BeliefNode:
    name_counter = 0

    @classmethod
    def reset_counter(cls):
        cls.name_counter = 0

    @classmethod
    def get_next_name(cls):
        n = cls.name_counter
        cls.name_counter += 1
        name = ""
        while True:
            name = chr(n % 26 + 65) + name
            n = n // 26 - 1
            if n < 0: break
        return "BS_" + name

    def __init__(self, states, parent=None, action=None):
        self.states = states 
        self.parent = parent
        self.action = action
        self.name = BeliefNode.get_next_name()
        self.cost = 0 if parent is None else parent.cost + 1

def child_node(node, action):
    new_state = result(node.state, action)
    return Node(new_state, node, action)

def solution(node):
    path = []
    while node.parent is not None:
        path.append(node.action)
        node = node.parent
    path.reverse()
    return path

# Các hàm phụ trợ cho Belief State
def bs_to_str(states):
    res = []
    for state in states:
        state_str = "[" + ",".join("[" + ",".join(str(val) for val in row) + "]" for row in state) + "]"
        res.append(state_str)
    return " | ".join(res)

def bs_goal_test(states):
    for state in states:
        if not goal_test(state):
            return False
    return True

def bs_result(states, action):
    new_states = []
    for s in states:
        if goal_test(s):
            new_states.append(copy_matrix(s))
        else:
            new_states.append(safe_apply_action(s, action))
    return new_states

def bs_child_node(node, action):
    new_states = bs_result(node.states, action)
    return BeliefNode(new_states, node, action)