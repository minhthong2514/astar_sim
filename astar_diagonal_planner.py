import math
import heapq
from maze import MicromouseMaze

def heuristic(cell, goals):
    x, y = cell
    return min(abs(x - gx) + abs(y - gy) for gx, gy in goals) * (math.sqrt(2) / 2)

def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path

def a_star_diagonal_search(maze):
    start = maze.start
    goals = maze.goals

    start_state = (start[0], start[1], -1)

    # Priority queue stores tuples of (f_score, g_score, current_state)
    open_set = []
    heapq.heappush(open_set, (0 + heuristic(start, goals), 0, start_state))

    came_from = {}
    g_score = {start_state: 0}
    f_score = {start_state: heuristic(start, goals)}

    closed_set = set()

    while open_set:
        _, current_g, current = heapq.heappop(open_set)
        cx, cy, current_heading = current   # CHANGED: moved up from below

        # Check if we reached any of the goal cells
        if (cx, cy) in goals:
            # CHANGED: convert states to points. The path runs through the midpoint of each
            # crossed edge (not through cell centers), so it never touches a wall corner
            cells = [(sx, sy) for sx, sy, _ in reconstruct_path(came_from, current)]
            path = [cells[0]]
            for (ax, ay), (bx, by) in zip(cells, cells[1:]):
                path.append(((ax + bx) / 2, (ay + by) / 2))
            path.append(cells[-1])
            return path

        if current in closed_set:
            continue
        closed_set.add(current)

        # Diagonal motion comes from turning 90 degrees inside a cell (corner cutting)
        neighbors = [
            (0,  1),   # North
            (1,  0),   # East
            (0, -1),   # South
            (-1, 0)    # West
        ]

        for heading, (dx, dy) in enumerate(neighbors):
            neighbor_cell = (cx + dx, cy + dy)

            if current_heading != -1 and heading == (current_heading + 2) % 4:
                continue

            # Use maze's built-in wall check (only straight neighbors are checked now)
            if maze.is_wall_between((cx, cy), neighbor_cell):
                continue

            neighbor = (neighbor_cell[0], neighbor_cell[1], heading)

            if neighbor in closed_set:
                continue

            if current_heading == -1:
                move_cost = 0.5                 # start: cell center -> edge midpoint
            elif heading == current_heading:
                move_cost = 1.0                 # straight through the cell
            else:
                move_cost = math.sqrt(2) / 2    # 90-degree turn: diagonal chord

            tentative_g = current_g + move_cost

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor_cell, goals)
                heapq.heappush(open_set, (f_score[neighbor], tentative_g, neighbor))

    return None

if __name__ == "__main__":
    maze = MicromouseMaze(width=16, height=16)
    path = a_star_diagonal_search(maze)
    print("Found diagonal path length:", len(path) if path else "No path found")
    print("Path coordinates:", path)