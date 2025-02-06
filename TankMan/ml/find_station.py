from collections import deque


class find_station:
    def __init__(self, row, col, size):
        self.row = row
        self.col = col
        self.size = size
        self.direction = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]

    def calculate_forward(self, angle):
        return self.direction[ int(angle / 45) ]

    def calculate_direction(self, angle):
        if angle == 0 or angle == 180:
            return (-1, 0), (1, 0)
        elif angle == 45 or angle == 225:
            return (-1, 1), (1, -1)
        elif angle == 90 or angle == 270:
            return (0, 1), (0, -1)
        else:
            return (1, 1), (-1, -1)
    
    def walk2target(self, start, end):
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        dangle = end[2] - start[2]
        if dangle == 45 or dangle == -315:
            return "TURN_LEFT"
        elif dangle == -45 or dangle == 315:
            return "TURN_RIGHT"
        elif (dx, dy) == self.calculate_forward(start[2]):
            return "FORWARD"
        else:
            return "BACKWARD"

    def bfs(self, start, target, map):
        queue = deque([start])
        visited = set([start])
        parent = {start: None}

        while queue:
            current = queue.popleft()
            if map[current[0], current[1]] == target:
                path = []
                while current is not None:
                    path.append((current))
                    current = parent[current]
                path.reverse()
                return path

            for direction in self.calculate_direction(current[2]):
                row, col = current[0] + direction[0], current[1] + direction[1]

                if 0 <= row < self.row and 0 <= col < self.col and map[row][col] != 1 and (row, col, current[2]) not in visited:
                    queue.append((row, col, current[2]))
                    visited.add((row, col, current[2]))
                    parent[(row, col, current[2])] = current
            
            for i in [-1, 1]:
                if current[2] + 45*i >= 360:
                    new_angle = 0
                elif current[2] + 45*i < 0:
                    new_angle = 315
                else:
                    new_angle = current[2] + 45*i
                if (current[0], current[1], new_angle) not in visited:
                    queue.append((current[0], current[1], new_angle))
                    visited.add((current[0], current[1], new_angle))
                    parent[(current[0], current[1], new_angle)] = current
        return []