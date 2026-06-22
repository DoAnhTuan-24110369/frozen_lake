# ui.py
import os
import time
import random
import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk

import config
from environment import count_gift, result, copy_matrix
from algorithms.utils import Node, BeliefNode, bs_goal_test, bs_result
from algorithms.uninformed import breadth_first_search_2, depth_first_search_2, uniform_cost_search
from algorithms.informed import greedy_search, a_star_search, ida_star_search
from algorithms.local import simple_hill_climbing, local_beam_search, simulated_annealing
from algorithms.complex_env import sensorless_bfs, partial_obs_bfs, and_or_graph_search
from algorithms.csp import CSPMapGenerator

class FrozenLakeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Frozen Lake Game")
        
        try:
            self.root.state('zoomed') 
        except Exception:
            try:
                self.root.attributes('-zoomed', True) 
            except Exception:
                w = self.root.winfo_screenwidth()
                h = self.root.winfo_screenheight()
                self.root.geometry(f"{w}x{h}+0+0")
                
        self.root.configure(bg="#F5F5F5")

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TButton', font=('Segoe UI', 10), padding=5)
        self.style.configure('TLabel', font=('Segoe UI', 10), background="#F5F5F5")

        self.initial_matrix = []
        self.current_matrix = []
        self.initial_belief_states = []
        self.current_belief_states = []
        self.active_view = "SINGLE" 
        
        self.is_running = False
        self.canvas_dim = config.CANVAS_DIM
        self.size_var = tk.StringVar(value=config.DEFAULT_MAP_SIZE)
        
        # Biến chọn loại Map Generator
        self.gen_mode_var = tk.StringVar(value="Random")
        
        self.image_cache = {}

        self.setup_ui()
        self.generate_map()

    def get_image(self, name, size):
        key = (name, size)
        if key not in self.image_cache:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            img_path = os.path.join(base_dir, "assets", name)
            img = Image.open(img_path).resize((int(size), int(size)), Image.Resampling.LANCZOS)
            self.image_cache[key] = ImageTk.PhotoImage(img)
        return self.image_cache[key]

    def setup_ui(self):
        self.bottom_frame = tk.Frame(self.root, bg="#F5F5F5")
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Label(self.bottom_frame, text="Solution Actions:", font=('Segoe UI', 10, 'bold')).pack(anchor="w", pady=(0, 5))
        self.sol_text = tk.Text(self.bottom_frame, height=3, font=("Consolas", 10), bd=1, relief="solid", bg="#FAFAFA")
        self.sol_text.pack(fill=tk.X)
        self.sol_text.config(state=tk.DISABLED)

        self.top_frame = tk.Frame(self.root, bg="#F5F5F5")
        self.top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Controls
        self.control_frame = tk.Frame(self.top_frame, bg="#F5F5F5")
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))

        ttk.Label(self.control_frame, text="Map Settings", font=('Segoe UI', 11, 'bold')).pack(anchor="w", pady=(0, 5))
        map_setting_frame = tk.Frame(self.control_frame, bg="#F5F5F5")
        map_setting_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.size_combo = ttk.Combobox(map_setting_frame, textvariable=self.size_var, values=["3x3", "4x4", "5x5", "6x6"], state="readonly", width=4)
        self.size_combo.pack(side=tk.LEFT, padx=(0, 5))
        self.size_combo.bind("<<ComboboxSelected>>", lambda event: self.generate_map())
        
        # Thêm Combobox chọn thuật toán sinh bản đồ CSP
        self.mode_combo = ttk.Combobox(map_setting_frame, textvariable=self.gen_mode_var, values=["Random", "CSP: Backtracking", "CSP: Forward Checking", "CSP: Min-Conflicts"], state="readonly", width=18)
        self.mode_combo.pack(side=tk.LEFT, padx=(0, 5))
        self.mode_combo.bind("<<ComboboxSelected>>", lambda event: self.generate_map())
        
        ttk.Button(map_setting_frame, text="Generate", command=self.generate_map, width=8).pack(side=tk.LEFT)
        ttk.Button(map_setting_frame, text="Reset", command=self.reset_map, width=6).pack(side=tk.LEFT, padx=(5, 0))

        ttk.Separator(self.control_frame, orient='horizontal').pack(fill='x', pady=8)

        button_columns_frame = tk.Frame(self.control_frame, bg="#F5F5F5")
        button_columns_frame.pack(fill=tk.BOTH, expand=True)

        col1 = tk.Frame(button_columns_frame, bg="#F5F5F5")
        col1.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), anchor="n")

        col2 = tk.Frame(button_columns_frame, bg="#F5F5F5")
        col2.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0), anchor="n")

        ttk.Label(col1, text="Uninformed Search", font=('Segoe UI', 10, 'bold')).pack(anchor="w", pady=(0, 5))
        ttk.Button(col1, text="BFS 2", command=lambda: self.run_algo("BFS2"), width=16).pack(pady=1)
        ttk.Button(col1, text="DFS 2", command=lambda: self.run_algo("DFS2"), width=16).pack(pady=1)
        ttk.Button(col1, text="UCS", command=lambda: self.run_algo("UCS"), width=16).pack(pady=1)
        
        ttk.Separator(col1, orient='horizontal').pack(fill='x', pady=5)
        ttk.Label(col1, text="Informed Search", font=('Segoe UI', 10, 'bold')).pack(anchor="w", pady=(0, 2))
        ttk.Button(col1, text="Greedy Search", command=lambda: self.run_algo("GS"), width=16).pack(pady=1)
        ttk.Button(col1, text="A* Search", command=lambda: self.run_algo("A*"), width=16).pack(pady=1)
        ttk.Button(col1, text="IDA* Search", command=lambda: self.run_algo("IDA*"), width=16).pack(pady=1)

        ttk.Label(col1, text="Local Search", font=('Segoe UI', 10, 'bold')).pack(anchor="w", pady=(0, 5))
        ttk.Button(col1, text="Simple HC", command=lambda: self.run_algo("SHC"), width=16).pack(pady=1)
        ttk.Button(col1, text="Local Beam Search", command=lambda: self.run_algo("LBS"), width=16).pack(pady=1)
        ttk.Button(col1, text="Simulated Annealing", command=lambda: self.run_algo("SA"), width=16).pack(pady=1)

        ttk.Separator(col2, orient='horizontal').pack(fill='x', pady=5)
        ttk.Label(col2, text="Sensorless Env", font=('Segoe UI', 10, 'bold')).pack(anchor="w", pady=(0, 2))
        ttk.Button(col2, text="Gen 2 States (BS)", command=self.generate_belief_states, width=16).pack(pady=1)
        ttk.Button(col2, text="Sensorless Search", command=self.run_sensorless_algo, width=16).pack(pady=1)

        ttk.Separator(col2, orient='horizontal').pack(fill='x', pady=5)
        ttk.Label(col2, text="Partial Obs Env", font=('Segoe UI', 10, 'bold')).pack(anchor="w", pady=(0, 2))
        ttk.Button(col2, text="Gen Partial BS", command=self.generate_partial_belief_states, width=16).pack(pady=1)
        ttk.Button(col2, text="Partial Obs Search", command=self.run_partial_obs_algo, width=16).pack(pady=1)
        
        ttk.Separator(col2, orient='horizontal').pack(fill='x', pady=5)
        ttk.Label(col2, text="Non-Deterministic Env", font=('Segoe UI', 10, 'bold')).pack(anchor="w", pady=(0, 2))
        ttk.Button(col2, text="AND-OR Search", command=self.run_and_or_algo, width=16).pack(pady=1)

        # Canvas
        self.canvas_frame = tk.Frame(self.top_frame, bg="white", bd=1, relief="solid")
        self.canvas_frame.pack(side=tk.LEFT, padx=10)
        self.canvas = tk.Canvas(self.canvas_frame, width=self.canvas_dim, height=self.canvas_dim, bg="white", highlightthickness=0)
        self.canvas.pack(padx=2, pady=2)

        # Log
        self.log_frame = tk.Frame(self.top_frame, bg="#F5F5F5")
        self.log_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))
        
        ttk.Label(self.log_frame, text="Execution Log", font=('Segoe UI', 10, 'bold')).pack(anchor="w", pady=(0, 5))
        self.log_text = scrolledtext.ScrolledText(self.log_frame, width=22, font=("Consolas", 9), bd=1, relief="solid")
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def generate_map(self):
        if self.is_running: return
        self.active_view = "SINGLE"
        
        size_str = self.size_var.get()
        size = int(size_str.split('x')[0])
        mode = self.gen_mode_var.get()
        
        obstacle_mapping = {3: 2, 4: 3, 5: 6, 6: 10}
        num_obstacles = obstacle_mapping.get(size, 8)
        
        max_gift_mapping = {3: 4, 4: 6, 5: 8, 6: 12}
        num_gift = random.randint(1, max_gift_mapping.get(size, 6))
        
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, f"Generating map via {mode}...\n")
        self.root.update()

        # LOGIC TẠO BẢN ĐỒ CSP HOẶC RANDOM
        if mode == "Random":
            self.initial_matrix = [[0 for _ in range(size)] for _ in range(size)]
            self.initial_matrix[random.randint(0, size-1)][random.randint(0, size-1)] = 2
            
            obs_placed = 0
            while obs_placed < num_obstacles:
                rx, ry = random.randint(0, size-1), random.randint(0, size-1)
                if self.initial_matrix[rx][ry] == 0:
                    self.initial_matrix[rx][ry] = 3
                    obs_placed += 1
                    
            gift_placed = 0
            while gift_placed < num_gift:
                rx, ry = random.randint(0, size-1), random.randint(0, size-1)
                if self.initial_matrix[rx][ry] == 0:
                    self.initial_matrix[rx][ry] = 1
                    gift_placed += 1
        else:
            csp = CSPMapGenerator(size, num_gift, num_obstacles)
            assignment = None
            
            if mode == "CSP: Backtracking":
                assignment = csp.backtracking()
            elif mode == "CSP: Forward Checking":
                assignment = csp.forward_checking()
            elif mode == "CSP: Min-Conflicts":
                assignment = csp.min_conflicts()
                
            if assignment:
                self.initial_matrix = [[0]*size for _ in range(size)]
                for var, pos in assignment.items():
                    if var == 'Santa': self.initial_matrix[pos[0]][pos[1]] = 2
                    elif var.startswith('Gift'): self.initial_matrix[pos[0]][pos[1]] = 1
                    elif var.startswith('Obs'): self.initial_matrix[pos[0]][pos[1]] = 3
                self.log_text.insert(tk.END, "[SUCCESS] CSP Found valid map.\n")
            else:
                # Nếu CSP chạm giới hạn (Timeout), fallback sang Random
                self.log_text.insert(tk.END, "[FAIL] CSP Timeout. Fallback to Random.\n")
                self.gen_mode_var.set("Random")
                self.generate_map()
                return
                
        self.current_matrix = [row[:] for row in self.initial_matrix]
        self.draw_grid(self.current_matrix)
        self.log_text.insert(tk.END, f"Ready with {num_gift} gifts.\n")
        self.update_solution_text("")

    def reset_map(self):
        if self.is_running: return
        
        if self.active_view == "SINGLE" and self.initial_matrix:
            self.current_matrix = [row[:] for row in self.initial_matrix]
            self.draw_grid(self.current_matrix)
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(tk.END, "Map reset to Initial State.\n")
            
        elif self.active_view == "DUAL" and self.initial_belief_states:
            self.current_belief_states = [copy_matrix(s) for s in self.initial_belief_states]
            self.draw_dual_grid(self.current_belief_states[0], self.current_belief_states[1])
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(tk.END, "Belief States reset.\n")
            
        elif self.active_view == "PARTIAL" and self.initial_belief_states:
            self.current_belief_states = [copy_matrix(s) for s in self.initial_belief_states]
            self.draw_dual_grid(self.current_belief_states[0], self.current_belief_states[1], getattr(self, 'known_coords', None))
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(tk.END, "Partial Belief States reset.\n")
            
        self.update_solution_text("")

    def draw_grid(self, matrix):
        self.canvas.delete("all")
        size = len(matrix)
        cell_size = self.canvas_dim / size
        
        for i in range(size):
            for j in range(size):
                val = matrix[i][j]
                x1, y1 = j * cell_size, i * cell_size
                
                snow_img = self.get_image("snow.jpg", cell_size)
                self.canvas.create_image(x1, y1, anchor=tk.NW, image=snow_img)
                
                if val == 1:
                    gift_img = self.get_image("gift.png", cell_size)
                    self.canvas.create_image(x1, y1, anchor=tk.NW, image=gift_img)
                elif val == 2:
                    santa_img = self.get_image("santa.png", cell_size)
                    self.canvas.create_image(x1, y1, anchor=tk.NW, image=santa_img)
                elif val == 3:
                    if (i * 7 + j * 13) % 2 == 0:
                        obs_img = self.get_image("hole.png", cell_size)
                    else:
                        obs_img = self.get_image("mount.webp", cell_size)
                    self.canvas.create_image(x1, y1, anchor=tk.NW, image=obs_img)

                self.canvas.create_rectangle(x1, y1, x1+cell_size, y1+cell_size, outline="#DDDDDD", width=1)
                
        self.root.update_idletasks()

    def draw_dual_grid(self, matrix1, matrix2, known_coords=None):
        self.canvas.delete("all")
        size = len(matrix1)
        padding = 20
        grid_width = (self.canvas_dim - padding) / 2
        cell_size = grid_width / size
        
        matrices = [(matrix1, 0), (matrix2, grid_width + padding)]
        
        for matrix, x_offset in matrices:
            for i in range(size):
                for j in range(size):
                    val = matrix[i][j]
                    x1 = x_offset + j * cell_size
                    y1 = i * cell_size
                    
                    snow_img = self.get_image("snow.jpg", cell_size)
                    self.canvas.create_image(x1, y1, anchor=tk.NW, image=snow_img)
                    
                    if val == 1:
                        gift_img = self.get_image("gift.png", cell_size)
                        self.canvas.create_image(x1, y1, anchor=tk.NW, image=gift_img)
                    elif val == 2:
                        santa_img = self.get_image("santa.png", cell_size)
                        self.canvas.create_image(x1, y1, anchor=tk.NW, image=santa_img)
                    elif val == 3:
                        if (i * 7 + j * 13) % 2 == 0:
                            obs_img = self.get_image("hole.png", cell_size)
                        else:
                            obs_img = self.get_image("mount.webp", cell_size)
                        self.canvas.create_image(x1, y1, anchor=tk.NW, image=obs_img)

                    is_known = known_coords and (i, j) in known_coords
                    outline_color = "#FFD700" if is_known else "#DDDDDD"
                    outline_width = 3 if is_known else 1
                    self.canvas.create_rectangle(x1, y1, x1+cell_size, y1+cell_size, outline=outline_color, width=outline_width)
        self.root.update_idletasks()

    def update_solution_text(self, text):
        self.sol_text.config(state=tk.NORMAL)
        self.sol_text.delete(1.0, tk.END)
        self.sol_text.insert(tk.END, text)
        self.sol_text.config(state=tk.DISABLED)

    def run_algo(self, algo_name):
        if self.is_running: return
        self.is_running = True
        
        Node.reset_counter()
        
        self.current_matrix = [row[:] for row in self.initial_matrix]
        self.draw_grid(self.current_matrix)
        
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, f"[{algo_name}] Running...\n")
        self.update_solution_text("Searching...")
        self.root.update()
        
        path = None
        if algo_name == "BFS2": path = breadth_first_search_2(self.current_matrix)
        elif algo_name == "DFS2": path = depth_first_search_2(self.current_matrix)
        elif algo_name == "UCS": path = uniform_cost_search(self.current_matrix)
        elif algo_name == "GS": path = greedy_search(self.current_matrix)
        elif algo_name == "A*": path = a_star_search(self.current_matrix)
        elif algo_name == "IDA*": path = ida_star_search(self.current_matrix)
        elif algo_name == "SHC": path = simple_hill_climbing(self.current_matrix)
        elif algo_name == "LBS": path = local_beam_search(self.current_matrix, k=2)
        elif algo_name == "SA": path = simulated_annealing(self.current_matrix, T0=100, Tmin=1, alpha=0.95)
        
        if path == "LOCAL_MINIMUM":
            self.update_solution_text("Kẹt ở Local Minimum")
            self.log_text.insert(tk.END, "Algorithm stopped (Local Minimum)\n")
        elif path == "CUTOFF":
            self.update_solution_text("Bị giới hạn (Cutoff)")
            self.log_text.insert(tk.END, "Algorithm stopped (Cutoff)\n")
        elif path is None or len(path) == 0:
            if count_gift(self.current_matrix) == 0:
                self.update_solution_text("Bản đồ đã sạch sẽ.")
            else:
                self.update_solution_text("Không tìm thấy solution")
                self.log_text.insert(tk.END, "Search Failed!\n")
        else:
            self.update_solution_text(f"Total steps: {len(path)}\nPath: " + " -> ".join(path))
            self.animate_path(path)
            
        self.is_running = False

    def animate_path(self, path):
        self.log_text.insert(tk.END, f"\n[Executing Path]\n")
        for idx, action in enumerate(path):
            self.log_text.insert(tk.END, f"Step {idx+1:02d}: {action}\n")
            self.log_text.see(tk.END)
            
            self.current_matrix = result(self.current_matrix, action)
            self.draw_grid(self.current_matrix)
            
            self.root.update()
            time.sleep(config.ANIMATION_SPEED)
        
        self.log_text.insert(tk.END, "\nAll gifts collected.")
        self.log_text.see(tk.END)

    def generate_random_single_state(self, size):
        matrix = [[0 for _ in range(size)] for _ in range(size)]
        matrix[random.randint(0, size-1)][random.randint(0, size-1)] = 2
        for _ in range(2):
            rx, ry = random.randint(0, size-1), random.randint(0, size-1)
            if matrix[rx][ry] == 0: matrix[rx][ry] = 3
        for _ in range(random.randint(2, 4)):
            rx, ry = random.randint(0, size-1), random.randint(0, size-1)
            if matrix[rx][ry] == 0: matrix[rx][ry] = 1
        return matrix

    def generate_belief_states(self):
        if self.is_running: return
        self.active_view = "DUAL"
        size = int(self.size_var.get().split('x')[0])
        state1 = self.generate_random_single_state(size)
        state2 = self.generate_random_single_state(size)
        
        self.initial_belief_states = [copy_matrix(state1), copy_matrix(state2)]
        self.current_belief_states = [copy_matrix(state1), copy_matrix(state2)]
        
        self.draw_dual_grid(state1, state2)
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, "Generated 2 Belief States.\n")
        self.update_solution_text("")
        
    def generate_partial_belief_states(self):
        if self.is_running: return
        self.active_view = "PARTIAL"
        size = int(self.size_var.get().split('x')[0])
        num_known = max(1, (size * size) // 3)
        state1 = self.generate_random_single_state(size)
        
        all_coords = [(i, j) for i in range(size) for j in range(size)]
        self.known_coords = random.sample(all_coords, num_known)
        
        while True:
            state2 = [[0 for _ in range(size)] for _ in range(size)]
            santa_in_known = False
            for (x, y) in self.known_coords:
                state2[x][y] = state1[x][y]
                if state2[x][y] == 2: santa_in_known = True
                    
            unknown_coords = [c for c in all_coords if c not in self.known_coords]
            
            if not santa_in_known:
                if not unknown_coords: continue 
                rx, ry = random.choice(unknown_coords)
                state2[rx][ry] = 2
                
            empty_unknown = [(x, y) for (x, y) in unknown_coords if state2[x][y] == 0]
            for _ in range(min(2, len(empty_unknown))): 
                rx, ry = random.choice(empty_unknown)
                state2[rx][ry] = 3
                empty_unknown.remove((rx, ry))
                
            for _ in range(min(random.randint(2, 3), len(empty_unknown))): 
                rx, ry = random.choice(empty_unknown)
                state2[rx][ry] = 1
                empty_unknown.remove((rx, ry))
            break
            
        self.initial_belief_states = [copy_matrix(state1), copy_matrix(state2)]
        self.current_belief_states = [copy_matrix(state1), copy_matrix(state2)]
        
        self.draw_dual_grid(state1, state2, self.known_coords)
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, "Generated Partial Obs BS.\n")
        self.update_solution_text("")

    def run_sensorless_algo(self):
        if self.is_running: return
        if not hasattr(self, 'current_belief_states') or not self.current_belief_states: 
            self.generate_belief_states()
            
        self.is_running = True
        BeliefNode.reset_counter()
        
        self.current_belief_states = [copy_matrix(s) for s in self.initial_belief_states]
        self.draw_dual_grid(self.current_belief_states[0], self.current_belief_states[1])
        
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, "[Sensorless BFS] Running...\n")
        self.update_solution_text("Searching in Belief Space...")
        self.root.update()
        
        path = sensorless_bfs(self.current_belief_states)
        
        if path is None or len(path) == 0:
            if bs_goal_test(self.current_belief_states):
                self.update_solution_text("Cả 2 trạng thái khởi tạo đều đã sạch.")
            else:
                self.update_solution_text("Không tìm thấy solution")
                self.log_text.insert(tk.END, "No common action sequence.\n")
        else:
            self.update_solution_text(f"Total steps: {len(path)}\nPath: " + " -> ".join(path))
            self.animate_bs_path(path)
            
        self.is_running = False
        
    def run_partial_obs_algo(self):
        if self.is_running: return
        if not hasattr(self, 'current_belief_states') or not hasattr(self, 'known_coords') or not self.current_belief_states:
            self.generate_partial_belief_states()
            
        self.is_running = True
        BeliefNode.reset_counter()
        
        self.current_belief_states = [copy_matrix(s) for s in self.initial_belief_states]
        self.draw_dual_grid(self.current_belief_states[0], self.current_belief_states[1], self.known_coords)
        
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, "[Partial Obs BFS] Running...\n")
        self.update_solution_text("Searching with Partial Knowledge...")
        self.root.update()
        
        path = partial_obs_bfs(self.current_belief_states)
        
        if path is None or len(path) == 0:
            if bs_goal_test(self.current_belief_states):
                self.update_solution_text("Cả 2 trạng thái đều đã sạch.")
            else:
                self.update_solution_text("Không tìm thấy solution")
        else:
            self.update_solution_text(f"Total steps: {len(path)}\nPath: " + " -> ".join(path))
            self.animate_bs_path(path)
            
        self.is_running = False

    def format_conditional_plan(self, plan, indent=""):
        if not plan: 
            return "NoOp (Goal)\n"
        if isinstance(plan, list) and len(plan) == 2:
            action, sub_plans = plan[0], plan[1]
            res = f"Action {action}:\n"
            for key, sub_plan in sub_plans.items():
                label, state_tuple = key 
                res += f"{indent}  + Nếu [{label}] -> {self.format_conditional_plan(sub_plan, indent + '    ')}"
            return res
        return str(plan)

    def run_and_or_algo(self):
        if self.is_running: return
        self.is_running = True
        
        self.current_matrix = [row[:] for row in self.initial_matrix]
        self.draw_grid(self.current_matrix)
        
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, "[AND-OR SEARCH] Running...\n")
        self.update_solution_text("Đang tìm kiếm Conditional Plan...")
        self.root.update()
        
        conditional_plan = and_or_graph_search(self.current_matrix)
        
        if conditional_plan == "failure":
            self.update_solution_text("Thất bại! Vô nghiệm.")
            self.log_text.insert(tk.END, "\n[FAIL] Không tìm thấy kế hoạch.\n")
        else:
            plan_str = self.format_conditional_plan(conditional_plan)
            self.update_solution_text("Tìm thấy Kế hoạch điều kiện.")
            self.log_text.insert(tk.END, f"\n[SUCCESS] Conditional Plan:\n{plan_str}")
            
        self.log_text.see(tk.END)
        self.is_running = False

    def animate_bs_path(self, path):
        self.log_text.insert(tk.END, f"\n[Executing Path]\n")
        states = self.current_belief_states
        
        for idx, action in enumerate(path):
            self.log_text.insert(tk.END, f"Step {idx+1:02d}: {action}\n")
            self.log_text.see(tk.END)
            
            states = bs_result(states, action)
            self.current_belief_states = states
            
            if self.active_view == "PARTIAL":
                self.draw_dual_grid(states[0], states[1], getattr(self, 'known_coords', None))
            else:
                self.draw_dual_grid(states[0], states[1])
                
            self.root.update()
            time.sleep(config.BS_ANIMATION_SPEED)
            
        self.log_text.insert(tk.END, "\nAll possible states clean.")
        self.log_text.see(tk.END)