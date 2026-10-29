import heapq
from maze import MicromouseMaze

def heuristic(cell, goals):
    x, y = cell
    return min(abs(x - gx) + abs(y - gy) for gx, gy in goals)

def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path

def a_star_search(maze):
    start = maze.start
    goals = maze.goals

    # Priority queue for open set stores tuples of (f_score, g_score, current_cell)
    open_set = []
    heapq.heappush(open_set, (0 + heuristic(start, goals), 0, start))

    # Dictionaries to track path and costs
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goals)}

    # Closed set to keep track of visited cells
    closed_set = set()

    while open_set:
        # Pop the node with the lowest f_score from the priority queue
        _, current_g, current = heapq.heappop(open_set)

        # Check if we have reached any of the goal cells
        if current in goals:
            return reconstruct_path(came_from, current)

        if current in closed_set:
            continue
        closed_set.add(current)

        # Define 4 cardinal directions (dx, dy)
        neighbors = [
            (0, 1),     # NORTH (Up)
            (1, 0),     # EAST (RIGHT)
            (0, -1),    # SOUTH (DOWN)
            (-1, 0),    # WEST (LEFT)     
        ]

        cx, cy = current
        for dx, dy in neighbors:
            neighbor = (cx + dx, cy + dy)

            # Check if movement is blocked by a wall or out of bounds
            if maze.is_wall_between(current, neighbor):
                continue

            if neighbor in closed_set:
                continue

            # Each step has a cost of 1
            tentative_g = current_g + 1

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(start, goals)
                heapq.heappush(open_set, (f_score[neighbor], tentative_g, neighbor))

    # Return none if no path exists
    return None 

if __name__ == "__main__":
    maze = MicromouseMaze(width=16, height=16)
    path = a_star_search(maze)
    print("Found path length:", len(path) if path else "No path found")
    print("Path coordinates:", path)