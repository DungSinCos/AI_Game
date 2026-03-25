# ai.py
from collections import deque
import heapq
import copy


def generate_moves(state):
    """
    Tạo tất cả các nước đi hợp lệ từ trạng thái hiện tại
    """
    moves = []
    characters = state.characters
    name_to_idx = state.name_to_idx

    # Lấy vị trí thuyền hiện tại
    boat_side = state.get_boat_side()

    # Lấy danh sách nhân vật ở cùng bờ với thuyền
    available_chars = [char for char in characters if state.state[name_to_idx[char]] == boat_side]

    # Sức chứa thuyền
    capacity = state.boat_config.get("capacity", 2)

    # Tạo các tổ hợp nhân vật lên thuyền
    # Luôn có người lái (nếu yêu cầu)
    drivers = state.boat_config.get("drivers", [])
    requires_driver = state.boat_config.get("requires_driver", False)

    if requires_driver:
        # Chỉ xét các tổ hợp có người lái
        available_drivers = [d for d in drivers if d in available_chars]
        for driver in available_drivers:
            driver_idx = name_to_idx[driver]

            # Trường hợp chỉ có người lái
            moves.append([driver_idx])

            # Kết hợp với các nhân vật khác
            other_chars = [c for c in available_chars if c != driver]
            for other in other_chars:
                if len([driver_idx, name_to_idx[other]]) <= capacity:
                    moves.append([driver_idx, name_to_idx[other]])
    else:
        # Không cần người lái, có thể chọn bất kỳ tổ hợp nào
        # Single character moves
        for char in available_chars:
            moves.append([name_to_idx[char]])

        # Pair moves
        if capacity >= 2:
            for i in range(len(available_chars)):
                for j in range(i + 1, len(available_chars)):
                    moves.append([name_to_idx[available_chars[i]], name_to_idx[available_chars[j]]])

    # Lọc các nước đi hợp lệ
    valid_moves = []
    for move_indices in moves:
        new_state = state.move(move_indices)
        if new_state:
            valid_moves.append(new_state)

    return valid_moves


def heuristic(state):
    """
    Heuristic function cho A* search
    Ước lượng số bước còn lại để hoàn thành
    """
    characters = state.characters
    state_tuple = state.state

    # Số nhân vật chưa qua sông
    remaining = sum(1 for side in state_tuple if side == 0)

    # Heuristic đơn giản: số nhân vật còn lại
    # Có thể cải thiện bằng cách tính khoảng cách Manhattan
    return remaining


def heuristic_advanced(state):
    """
    Heuristic nâng cao hơn cho các level phức tạp
    """
    characters = state.characters
    state_tuple = state.state
    boat_side = state.get_boat_side()

    # Số nhân vật chưa qua sông
    remaining = sum(1 for side in state_tuple if side == 0)

    # Bonus nếu thuyền ở bờ trái (có thể chở thêm người)
    if boat_side == 0:
        remaining = max(0, remaining - 1)

    # Penalty cho các cặp nguy hiểm
    danger_penalty = 0
    state_dict = {characters[i]: state_tuple[i] for i in range(len(characters))}

    # Kiểm tra các rule nguy hiểm
    for rule in state.rules:
        if "if_alone" in rule:
            alone_chars = rule["if_alone"]
            if state._are_together(state_dict, alone_chars):
                unless_present = rule.get("unless_present", [])
                if unless_present:
                    side = state_dict[alone_chars[0]]
                    if not state._is_any_present(state_dict, unless_present, side):
                        danger_penalty += 2
                else:
                    danger_penalty += 1

    return remaining + danger_penalty


def bfs(start):
    """
    Breadth-First Search - Tìm đường đi ngắn nhất
    """
    if start.is_goal():
        return [start]

    queue = deque([(start, [start])])
    visited = set()
    visited.add(start.state)

    while queue:
        current_state, path = queue.popleft()

        for next_state in generate_moves(current_state):
            if next_state.state not in visited:
                visited.add(next_state.state)
                new_path = path + [next_state]

                if next_state.is_goal():
                    return new_path

                queue.append((next_state, new_path))

    return None


def dfs(start, max_depth=100):
    """
    Depth-First Search với giới hạn độ sâu
    """
    if start.is_goal():
        return [start]

    stack = [(start, [start])]
    visited = set()
    visited.add(start.state)

    while stack:
        current_state, path = stack.pop()

        if len(path) > max_depth:
            continue

        for next_state in generate_moves(current_state):
            if next_state.state not in visited:
                visited.add(next_state.state)
                new_path = path + [next_state]

                if next_state.is_goal():
                    return new_path

                stack.append((next_state, new_path))

    return None


def dfs_recursive(state, path, visited, max_depth):
    """
    DFS đệ quy (dùng cho các bài toán có độ sâu lớn)
    """
    if state.is_goal():
        return path

    if len(path) > max_depth:
        return None

    for next_state in generate_moves(state):
        if next_state.state not in visited:
            visited.add(next_state.state)
            result = dfs_recursive(next_state, path + [next_state], visited, max_depth)
            if result:
                return result
            visited.remove(next_state.state)

    return None


def astar(start, use_advanced_heuristic=True):
    """
    A* Search Algorithm
    """
    if start.is_goal():
        return [start]

    heuristic_func = heuristic_advanced if use_advanced_heuristic else heuristic

    # Priority queue: (f_score, g_score, state, path)
    pq = [(heuristic_func(start), 0, start, [start])]
    visited = {}  # state -> g_score

    while pq:
        f, g, current_state, path = heapq.heappop(pq)

        # Kiểm tra nếu đã tìm thấy đường đi tốt hơn
        if current_state.state in visited and visited[current_state.state] <= g:
            continue

        visited[current_state.state] = g

        for next_state in generate_moves(current_state):
            new_g = g + 1
            new_f = new_g + heuristic_func(next_state)

            if next_state.is_goal():
                return path + [next_state]

            # Chỉ thêm vào queue nếu chưa thăm hoặc tìm được đường đi tốt hơn
            if next_state.state not in visited or visited[next_state.state] > new_g:
                heapq.heappush(pq, (new_f, new_g, next_state, path + [next_state]))

    return None


def ida_star(start, use_advanced_heuristic=True):
    """
    Iterative Deepening A* - Tiết kiệm bộ nhớ hơn A* thông thường
    """
    heuristic_func = heuristic_advanced if use_advanced_heuristic else heuristic

    def search(path, g, bound):
        current = path[-1]
        f = g + heuristic_func(current)

        if f > bound:
            return f
        if current.is_goal():
            return "FOUND"

        min_f = float('inf')
        for next_state in generate_moves(current):
            if next_state not in path:  # Tránh vòng lặp
                path.append(next_state)
                result = search(path, g + 1, bound)
                if result == "FOUND":
                    return "FOUND"
                if isinstance(result, (int, float)) and result < min_f:
                    min_f = result
                path.pop()

        return min_f

    bound = heuristic_func(start)
    path = [start]

    while True:
        result = search(path, 0, bound)
        if result == "FOUND":
            return path
        if result == float('inf'):
            return None
        bound = result


def hint(state):
    """
    Gợi ý nước đi tiếp theo (sử dụng BFS để tìm đường đi ngắn nhất)
    """
    solution = bfs(state)
    if solution and len(solution) > 1:
        return solution[1]
    return None


def get_solution_info(solution):
    """
    Lấy thông tin về lời giải
    """
    if not solution:
        return {
            "found": False,
            "steps": 0,
            "path": []
        }

    return {
        "found": True,
        "steps": len(solution) - 1,
        "path": solution
    }


def compare_algorithms(start_state):
    """
    So sánh hiệu suất của các thuật toán (dùng để debug)
    """
    import time

    results = {}

    # BFS
    start_time = time.time()
    bfs_sol = bfs(start_state)
    bfs_time = time.time() - start_time
    results["BFS"] = {
        "found": bfs_sol is not None,
        "steps": len(bfs_sol) - 1 if bfs_sol else 0,
        "time": bfs_time
    }

    # DFS
    start_time = time.time()
    dfs_sol = dfs(start_state)
    dfs_time = time.time() - start_time
    results["DFS"] = {
        "found": dfs_sol is not None,
        "steps": len(dfs_sol) - 1 if dfs_sol else 0,
        "time": dfs_time
    }

    # A*
    start_time = time.time()
    astar_sol = astar(start_state)
    astar_time = time.time() - start_time
    results["A*"] = {
        "found": astar_sol is not None,
        "steps": len(astar_sol) - 1 if astar_sol else 0,
        "time": astar_time
    }

    return results