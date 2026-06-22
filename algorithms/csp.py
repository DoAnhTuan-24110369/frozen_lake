# algorithms/csp.py
import random
from collections import deque
from environment import copy_matrix

class CSPMapGenerator:
    def __init__(self, size, num_gifts, num_obstacles):
        self.size = size
        self.num_gifts = num_gifts
        self.num_obstacles = num_obstacles
        # Danh sách các biến cần gán vị trí
        self.variables = ['Santa'] + [f'Gift_{i}' for i in range(num_gifts)] + [f'Obs_{i}' for i in range(num_obstacles)]
        # Miền giá trị ban đầu: Tất cả các tọa độ trên lưới
        self.domain = [(r, c) for r in range(size) for c in range(size)]
        self.iterations = 0

    def is_connected(self, assignment):
        """Kiểm tra Ràng buộc: Santa có thể ăn được tất cả các món quà không?"""
        if len(assignment) < len(self.variables):
            return True # Cho phép gán tạm thời khi chưa hoàn chỉnh bản đồ
            
        grid = [[0]*self.size for _ in range(self.size)]
        santa_pos = assignment.get('Santa')
        gift_positions = set()
        
        for var, pos in assignment.items():
            if var.startswith('Obs'):
                grid[pos[0]][pos[1]] = 3
            elif var.startswith('Gift'):
                gift_positions.add(pos)
                
        if not santa_pos: return False
        
        # Dùng thuật toán Loang (BFS) nhẹ để kiểm tra đường đi
        queue = deque([santa_pos])
        visited = set([santa_pos])
        gifts_found = 0
        
        while queue:
            r, c = queue.popleft()
            if (r, c) in gift_positions:
                gifts_found += 1
            
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.size and 0 <= nc < self.size and (nr, nc) not in visited:
                    if grid[nr][nc] != 3:
                        visited.add((nr, nc))
                        queue.append((nr, nc))
                        
        return gifts_found == self.num_gifts

    def backtracking(self, limit=5000):
        """1. Backtracking: Thử, nếu sai thì quay lại bước trước"""
        def backtrack(assignment):
            self.iterations += 1
            if self.iterations > limit: return None # Tránh treo máy
            
            if len(assignment) == len(self.variables):
                return assignment if self.is_connected(assignment) else None
            
            # Chọn biến chưa gán
            var = [v for v in self.variables if v not in assignment][0]
            
            # Thử từng giá trị trong miền
            for val in self.domain:
                if val not in assignment.values(): # Ràng buộc: Không nằm đè lên nhau
                    assignment[var] = val
                    result = backtrack(assignment) # Gọi đệ quy
                    if result: return result
                    del assignment[var] # Quay lui (Backtrack)
            return None
            
        random.shuffle(self.domain)
        return backtrack({})

    def forward_checking(self, limit=5000):
        """2. Forward Checking: Cập nhật lại domain của các biến chưa gán"""
        def backtrack_fc(assignment, domains):
            self.iterations += 1
            if self.iterations > limit: return None
            
            if len(assignment) == len(self.variables):
                return assignment if self.is_connected(assignment) else None
                
            var = [v for v in self.variables if v not in assignment][0]
            
            for val in domains[var]:
                assignment[var] = val
                
                # Cập nhật Domain cho các biến còn lại (Xóa tọa độ đã bị chiếm)
                new_domains = {k: v[:] for k, v in domains.items()}
                valid = True
                for other_var in self.variables:
                    if other_var not in assignment:
                        if val in new_domains[other_var]:
                            new_domains[other_var].remove(val)
                        if not new_domains[other_var]: # Domain = rỗng => Sai
                            valid = False
                            break
                            
                if valid:
                    result = backtrack_fc(assignment, new_domains)
                    if result: return result
                    
                del assignment[var] # Quay lui
            return None
            
        initial_domains = {v: self.domain[:] for v in self.variables}
        for v in initial_domains: random.shuffle(initial_domains[v])
        return backtrack_fc({}, initial_domains)

    def min_conflicts(self, max_steps=2000):
        """3. Min-Conflicts: Bắt đầu bằng complete assignment và giảm thiểu xung đột"""
        assignment = {}
        available = self.domain[:]
        random.shuffle(available)
        
        # Bắt đầu với một phép gán hoàn chỉnh ngẫu nhiên (đảm bảo không đè lên nhau)
        for var in self.variables:
            assignment[var] = available.pop()
            
        def count_conflicts(var, val, current_assignment):
            old_val = current_assignment[var]
            current_assignment[var] = val
            conflicts = 0
            
            # Xung đột 1: Nằm đè lên nhau
            for other_var, other_val in current_assignment.items():
                if var != other_var and val == other_val:
                    conflicts += 1
                    
            # Xung đột 2: Gây tắc nghẽn đường đi (Phạt nặng)
            if not self.is_connected(current_assignment):
                conflicts += 5 
                
            current_assignment[var] = old_val
            return conflicts

        for _ in range(max_steps):
            if self.is_connected(assignment) and len(set(assignment.values())) == len(self.variables):
                return assignment # Giải quyết xong
                
            # Chọn ngẫu nhiên một biến để sửa (ưu tiên sửa để giảm xung đột)
            var = random.choice(self.variables)
            
            # Tìm giá trị ít xung đột nhất
            min_c = float('inf')
            best_vals = []
            for val in self.domain:
                c = count_conflicts(var, val, assignment)
                if c < min_c:
                    min_c = c
                    best_vals = [val]
                elif c == min_c:
                    best_vals.append(val)
                    
            # Gán lại giá trị tốt nhất
            assignment[var] = random.choice(best_vals)
            
        return None # Thất bại sau max_steps