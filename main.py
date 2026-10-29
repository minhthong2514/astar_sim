from maze import MicromouseMaze
from astar_planner import a_star_search
from simulation import MazeVisualizer

def main():
    maze = MicromouseMaze(width=16, height=16)
    
    path = a_star_search(maze)
    
    if path:
        print("Found path length:", len(path) if path else "No path found")
        print("Path coordinates:", path)
    else:
        path = []

    visualizer = MazeVisualizer(maze)    
    
    visualizer.ax.clear()
    visualizer.draw_maze(mouse_pos=maze.start, heading='NORTH')
    
    if path:
        path_x = [p[0] for p in path]
        path_y = [p[1] for p in path]
        visualizer.ax.plot(path_x, path_y, color="#00ff55", linewidth=2.5, 
                           linestyle='-', alpha=0.9, marker='o', markersize=3, zorder=4)

    visualizer.fig.show()
    import matplotlib.pyplot as plt
    plt.show()

if __name__ == "__main__":
    main()