def copy_matrix(matrix):
    return [row[:] for row in matrix]

def find_santa(matrix):
    rows = len(matrix)
    cols = len(matrix[0])
    for i in range(rows):
        for j in range(cols):
            if matrix[i][j] == 2:
                return [i, j]
    return None

def goal_test(state):
    for row in state:
        if 1 in row:
            return False
    return True

def actions(state):
    x, y = find_santa(state)
    move = []
    rows = len(state)
    cols = len(state[0])
    
    if x > 0 and state[x-1][y] != 3: move.append("UP")
    if x < rows - 1 and state[x+1][y] != 3: move.append("DOWN")
    if y > 0 and state[x][y-1] != 3: move.append("LEFT")
    if y < cols - 1 and state[x][y+1] != 3: move.append("RIGHT")
    return move

def result(state, action):
    new_state = copy_matrix(state)
    x, y = find_santa(new_state)
    new_state[x][y] = 0
    nx, ny = x, y
    
    if action == "UP": nx -= 1
    elif action == "DOWN": nx += 1
    elif action == "LEFT": ny -= 1
    elif action == "RIGHT": ny += 1
        
    new_state[nx][ny] = 2
    return new_state

def safe_apply_action(state, action):
    new_state = copy_matrix(state)
    pos = find_santa(new_state)
    if not pos: return new_state
    
    x, y = pos
    nx, ny = x, y
    if action == "UP": nx -= 1
    elif action == "DOWN": nx += 1
    elif action == "LEFT": ny -= 1
    elif action == "RIGHT": ny += 1

    rows, cols = len(new_state), len(new_state[0])
    if 0 <= nx < rows and 0 <= ny < cols and new_state[nx][ny] != 3:
        new_state[x][y] = 0
        new_state[nx][ny] = 2
        
    return new_state

def count_gift(matrix):
    count = 0
    for row in matrix:
        count += row.count(1)
    return count

def get_gift_positions(matrix):
    gifts = []
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            if matrix[i][j] == 1:
                gifts.append((i, j))
    return gifts

def heuristic_cost(state):
    santa_pos = find_santa(state)
    gifts = get_gift_positions(state)
    
    if not gifts or not santa_pos:
        return 0
        
    rx, ry = santa_pos
    min_distance = float('inf')
    
    for dx, dy in gifts:
        distance = abs(rx - dx) + abs(ry - dy)
        if distance < min_distance:
            min_distance = distance
            
    return min_distance + (len(gifts) - 1)

def nondeterministic_results(state, action):
    results = []
    res_intended = safe_apply_action(state, action)
    results.append(("Thành công", res_intended))
    
    slip_mapping = {"UP": "LEFT", "DOWN": "RIGHT", "LEFT": "DOWN", "RIGHT": "UP"}
    slip_action = slip_mapping.get(action, action)
    res_slip = safe_apply_action(state, slip_action)
    
    if res_slip != res_intended:
        results.append((f"Trượt ({slip_action})", res_slip))
        
    return results

def state_to_tuple_key(state):
    return tuple(tuple(row) for row in state)