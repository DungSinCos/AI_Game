from collections import deque
import heapq
from game_logic import GameState
import time
from itertools import combinations


def generate_moves(state):
    moves = []
    characters = state.characters

    # Level 6 xử lý đặc biệt
    if state.level == 6:
        same_side = [i for i, v in enumerate(state.state) if v == state.boat_side]
        for r in range(1, state.boat_capacity + 1):
            for combo in combinations(same_side, r):
                new_state = state.move(combo)
                if new_state:
                    moves.append(new_state)
        return moves

    # Tìm tất cả người có thể lái thuyền
    driver_indices = []
    if "person" in characters:
        driver_indices.append(characters.index("person"))
    if "scientist" in characters:
        driver_indices.append(characters.index("scientist"))

    # Nếu không có người lái, cho phép bất kỳ ai lên thuyền
    if not driver_indices:
        same_side = [i for i, v in enumerate(state.state) if v == state.boat_side]
        for r in range(1, state.boat_capacity + 1):
            for combo in combinations(same_side, r):
                new_state = state.move(combo)
                if new_state:
                    moves.append(new_state)
        return moves

    # Xác định số lượng vật tối đa được chở
    max_items = state.boat_capacity - 1

    # Level 4 chỉ cho chở tối đa 1 vật
    if state.level == 4:
        max_items = 1

    # Với mỗi người lái có thể
    for driver_idx in driver_indices:
        # Kiểm tra người lái có ở cùng bờ không
        if state.state[driver_idx] != state.boat_side:
            continue

        # Các nhân vật khác (không phải người lái hiện tại)
        other_indices = [i for i in range(len(characters)) if i != driver_idx]

        # Tạo các tổ hợp: người lái + 0 đến max_items vật
        for r in range(0, max_items + 1):
            for combo in combinations(other_indices, r):
                move_indices = [driver_idx] + list(combo)

                # Kiểm tra tất cả đều ở cùng bờ với thuyền
                valid = all(state.state[idx] == state.boat_side for idx in move_indices)

                if valid:
                    new_state = state.move(move_indices)
                    if new_state:
                        moves.append(new_state)

    return moves


def heuristic(state):
    left_bank_count = sum(1 for i, pos in enumerate(state.state) if pos == 0)

    if left_bank_count == 0:
        return 0

    if state.level == 5:
        tiger_times = state.level_data.get("tiger_times", {})
        total_time = 0
        for i, pos in enumerate(state.state):
            if i > 0 and pos == 0:
                item_name = state.characters[i]
                total_time += tiger_times.get(item_name, 1)
        return total_time

    elif state.level == 6:
        lazy_idx = state.characters.index("scientist1")
        arrogant_idx = state.characters.index("scientist2")
        brave1_idx = state.characters.index("person1")
        brave2_idx = state.characters.index("person2")

        lazy_left = 1 if state.state[lazy_idx] == 0 else 0
        arrogant_left = 1 if state.state[arrogant_idx] == 0 else 0
        brave1_left = 1 if state.state[brave1_idx] == 0 else 0
        brave2_left = 1 if state.state[brave2_idx] == 0 else 0

        # Heuristic đơn giản: số người chưa qua sông
        return lazy_left + arrogant_left + brave1_left + brave2_left

    elif state.level == 7:
        bomb_idx = state.characters.index("bomb") if "bomb" in state.characters else -1
        if bomb_idx != -1 and state.state[bomb_idx] == 0:
            return left_bank_count * 2
        return left_bank_count

    else:
        return left_bank_count


def bfs(start):
    start_time = time.perf_counter()  # Dùng perf_counter thay vì time.time()
    queue = deque([(start, [])])
    visited = set()
    states_explored = 0

    while queue:
        state, path = queue.popleft()
        key = (state.state, state.boat_side)

        if key in visited:
            continue
        visited.add(key)
        states_explored += 1

        if state.is_goal():
            solution_path = path + [state]
            exec_time = time.perf_counter() - start_time
            solution_length = len(solution_path) - 1
            cost = state.cost
            return solution_path, exec_time, states_explored, solution_length, cost

        for next_state in generate_moves(state):
            queue.append((next_state, path + [state]))
    return None, time.perf_counter() - start_time, states_explored, None, None


def dfs(start):
    start_time = time.perf_counter()  # Dùng perf_counter thay vì time.time()
    stack = [(start, [])]
    visited = set()
    states_explored = 0

    while stack:
        state, path = stack.pop()
        key = (state.state, state.boat_side)

        if key in visited:
            continue
        visited.add(key)
        states_explored += 1

        if state.is_goal():
            solution_path = path + [state]
            exec_time = time.perf_counter() - start_time
            solution_length = len(solution_path) - 1
            cost = state.cost
            return solution_path, exec_time, states_explored, solution_length, cost

        for next_state in generate_moves(state):
            stack.append((next_state, path + [state]))
    return None, time.perf_counter() - start_time, states_explored, None, None


def ucs(start):
    start_time = time.perf_counter()  # Dùng perf_counter thay vì time.time()
    count = 0
    pq = [(0, count, start, [])]
    visited = {}
    states_explored = 0

    while pq:
        cost, _, state, path = heapq.heappop(pq)
        key = (state.state, state.boat_side)

        if key in visited and visited[key] <= state.cost:
            continue

        visited[key] = state.cost
        states_explored += 1

        if state.is_goal():
            solution_path = path + [state]
            exec_time = time.perf_counter() - start_time
            solution_length = len(solution_path) - 1
            return solution_path, exec_time, states_explored, solution_length, state.cost

        for next_state in generate_moves(state):
            new_cost = next_state.cost
            count += 1
            heapq.heappush(pq, (new_cost, count, next_state, path + [state]))

    return None, time.perf_counter() - start_time, states_explored, None, None


def greedy(start):
    start_time = time.perf_counter()  # Dùng perf_counter thay vì time.time()
    count = 0
    pq = [(heuristic(start), count, start, [])]
    visited = set()
    states_explored = 0

    while pq:
        h, _, state, path = heapq.heappop(pq)
        key = (state.state, state.boat_side)

        if key in visited:
            continue
        visited.add(key)
        states_explored += 1

        if state.is_goal():
            solution_path = path + [state]
            exec_time = time.perf_counter() - start_time
            solution_length = len(solution_path) - 1
            cost = state.cost
            return solution_path, exec_time, states_explored, solution_length, cost

        for next_state in generate_moves(state):
            count += 1
            heapq.heappush(pq, (heuristic(next_state), count, next_state, path + [state]))

    return None, time.perf_counter() - start_time, states_explored, None, None


def astar(start):
    start_time = time.perf_counter()  # Dùng perf_counter thay vì time.time()
    count = 0
    pq = [(heuristic(start), count, start, [])]
    visited = {}
    states_explored = 0

    while pq:
        f, _, state, path = heapq.heappop(pq)
        key = (state.state, state.boat_side)

        if key in visited and visited[key] <= state.cost:
            continue

        visited[key] = state.cost
        states_explored += 1

        if state.is_goal():
            solution_path = path + [state]
            exec_time = time.perf_counter() - start_time
            solution_length = len(solution_path) - 1
            return solution_path, exec_time, states_explored, solution_length, state.cost

        for next_state in generate_moves(state):
            g_new = next_state.cost
            h_new = heuristic(next_state)
            f_new = g_new + h_new

            count += 1
            heapq.heappush(pq, (f_new, count, next_state, path + [state]))

    return None, time.perf_counter() - start_time, states_explored, None, None


def hint(state):
    path, _, _, _, _ = bfs(state)

    if path and len(path) > 1:
        return path[1]

    return None