from itertools import combinations

class GameState:
    def __init__(self, characters, state=None, level=1, boat_capacity=2, rules=None, level_data=None):
        self.characters = characters
        self.level = level
        self.level_data = level_data or {}
        self.boat_capacity = boat_capacity
        self.rules = rules or {"type": "classic"}
        self.state = state if state else tuple([0] * len(characters))
        self.moves = 0

    # ========================
    # CHECK STATE HỢP LỆ
    # ========================
    def is_valid(self, state=None):
        state = state if state else self.state

        # 🔹 LEVEL 3: simple → luôn hợp lệ
        if self.rules["type"] == "simple":
            return True

        # 🔹 fallback (sau này thêm rule khác)
        return True

    # ========================
    # CHECK WIN
    # ========================
    def is_goal(self):
        return all(x == 1 for x in self.state)

    # ========================
    # MOVE
    # ========================
    def move(self, move_indices):
        # quá số người trên thuyền
        if len(move_indices) > self.boat_capacity:
            return None

        boat_side = self.state[0]

        # tất cả phải cùng bờ với người
        for i in move_indices:
            if self.state[i] != boat_side:
                return None

        new_state = list(self.state)

        # người luôn di chuyển
        new_state[0] = 1 - new_state[0]

        for i in move_indices:
            if i != 0:
                new_state[i] = 1 - new_state[i]

        new_state = tuple(new_state)

        # check valid (level 3 luôn true)
        if not self.is_valid(new_state):
            return None

        new_state_obj = GameState(
            self.characters,
            new_state,
            self.level,
            self.boat_capacity,
            self.rules,
            self.level_data
        )
        new_state_obj.moves = self.moves + 1

        return new_state_obj

    # ========================
    # GET ALL POSSIBLE MOVES
    # ========================
    def get_possible_moves(self):
        boat_side = self.state[0]

        # các nhân vật cùng bờ
        same_side = [i for i, v in enumerate(self.state) if v == boat_side]

        all_moves = []

        for r in range(1, self.boat_capacity + 1):
            for combo in combinations(same_side, r):

                # bắt buộc có người
                if 0 not in combo:
                    continue

                new_state = self.move(combo)
                if new_state:
                    all_moves.append(new_state)

        return all_moves
