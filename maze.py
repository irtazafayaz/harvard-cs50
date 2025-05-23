import sys
import heapq


class Node:
    def __init__(self, state, parent, action, g=0, h=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.g = g
        self.h = h
        self.f = g + h

    def __lt__(self, other):
        return self.f < other.f


class StackFrontier:
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("=> empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node


class QueueFrontier(StackFrontier):
    def remove(self):
        if self.empty():
            raise Exception("frontier empty")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node


class PriorityQueueFrontier:
    def __init__(self):
        self.frontier = []
        self.entry_finder = {}

    def add(self, node):
        if node.state not in self.entry_finder:
            entry = (node.f, node)
            heapq.heappush(self.frontier, entry)
            self.entry_finder[node.state] = entry

    def contains(self, state):
        return state in self.entry_finder

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        while self.frontier:
            f, node = heapq.heappop(self.frontier)
            if node.state in self.entry_finder:
                del self.entry_finder[node.state]
                return node
        raise Exception("-- empty frontier")


class Maze:

    def __init__(self, filename):

        # Read file and set height and width of maze
        with open(filename) as f:
            contents = f.read()

        # Validate start and goal
        if contents.count("A") != 1:
            raise Exception("maze must have exactly one start point")
        if contents.count("B") != 1:
            raise Exception("maze must have exactly one goal")

        # Determine height and width of maze
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        # Keep track of walls
        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)

                    elif contents[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)

        self.solution = None

    def print(self):
        solution = self.solution[1] if self.solution is not None else None
        print()
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("▓", end="")  # Medium shaded block
                elif (i, j) == self.start:
                    print("A", end="")
                elif (i, j) == self.goal:
                    print("B", end="")
                elif solution is not None and (i, j) in solution:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
        print()

    def neighbors(self, state):
        row, col = state
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1)),
        ]

        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))
        return result

    def heuristic(self, state):
        print(state)
        row1, col1 = state
        row2, col2 = self.goal
        return abs(row1 - row2) + abs(col1 - col2)  # Manhattan distance

    def solve(self):

        self.num_explored = 0
        start = Node(
            state=self.start,
            parent=None,
            action=None,
            g=0,
            h=self.heuristic(self.start),
        )
        frontier = PriorityQueueFrontier()
        frontier.add(start)
        self.explored = set()

        while True:
            if frontier.empty():
                raise Exception("no solution")

            node = frontier.remove()
            self.num_explored += 1

            if self.goal == node.state:
                actions = []
                cells = []

                while node.parent is not None:
                    cells.append(node.state)
                    actions.append(node.action)

                    node = node.parent
                cells.reverse()
                actions.reverse()
                self.solution = (actions, cells)
                return

            self.explored.add(node.state)

            for action, state in self.neighbors(node.state):
                if not frontier.contains(state) and state not in self.explored:
                    new_node = Node(
                        state=state,
                        parent=node,
                        action=action,
                        g=node.g + 1,
                        h=self.heuristic(state),
                    )
                    frontier.add(new_node)

    def solve_using_uninformed(self):
        """Find a solution to maze, if it exists"""

        # Keep track of number of states explored (Info purposes)
        self.num_explored = 0

        # Initializing the frontier to the starting point
        start = Node(state=self.start, parent=None, action=None)
        frontier = QueueFrontier()
        frontier.add(start)

        # Initialize the empty explored set
        self.explored = set()

        while True:

            if frontier.empty():
                raise Exception("no solution")

            node = frontier.remove()
            self.num_explored += 1

            if self.goal == node.state:
                # Explore the path
                actions = []
                cells = []

                while node.parent is not None:
                    cells.append(node.state)
                    actions.append(node.action)

                    node = node.parent
                cells.reverse()
                actions.reverse()
                self.solution = (actions, cells)
                return

            self.explored.add(node.state)

            for action, state in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in self.explored:
                    child = Node(state=state, parent=node, action=action)
                    frontier.add(child)

    def output_image(self, filename, show_solution=True, show_explored=False):
        from PIL import Image, ImageDraw, ImageFont

        cell_size = 50
        cell_border = 2

        # Try to load a default font
        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()

        img = Image.new(
            "RGBA", (self.width * cell_size, self.height * cell_size), "black"
        )
        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution is not None else None
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                x0 = j * cell_size + cell_border
                y0 = i * cell_size + cell_border
                x1 = (j + 1) * cell_size - cell_border
                y1 = (i + 1) * cell_size - cell_border
                box = [(x0, y0), (x1, y1)]

                # Walls
                if col:
                    fill = (40, 40, 40)
                # Start
                elif (i, j) == self.start:
                    fill = (255, 0, 0)
                # Goal
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)
                # Solution
                elif solution is not None and show_solution and (i, j) in solution:
                    fill = (220, 235, 113)
                # Explored
                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)
                else:
                    fill = (237, 240, 252)

                draw.rectangle(box, fill=fill)

                # Draw heuristic value on non-wall, non-start, non-goal cells
                if not col and (i, j) != self.start and (i, j) != self.goal:
                    h_val = self.heuristic((i, j))
                    draw.text((x0 + 5, y0 + 5), str(h_val), fill=(0, 0, 0), font=font)

            img.save(filename)


if len(sys.argv) != 2:
    sys.exit("Usage: python maze.py maze.txt")

m = Maze(sys.argv[1])
print("Maze:")
m.print()
print("Solving...")
m.solve()
print("States Explored:", m.num_explored)
print("Solution:")
m.print()
m.output_image("maze.png", show_explored=True)
