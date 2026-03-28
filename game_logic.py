# game_logic.py
class GameState:
    def __init__(self, characters, state=None, level=1, boat_capacity=2, rules=None, level_data=None):
        self.characters = characters
        self.level = level
        self.level_data = level_data or {}
        self.boat_capacity = boat_capacity
        self.rules = rules or {"type": "classic"}
        self.state = state if state else tuple([0] * len(characters))
        self.cost = 0  # for UCS and A*

    def is_valid(self, state=None):
        if state is None:
            state = self.state

        # Level 1: Classic wolf-sheep-cabbage
        if self.level == 1:
            p, w, s, c = state
            if w == s and p != w:
                return False
            if s == c and p != s:
                return False

        # Level 2: No constraints
        elif self.level == 2:
            # Không có ràng buộc
            pass

        # Level 3: Scientist and bomb
        elif self.level == 3:
            chars = self.characters
            idx = {c: i for i, c in enumerate(chars)}
            scientist_pos = state[idx["scientist"]]
            bom_pos = state[idx["bom"]]
            robot1_pos = state[idx["robot1"]]
            robot2_pos = state[idx["robot2"]]

            # Bom và robot không được ở cùng bờ nếu không có scientist
            if bom_pos == robot1_pos and scientist_pos != bom_pos:
                return False
            if bom_pos == robot2_pos and scientist_pos != bom_pos:
                return False

        # Level 4: Weight limit handled in move
        # Level 5: No special validation needed

        return True

    def is_goal(self):
        return all(x == 1 for x in self.state)

    def get_weight(self, items):
        """Tính tổng trọng lượng của các vật được chọn (Level 4)"""
        if self.level != 4:
            return 0

        weights = self.level_data.get("weights", {})
        total = 0
        for item in items:
            if item != "person":  # person không tính trọng lượng
                total += weights.get(item, 0)
        return total

    def move(self, move_indices):
        """
        move_indices: list of indices to move (includes person)
        """
        # Kiểm tra sức chứa thuyền
        if len(move_indices) > self.boat_capacity:
            return None

        # Level 4: Kiểm tra trọng lượng
        if self.level == 4:
            item_names = [self.characters[i] for i in move_indices]
            total_weight = self.get_weight(item_names)
            weight_limit = self.level_data.get("weight_limit", 100)
            if total_weight > weight_limit:
                return None

        new_state = list(self.state)
        # Đảo vị trí người và các vật được chọn
        new_state[0] = 1 - new_state[0]  # person always moves

        for idx in move_indices:
            if idx != 0:  # không đảo person lần nữa
                new_state[idx] = 1 - new_state[idx]

        new_state = tuple(new_state)

        if not self.is_valid(new_state):
            return None

        # Tính cost cho Level 5 (thời gian)
        new_cost = self.cost
        if self.level == 5:
            # Tính thời gian di chuyển dựa trên vật chậm nhất
            tiger_times = self.level_data.get("tiger_times", {})
            max_time = 0
            for idx in move_indices:
                if idx != 0:
                    item_name = self.characters[idx]
                    max_time = max(max_time, tiger_times.get(item_name, 1))
            new_cost = self.cost + max_time

        new_state_obj = GameState(
            self.characters,
            new_state,
            self.level,
            self.boat_capacity,
            self.rules,
            self.level_data
        )
        new_state_obj.cost = new_cost
        return new_state_obj

    def __hash__(self):
        return hash(self.state)

    def __eq__(self, other):
        return self.state == other.state