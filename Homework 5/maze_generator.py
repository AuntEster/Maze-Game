"""
Maze generation using Prim's algorithm
Converted to py using Claude from C++ code written for COSC 2436

"""

import random
from queue import PriorityQueue

class Cell:
    """Represents a single cell in the maze with 4 walls"""
    def __init__(self):
        # Walls: [North, East, South, West] = [0, 1, 2, 3]
        self.wall = [True, True, True, True]

class Maze:
    """Maze data structure with generation and utility functions"""
    
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [Cell() for _ in range(rows * cols)]
        
        # Direction vectors: North, East, South, West
        self.dr = [-1, 0, 1, 0]
        self.dc = [0, 1, 0, -1]
    
    def index(self, r, c):
        """Convert 2D coordinates to 1D index"""
        return r * self.cols + c
    
    def remove_wall(self, a, b):
        """Remove wall between two adjacent cells"""
        ar = a // self.cols
        ac = a % self.cols
        br = b // self.cols
        bc = b % self.cols
        
        # Find which direction b is from a
        for d in range(4):
            if ar + self.dr[d] == br and ac + self.dc[d] == bc:
                self.grid[a].wall[d] = False
                self.grid[b].wall[(d + 2) % 4] = False  # Opposite wall
                return
    
    def generate_prim(self, seed=None):
        """Generate maze using Prim's algorithm"""
        if seed is not None:
            random.seed(seed)
        
        # Reset all walls to closed
        for cell in self.grid:
            cell.wall = [True, True, True, True]
        
        N = self.rows * self.cols
        in_tree = [False] * N
        
        # Priority queue: (random_weight, from_cell, to_cell)
        pq = PriorityQueue()
        
        # Start from cell (0, 0)
        in_tree[0] = True
        sr, sc = 0, 0
        
        # Add all neighbors of starting cell to priority queue
        for d in range(4):
            nr = sr + self.dr[d]
            nc = sc + self.dc[d]
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                weight = random.random()
                pq.put((weight, 0, self.index(nr, nc)))
        
        count = 1
        while count < N and not pq.empty():
            weight, u, v = pq.get()
            
            if in_tree[v]:
                continue
            
            # Add edge to maze
            self.remove_wall(u, v)
            in_tree[v] = True
            count += 1
            
            # Add neighbors of v to priority queue
            vr = v // self.cols
            vc = v % self.cols
            
            for d in range(4):
                nr = vr + self.dr[d]
                nc = vc + self.dc[d]
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    vn = self.index(nr, nc)
                    if not in_tree[vn]:
                        weight = random.random()
                        pq.put((weight, v, vn))
    
    def solve_bfs(self):
        """Find shortest path from (0,0) to (rows-1, cols-1) using BFS"""
        N = self.rows * self.cols
        visited = [False] * N
        parent = [-1] * N
        queue = []
        
        visited[0] = True
        queue.append(0)
        
        goal = N - 1
        
        while queue:
            u = queue.pop(0)
            
            if u == goal:
                break
            
            ur = u // self.cols
            uc = u % self.cols
            
            # Check all 4 directions
            for d in range(4):
                if not self.grid[u].wall[d]:  # If there's no wall in this direction
                    vr = ur + self.dr[d]
                    vc = uc + self.dc[d]
                    v = self.index(vr, vc)
                    
                    if not visited[v]:
                        visited[v] = True
                        parent[v] = u
                        queue.append(v)
        
        return parent
    
    def get_path(self):
        """Get the solution path as a list of cell indices"""
        parent = self.solve_bfs()
        path = []
        
        v = self.rows * self.cols - 1  # Goal
        while v != -1:
            path.append(v)
            v = parent[v]
        
        path.reverse()
        return path
    
    def print_maze(self, path=None):
        """Print ASCII representation of maze"""
        path_set = set(path) if path else set()
        
        # Top border
        for c in range(self.cols):
            print("+---", end="")
        print("+")
        
        # Maze cells
        for r in range(self.rows):
            # Left wall and cell content
            for c in range(self.cols):
                idx = self.index(r, c)
                
                # Left wall
                if self.grid[idx].wall[3]:  # West wall
                    print("|", end="")
                else:
                    print(" ", end="")
                
                # Cell content
                if idx in path_set:
                    print(" * ", end="")
                else:
                    print("   ", end="")
            
            print("|")  # Right border
            
            # Bottom walls
            for c in range(self.cols):
                idx = self.index(r, c)
                print("+", end="")
                if self.grid[idx].wall[2]:  # South wall
                    print("---", end="")
                else:
                    print("   ", end="")
            print("+")


# Test the maze generation
if __name__ == "__main__":
    print("Testing Maze Generation with Prim's Algorithm\n")
    
    # Create a 10x10 maze
    maze = Maze(10, 10)
    maze.generate_prim(seed=42)
    
    # Solve and print
    path = maze.get_path()
    print(f"Solution uses {len(path)} cells out of {maze.rows * maze.cols} total")
    print(f"Percentage: {100.0 * len(path) / (maze.rows * maze.cols):.1f}%\n")
    
    maze.print_maze(path)
    
    print("\n" + "="*50)
    print("Testing with a smaller 5x5 maze:\n")
    
    small_maze = Maze(5, 5)
    small_maze.generate_prim(seed=123)
    small_path = small_maze.get_path()
    small_maze.print_maze(small_path)