import numpy as np

# Bitmask constants for wall representation
NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

# ---------------------------------------------------------------------------
# Maze layout copied from the reference image.
#
# Format (33 lines x 49 chars):
#   - Even lines (0, 2, 4, ...) are horizontal wall lines: "+--" = wall, "+  " = open
#   - Odd lines (1, 3, 5, ...)  are vertical wall lines:   "|  " = wall, "   " = open
#   - The FIRST text line is the TOP of the maze (row y = 15),
#     the LAST text line is the BOTTOM of the maze (row y = 0).
#
# Coordinates used by the code: (x, y) = (column R, row C),
# with (0, 0) at the bottom-left corner, exactly like the labels in the image.
# To fix a wall, just edit the characters below.
# ---------------------------------------------------------------------------
MAZE_LAYOUT = """
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                                               |
+  +--+--+--+--+--+--+--+--+--+--+--+--+--+--+  +
|  |                                            |
+  +  +--+--+--+--+--+--+--+--+  +--+--+--+--+  +
|  |  |                    |                 |  |
+  +  +  +--+--+--+  +--+--+--+--+  +--+--+  +  +
|  |  |  |  |     |        |  |     |        |  |
+  +  +  +  +  +  +--+--+  +  +  +--+  +--+--+  +
|  |  |  |     |  |     |     |  |           |  |
+  +  +  +  +--+  +  +  +--+  +  +--+--+--+  +  +
|  |  |  |     |  |  |     |     |           |  |
+  +  +  +--+  +  +  +--+  +--+--+  +--+--+--+  +
|  |  |        |  |  |           |        |  |  |
+  +  +--+--+--+  +  +--+--+--+  +--+--+  +  +  +
|  |  |     |     |  |        |           |  |  |
+  +  +  +  +--+  +  +  +  +  +--+--+--+--+  +  +
|  |  |  |     |  |  |     |        |        |  |
+  +  +  +--+  +  +  +--+--+--+  +--+  +  +  +  +
|  |  |  |     |     |        |     |  |  |  |  |
+  +  +  +  +--+  +--+--+  +  +--+  +  +--+  +  +
|  |  |  |        |     |  |     |           |  |
+  +  +  +--+--+--+  +  +  +--+  +--+  +--+  +  +
|  |  |           |  |  |     |     |     |  |  |
+  +  +--+--+--+  +  +  +--+  +--+  +--+  +  +  +
|  |  |           |  |  |        |     |     |  |
+  +  +  +--+--+--+  +  +--+--+  +--+  +--+  +  +
|     |  |           |  |           |     |  |  |
+  +  +  +--+--+--+  +  +--+--+--+  +--+  +  +  +
|  |  |              |              |        |  |
+  +  +--+--+--+--+--+--+--+--+--+--+--+--+--+  +
|  |                                            |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
""".strip("\n")


class MicromouseMaze:
    def __init__(self, width=16, height=16):
        self.width = width
        self.height = height
        self.walls = np.zeros((self.height, self.width), dtype=int)

        # Start position at bottom-left corner (R0, C0)
        self.start = (0, 0)

        # Central goal region (2x2 area)
        self.goals = {(7, 7), (7, 8), (8, 7), (8, 8)}

        self._build_exact_maze_layout()

    def add_wall(self, x, y, direction):
        """Add a wall to a specific cell and update the adjacent cell accordingly."""
        self.walls[y, x] |= direction

        if direction == NORTH and y < self.height - 1:
            self.walls[y + 1, x] |= SOUTH
        elif direction == EAST and x < self.width - 1:
            self.walls[y, x + 1] |= WEST
        elif direction == SOUTH and y > 0:
            self.walls[y - 1, x] |= NORTH
        elif direction == WEST and x > 0:
            self.walls[y, x - 1] |= EAST

    def _build_exact_maze_layout(self):
        """Build the walls by parsing MAZE_LAYOUT (ASCII map taken from the image)."""
        lines = MAZE_LAYOUT.split("\n")
        expected = 2 * self.height + 1
        if len(lines) != expected:
            raise ValueError(f"MAZE_LAYOUT must have {expected} lines, got {len(lines)}")

        for row in range(self.height):          # row 0 in text = top of the maze
            y = self.height - 1 - row           # convert to y (0 = bottom)
            h_top = lines[2 * row]              # horizontal line above this row
            v_line = lines[2 * row + 1]         # vertical walls of this row
            h_bottom = lines[2 * row + 2]       # horizontal line below this row

            for x in range(self.width):
                c = 3 * x                       # char offset of this cell
                if h_top[c + 1] == "-":
                    self.add_wall(x, y, NORTH)
                if h_bottom[c + 1] == "-":
                    self.add_wall(x, y, SOUTH)
                if v_line[c] == "|":
                    self.add_wall(x, y, WEST)
                if v_line[c + 3] == "|":
                    self.add_wall(x, y, EAST)

    def is_wall_between(self, current, neighbor):
        """Check if movement between current cell and neighbor cell is blocked by a wall."""
        cx, cy = current
        nx, ny = neighbor

        # Neighbor outside the maze is always blocked
        if not (0 <= nx < self.width and 0 <= ny < self.height):
            return True

        dx = nx - cx
        dy = ny - cy

        if dx == 0 and dy == 1:
            return bool(self.walls[cy, cx] & NORTH)
        elif dx == 1 and dy == 0:
            return bool(self.walls[cy, cx] & EAST)
        elif dx == 0 and dy == -1:
            return bool(self.walls[cy, cx] & SOUTH)
        elif dx == -1 and dy == 0:
            return bool(self.walls[cy, cx] & WEST)

        # Diagonal collision checks to prevent corner cutting
        elif dx == 1 and dy == 1:
            return bool(self.walls[cy, cx] & (NORTH | EAST)) or \
                   bool(self.walls[cy + 1, cx] & EAST) or bool(self.walls[cy, cx + 1] & NORTH)
        elif dx == -1 and dy == 1:
            return bool(self.walls[cy, cx] & (NORTH | WEST)) or \
                   bool(self.walls[cy + 1, cx] & WEST) or bool(self.walls[cy, cx - 1] & NORTH)
        elif dx == 1 and dy == -1:
            return bool(self.walls[cy, cx] & (SOUTH | EAST)) or \
                   bool(self.walls[cy - 1, cx] & EAST) or bool(self.walls[cy, cx + 1] & SOUTH)
        elif dx == -1 and dy == -1:
            return bool(self.walls[cy, cx] & (SOUTH | WEST)) or \
                   bool(self.walls[cy - 1, cx] & WEST) or bool(self.walls[cy, cx - 1] & SOUTH)

        return True