from collections import deque
from game_logic import GameState

def bfs(start):
    queue = deque([(start, [])])
    visited = set()

    while queue:
        state, path = queue.popleft()

        if state.state in visited:
            continue
        visited.add(state.state)

        if state.is_goal():
            return path + [state]

        for next_state in generate_moves(state):
            queue.append((next_state, path + [state]))

    return None

def generate_moves(state):
    names = ["person","wolf","sheep","cabbage"]
    moves = []

    for item in names:
        selected = ["person"]
        if item != "person":
            selected.append(item)

        new_state = state.move(selected)
        if new_state:
            moves.append(new_state)

    return moves

def hint(state):
    sol = bfs(state)
    if sol and len(sol) > 1:
        return sol[1]
    return None