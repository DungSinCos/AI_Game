from collections import deque
import heapq
from game_logic import GameState


def generate_moves(state):
    """Tạo các nước đi khả thi từ trạng thái hiện tại"""
    moves = []
    characters = state.characters

    # Person luôn đi
    person_idx = 0

    # Các tổ hợp vật có thể chở (1 hoặc nhiều tùy boat_capacity)
    # Với mỗi vật có thể chọn hoặc không
    other_indices = list(range(1, len(characters)))

    # Tạo tất cả tổ hợp vật (subset) với kích thước từ 1 đến boat_capacity-1
    for r in range(1, state.boat_capacity):
        from itertools import combinations
        for combo in combinations(other_indices, r):
            move_indices = [person_idx] + list(combo)
            # Kiểm tra vật được chọn phải cùng bờ với người
            valid = True
            for idx in move_indices:
                if state.state[idx] != state.state[person_idx]:
                    valid = False
                    break
            if valid:
                new_state = state.move(move_indices)
                if new_state:
                    moves.append(new_state)

    # Trường hợp chỉ chở mình người
    move_indices = [person_idx]
    new_state = state.move(move_indices)
    if new_state:
        moves.append(new_state)

    return moves


def heuristic(state):
    """Heuristic: số lượng vật còn ở bờ trái"""
    if state.level == 5:
        # Level 5: ưu tiên vật có thời gian lớn
        tiger_times = state.level_data.get("tiger_times", {})
        total_time = 0
        for i, pos in enumerate(state.state):
            if i > 0 and pos == 0:  # vật ở bờ trái
                item_name = state.characters[i]
                total_time += tiger_times.get(item_name, 1)
        return total_time
    else:
        return sum(1 for x in state.state if x == 0)


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


def dfs(start):
    stack = [(start, [])]
    visited = set()

    while stack:
        state, path = stack.pop()

        if state.state in visited:
            continue
        visited.add(state.state)

        if state.is_goal():
            return path + [state]

        for next_state in generate_moves(state):
            stack.append((next_state, path + [state]))
    return None


def ucs(start):
    count = 0
    pq = [(0, count, start, [])]
    visited = {}

    while pq:
        cost, _, state, path = heapq.heappop(pq)

        if state.state in visited and visited[state.state] <= cost:
            continue
        visited[state.state] = cost

        if state.is_goal():
            return path + [state]

        for next_state in generate_moves(state):
            count += 1
            heapq.heappush(pq, (next_state.cost, count, next_state, path + [state]))
    return None


def greedy(start):
    count = 0
    pq = [(heuristic(start), count, start, [])]
    visited = set()

    while pq:
        h, _, state, path = heapq.heappop(pq)

        if state.state in visited:
            continue
        visited.add(state.state)

        if state.is_goal():
            return path + [state]

        for next_state in generate_moves(state):
            count += 1
            heapq.heappush(pq, (heuristic(next_state), count, next_state, path + [state]))
    return None


def astar(start):
    count = 0
    pq = [(heuristic(start), count, 0, start, [])]
    visited = {}

    while pq:
        f, _, g, state, path = heapq.heappop(pq)

        if state.state in visited and visited[state.state] <= g:
            continue
        visited[state.state] = g

        if state.is_goal():
            return path + [state]

        for next_state in generate_moves(state):
            new_g = next_state.cost
            new_f = new_g + heuristic(next_state)
            count += 1
            heapq.heappush(pq, (new_f, count, new_g, next_state, path + [state]))
    return None


def hint(state):
    """Gợi ý nước đi tiếp theo"""
    sol = bfs(state)
    if sol and len(sol) > 1:
        return sol[1]
    return None