from collections import deque
import heapq
from game_logic import GameState


def generate_moves(state):
    """Tạo các nước đi khả thi từ trạng thái hiện tại"""
    moves = []
    characters = state.characters

    # Tìm người lái thuyền (person hoặc scientist)
    driver_idx = None
    if "person" in characters:
        driver_idx = characters.index("person")
    elif "scientist" in characters:
        driver_idx = characters.index("scientist")

    if driver_idx is None:
        return moves

    # Các vật có thể chở (không bao gồm người lái)
    other_indices = [i for i in range(len(characters)) if i != driver_idx]

    # Tạo tất cả tổ hợp vật với kích thước từ 0 đến boat_capacity-1
    # (0 nghĩa là chỉ chở người lái)
    from itertools import combinations

    for r in range(0, state.boat_capacity):
        for combo in combinations(other_indices, r):
            move_indices = [driver_idx] + list(combo)

            # Kiểm tra tất cả vật được chọn phải cùng bờ với người lái
            valid = True
            for idx in move_indices:
                if state.state[idx] != state.state[driver_idx]:
                    valid = False
                    break

            if valid:
                # Đối với level 6, cần kiểm tra thêm ràng buộc Robot phải đi cùng người
                if state.level == 6:
                    moving = [characters[i] for i in move_indices]
                    # Robot phải đi cùng người (person)
                    if "robot" in moving and "person" not in moving:
                        continue

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
        # Heuristic đơn giản: số lượng vật còn ở bờ trái
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