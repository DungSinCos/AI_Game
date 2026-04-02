from itertools import combinations


class GameState:
    def __init__(self, characters, state=None, level=1, boat_capacity=2, rules=None, level_data=None, boat_side=0):
        self.characters = characters
        self.level = level
        self.level_data = level_data or {}
        self.boat_capacity = boat_capacity
        self.rules = rules or {"type": "classic"}
        self.state = tuple(state) if state is not None else tuple([0] * len(characters))
        self.boat_side = boat_side
        self.moves = 0
        self.cost = 0

    # ========================
    # CHECK STATE HỢP LỆ
    # ========================
    def is_valid(self, state=None):
        state = state if state is not None else self.state

        if self.level == 1:
            return self._validate_classic(state)
        elif self.level == 2:
            return self._validate_sheep(state)
        elif self.level == 3:
            return self._validate_simple(state)
        elif self.level == 4:
            return self._validate_weight(state)
        elif self.level == 5:
            return self._validate_tiger(state)
        elif self.level == 6:
            return self._validate_special_people(state)
        elif self.level == 7:
            return self._validate_timed_bomb(state)
        elif self.level == 8:
            return self._validate_level8(state)
        elif self.level == 9:
            return self._validate_robot_light(state)
        elif self.level == 10:
            return self._validate_pure_balance(state)
        return True

    def _validate_special_people(self, state):
        """Level 6: Chỉ kiểm tra Lười không ở một mình trên bờ"""
        lazy_idx = self.characters.index("scientist1")
        brave1_idx = self.characters.index("person1")
        brave2_idx = self.characters.index("person2")
        arrogant_idx = self.characters.index("scientist2")

        for side in [0, 1]:
            if state[lazy_idx] == side:
                other_people = 0
                if state[brave1_idx] == side:
                    other_people += 1
                if state[brave2_idx] == side:
                    other_people += 1
                if state[arrogant_idx] == side:
                    other_people += 1
                if other_people == 0:
                    return False
        return True

    def _validate_classic(self, state):
        person_idx = self.characters.index("person")
        wolf_idx = self.characters.index("wolf")
        sheep_idx = self.characters.index("sheep")
        cabbage_idx = self.characters.index("cabbage")

        for side in [0, 1]:
            person_here = (state[person_idx] == side)
            if not person_here:
                if state[wolf_idx] == side and state[sheep_idx] == side:
                    return False
                if state[sheep_idx] == side and state[cabbage_idx] == side:
                    return False
        return True

    def _validate_sheep(self, state):
        person_idx = self.characters.index("person")
        sheep_indices = [i for i, name in enumerate(self.characters) if name.startswith("sheep")]

        for side in [0, 1]:
            person_here = (state[person_idx] == side)
            if not person_here:
                sheep_on_bank = [i for i in sheep_indices if state[i] == side]
                for i in range(len(sheep_on_bank)):
                    for j in range(i + 1, len(sheep_on_bank)):
                        age1 = int(self.characters[sheep_on_bank[i]][-1])
                        age2 = int(self.characters[sheep_on_bank[j]][-1])
                        if abs(age1 - age2) == 1:
                            return False
        return True

    def _validate_simple(self, state):
        return True

    def _validate_weight(self, state):
        person_idx = self.characters.index("person")
        box_small_idx = self.characters.index("box_small")
        box_medium_idx = self.characters.index("box_medium")
        box_large_idx = self.characters.index("box_large")

        for side in [0, 1]:
            person_here = (state[person_idx] == side)
            if not person_here:
                if state[box_small_idx] == side and state[box_medium_idx] == side:
                    return False
                if state[box_small_idx] == side and state[box_large_idx] == side:
                    return False
        return True

    def _validate_tiger(self, state):
        return True

    def _validate_timed_bomb(self, state):
        person_idx = self.characters.index("person")
        wolf_idx = self.characters.index("wolf")
        sheep_idx = self.characters.index("sheep")

        for side in [0, 1]:
            person_here = (state[person_idx] == side)
            if not person_here:
                if state[wolf_idx] == side and state[sheep_idx] == side:
                    return False
        return True

    def _validate_level8(self, state):
        person_idx = self.characters.index("person")
        wolf_idx = self.characters.index("wolf")
        sheep_idx = self.characters.index("sheep")
        bomb_idx = self.characters.index("bomb")

        for side in [0, 1]:
            person_here = (state[person_idx] == side)
            if not person_here:
                if state[wolf_idx] == side and state[sheep_idx] == side:
                    return False
                if state[bomb_idx] == side and state[sheep_idx] == side:
                    return False
        return True

    def _validate_robot_light(self, state):
        return True

    def _validate_pure_balance(self, state):
        tiger_indices = [i for i, name in enumerate(self.characters) if name.startswith("tiger")]
        wolf_indices = [i for i, name in enumerate(self.characters) if name.startswith("wolf")]

        for side in [0, 1]:
            num_tigers = sum(1 for i in tiger_indices if state[i] == side)
            num_wolves = sum(1 for i in wolf_indices if state[i] == side)
            if num_tigers > num_wolves and num_wolves > 0:
                return False
        return True


    def is_goal(self):
        return all(x == 1 for x in self.state)


    def move(self, move_indices):
        if len(move_indices) > self.boat_capacity:
            return None

        for i in move_indices:
            if self.state[i] != self.boat_side:
                return None


        if self.level == 6:
            arrogant_idx = self.characters.index("scientist2")
            lazy_idx = self.characters.index("scientist1")

            if arrogant_idx in move_indices and len(move_indices) > 1:
                return None

            if len(move_indices) == 1 and lazy_idx in move_indices:
                return None

            if lazy_idx in move_indices:
                has_driver = any(i != lazy_idx for i in move_indices)
                if not has_driver:
                    return None

        new_state = list(self.state)
        for i in move_indices:
            new_state[i] = 1 - new_state[i]
        new_state = tuple(new_state)

        # Kiểm tra trạng thái mới
        if not self.is_valid(new_state):
            return None

        new_state_obj = GameState(
            self.characters,
            new_state,
            self.level,
            self.boat_capacity,
            self.rules,
            self.level_data,
            boat_side=1 - self.boat_side
        )
        new_state_obj.moves = self.moves + 1
        move_cost = self.get_move_cost(move_indices)
        new_state_obj.cost = self.cost + move_cost  # Sửa: cost = số bước, không phải self.cost + 1

        return new_state_obj

    def get_move_cost(self, move_indices):
        if self.level == 5:
            tiger_times = self.level_data.get("tiger_times", {})
            max_time = 0
            for idx in move_indices:
                if idx != 0:
                    item_name = self.characters[idx]
                    if item_name in tiger_times:
                        max_time = max(max_time, tiger_times[item_name])
            return max_time
        return 1

    def get_possible_moves(self):
        same_side = [i for i, v in enumerate(self.state) if v == self.boat_side]
        all_moves = []

        if self.level == 6:
            for r in range(1, self.boat_capacity + 1):
                for combo in combinations(same_side, r):
                    new_state = self.move(combo)
                    if new_state:
                        all_moves.append(new_state)
        else:
            # Tìm tất cả người có thể lái thuyền
            driver_indices = []
            if "person" in self.characters:
                driver_indices.append(self.characters.index("person"))
            if "scientist" in self.characters:
                driver_indices.append(self.characters.index("scientist"))

            # Nếu không có người lái, cho phép bất kỳ ai
            if not driver_indices:
                for r in range(1, self.boat_capacity + 1):
                    for combo in combinations(same_side, r):
                        new_state = self.move(combo)
                        if new_state:
                            all_moves.append(new_state)
            else:
                # Xác định số lượng vật tối đa được chở
                max_items = self.boat_capacity - 1

                # Level 4 chỉ cho chở tối đa 1 vật
                if self.level == 4:
                    max_items = 1

                # Với mỗi người lái có thể
                for driver_idx in driver_indices:
                    # Kiểm tra người lái có ở cùng bờ
                    if self.state[driver_idx] != self.boat_side:
                        continue

                    other_indices = [i for i in same_side if i != driver_idx]

                    # Tạo các tổ hợp: người lái + 0 đến max_items vật
                    for r in range(0, max_items + 1):
                        for combo in combinations(other_indices, r):
                            move_indices = [driver_idx] + list(combo)
                            new_state = self.move(move_indices)
                            if new_state:
                                all_moves.append(new_state)

        return all_moves