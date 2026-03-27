from collections import deque
import heapq
from game_logic import GameState

# --- 1. HÀM HỖ TRỢ (Dùng chung cho các thuật toán) ---
def generate_moves(state):
    # Mapping từ tên sang chỉ số (index) tương ứng trong trạng thái (0,0,0,0)
    name_to_idx = {"person": 0, "wolf": 1, "sheep": 2, "cabbage": 3}
    names = ["person", "wolf", "sheep", "cabbage"]
    moves = []

    for item in names:
        # Tạo danh sách chứa chỉ số (số nguyên), không phải chứa chữ (string)
        selected_indices = [name_to_idx["person"]] 
        if item != "person":
            selected_indices.append(name_to_idx[item])

        # Truyền danh sách số vào hàm move của Hoa
        new_state = state.move(selected_indices)
        if new_state:
            moves.append(new_state)

    return moves

# --- 2. THUẬT TOÁN BFS (Tìm đường ngắn nhất) ---
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

# --- 3. THUẬT TOÁN DFS (Tìm đường bất kỳ) ---
def dfs(start):
    stack = [(start, [])]
    visited = set()

    while stack:
        state, path = stack.pop() # LIFO - Lấy cuối cùng

        if state.state in visited:
            continue
        visited.add(state.state)

        if state.is_goal():
            return path + [state]

        for next_state in generate_moves(state):
            stack.append((next_state, path + [state]))
    return None

# --- 4. THUẬT TOÁN A* (Tìm kiếm tối ưu với Heuristic) ---
def heuristic(state):
    """Ước lượng: Càng nhiều vật bên bờ trái (0), giá trị càng cao"""
    return sum(1 for x in state.state if x == 0)

# --- 6. THUẬT TOÁN UCS (Uniform Cost Search) ---
def ucs(start):
    count = 0
    # (cost, count, state, path)
    pq = [(0, count, start, [])]
    visited = {}

    while pq:
        g, _, state, path = heapq.heappop(pq)

        if state.state in visited and visited[state.state] <= g:
            continue
        visited[state.state] = g

        if state.is_goal():
            return path + [state]

        for next_state in generate_moves(state):
            count += 1
            heapq.heappush(pq, (g + 1, count, next_state, path + [state]))
    return None

# --- 7. THUẬT TOÁN GREEDY BEST-FIRST SEARCH ---
def greedy(start):
    count = 0
    # (h, count, state, path)
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

# --- 8. THUẬT TOÁN A* (Duy đã có, đây là bản tối ưu hơn) ---
def astar(start):
    count = 0
    # (f, count, g, state, path)
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
            new_g = g + 1
            new_f = new_g + heuristic(next_state)
            count += 1
            heapq.heappush(pq, (new_f, count, new_g, next_state, path + [state]))
    return None

# --- 5. GỢI Ý (Hint) ---
def hint(state):
    """Dùng BFS để gợi ý bước đi tiếp theo tối ưu nhất"""
    sol = bfs(state)
    if sol and len(sol) > 1:
        return sol[1]
    return None