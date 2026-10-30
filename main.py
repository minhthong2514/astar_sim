from maze import MicromouseMaze
from astar_cardinal_planner import a_star_cardinal_search
from astar_diagonal_planner import a_star_diagonal_search
from simulation import MazeVisualizer
import math

def path_length(path):
    return sum(math.hypot(p2[0] - p1[0], p2[1] - p1[1]) for p1, p2 in zip(path, path[1:]))

def main():
    # Initialize the 16x16 maze
    maze = MicromouseMaze(width=16, height=16)
    
    # 1. Run Cardinal A* (4-connected, straight lines only)
    path_cardinal = a_star_cardinal_search(maze)
    print("Cardinal Path Length:", path_length(path_cardinal) if path_cardinal else "No path found")

    # 2. Run Diagonal A* (8-connected, allows diagonal steps)
    path_diagonal = a_star_diagonal_search(maze)
    print("Diagonal Path Length:", path_length(path_diagonal) if path_diagonal else "No path found")
    
    # 3. Visualize side-by-side comparison using MazeVisualizer
    visualizer = MazeVisualizer(maze)
    visualizer.show_comparison(path_cardinal, path_diagonal)

if __name__ == "__main__":
    main()