import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import LineCollection
from matplotlib.transforms import Affine2D
import numpy as np
from maze import MicromouseMaze, NORTH, EAST, SOUTH, WEST

class MazeVisualizer:
    def __init__(self, maze):
        self.maze = maze

    def draw_mouse(self, ax, pos, heading='NORTH'):
        """Draw a top-down cartoon mouse icon on a specific axis, rotated to face the given heading."""
        mx, my = pos
        angle = {'NORTH': 0, 'EAST': -90, 'SOUTH': 180, 'WEST': 90}.get(heading, 0)

        trans = Affine2D().rotate_deg_around(mx, my, angle) + ax.transData

        def add(patch):
            patch.set_transform(trans)
            ax.add_patch(patch)

        # Tail
        tail_x = mx + np.array([0.00, 0.06, 0.16, 0.18, 0.12])
        tail_y = my + np.array([-0.24, -0.34, -0.38, -0.46, -0.50])
        ax.plot(tail_x, tail_y, color='#e8a0a8', linewidth=2.5,
                solid_capstyle='round', transform=trans, zorder=5)

        # Body
        add(patches.Ellipse((mx, my - 0.02), 0.40, 0.56, fc='#9e9e9e',
                            ec='#5f5f5f', linewidth=1.5, zorder=6))
        # Ears
        for sx in (-1, 1):
            add(patches.Circle((mx + sx * 0.15, my + 0.17), 0.09, fc='#9e9e9e',
                               ec='#5f5f5f', linewidth=1.2, zorder=7))
            add(patches.Circle((mx + sx * 0.15, my + 0.17), 0.05, fc='#f4b6c0',
                               ec='none', zorder=8))
        # Head
        add(patches.Ellipse((mx, my + 0.22), 0.26, 0.28, fc='#b5b5b5',
                            ec='#5f5f5f', linewidth=1.5, zorder=9))
        # Eyes
        for sx in (-1, 1):
            add(patches.Circle((mx + sx * 0.055, my + 0.26), 0.02, fc='black',
                               ec='none', zorder=10))
        # Nose
        add(patches.Circle((mx, my + 0.36), 0.03, fc='#e56b7f', ec='none', zorder=10))

    def _collect_wall_segments(self):
        border, inner = [], []
        W, H = self.maze.width, self.maze.height
        for y in range(H):
            for x in range(W):
                w = self.maze.walls[y, x]
                if w & NORTH:
                    seg = [(x - 0.5, y + 0.5), (x + 0.5, y + 0.5)]
                    (border if y == H - 1 else inner).append(seg)
                if w & EAST:
                    seg = [(x + 0.5, y - 0.5), (x + 0.5, y + 0.5)]
                    (border if x == W - 1 else inner).append(seg)
                if (w & SOUTH) and y == 0:
                    border.append([(x - 0.5, y - 0.5), (x + 0.5, y - 0.5)])
                if (w & WEST) and x == 0:
                    border.append([(x - 0.5, y - 0.5), (x - 0.5, y + 0.5)])
        return border, inner

    def draw_maze_on_axis(self, ax, mouse_pos=None, heading='NORTH'):
        """Helper to render the maze, walls, zones, and mouse icon on a specific axis."""
        ax.set_facecolor('black')
        ax.set_aspect('equal')
        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.set_xlim(-0.5, self.maze.width - 0.5)
        ax.set_ylim(-0.5, self.maze.height - 0.5)

        ax.set_xticks(range(self.maze.width))
        ax.set_yticks(range(self.maze.height))
        ax.set_xticklabels([f"C{i}" for i in range(self.maze.width)], fontsize=8)
        ax.set_yticklabels([f"R{i}" for i in range(self.maze.height)], fontsize=8)

        ax.set_xticks(np.arange(-0.5, self.maze.width, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, self.maze.height, 1), minor=True)
        ax.grid(which='minor', color='#3a3a3a', linestyle=':', linewidth=0.8)
        ax.grid(which='major', color='none')
        ax.tick_params(which='minor', length=0)
        ax.tick_params(which='major', colors='white')

        # Goal Zone
        for gx, gy in self.maze.goals:
            ax.add_patch(patches.Rectangle((gx - 0.5, gy - 0.5), 1, 1, color='#ffc107', alpha=0.75))
            ax.text(gx, gy, 'G', color='black', weight='bold', fontsize=12, ha='center', va='center')

        # Start Zone
        sx, sy = self.maze.start
        ax.add_patch(patches.Rectangle((sx - 0.5, sy - 0.5), 1, 1, color='limegreen', alpha=0.6))
        ax.text(sx, sy, 'S', color='white', weight='bold', fontsize=12, ha='center', va='center')

        # Walls
        border, inner = self._collect_wall_segments()
        ax.add_collection(LineCollection(inner, colors='#ff2d2d', linewidths=3, capstyle='projecting', zorder=3))
        ax.add_collection(LineCollection(border, colors='#ff2d2d', linewidths=3, capstyle='projecting', zorder=4))

        # Draw Mouse Icon (Restored!)
        if mouse_pos is None:
            mouse_pos = self.maze.start
        self.draw_mouse(ax, mouse_pos, heading)

    def show_comparison(self, path_cardinal, path_diagonal):
        """Display side-by-side comparison of Cardinal A* vs Diagonal A* with custom colors."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
        fig.patch.set_facecolor('#111111')

        # Left plot: Cardinal 
        self.draw_maze_on_axis(ax1, mouse_pos=self.maze.start, heading='NORTH')
        ax1.set_title("A* Cardinal Planner", color='white', fontsize=12, pad=10)
        if path_cardinal:
            px = [p[0] for p in path_cardinal]
            py = [p[1] for p in path_cardinal]
            ax1.plot(px, py, color="#00ff55", linewidth=2.5, linestyle='-', marker='o', markersize=3, zorder=4, label="Cardinal Path")
            ax1.legend(loc="upper right")

        # Right plot: Diagonal 
        self.draw_maze_on_axis(ax2, mouse_pos=self.maze.start, heading='NORTH')
        ax2.set_title("A* Diagonal Planner", color='white', fontsize=12, pad=10)
        if path_diagonal:
            px_d = [p[0] for p in path_diagonal]
            py_d = [p[1] for p in path_diagonal]
            ax2.plot(px_d, py_d, color="#00bfff", linewidth=2.5, linestyle='-', marker='o', markersize=3, zorder=4, label="Diagonal Path")
            ax2.legend(loc="upper right")

        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    maze = MicromouseMaze(width=16, height=16)
    visualizer = MazeVisualizer(maze)
    visualizer.show()