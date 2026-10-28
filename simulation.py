import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import LineCollection
from matplotlib.transforms import Affine2D
import numpy as np
from maze import MicromouseMaze, NORTH, EAST, SOUTH, WEST

class MazeVisualizer:
    def __init__(self, maze):
        self.maze = maze
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.ax.set_aspect('equal')
        self.fig.patch.set_facecolor('#111111')

    def draw_mouse(self, pos, heading='NORTH'):
        """Draw a top-down cartoon mouse icon, rotated to face the given heading."""
        mx, my = pos
        angle = {'NORTH': 0, 'EAST': -90, 'SOUTH': 180, 'WEST': 90}.get(heading, 0)

        # Rotate the whole icon around the cell center, then map to data coordinates
        trans = Affine2D().rotate_deg_around(mx, my, angle) + self.ax.transData

        def add(patch):
            patch.set_transform(trans)
            self.ax.add_patch(patch)

        # Tail (drawn first so it sits under the body)
        tail_x = mx + np.array([0.00, 0.06, 0.16, 0.18, 0.12])
        tail_y = my + np.array([-0.24, -0.34, -0.38, -0.46, -0.50])
        self.ax.plot(tail_x, tail_y, color='#e8a0a8', linewidth=2.5,
                     solid_capstyle='round', transform=trans, zorder=5)

        # Body
        add(patches.Ellipse((mx, my - 0.02), 0.40, 0.56, fc='#9e9e9e',
                            ec='#5f5f5f', linewidth=1.5, zorder=6))
        # Ears (outer gray, inner pink)
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
        """Return (border_segments, inner_segments); shared walls are stored only once."""
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
                # SOUTH / WEST of interior cells are drawn by the neighbouring cell
                if (w & SOUTH) and y == 0:
                    border.append([(x - 0.5, y - 0.5), (x + 0.5, y - 0.5)])
                if (w & WEST) and x == 0:
                    border.append([(x - 0.5, y - 0.5), (x - 0.5, y + 0.5)])
        return border, inner

    def draw_maze(self, mouse_pos=None, heading='NORTH'):
        """Render the complete 16x16 maze grid, walls, start zone, and goal zone."""
        self.ax.clear()
        self.ax.set_facecolor('black')
        for spine in self.ax.spines.values():
            spine.set_visible(False)

        # Set precise limits matching cell coordinate boundaries
        self.ax.set_xlim(-0.5, self.maze.width - 0.5)
        self.ax.set_ylim(-0.5, self.maze.height - 0.5)

        # Major ticks = cell centers, labelled C0..C15 (columns, x axis) and R0..R15 (rows, y axis)
        self.ax.set_xticks(range(self.maze.width))
        self.ax.set_yticks(range(self.maze.height))
        self.ax.set_xticklabels([f"C{i}" for i in range(self.maze.width)], fontsize=8)
        self.ax.set_yticklabels([f"R{i}" for i in range(self.maze.height)], fontsize=8)

        # Minor ticks = cell boundaries (used only for the light grid)
        self.ax.set_xticks(np.arange(-0.5, self.maze.width, 1), minor=True)
        self.ax.set_yticks(np.arange(-0.5, self.maze.height, 1), minor=True)
        self.ax.grid(which='minor', color='#3a3a3a', linestyle=':', linewidth=0.8)
        self.ax.grid(which='major', color='none')
        self.ax.tick_params(which='minor', length=0)
        self.ax.tick_params(which='major', colors='white')

        # 1. Draw Goal Zone (center 2x2 cells)
        for gx, gy in self.maze.goals:
            self.ax.add_patch(plt.Rectangle((gx - 0.5, gy - 0.5), 1, 1,
                                            color='#ffc107', alpha=0.75))
            self.ax.text(gx, gy, 'G', color='black', weight='bold',
                         fontsize=12, ha='center', va='center')

        # 2. Draw Start Zone (bottom-left cell)
        sx, sy = self.maze.start
        self.ax.add_patch(plt.Rectangle((sx - 0.5, sy - 0.5), 1, 1,
                                        color='limegreen', alpha=0.6))
        self.ax.text(sx, sy, 'S', color='white', weight='bold',
                     fontsize=12, ha='center', va='center')

        # 3. Draw Maze Walls: all walls (border and inner) in red
        border, inner = self._collect_wall_segments()
        self.ax.add_collection(LineCollection(inner, colors='#ff2d2d', linewidths=3,
                                              capstyle='projecting', zorder=3))
        self.ax.add_collection(LineCollection(border, colors='#ff2d2d', linewidths=3,
                                              capstyle='projecting', zorder=4))

        # 4. Draw Mouse Icon
        if mouse_pos is None:
            mouse_pos = self.maze.start
        self.draw_mouse(mouse_pos, heading)

        self.ax.set_title("Micromouse 16x16 Maze Simulation Environment", fontsize=14, pad=10, color='white')
        self.ax.set_xlabel("Column (C)", color="white")
        self.ax.set_ylabel("Row (R)", color="white")

    def show(self):
        """Display the simulation window."""
        self.draw_maze(mouse_pos=self.maze.start, heading='NORTH')
        plt.show()


if __name__ == "__main__":
    maze = MicromouseMaze(width=16, height=16)
    visualizer = MazeVisualizer(maze)
    visualizer.show()